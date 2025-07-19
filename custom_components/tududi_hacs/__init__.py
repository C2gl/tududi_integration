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
    
    # Remove stored panel configuration
    try:
        if DOMAIN + "_panels" in hass.data and entry.entry_id in hass.data[DOMAIN + "_panels"]:
            panel_info = hass.data[DOMAIN + "_panels"].pop(entry.entry_id)
            _LOGGER.info("Removed panel configuration for: %s", panel_info.get("title", panel_name))
    except Exception as e:
        _LOGGER.warning("Could not remove panel configuration %s: %s", panel_name, e)
    
    # Remove from frontend panels
    try:
        if hasattr(hass.data, "frontend_panels") and panel_name in hass.data.get("frontend_panels", {}):
            hass.data["frontend_panels"].pop(panel_name, None)
            # Trigger frontend refresh
            hass.bus.async_fire("frontend_panels_updated")
            _LOGGER.info("Removed frontend panel: %s", panel_name)
    except Exception as e:
        _LOGGER.warning("Could not remove frontend panel %s: %s", panel_name, e)
    
    # Clean up the HTML file asynchronously
    def remove_panel_file():
        """Remove panel file synchronously."""
        try:
            panel_file = Path(hass.config.path("www")) / "tududi_hacs" / f"panel_{entry.entry_id}.html"
            if panel_file.exists():
                panel_file.unlink()
                _LOGGER.info("Removed panel file: %s", panel_file)
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
    
    # Create panel configuration
    panel_name = f"tududi_{entry.entry_id}"
    panel_url = f"/local/tududi_hacs/panel_{entry.entry_id}.html"
    
    # Store panel configuration
    hass.data.setdefault(DOMAIN + "_panels", {})[entry.entry_id] = {
        "name": panel_name,
        "title": title,
        "icon": icon,
        "url": panel_url,
    }
    
    # Automatically register the panel using Home Assistant's frontend API
    try:
        # Use the async_register_built_in_panel method directly
        await hass.async_add_executor_job(
            _register_frontend_panel,
            hass,
            panel_name,
            title,
            icon,
            panel_url
        )
        _LOGGER.info("Successfully registered Tududi panel: %s", title)
    except Exception as e:
        _LOGGER.error("Failed to register panel automatically: %s", e)
        # Fallback: show manual configuration
        _LOGGER.error("Please add the following to your configuration.yaml manually:")
        _LOGGER.error("""
panel_custom:
  - name: %s
    sidebar_title: %s
    sidebar_icon: %s
    url_path: %s
    module_url: %s
    embed_iframe: true
    require_admin: false""", panel_name, title, icon, panel_name, panel_url)


def _register_frontend_panel(hass: HomeAssistant, panel_name: str, title: str, icon: str, panel_url: str) -> None:
    """Register panel with frontend synchronously."""
    try:
        # Access the frontend component and register the panel
        frontend = hass.components.frontend
        if hasattr(frontend, 'async_register_built_in_panel'):
            # Call the registration function directly
            frontend.async_register_built_in_panel(
                hass,
                component_name="iframe",
                sidebar_title=title,
                sidebar_icon=icon,
                frontend_url_path=panel_name,
                config={"url": panel_url, "title": title},
                require_admin=False,
            )
        else:
            # Alternative approach using the panel data structure
            if not hasattr(hass.data, "frontend_panels"):
                hass.data["frontend_panels"] = {}
            
            hass.data["frontend_panels"][panel_name] = {
                "component_name": "iframe", 
                "sidebar_title": title,
                "sidebar_icon": icon,
                "frontend_url_path": panel_name,
                "config": {"url": panel_url, "title": title},
                "require_admin": False,
            }
            
            # Trigger frontend refresh if possible
            hass.bus.async_fire("frontend_panels_updated")
            
    except Exception as e:
        _LOGGER.error("Failed to register frontend panel: %s", e)
        raise

