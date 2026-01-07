"""Sensor platform for Tududi HACS integration."""
from __future__ import annotations

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
    CONF_TITLE,
    CONF_API_KEY,
    SENSOR_UPDATE_INTERVAL,
    SENSOR_TIMEOUT,
    API_BASE_PATH,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="next_todo",
        translation_key="next_todo",
        icon="mdi:clipboard-text",
    ),
    SensorEntityDescription(
        key="upcoming_todos_count",
        translation_key="upcoming_todos_count",
        icon="mdi:counter",
    ),
    SensorEntityDescription(
        key="today_todos_count",
        translation_key="today_todos_count",
        icon="mdi:calendar-today",
    ),
)


class TududiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Tududi data."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        api_key: Optional[str] = None,
    ) -> None:
        """Initialize the coordinator."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._session = None
        
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
            _LOGGER.warning("Error communicating with Tududi API: %s", exception)
            # Return empty data instead of raising exception so sensors stay available
            return {
                "next_todo": None,
                "upcoming_todos_count": 0,
                "today_todos_count": 0,
                "all_tasks": [],
            }

    async def async_shutdown(self) -> None:
        """Close the session when coordinator is shutting down."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _fetch_tududi_data(self) -> Dict[str, Any]:
        """Fetch data from Tududi API v1."""
        if not self.api_key:
            _LOGGER.debug("No API key configured, sensors will not function")
            return {
                "next_todo": None,
                "upcoming_todos_count": 0,
                "today_todos_count": 0,
                "all_tasks": [],
            }

        # Create or reuse session
        if not self._session or self._session.closed:
            connector = aiohttp.TCPConnector(force_close=True, enable_cleanup_closed=True)
            self._session = aiohttp.ClientSession(connector=connector)

        try:
            # Use the new API v1 endpoint
            tasks_url = f"{self.base_url}{API_BASE_PATH}/tasks"
            
            # Use Bearer token authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            }
            
            _LOGGER.debug("Fetching tasks from: %s", tasks_url)
            
            async with self._session.get(tasks_url, headers=headers) as response:
                if response.status == 401:
                    raise UpdateFailed("Authentication failed - invalid API key")
                elif response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Successfully fetched data from API v1")
                else:
                    response_text = await response.text()
                    raise UpdateFailed(f"API request failed: {response.status} - {response_text}")

            return await self._process_tududi_data(data)
            
        except UpdateFailed:
            raise
        except Exception as exception:
            _LOGGER.error("Error fetching Tududi data: %s", exception)
            raise UpdateFailed(f"Error fetching data: {exception}")

    async def _process_tududi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the fetched Tududi data."""
        _LOGGER.debug("Processing Tududi API response")
        
        # The API v1 returns tasks directly or in a wrapper
        # Check if tasks are in a wrapper object or directly in the response
        if isinstance(data, list):
            tasks = data
        else:
            tasks = data.get("tasks", data.get("data", []))
        
        _LOGGER.debug("Found %d tasks in API response", len(tasks))
        
        # Find the next upcoming todo
        next_todo = None
        upcoming_todos = []
        today_todos = []
        
        now = datetime.now()
        today_date = now.date()
        
        for task in tasks:
            # Skip completed tasks (status 2 = DONE in Tududi)
            if task.get("status") == 2:
                continue
                
            task_due_date = task.get("due_date")
            
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
            -x.get("priority", 0)  # Higher priority first
        ))
        
        # Sort today todos by priority
        today_todos.sort(key=lambda x: -x.get("priority", 0))
        
        # Get the next todo (today todos take precedence)
        if today_todos:
            next_todo = today_todos[0]
        elif upcoming_todos:
            next_todo = upcoming_todos[0]
        
        result = {
            "next_todo": next_todo,
            "upcoming_todos_count": len(upcoming_todos),
            "today_todos_count": len(today_todos),
            "all_tasks": tasks,
        }
        
        _LOGGER.debug("Processed data - Next todo: %s, Upcoming: %d, Today: %d", 
                     next_todo.get("name") if next_todo else None,
                     len(upcoming_todos), len(today_todos))
        
        return result


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tududi sensors based on a config entry."""
    base_url = config_entry.data[CONF_URL]
    api_key = config_entry.data.get(CONF_API_KEY)
    
    if not api_key:
        _LOGGER.warning(
            "No API key configured. Sensors will not function. "
            "Please configure an API key in the integration options."
        )
    
    coordinator = TududiDataUpdateCoordinator(hass, base_url, api_key)
    
    # Try to fetch initial data, but don't fail if it doesn't work
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning("Failed to fetch initial data: %s", err)
        # Continue anyway - sensors will show as unavailable until data is fetched
    
    entities = []
    for description in SENSOR_TYPES:
        entities.append(TududiSensor(coordinator, description, config_entry))
    
    async_add_entities(entities, update_before_add=False)


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
            "name": config_entry.data.get(CONF_TITLE, "Tududi"),
            "manufacturer": "Tududi",
            "model": "Task Manager",
            "sw_version": "2.0 (API v1)",
        }

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        title = self._config_entry.data.get(CONF_TITLE, "Tududi")
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
                # Handle both nested and flat project structure
                project_name = None
                if isinstance(next_todo.get("project"), dict):
                    project_name = next_todo["project"].get("name")
                elif isinstance(next_todo.get("Project"), dict):
                    project_name = next_todo["Project"].get("name")
                
                # Handle tags
                tags = []
                if isinstance(next_todo.get("tags"), list):
                    tags = [tag.get("name") for tag in next_todo["tags"] if isinstance(tag, dict)]
                elif isinstance(next_todo.get("Tags"), list):
                    tags = [tag.get("name") for tag in next_todo["Tags"] if isinstance(tag, dict)]
                
                attributes.update({
                    "task_id": next_todo.get("id"),
                    "description": next_todo.get("note", next_todo.get("description", "")),
                    "due_date": next_todo.get("due_date"),
                    "priority": next_todo.get("priority", 0),
                    "priority_name": self._get_priority_name(next_todo.get("priority", 0)),
                    "status": next_todo.get("status"),
                    "status_name": self._get_status_name(next_todo.get("status", 0)),
                    "project": project_name,
                    "tags": tags,
                    "today": next_todo.get("today", False),
                    "created_at": next_todo.get("created_at"),
                    "updated_at": next_todo.get("updated_at"),
                })
        
        # Add update timestamp
        attributes["last_updated"] = datetime.now().isoformat()
        
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # If no API key, mark as unavailable
        if not self.coordinator.api_key:
            return False
        return super().available

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