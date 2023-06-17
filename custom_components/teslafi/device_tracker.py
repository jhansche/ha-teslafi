"""Device tracker for MyBMW vehicles."""
from __future__ import annotations

from typing import Any
from typing_extensions import override

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiBaseEntity
from .const import DOMAIN
from .coordinator import TeslaFiCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiTracker] = [
        TeslaFiTracker(coordinator),
    ]
    async_add_entities(entities)


class TeslaFiTracker(TeslaFiBaseEntity, TrackerEntity):
    """TeslaFi Device Tracker"""
    _attr_force_update = False
    _attr_icon = "mdi:car"

    def __init__(self, coordinator: TeslaFiCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.data.vin}-tracker"
        self._attr_name = "Location"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        heading = (
            int(h)
            if (h := self.coordinator.data.get("heading", None)) is not None
            else None
        )
        cardinal = _degrees_to_cardinal(heading) if heading is not None else None
        return {
            "heading": heading,
            "heading_direction": cardinal,
        }

    @property
    @override
    def location_name(self) -> str | None:
        if (loc := self.coordinator.data.get("location")):
            # Note: better to let HA determine the location name, instead of TeslaFi?
            # return loc
            pass
        return super().location_name

    @property
    @override
    def longitude(self) -> float | None:
        return _float_or_none(self.coordinator.data.get("longitude", None))

    @property
    @override
    def latitude(self) -> float | None:
        return _float_or_none(self.coordinator.data.get("latitude", None))

    @property
    @override
    def source_type(self) -> SourceType | str:
        return SourceType.GPS


def _degrees_to_cardinal(deg: int) -> str:
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    idx = round(deg / (360. / len(dirs)))
    return dirs[idx % len(dirs)]

def _float_or_none(value :any) -> float | None:
    return float(value) if value is not None else None