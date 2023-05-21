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

    def __init__(
        self,
        hass: HomeAssistant,
        client: TeslaFiClient,
    ) -> None:
        self._client = client
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=POLLING_INTERVAL,
            update_method=self._refresh,
        )

    @override
    @callback
    def _schedule_refresh(self) -> None:
        # TODO: Adjust polling interval temporarily based on state:
        # - Idling = normal
        # - Driving = increased
        # - Sleeping = decreased
        return super()._schedule_refresh()

    async def _refresh(self) -> TeslaFiVehicle:
        """Refresh"""
        current = await self._client.last_good()
        LOGGER.info("Last good: %s", current)
        LOGGER.info("Mixing into: %s", self._vehicle)
        self._vehicle.update_non_empty(current)
        assert current.vin
        assert self._vehicle.vin
        return self._vehicle
