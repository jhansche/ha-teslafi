"""TeslaFi data update coordinator"""

from datetime import datetime, timedelta
from typing import override

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import TeslaFiClient
from .const import (
    DELAY_CMD_WAKE,
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

    _last_charge_reset: datetime | None = None
    _override_next_refresh: timedelta | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        client: TeslaFiClient,
    ) -> None:
        self._client = client
        self.data = None
        self._vehicle = TeslaFiVehicle({})
        self._last_charge_reset = None
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
        if self.data.is_sleeping:
            kwargs["wake"] = DELAY_CMD_WAKE.seconds

        response = await self._client.command(cmd, **kwargs)
        await self._update_command_request_counts(response)
        
        # Force update HA antity data after command execution
        await self.async_request_refresh()        
        return response

    def schedule_refresh_in(self, delta: timedelta):
        """Attempt to schedule a refresh"""
        self._override_next_refresh = delta
        self._schedule_refresh()

    @property
    def last_charge_reset(self) -> datetime | None:
        """Last charge reset time."""
        return self._last_charge_reset

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

        self._infer_charge_session(prev=self.data, current=current)

        self._vehicle.update_non_empty(current)
        LOGGER.debug("Remote data last updated %s", self._vehicle.last_remote_update)
        
        api_requests = await self._client.request_counts()
        self._vehicle.update_non_empty(api_requests)
        LOGGER.debug("API Request counts updated %s", self._vehicle.api_requests)


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

    def _infer_charge_session(
        self,
        prev: TeslaFiVehicle,
        current: TeslaFiVehicle,
    ):
        if prev and current and (prev != current):
            if not prev.is_plugged_in and current.is_plugged_in:
                LOGGER.info("Vehicle is newly plugged in: resetting charge session")
                self._last_charge_reset = current.last_remote_update
            elif current.charge_session_number and (
                prev.charge_session_number != current.charge_session_number
            ):
                LOGGER.info(
                    f"New charge session detected: {prev.charge_session_number} -> {current.charge_session_number}"
                )
                self._last_charge_reset = current.last_remote_update
                
    async def _update_command_request_counts(
        self,
        response: dict
    ) -> None:
        """Update request counts."""
        if response and (request_counts := response.get("tesla_request_counter")):
            self._vehicle.update_non_empty(request_counts)
        else:
            LOGGER.warning("No request counts included from command response")
