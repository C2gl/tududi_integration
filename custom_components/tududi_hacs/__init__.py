"""Tududi HACS integration for Home Assistant."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_URL, CONF_TITLE, CONF_ICON

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Tududi HACS component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tududi HACS from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Register the frontend panel
    await async_register_panel(hass, entry)
    
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    # Unregister the old panel
    await async_unregister_panel(hass, entry)
    
    # Register the new panel with updated config
    await async_register_panel(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the panel
    await async_unregister_panel(hass, entry)
    
    # Clean up stored data
    hass.data[DOMAIN].pop(entry.entry_id, None)
    
    return True


async def async_unregister_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unregister the panel and clean up files."""
    panel_name = f"tududi_{entry.entry_id}"
    
    # Remove the panel from frontend data
    if "frontend_panels" in hass.data and panel_name in hass.data["frontend_panels"]:
        hass.data["frontend_panels"].pop(panel_name, None)
    
    # Remove the panel from frontend component
    try:
        from homeassistant.components import frontend
        frontend.async_remove_panel(hass, panel_name)
    except Exception as e:
        _LOGGER.warning("Could not remove panel %s: %s", panel_name, e)
    
    # Clean up the HTML file asynchronously
    def remove_panel_file():
        """Remove panel file synchronously."""
        try:
            panel_file = Path(hass.config.path("www")) / "tududi_hacs" / f"panel_{entry.entry_id}.html"
            if panel_file.exists():
                panel_file.unlink()
        except Exception as e:
            _LOGGER.warning("Could not remove panel file: %s", e)
    
    await hass.async_add_executor_job(remove_panel_file)


async def async_register_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register the Tududi panel."""
    url = entry.data[CONF_URL]
    title = entry.data.get(CONF_TITLE, "Tududi")
    icon = entry.data.get(CONF_ICON, "mdi:clipboard-text")
    
    # Create the HTML content with the configured URL
    panel_html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <title>{title} HA Panel</title>
    <meta charset="UTF-8" />
  </head>
  <body style="margin:0;padding:0;height:100vh;width:100vw;overflow:hidden">
    <iframe src="{url}" width="100%" height="100%" style="border:none;"></iframe>
  </body>
</html>"""
    
    # Ensure the www directory exists
    www_dir = Path(hass.config.path("www"))
    panel_dir = www_dir / "tududi_hacs"
    
    def create_panel_files():
        """Create panel directory and file synchronously."""
        panel_dir.mkdir(parents=True, exist_ok=True)
        panel_file = panel_dir / f"panel_{entry.entry_id}.html"
        with open(panel_file, "w", encoding="utf-8") as f:
            f.write(panel_html_content)
    
    await hass.async_add_executor_job(create_panel_files)
    
    # Register the panel using the correct frontend API
    panel_name = f"tududi_{entry.entry_id}"
    panel_url = f"/local/tududi_hacs/panel_{entry.entry_id}.html"
    
    # Use the frontend service to register the panel
    hass.data.setdefault("frontend_panels", {})
    hass.data["frontend_panels"][panel_name] = {
        "component_name": "iframe",
        "sidebar_title": title,
        "sidebar_icon": icon,
        "frontend_url_path": panel_name,
        "config": {"url": panel_url, "title": title},
        "require_admin": False,
    }
    
    # Register with frontend component
    if hasattr(hass.components, "frontend"):
        from homeassistant.components import frontend
        frontend.async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title=title,
            sidebar_icon=icon,
            frontend_url_path=panel_name,
            config={"url": panel_url, "title": title},
            require_admin=False,
        )
    
    _LOGGER.info("Registered Tududi panel: %s at %s", title, url)