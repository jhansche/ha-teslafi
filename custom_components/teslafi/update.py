"""TeslaFi Update sensor"""

from __future__ import annotations
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiEntity, TeslaFiUpdateEntityDescription
from .const import DOMAIN, LOGGER
from .coordinator import TeslaFiCoordinator

UPDATERS = [
    TeslaFiUpdateEntityDescription(
        key="update",
        name="Software",
        icon="mdi:cellphone-arrow-down",
        device_class=UpdateDeviceClass.FIRMWARE,
    ),
]


class TeslaFiUpdater(TeslaFiEntity[TeslaFiUpdateEntityDescription], UpdateEntity):
    """Tesla Firmware updates"""

    _attr_supported_features = UpdateEntityFeature(UpdateEntityFeature.PROGRESS)

    @property
    def installed_version(self) -> str | None:
        return self.coordinator.data.firmware_version

    @property
    def latest_version(self) -> str | None:
        return (
            self.coordinator.data.get("newVersion") or ""
        ).strip() or self.installed_version

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return {
            "new_version_status": self.coordinator.data.get("newVersionStatus", None),
        }

    @property
    def in_progress(self) -> bool | int | None:
        status = self.coordinator.data.get("newVersionStatus", None)
        if status:
            # downloading_wifi_wait, downloading, available, scheduled, installing
            # available, waiting, downloading, installing, etc?
            LOGGER.info("Update status: %s", status)
            return status in ["installing", "downloading"]
        return super().in_progress

    # pylint:disable=useless-parent-delegation
    def _handle_coordinator_update(self) -> None:
        # TODO: should we override __in_progress?
        #  If newVersionStatus is installing
        return super()._handle_coordinator_update()

    @property
    def release_url(self) -> str | None:
        """Full release notes are made available by NotATeslaApp and TeslaFi."""
        version = self.latest_version or ""
        version = next(iter(version.split()), None)
        if version:
            return f"https://www.notateslaapp.com/software-updates/version/{version}/release-notes"
        return super().release_url

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        raise NotImplementedError("TeslaFi cannot initiate installation")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiUpdater] = []
    entities.extend(
        [TeslaFiUpdater(coordinator, description) for description in UPDATERS]
    )
    async_add_entities(entities)
