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

PLATFORMS: list[str] = ["sensor"]


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
    
    # Set up sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    # Reload the config entry to apply new settings
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Remove the panel
    await async_unregister_panel(hass, entry)
    
    # Clean up stored data
    hass.data[DOMAIN].pop(entry.entry_id, None)
    
    return unload_ok


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
        from homeassistant.components import frontend
        
        # Use the frontend component to remove the panel
        if panel_name in hass.data.get("frontend_panels", {}):
            frontend.async_remove_panel(hass, panel_name)
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
        # Import and use frontend component properly
        from homeassistant.components import frontend
        
        # Register the panel asynchronously
        frontend.async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title=title,
            sidebar_icon=icon,
            frontend_url_path=panel_name,
            config={"url": panel_url, "title": title},
            require_admin=False,
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



