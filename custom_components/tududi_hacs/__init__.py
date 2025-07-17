from homeassistant.core import HomeAssistant

DOMAIN = "tududi_hacs"

async def async_setup(hass: HomeAssistant, config: dict):
    hass.components.frontend.async_register_built_in_panel(
        component_name="iframe",
        sidebar_title="Tududi",
        sidebar_icon="mdi:checkbox-marked-outline",
        frontend_url_path="tududi",
        config={
            "url": "https://ha.guilatrien.com/local/tududi_hacs/panel.html"
        },
        require_admin=False
    )
    return True