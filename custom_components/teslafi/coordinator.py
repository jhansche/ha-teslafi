"""TeslaFi data update coordinator"""

from datetime import timedelta
from typing_extensions import override
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import TeslaFiClient
from .const import DOMAIN, LOGGER, POLLING_INTERVAL
from .model import TeslaFiVehicle


class TeslaFiCoordinator(DataUpdateCoordinator[TeslaFiVehicle]):
    """TeslaFi Update Coordinator"""

    _vehicle = TeslaFiVehicle({})
    data: TeslaFiVehicle

    _override_next_refresh: timedelta = None

    def __init__(
        self,
        hass: HomeAssistant,
        client: TeslaFiClient,
    ) -> None:
        self._client = client
        # TODO: implement custom Debouncer to ensure no more than 2x per min,
        #  as per API rate limit?
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=POLLING_INTERVAL,
            update_method=self._refresh,
        )

    async def execute_command(self, cmd: str) -> dict:
        """Execute the remote command."""
        return await self._client.command(cmd)

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
            self._override_next_refresh = None
            self.update_interval = temp
            result = super()._schedule_refresh()
            self.update_interval = stash
            return result

        return super()._schedule_refresh()

    async def _refresh(self) -> TeslaFiVehicle:
        """Refresh"""
        current = await self._client.last_good()
        LOGGER.info("Last good: %s", current)
        self._vehicle.update_non_empty(current)
        last_remote_update = self._vehicle.get("Date")
        LOGGER.debug("Remote data last updated %s", last_remote_update)

        assert current.vin
        assert self._vehicle.vin
        return self._vehicle
