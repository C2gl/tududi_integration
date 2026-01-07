"""Config flow for Tududi integration."""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_URL,
    CONF_TITLE,
    CONF_ICON,
    CONF_API_KEY,
    API_BASE_PATH,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Optional(CONF_TITLE, default="Tududi"): cv.string,
        vol.Optional(CONF_ICON, default="mdi:clipboard-text"): cv.string,
        vol.Optional(CONF_API_KEY): cv.string,
    }
)


def validate_url(url: str) -> bool:
    """Validate the URL format."""
    try:
        url = str(url).strip()
        if not url:
            return False
            
        result = urlparse(url)
        return (
            result.scheme in ("http", "https") 
            and result.netloc 
            and len(result.netloc) > 0
        )
    except Exception:
        return False


async def validate_api_connection(
    hass: HomeAssistant, base_url: str, api_key: str | None = None
) -> bool:
    """Test if we can connect to the Tududi API."""
    if not api_key:
        # If no API key provided, just check if the URL is accessible
        _LOGGER.info("No API key provided, skipping API validation")
        return True
    
    try:
        url = f"{base_url.rstrip('/')}{API_BASE_PATH}/tasks"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        _LOGGER.info("Successfully validated API connection")
                        return True
                    elif response.status == 401:
                        _LOGGER.error("Invalid API key")
                        raise InvalidAuth
                    else:
                        _LOGGER.error("API returned status %s", response.status)
                        raise CannotConnect
                        
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout connecting to Tududi API")
        raise CannotConnect
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to Tududi API: %s", err)
        raise CannotConnect


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    url = data[CONF_URL]
    
    if not validate_url(url):
        raise InvalidURL
    
    # Test API connection if API key is provided
    api_key = data.get(CONF_API_KEY)
    if api_key:
        await validate_api_connection(hass, url, api_key)
    
    return {
        "title": f"Tududi Panel - {data[CONF_TITLE]}",
        "url": url,
        "panel_title": data[CONF_TITLE],
        "panel_icon": data[CONF_ICON],
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tududi HACS."""

    VERSION = 2  # Increment version for migration

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
            except InvalidAuth:
                errors[CONF_API_KEY] = "invalid_auth"
            except InvalidURL:
                errors[CONF_URL] = "invalid_url"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_URL])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "api_key_help": "Generate an API key from your Tududi settings (User menu → API Keys)"
            }
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Tududi HACS."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors[CONF_API_KEY] = "invalid_auth"
            except InvalidURL:
                errors[CONF_URL] = "invalid_url"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Update the config entry data
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input
                )
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
                vol.Optional(
                    CONF_API_KEY, default=current_data.get(CONF_API_KEY, "")
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "api_key_help": "Generate an API key from your Tududi settings (User menu → API Keys)"
            }
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate authentication failed."""


class InvalidURL(HomeAssistantError):
    """Error to indicate the URL is invalid."""