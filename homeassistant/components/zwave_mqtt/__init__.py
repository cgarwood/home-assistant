"""The zwave_mqtt integration."""
import asyncio
import logging

import voluptuous as vol
from pydispatch import dispatcher

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT

from homeassistant.components import mqtt

from .const import DOMAIN, TOPIC_OPENZWAVE, SIGNAL_NODE_ADDED, SIGNAL_VALUE_CHANGED
from .manager import ZWaveManager

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = []


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the zwave_mqtt component."""
    if not hass.config_entries.async_entries(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data={}
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up zwave_mqtt from a config entry."""

    manager = ZWaveManager()

    # Subscribe to topic
    await mqtt.async_subscribe(hass, f"/{TOPIC_OPENZWAVE}/#", manager.process_message)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    def node_added(node):
        _LOGGER.info("node added: %s", node)

    def value_changed(value):
        # _LOGGER.info("value changed: %s", value)
        pass

    dispatcher.connect(node_added, signal=SIGNAL_NODE_ADDED, sender=DOMAIN, weak=False)
    dispatcher.connect(
        value_changed, signal=SIGNAL_VALUE_CHANGED, sender=DOMAIN, weak=False
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
