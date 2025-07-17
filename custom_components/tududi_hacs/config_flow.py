from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback

DOMAIN = "tududi_hacs" # domain mentioned in manifest.json

class MyIntegrationConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for your HACS integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="TuDudi Panel", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("url"): str
            })
        )