"""TeslaFi data update coordinator"""

from datetime import timedelta
from typing_extensions import override
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import TeslaFiClient
from .const import (
    DOMAIN,
    LOGGER,
    POLLING_INTERVAL_DEFAULT,
    POLLING_INTERVAL_DRIVING,
    POLLING_INTERVAL_SLEEPING,
)
from .model import TeslaFiVehicle


class TeslaFiCoordinator(DataUpdateCoordinator[TeslaFiVehicle]):
    """TeslaFi Update Coordinator"""

    _vehicle: TeslaFiVehicle
    data: TeslaFiVehicle

    _override_next_refresh: timedelta = None

    def __init__(
        self,
        hass: HomeAssistant,
        client: TeslaFiClient,
    ) -> None:
        self._client = client
        self.data = None
        self._vehicle = TeslaFiVehicle({})
        # TODO: implement custom Debouncer to ensure no more than 2x per min,
        #  as per API rate limit?
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=POLLING_INTERVAL_DEFAULT,
            update_method=self._refresh,
        )

    async def execute_command(self, cmd: str, **kwargs) -> dict:
        """Execute the remote command."""
        LOGGER.debug(">> executing command %s; args=%s", cmd, kwargs)
        result = await self._client.command(cmd, **kwargs)
        LOGGER.debug("<< command %s response: %s", cmd, result)
        return result

    def schedule_refresh_in(self, delta: timedelta):
        """Attempt to schedule a refresh"""
        self._override_next_refresh = delta
        self._schedule_refresh()

    @override
    @callback
    def _schedule_refresh(self) -> None:
        # TODO: Adjust polling interval temporarily based on state:
        # - Idling = normal
        # - Driving = increased
        # - Sleeping = decreased
        if (stash := self.update_interval) and (temp := self._override_next_refresh):
            LOGGER.debug(
                "Overriding next refresh: %s instead of the usual %s", temp, stash
            )
            self._override_next_refresh = None
            self.update_interval = temp
            result = super()._schedule_refresh()
            self.update_interval = stash
            return result

        return super()._schedule_refresh()

    async def _refresh(self) -> TeslaFiVehicle:
        """Refresh"""
        current = await self._client.last_good()
        LOGGER.debug("Last good: %s", current)
        self._vehicle.update_non_empty(current)
        last_remote_update = self._vehicle.get("Date")
        LOGGER.debug("Remote data last updated %s", last_remote_update)

        assert current.vin
        assert self._vehicle.vin

        if (car_state := self._vehicle.car_state) == "sleeping":
            self._override_next_refresh = POLLING_INTERVAL_SLEEPING
            LOGGER.debug(
                "car is sleeping, decreasing polling interval to %s",
                self._override_next_refresh,
            )
        elif car_state == "driving":
            self._override_next_refresh = POLLING_INTERVAL_DRIVING
            LOGGER.debug(
                "car is driving, increasing polling interval to %s",
                self._override_next_refresh,
            )
        else:
            self._override_next_refresh = None

        return self._vehicle
