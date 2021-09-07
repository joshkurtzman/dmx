"""Config flow for Ademco RS232 Alarm Panel integration."""
from __future__ import annotations
from .dmxSerialController import DmxController
import logging
from typing import Any
#from typing_extensions import Required

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from .const import DOMAIN
from homeassistant.helpers import config_validation as cv, device_registry as dr

_LOGGER = logging.getLogger(__name__)

# # TODO adjust the data schema to the data that you need


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
            vol.Required("device"): cv.string,
            vol.Optional("baud", default=9600): cv.positive_int,

    }
)



class PlaceholderHub:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host: str) -> None:
        """Initialize."""
        self.host = host

    async def authenticate(self, username: str, password: str) -> bool:
        """Test if we can authenticate with the host."""
        return True


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )
    from serial import SerialException
    try:
        dmxController = DmxController(device=data['device'], baud=data['baud'], loop=hass.loop )

    except SerialException:
        raise CannotConnect

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth
    # Return info that you want to store in the config entry.
    return {"title": "DMX Serial Controller"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
                    self, user_input: dict[str, Any] | None = None
                    ) -> FlowResult:
        
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry:ConfigEntry) -> None:

        self.STEP_OPTIONS_DATA_SCHEMA = vol.Schema(
        {
            vol.Optional("single",default=config_entry.options.get("single","")): cv.string,
            vol.Optional("rgb",default=config_entry.options.get("rgb","")): cv.string
        }
    )
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="Set up Lights", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.STEP_OPTIONS_DATA_SCHEMA
        )


            
class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

