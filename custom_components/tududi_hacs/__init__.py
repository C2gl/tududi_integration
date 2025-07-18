"""Tududi web wrapper integration for Home Assistant."""
import os
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.http.static import StaticPathConfig
from aiohttp import web

from .const import DOMAIN, DEFAULT_URL

_LOGGER = logging.getLogger(__name__)

# Path to the custom panel HTML file
PANEL_DIR = os.path.join(os.path.dirname(__file__), "panel")

async def async_setup(hass: HomeAssistant, config):
    """Set up the Tududi component."""
    # Register the panel
    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Tududi",
        sidebar_icon="mdi:calendar-check",
        frontend_url_path=DOMAIN,
        require_admin=False,
        config={
            "_panel_custom": {
                "name": "tududi-panel",
                "embed_iframe": True,
                "trust_external": True,
                "module_url": f"/{DOMAIN}_panel/tududi-panel.js",
            }
        },
    )

    # Register static directory for panel files - using the async method
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            f"/{DOMAIN}_panel", 
            PANEL_DIR, 
            cache_headers=False
        )
    ])

    # Register the iframe view
    hass.http.register_view(TududiIframeView())

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Tududi from a config entry."""
    # Store entry data in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Make data available to our panel JS
    hass.http.register_view(TududiConfigView(entry))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Remove entry data from hass.data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return True

class TududiConfigView(HomeAssistantView):
    """View to provide configuration data to the panel."""
    
    requires_auth = True
    url = "/api/tududi_hacs/config"
    name = "api:tududi_hacs:config"
    
    def __init__(self, config_entry):
        """Initialize with config entry."""
        self.config_entry = config_entry
        
    async def get(self, request):
        """Return the configuration data."""
        return web.json_response({
            "url": self.config_entry.data.get("url", DEFAULT_URL)
        })

class TududiIframeView(HomeAssistantView):
    """View for serving the Tududi iframe."""

    requires_auth = False
    url = "/tududi/iframe"
    name = "tududi:iframe"

    async def get(self, request):
        """Return the iframe to the Tududi website."""
        # Get the first config entry
        entries = request.app["hass"].config_entries.async_entries(DOMAIN)
        if entries:
            url = entries[0].data.get("url", DEFAULT_URL)
        else:
            url = DEFAULT_URL
            
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tududi</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                }}
                iframe {{
                    width: 100%;
                    height: 100%;
                    border: none;
                }}
            </style>
        </head>
        <body>
            <iframe src="{url}" allow="fullscreen"></iframe>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")