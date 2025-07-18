""" Tududi HACS integration for Home Assistant. """




async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up the Tududi HACS integration from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
    
    url = entry.data[CONF_URL]

    client = await hass.async_add_executor_job(
        
)