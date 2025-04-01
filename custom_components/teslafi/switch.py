from typing import Any
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiEntity, TeslaFiSwitchEntityDescription
from .const import DOMAIN, LOGGER
from .coordinator import TeslaFiCoordinator
from .util import _convert_to_bool

SWITCHES = [
    TeslaFiSwitchEntityDescription(
        key="steering_wheel_heater",
        name="Steering Wheel Heater",
        entity_registry_enabled_default=False,
        icon="mdi:steering",
        available=lambda u, v, h: u and v.is_climate_on,
        cmd=lambda c, v: c.execute_command("steering_wheel_heater", statement=v),
    ),
    TeslaFiSwitchEntityDescription(
        key="_set_charging",
        name="Charging",
        icon="mdi:ev-station",
        entity_registry_enabled_default=False,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.DIAGNOSTIC,
        available=lambda u, v, h: u and v.is_plugged_in,
        value=lambda d, h: d.is_charging,
        cmd=lambda c, v: c.execute_command("charge_start" if v else "charge_stop"),
    ),
]


class TeslaFiSwitchEntity(
    TeslaFiEntity[TeslaFiSwitchEntityDescription],
    ToggleEntity,
):
    """TeslaFi Switch Entity"""

    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self._attr_state = self._get_value()
        return super()._handle_coordinator_update()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.entity_description.cmd(self.coordinator, True)
        self._attr_is_on = True
        return self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.entity_description.cmd(self.coordinator, False)
        self._attr_is_on = False
        return self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiSwitchEntity] = []
    entities.extend(
        [TeslaFiSwitchEntity(coordinator, description) for description in SWITCHES]
    )
    async_add_entities(entities)
