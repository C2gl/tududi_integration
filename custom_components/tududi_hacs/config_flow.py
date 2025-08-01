"""Config flow for Tududi HACS integration."""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_URL, CONF_TITLE, CONF_ICON, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Optional(CONF_TITLE, default="Tududi"): cv.string,
        vol.Optional(CONF_ICON, default="mdi:clipboard-text"): cv.string,
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


def validate_url(url: str) -> bool:
    """Validate the URL format."""
    try:
        # Strip whitespace and ensure it's a string
        url = str(url).strip()
        if not url:
            return False
            
        result = urlparse(url)
        # Check that we have both scheme and netloc, and scheme is http/https
        return (
            result.scheme in ("http", "https") 
            and result.netloc 
            and len(result.netloc) > 0
        )
    except Exception:
        return False


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    url = data[CONF_URL]
    
    if not validate_url(url):
        raise InvalidURL
    
    # Return info that you want to store in the config entry.
    return {
        "title": f"Tududi Panel - {data[CONF_TITLE]}",
        "url": url,
        "panel_title": data[CONF_TITLE],
        "panel_icon": data[CONF_ICON],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tududi HACS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidURL:
                errors[CONF_URL] = "invalid_url"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Tududi HACS."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except InvalidURL:
                errors[CONF_URL] = "invalid_url"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Update the config entry
                return self.async_create_entry(title="", data=user_input)

        # Pre-fill with current values
        current_data = self.config_entry.data
        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default=current_data.get(CONF_URL, "")): cv.string,
                vol.Optional(
                    CONF_TITLE, default=current_data.get(CONF_TITLE, "Tududi")
                ): cv.string,
                vol.Optional(
                    CONF_ICON, default=current_data.get(CONF_ICON, "mdi:clipboard-text")
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidURL(HomeAssistantError):
    """Error to indicate the URL is invalid."""
