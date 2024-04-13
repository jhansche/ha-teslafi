from typing import Any
from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiEntity, TeslaFiCoverEntityDescription
from .const import DOMAIN, LOGGER
from .coordinator import TeslaFiCoordinator
from .errors import TeslaFiApiError
from .util import _convert_to_bool

COVERS = [
    TeslaFiCoverEntityDescription(
        key="charge_port_door_open",
        name="Charge Port Door",
        device_class=CoverDeviceClass.DOOR,
        icon="mdi:ev-plug-tesla",
        value=lambda d, h: d.get("charge_port_door_open", False),
        available=lambda u, d, h: u and d.car_state != "driving",
        cmd=lambda c, v: c.execute_command(
            "charge_port_door_open" if v else "charge_port_door_close"
        ),
    )
]


class TeslaFiCoverEntity(
    TeslaFiEntity[TeslaFiCoverEntityDescription],
    CoverEntity,
):
    """TeslaFi Cover Entity"""

    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
    _attr_is_closed = False
    _attr_is_closing = False
    _attr_is_opening = False

    def _handle_coordinator_update(self) -> None:
        self._attr_is_closed = self._get_value() == False
        self._attr_is_opening = False
        self._attr_is_closing = False
        return super()._handle_coordinator_update()

    async def async_close_cover(self, **kwargs: Any):
        if self.coordinator.data.is_plugged_in:
            LOGGER.warning("Cannot close charge port door while plugged in!")

        try:
            self._attr_is_opening = False
            await self.entity_description.cmd(self.coordinator, False)
            self._attr_is_closed = True
        except TeslaFiApiError as e:
            if "already closed" not in str(e):
                raise e
        self._attr_is_closed = True
        return self.async_write_ha_state()

    async def async_open_cover(self, **kwargs: Any) -> None:
        if self.coordinator.data.shift_state != "park":
            LOGGER.warning("Cannot open charge port door while driving!")
        try:
            self._attr_is_closing = False
            await self.entity_description.cmd(self.coordinator, True)
            self._attr_is_closed = False
        except TeslaFiApiError as e:
            if "already open" not in str(e):
                raise e
        self._attr_is_closed = False
        return self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiCoverEntity] = []
    entities.extend(
        [TeslaFiCoverEntity(coordinator, description) for description in COVERS]
    )
    async_add_entities(entities)
