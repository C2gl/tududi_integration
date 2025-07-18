"""Config flow for Tududi integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_URL

class TududiFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tududi."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        
        if user_input is not None:
            # Save the URL from user input
            return self.async_create_entry(
                title="Tududi Web Panel",
                data={"url": user_input["url"]}
            )

        # Form with URL field
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("url", default=DEFAULT_URL): str
            })
        )