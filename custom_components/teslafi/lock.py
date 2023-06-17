"""TeslaFi Locks"""

from typing import Any
from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_LOCKING, STATE_UNLOCKING
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DELAY_LOCKS,
    DELAY_WAKEUP,
    DOMAIN,
    LOGGER,
)
from .coordinator import TeslaFiCoordinator
from .base import TeslaFiEntity, TeslaFiLockEntityDescription


LOCKS = [
    TeslaFiLockEntityDescription(
        key="_locks",
        name="Lock",
        value=lambda d, h: d.is_locked,
    ),
]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiLock] = []
    entities.extend([
        TeslaFiLock(coordinator, description)
        for description in LOCKS
    ])
    async_add_entities(entities)

class TeslaFiLock(TeslaFiEntity[TeslaFiLockEntityDescription], LockEntity):
    """TeslaFi Door Locks"""
    _pending_action: str | None = None

    async def async_lock(self, **kwargs: Any) -> None:
        """Ask TeslaFi to lock the vehicle"""
        self._attr_is_unlocking = False

        response = await self.coordinator.execute_command("door_lock")
        assert response

        if response:
            LOGGER.debug("Lock response %s", response)
            self._pending_action = STATE_LOCKING
            self._attr_is_locking = True
            self.async_write_ha_state()
            if self.coordinator.data.is_sleeping:
                LOGGER.info("Car is currently sleeping, please wait")
                self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
            else:
                self.coordinator.schedule_refresh_in(DELAY_LOCKS)

    async def async_unlock(self, **kwargs: Any) -> None:
        """Ask TeslaFi to unlock the vehicle"""
        self._attr_is_locking = False

        response = await self.coordinator.execute_command("door_unlock")
        assert response

        if response:
            LOGGER.debug("Unlock response %s", response)
            self._pending_action = STATE_UNLOCKING
            self._attr_is_unlocking = True
            self.async_write_ha_state()
            if self.coordinator.data.is_sleeping:
                LOGGER.info("Car is currently sleeping, please wait")
                self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
            else:
                self.coordinator.schedule_refresh_in(DELAY_LOCKS)

    def _handle_coordinator_update(self) -> None:
        prev = self.state
        newest = self._get_value()
        waiting = self._pending_action is not None
        target = prev == STATE_LOCKING if waiting else None
        LOGGER.debug("lock %s: prev=%s, new=%s, pending=%s, target=%s",
                     self.entity_id, prev, newest, self._pending_action, target)

        if target is None:
            LOGGER.debug("Not waiting for a lock change, using state %s", newest)
            self._attr_is_unlocking = False
            self._attr_is_locking = False
            self._attr_is_locked = newest
            # write the state
            super()._handle_coordinator_update()
        elif target == newest:
            # It succeeded
            LOGGER.debug("Waiting for %s complete, state=%s", self._pending_action, newest)
            self._attr_is_unlocking = False
            self._attr_is_locking = False
            self._pending_action = None
            self._attr_is_locked = newest
            # write the state
            super()._handle_coordinator_update()
        else:
            # Still waiting...
            LOGGER.debug("Still waiting for %s", self._pending_action)
            self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
