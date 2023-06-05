"""TeslaFi on-demand action buttons"""

from datetime import timedelta
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER
from .coordinator import TeslaFiCoordinator
from .base import TeslaFiEntity, TeslaFiButtonEntityDescription


BUTTONS = [
    TeslaFiButtonEntityDescription(
        key="cmd_wake_up",
        name="Wake Up",
        icon="mdi:sleep-off",
        teslafi_cmd="wake_up",
        # available=lambda u, d, h: u and d.is_sleeping, # Needed?
    ),
    TeslaFiButtonEntityDescription(
        key="cmd_honk",
        name="Horn",
        icon="mdi:air-horn",
        teslafi_cmd="honk",
    ),
    TeslaFiButtonEntityDescription(
        key="cmd_flash_lights",
        name="Flash Lights",
        icon="mdi:car-parking-lights",
        teslafi_cmd="flash_lights",
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
    entities: list[TeslaFiButton] = []
    entities.extend([
        TeslaFiButton(coordinator, description)
        for description in BUTTONS
    ])
    async_add_entities(entities)


class TeslaFiButton(TeslaFiEntity[TeslaFiButtonEntityDescription], ButtonEntity):
    """Base TeslaFi Sensor"""

    async def async_press(self) -> None:
        cmd = self.entity_description.teslafi_cmd
        response = await self.coordinator.execute_command(cmd)
        LOGGER.debug("Button command response: %s", bool(response))

        if self.entity_description.key == "cmd_wake_up":
            # TODO: invoke after-pressed function?
            #  We should schedule a refresh soon after wake_up.
            LOGGER.info("Wake-up button pressed, refresh imminent")
            self.coordinator.schedule_refresh_in(timedelta(seconds=15))
