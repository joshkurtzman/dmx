from homeassistant.config_entries import ConfigEntry
from .dmxSerialController import DmxController
import homeassistant
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA
from homeassistant.components.light import (
    COLOR_MODE_RGB,
    COLOR_MODE_BRIGHTNESS,
    SUPPORT_TRANSITION,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ATTR_TRANSITION,
)
import logging
import asyncio

log = logging.getLogger(__name__)

from homeassistant.core import HomeAssistant, State
from .const import DOMAIN
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from typing import Callable, Optional, Sequence


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: ConfigEntry,
    async_add_entities: Callable[[Sequence["DmxLight"], bool], None],
) -> None:
    log.debug("DMX Light Setup"+str(config_entry.data))
    entities = []
    controller = hass.data[DOMAIN]["controller"]
    
    for x in config_entry.options.get("rgb").split(","):
        entities.append(DmxRGBLight(controller, int(x)))

    for x in config_entry.options.get("single").split(","):
        entities.append(DmxLight(controller, int(x)))

    async_add_entities(entities)

    return True


class GenericDmxLight(LightEntity):
    def __init__(self, controller: "DmxController", startAddr: int) -> None:
        log.debug("Initializing Generic DMX")
        self.startAddr = startAddr
        self.controller = controller
        self._brightness = 0
        self._transition = 0
        self._isOn = False
   
   
    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "name": self.name,
            "manufacturer": "Custom DMX Controller",
            "model": self.__class__.__name__,
            "sw_version": None,
            "via_device": None,
        }

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def should_poll(self):
        return False

    @property
    def identifiers(self):
        return (DOMAIN, self.unique_id)

    @property
    def unique_id(self):
        return "{}{}".format(self.__class__.__name__.lower(), self.startAddr)

    @property
    def supported_features(self) -> int:
        return SUPPORT_TRANSITION

    @property
    def is_on(self) -> bool:
        return self._isOn

    @property
    def name(self):
        return "{}{}".format(self.__class__.__name__.lower(), self.startAddr)

    def turn_on(self, **kwargs) -> None:
        if ATTR_BRIGHTNESS in kwargs.keys():
            self._brightness = kwargs.get(ATTR_BRIGHTNESS)
        if self.brightness == 0:
            self._brightness = 255
        if ATTR_TRANSITION in kwargs.keys():
            self._transition = int(kwargs.get(ATTR_TRANSITION,0))
        self._isOn = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs) -> None:
        self._isOn = False
        self.schedule_update_ha_state()

    # async def async_added_to_hass(self):
    #     #Called by child class only when states exist
    #     self._brightness = self.hass.states.get(self.entity_id).attributes.get(ATTR_BRIGHTNESS, 0)
    #     self.is_on = True if self.hass.states.get(self.entity_id).state == "on" else False


class DmxRGBLight(GenericDmxLight):
    def __init__(self, controller, startAddr) -> None:
        log.debug("Initializing RGB DMX")
        GenericDmxLight.__init__(self, controller, startAddr)
        self._rgb_color = (255, 255, 255)

    @property
    def rgb_color(self):
        return self._rgb_color

    @property
    def color_mode(self):
        return COLOR_MODE_RGB

    @property
    def supported_color_modes(self):
        return {COLOR_MODE_RGB}

    async def async_turn_on(self, **kwargs):
        log.debug(str(kwargs))
        if ATTR_RGB_COLOR in kwargs.keys():
            self._rgb_color = kwargs.get(ATTR_RGB_COLOR)
        GenericDmxLight.turn_on(self, **kwargs)
        await self.controller.getChannel(self.startAddr).setLevel(
            self.rgb_color[0] * (self.brightness / 255), fadeSpeed=self._transition
        )
        await self.controller.getChannel(self.startAddr + 1).setLevel(
            self.rgb_color[1] * (self.brightness / 255), fadeSpeed=self._transition
        )
        await self.controller.getChannel(self.startAddr + 2).setLevel(
            self.rgb_color[2] * (self.brightness / 255), fadeSpeed=self._transition
        )
        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        GenericDmxLight.turn_off(self, **kwargs)
        await self.controller.getChannel(self.startAddr).setLevel(0, fadeSpeed=self._transition)
        await self.controller.getChannel(self.startAddr + 1).setLevel(0, fadeSpeed=self._transition)
        await self.controller.getChannel(self.startAddr + 2).setLevel(0, fadeSpeed=self._transition)

    # async def async_added_to_hass(self):
    #     if self.hass.states.get(self.entity_id):
    #         GenericDmxLight.async_added_to_hass(self)
    #         self._rgb_color = self.hass.states[self.entity_id].attributes.get(ATTR_RGB_COLOR,(255,255,255))


class DmxLight(GenericDmxLight):
    def __init__(self, controller, startAddr) -> None:
        log.debug("Initializing  DMX Light")
        GenericDmxLight.__init__(self, controller, startAddr)

    @property
    def brightness(self):
        return self._brightness

    @property
    def color_mode(self):
        return COLOR_MODE_BRIGHTNESS

    @property
    def supported_color_mode(self):
        return {COLOR_MODE_BRIGHTNESS}

    async def async_turn_on(self, **kwargs):
        log.debug(str(kwargs))
        GenericDmxLight.turn_on(self, **kwargs)
        await self.controller.getChannel(self.startAddr).setLevel(self.brightness, fadeSpeed=self._transition)

    async def async_turn_off(self, **kwargs):
        GenericDmxLight.turn_off(self, **kwargs)
        await self.controller.getChannel(self.startAddr).setLevel(0, fadeSpeed=self._transition)

    # async def async_added_to_hass(self):
    #     if self.hass.states.get(self.entity_id):
    #         GenericDmxLight.async_added_to_hass(self)
