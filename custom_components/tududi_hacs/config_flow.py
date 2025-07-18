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
        
        errors = {}
        
        if user_input is not None:
            # Validate URL (basic validation)
            url = user_input["url"]
            if not url.startswith(("http://", "https://")):
                errors["url"] = "invalid_url"
            else:
                # Save the URL from user input
                return self.async_create_entry(
                    title="Tududi Web Panel",
                    data={"url": url}
                )

        # Form with URL field
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("url", default=DEFAULT_URL): str
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TududiOptionsFlowHandler(config_entry)


class TududiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Tududi options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        
        if user_input is not None:
            # Validate URL (basic validation)
            url = user_input["url"]
            if not url.startswith(("http://", "https://")):
                errors["url"] = "invalid_url"
            else:
                return self.async_create_entry(title="", data=user_input)

        # Get current URL
        current_url = self.config_entry.data.get("url", DEFAULT_URL)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("url", default=current_url): str
            }),
            errors=errors
        )