"""TeslaFi integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.httpx_client import create_async_httpx_client
from homeassistant.helpers.typing import ConfigType

from .client import TeslaFiClient
from .const import DOMAIN, HTTP_CLIENT, LOGGER
from .coordinator import TeslaFiCoordinator

PLATFORMS: list[Platform] = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.COVER,
    Platform.DEVICE_TRACKER,
    Platform.LOCK,
    Platform.NUMBER,
    # Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.UPDATE,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][HTTP_CLIENT] = create_async_httpx_client(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up from a config entry."""
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


async def async_migrate_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    """Migrate old entry."""
    current = config_entry.version
    LOGGER.debug("Migrating from version %s", current)

    if current < 2:
        dev_reg = dr.async_get(hass)
        entries = dr.async_entries_for_config_entry(
            dev_reg,
            config_entry.entry_id,
        )
        if len(entries) > 1:
            LOGGER.info("Too many devices for config entry %s", config_entry.entry_id)

        for device in entries:
            is_corrupt = len(device.identifiers) > 3 or len(entries) > 1

            if len(device.config_entries) == 1 and len(device.identifiers) == 3:
                # Only 3 identifiers: likely all we need to do is move them around
                new_identifiers = {
                    (DOMAIN, identifier)
                    for (n, identifier) in device.identifiers
                    if n == "vin" and identifier
                }
                if new_identifiers:
                    LOGGER.info(
                        "Migrating device %s identifiers %s to %s",
                        device.id,
                        device.identifiers,
                        new_identifiers,
                    )

                    dev_reg.async_update_device(
                        device.id, new_identifiers=new_identifiers
                    )
                else:
                    LOGGER.info(
                        "Unable to migrate device %s identifiers: %s",
                        device.id,
                        device.identifiers,
                    )
                    is_corrupt = True

            if is_corrupt:
                LOGGER.warning("Removing corrupted device %s", device.id)
                # First clear the identifiers
                dev_reg.async_update_device(device.id, new_identifiers=set())
                # Then remove the config entry
                # Otherwise if we removed the last config entry, it will
                # remove the device without updating identifiers.
                new = dev_reg.async_update_device(
                    device.id,
                    new_identifiers=set(),
                    remove_config_entry_id=config_entry.entry_id,
                )
                if new is not None:
                    # If the device is still present, remove it now
                    dev_reg.async_remove_device(device.id)

        current = config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry)

    if current < 3:
        # v3 fixes config_entry.unique_id
        if not config_entry.unique_id:
            LOGGER.warning(
                "Config entry %s does not have a unique_id: setting one now",
                config_entry.entry_id,
            )

            client = TeslaFiClient(
                config_entry.data[CONF_API_KEY],
                hass.data[DOMAIN][HTTP_CLIENT],
            )
            coordinator = TeslaFiCoordinator(hass, client)

            await coordinator.async_config_entry_first_refresh()
            current = config_entry.version = 3
            hass.config_entries.async_update_entry(
                config_entry,
                unique_id=coordinator.data.vin,
            )
            assert config_entry.unique_id == coordinator.data.vin
        else:
            # Already had a unique_id?
            LOGGER.info(
                "Config entry %s already has a unique_id=%s",
                config_entry.entry_id,
                config_entry.unique_id,
            )
            current = config_entry.version = 3
            hass.config_entries.async_update_entry(config_entry)

    return True
