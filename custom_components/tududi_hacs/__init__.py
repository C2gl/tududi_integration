from homeassistant.core import HomeAssistant

DOMAIN = "tududi_hacs"

async def async_setup(hass: HomeAssistant, config: dict):
    hass.http.register_static_path(
        "/tududi-panel",
        hass.config.path("www/tududi_hacs/panel.html"),
        cache_headers=False,
    )
    hass.components.frontend.async_register_panel(
        component_name="custom",
        frontend_url_path="tududi",
        sidebar_title="Tududi",
        sidebar_icon="mdi:checkbox-marked-outline",
        config={},
        require_admin=False,
        module_url="/tududi-panel",
    )
    return True