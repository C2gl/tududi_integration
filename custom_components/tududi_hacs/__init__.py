"""Tududi web wrapper integration for Home Assistant."""
import os
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import HomeAssistantView

DOMAIN = "tududi_hacs"
_LOGGER = logging.getLogger(__name__)

# Path to the custom panel HTML file
PANEL_DIR = os.path.join(os.path.dirname(__file__), "panel")
PANEL_FILENAME = "tududi-panel.html"

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
                "module_url": f"/tududi_panel/tududi-panel.js",
            }
        },
    )

    # Register static directory for panel files
    hass.http.register_static_path(
        f"/{DOMAIN}_panel", PANEL_DIR, cache_headers=False
    )

    # Register the iframe view
    hass.http.register_view(TududiIframeView())

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Tududi from a config entry."""
    # Store entry data in hass.data
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # No need for forward_entry_setup since we're not using platform entities
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # Remove entry data from hass.data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return True

class TududiIframeView(HomeAssistantView):
    """View for serving the Tududi iframe."""

    requires_auth = False
    url = "/tududi/iframe"
    name = "tududi:iframe"

    async def get(self, request):
        """Return the iframe to the Tududi website."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tududi</title>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    overflow: hidden;
                }
                iframe {
                    width: 100%;
                    height: 100%;
                    border: none;
                }
            </style>
        </head>
        <body>
            <iframe src="https://tududi.com" allow="fullscreen"></iframe>
        </body>
        </html>
        """
        return web.Response(text=html, content_type="text/html")