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
        available=lambda u, v, h: u and _convert_to_bool(v.get("is_climate_on")),
        cmd=lambda c, v: c.execute_command("steering_wheel_heater", statement=v),
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
        return self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.entity_description.cmd(self.coordinator, False)
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
