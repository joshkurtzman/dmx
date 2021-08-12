from __future__ import annotations
from homeassistant.helpers import config_validation as cv, device_registry as dr
import voluptuous as vol
import logging

# from homeassistant.components.http import CONFIG_SCHEMA

# from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

import asyncio
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.discovery import load_platform, async_load_platform
from homeassistant.helpers.entity_component import async_update_entity

from .dmxSerialController import DmxController

from .const import DOMAIN


PLATFORMS = ["light"]

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    log.debug(config_entry)
    log.debug(config_entry.as_dict())
    c = config_entry.data

    controller = DmxController(c["device"], c["baud"], hass.loop)
    hass.data[DOMAIN] = {"controller": controller}

    log.debug("DMX Controller Starting.... Config:" + str(c))

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "light")
    )

    # if config update rerun platform setup
    config_entry.add_update_listener(update_listener)

    return True


async def update_listener(hass: HomeAssistant, config_entry:ConfigEntry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "light"))


# async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
#     """Unload a config entry."""
#     unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
#     hass.data[DOMAIN].writer.close()
#     hass.data[DOMAIN].reader.close()
#     #await hass.data[DOMAIN].writer.wait_closed()
#     #await hass.data[DOMAIN].reader.wait_closed()
#     if unload_ok:
#         hass.data[DOMAIN].pop(entry.entry_id)

#     return unload_ok
