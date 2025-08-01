"""Sensor platform for Tududi HACS integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import aiohttp
import async_timeout
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_URL,
    CONF_USERNAME,
    CONF_PASSWORD,
    SENSOR_UPDATE_INTERVAL,
    SENSOR_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="next_todo",
        name="Next Todo",
        icon="mdi:clipboard-text",
    ),
    SensorEntityDescription(
        key="upcoming_todos_count",
        name="Upcoming Todos Count",
        icon="mdi:counter",
    ),
    SensorEntityDescription(
        key="today_todos_count",
        name="Today Todos Count",
        icon="mdi:calendar-today",
    ),
)


class TududiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Tududi data."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """Initialize the coordinator."""
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self._session_cookies = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SENSOR_UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Update data via library."""
        try:
            async with async_timeout.timeout(SENSOR_TIMEOUT):
                return await self._fetch_tududi_data()
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with Tududi API: {exception}")

    async def _authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate with Tududi server."""
        if not self.username or not self.password:
            _LOGGER.debug("No credentials provided, trying without authentication")
            return True

        try:
            # Login to Tududi
            login_url = f"{self.base_url}/api/auth/login"
            login_data = {
                "email": self.username,
                "password": self.password,
            }
            
            async with session.post(login_url, json=login_data) as response:
                if response.status == 200:
                    # Store session cookies for future requests
                    self._session_cookies = session.cookie_jar
                    _LOGGER.debug("Successfully authenticated with Tududi")
                    return True
                else:
                    _LOGGER.error(
                        "Failed to authenticate with Tududi: %s", response.status
                    )
                    return False
                    
        except Exception as exception:
            _LOGGER.error("Authentication error: %s", exception)
            return False

    async def _fetch_tududi_data(self) -> Dict[str, Any]:
        """Fetch data from Tududi API."""
        connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # Restore session cookies if available
            if self._session_cookies:
                session.cookie_jar = self._session_cookies
            
            # Authenticate if credentials are provided
            if not await self._authenticate(session):
                raise UpdateFailed("Authentication failed")

            try:
                # Fetch tasks with metrics
                tasks_url = f"{self.base_url}/api/tasks?type=upcoming&order_by=due_date"
                
                async with session.get(tasks_url) as response:
                    if response.status == 401:
                        # Session expired, try to re-authenticate
                        if await self._authenticate(session):
                            async with session.get(tasks_url) as retry_response:
                                if retry_response.status == 200:
                                    data = await retry_response.json()
                                else:
                                    raise UpdateFailed(f"API request failed: {retry_response.status}")
                        else:
                            raise UpdateFailed("Authentication failed")
                    elif response.status == 200:
                        data = await response.json()
                    else:
                        raise UpdateFailed(f"API request failed: {response.status}")

                return await self._process_tududi_data(data)
                
            except Exception as exception:
                _LOGGER.error("Error fetching Tududi data: %s", exception)
                raise UpdateFailed(f"Error fetching data: {exception}")

    async def _process_tududi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the fetched Tududi data."""
        tasks = data.get("tasks", [])
        metrics = data.get("metrics", {})
        
        # Find the next upcoming todo
        next_todo = None
        upcoming_todos = []
        today_todos = []
        
        now = datetime.now()
        today_date = now.date()
        
        for task in tasks:
            # Skip completed tasks
            if task.get("status") in [2, "done"]:  # 2 is DONE status
                continue
                
            task_due_date = task.get("due_date")
            task_name = task.get("name", "Unnamed Task")
            task_priority = task.get("priority", 0)
            
            # Parse due date if available
            due_date = None
            if task_due_date:
                try:
                    due_date = datetime.fromisoformat(task_due_date.replace('Z', '+00:00')).date()
                except ValueError:
                    try:
                        due_date = datetime.strptime(task_due_date, "%Y-%m-%d").date()
                    except ValueError:
                        _LOGGER.warning("Could not parse due date: %s", task_due_date)
            
            # Categorize tasks
            if due_date == today_date or task.get("today", False):
                today_todos.append(task)
            elif due_date and due_date > today_date:
                upcoming_todos.append(task)
            elif not due_date:  # Tasks without due date
                upcoming_todos.append(task)
        
        # Sort upcoming todos by due date and priority
        upcoming_todos.sort(key=lambda x: (
            datetime.fromisoformat(x.get("due_date", "9999-12-31").replace('Z', '+00:00')).date() 
            if x.get("due_date") else datetime(9999, 12, 31).date(),
            -x.get("priority", 0)  # Higher priority first (negative for reverse sort)
        ))
        
        # Sort today todos by priority
        today_todos.sort(key=lambda x: -x.get("priority", 0))
        
        # Get the next todo (today todos take precedence)
        if today_todos:
            next_todo = today_todos[0]
        elif upcoming_todos:
            next_todo = upcoming_todos[0]
        
        # Also check suggested tasks from metrics
        suggested_tasks = metrics.get("suggested_tasks", [])
        if not next_todo and suggested_tasks:
            # Filter out completed suggested tasks
            active_suggested = [t for t in suggested_tasks if t.get("status") not in [2, "done"]]
            if active_suggested:
                next_todo = active_suggested[0]
        
        return {
            "next_todo": next_todo,
            "upcoming_todos_count": len(upcoming_todos),
            "today_todos_count": len(today_todos),
            "all_tasks": tasks,
            "metrics": metrics,
        }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tududi sensors based on a config entry."""
    base_url = config_entry.data[CONF_URL]
    username = config_entry.data.get(CONF_USERNAME)
    password = config_entry.data.get(CONF_PASSWORD)
    
    coordinator = TududiDataUpdateCoordinator(
        hass, base_url, username, password
    )
    
    # Fetch initial data so we have data when entities are added
    await coordinator.async_config_entry_first_refresh()
    
    entities = []
    for description in SENSOR_TYPES:
        entities.append(TududiSensor(coordinator, description, config_entry))
    
    async_add_entities(entities, update_before_add=True)


class TududiSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a Tududi sensor."""

    def __init__(
        self,
        coordinator: TududiDataUpdateCoordinator,
        description: SensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._config_entry = config_entry
        
        # Set unique_id
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        
        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, config_entry.entry_id)},
            "name": config_entry.data.get(CONF_URL, "Tududi"),
            "manufacturer": "Tududi",
            "model": "Task Manager",
            "sw_version": "1.0",
        }

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        title = self._config_entry.data.get("title", "Tududi")
        return f"{title} {self.entity_description.name}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        if self.entity_description.key == "next_todo":
            next_todo = self.coordinator.data.get("next_todo")
            if next_todo:
                return next_todo.get("name", "Unnamed Task")
            return "No upcoming todos"
            
        elif self.entity_description.key == "upcoming_todos_count":
            return self.coordinator.data.get("upcoming_todos_count", 0)
            
        elif self.entity_description.key == "today_todos_count":
            return self.coordinator.data.get("today_todos_count", 0)
            
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}
            
        attributes = {}
        
        if self.entity_description.key == "next_todo":
            next_todo = self.coordinator.data.get("next_todo")
            if next_todo:
                attributes.update({
                    "task_id": next_todo.get("id"),
                    "description": next_todo.get("note", ""),
                    "due_date": next_todo.get("due_date"),
                    "priority": next_todo.get("priority", 0),
                    "priority_name": self._get_priority_name(next_todo.get("priority", 0)),
                    "status": next_todo.get("status"),
                    "status_name": self._get_status_name(next_todo.get("status", 0)),
                    "project": next_todo.get("project", {}).get("name") if next_todo.get("project") else None,
                    "tags": [tag.get("name") for tag in next_todo.get("tags", [])],
                    "today": next_todo.get("today", False),
                    "created_at": next_todo.get("created_at"),
                    "updated_at": next_todo.get("updated_at"),
                })
        
        # Add metrics data for all sensors
        metrics = self.coordinator.data.get("metrics", {})
        if metrics:
            attributes.update({
                "total_open_tasks": metrics.get("total_open_tasks", 0),
                "tasks_in_progress_count": metrics.get("tasks_in_progress_count", 0),
                "last_updated": datetime.now().isoformat(),
            })
        
        return attributes

    def _get_priority_name(self, priority: int) -> str:
        """Convert priority number to name."""
        priority_map = {
            0: "Low",
            1: "Medium", 
            2: "High",
            3: "Critical"
        }
        return priority_map.get(priority, "Unknown")

    def _get_status_name(self, status: int) -> str:
        """Convert status number to name."""
        status_map = {
            0: "Not Started",
            1: "In Progress",
            2: "Done",
            3: "Waiting",
            4: "Archived"
        }
        return status_map.get(status, "Unknown")
