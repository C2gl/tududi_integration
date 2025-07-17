from homeassistant.core import HomeAssistant
from homeassistant.components.http.static import StaticPathConfig


DOMAIN = "tududi_hacs"

async def async_setup(hass: HomeAssistant, config: dict):
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            url_path="/tududi-panel",
            file_path=hass.config.path("www/tududi_hacs/panel.html"),
            cache_headers=False,
        )
    ])
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