"""TeslaFi integration."""
from __future__ import annotations
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.httpx_client import create_async_httpx_client
from homeassistant.helpers.typing import ConfigType

from .client import TeslaFiClient
from .const import DOMAIN, HTTP_CLIENT
from .coordinator import TeslaFiCoordinator


PLATFORMS: list[Platform] = [
    # TODO? Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    # TODO: Platform.COVER,
    Platform.LOCK,
    # Platform.SELECT,
    Platform.SENSOR,
    # TODO: Platform.SWITCH,
    # TODO: Platform.UPDATE,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Setup the integration"""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][HTTP_CLIENT] = create_async_httpx_client(hass)
    # TODO: services?
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Setup from a config entry"""
    http_client = hass.data[DOMAIN][HTTP_CLIENT]
    client = TeslaFiClient(entry.data[CONF_API_KEY], http_client)
    coordinator = TeslaFiCoordinator(hass, client)
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}

    await coordinator.async_config_entry_first_refresh()
    # VIN is the one thing vital for all entities.
    assert coordinator.data.vin

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )
    # Everything succeeded, now tell the listeners to update their states
    coordinator.async_update_listeners()
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """Remove a config entry from a device."""
    return True
