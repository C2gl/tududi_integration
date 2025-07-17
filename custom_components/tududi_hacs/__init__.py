from homeassistant.core import HomeAssistant

DOMAIN = "tududi_hacs"

async def async_setup(hass: HomeAssistant, config: dict):
    # Ensure frontend is loaded
    await hass.helpers.discovery.async_load_platform("frontend", DOMAIN, {}, config)

    # Import the register function directly
    from homeassistant.components.frontend import async_register_panel

    async_register_panel(
        hass,
        component_name="custom",
        frontend_url_path="tududi",
        sidebar_title="Tududi",
        sidebar_icon="mdi:checkbox-marked-outline",
        config={},
        require_admin=False,
        module_url="/local/tududi_hacs/panel.html",
    )
    return True