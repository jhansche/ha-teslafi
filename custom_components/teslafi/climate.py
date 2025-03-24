"""TeslaFi Climate controls"""

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_OFF,
    PRESET_NONE,
    PRESET_BOOST,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_conversion import TemperatureConverter

from .coordinator import TeslaFiCoordinator
from .base import (
    TeslaFiBinarySensorEntityDescription,
    TeslaFiClimateEntityDescription,
    TeslaFiEntity,
)
from .const import DELAY_CLIMATE, DELAY_WAKEUP, DOMAIN, LOGGER
from .util import _convert_to_bool

CLIMATES = [
    TeslaFiClimateEntityDescription(
        key="climate",
        name="Climate",
        entity_registry_enabled_default=False,
    ),
]

ACTION_DOG_MODE = "dog"
ACTION_CAMP_MODE = "camp"
ACTION_KEEP_ON = "on"
ACTION_DEFROST = "defrost"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tesla climate by config_entry."""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiClimate] = []
    entities.extend(
        [TeslaFiClimate(coordinator, description) for description in CLIMATES]
    )
    async_add_entities(entities)


class TeslaFiClimate(TeslaFiEntity[TeslaFiClimateEntityDescription], ClimateEntity):
    """TeslaFi Climate"""

    _attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature(
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        # FIXME: min 2024.2
        | ClimateEntityFeature(128)
        | ClimateEntityFeature(256)
    )

    _attr_fan_modes = [FAN_AUTO, FAN_OFF]
    _attr_preset_modes = [PRESET_NONE, PRESET_BOOST]

    # FIXME: why isn't this inherited?
    _attr_hvac_action = None
    _attr_hvac_mode = None
    _attr_preset_mode = None

    _pending_mode = None

    def _handle_coordinator_update(self) -> None:
        # These are in Celsius, despite user settings
        self._attr_target_temperature = (
            float(temp)
            if (temp := self.coordinator.data.get("driver_temp_setting"))
            else None
        )
        self._attr_current_temperature = (
            float(temp) if (temp := self.coordinator.data.get("inside_temp")) else None
        )

        is_on = self.coordinator.data.is_climate_on

        new_mode = None if is_on is None else HVACMode.AUTO if is_on else HVACMode.OFF
        want_mode = self._pending_mode

        if want_mode is None:
            self._attr_hvac_mode = new_mode
        elif new_mode == want_mode:
            self._attr_hvac_mode = new_mode
            self._pending_mode = None
            LOGGER.info("Target state succeeded: %s", want_mode)
        else:
            LOGGER.debug("Still waiting for %s", want_mode)
            return self.coordinator.schedule_refresh_in(DELAY_WAKEUP)

        self._attr_fan_mode = (
            FAN_AUTO if self.coordinator.data.get("fan_status") == "2" else FAN_OFF
        )

        keeper_mode = self.coordinator.data.get("climate_keeper_mode")
        # Use hvac_action for keeper mode, since we cannot set them
        if keeper_mode == "dog":
            self._attr_hvac_action = ACTION_DOG_MODE
        elif keeper_mode == "camp":
            self._attr_hvac_action = ACTION_CAMP_MODE
        elif keeper_mode == "on":
            self._attr_hvac_action = ACTION_KEEP_ON
        else:
            self._attr_hvac_action = None

        if is_on and self.coordinator.data.is_defrosting:
            self._attr_preset_mode = PRESET_BOOST
            if not self._attr_hvac_action:
                self._attr_hvac_action = ACTION_DEFROST
        else:
            self._attr_preset_mode = PRESET_NONE

        # TODO seat heaters? or switches
        # seat_heater_left, seat_heater_rear_right_back, seat_heater_rear_left,
        # seat_heater_right, rear_seat_heaters,
        # TODO others: side_mirror_heaters, wiper_blade_heater, steering_wheel_heater,
        #  not_enough_power_to_heat (cannot turn on heater because battery low...)

        return super()._handle_coordinator_update()

    def _refresh_soon(self):
        if self.coordinator.data.is_sleeping:
            LOGGER.info("Car is currently sleeping, please wait")
            self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
        else:
            self.coordinator.schedule_refresh_in(DELAY_CLIMATE)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        LOGGER.debug("set_hvac_mode: %s", hvac_mode)
        if hvac_mode == HVACMode.AUTO:
            cmd = "auto_conditioning_start"
        elif hvac_mode == HVACMode.OFF:
            await self.async_set_preset_mode(PRESET_NONE)
            cmd = "auto_conditioning_stop"
        else:
            raise f"Mode '{hvac_mode}' not supported."

        self._pending_mode = hvac_mode
        await self.coordinator.execute_command(cmd)
        self._attr_hvac_mode = hvac_mode
        self._attr_hvac_action = None
        self.async_write_ha_state()
        self._refresh_soon()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        LOGGER.debug("set_preset_mode: %s", preset_mode)

        if preset_mode == PRESET_BOOST:
            await self.coordinator.execute_command(
                "set_preconditioning_max", statement=True
            )
            # Preconditioning also turns on climate
            self._attr_hvac_mode = HVACMode.AUTO
            self._pending_mode = self._attr_hvac_mode
            if not self._attr_hvac_action:
                self._attr_hvac_action = ACTION_DEFROST

            self._attr_preset_mode = preset_mode

            self.async_write_ha_state()
            self._refresh_soon()
        elif preset_mode == PRESET_NONE:
            if self._attr_preset_mode == PRESET_BOOST:
                await self.coordinator.execute_command(
                    "set_preconditioning_max", statement=False
                )
                if self._attr_hvac_action == ACTION_DEFROST:
                    self._attr_hvac_action = None
            self._attr_preset_mode = None

            self.async_write_ha_state()
            self._refresh_soon()

        else:
            # User presets are configurable at https://teslafi.com/climates.php
            # But we cannot discover those presets automatically. We could put these into an Options Flow?
            raise NotImplementedError(f"Unknown preset {preset_mode}")

    async def async_turn_on(self) -> None:
        return await self.async_set_hvac_mode(HVACMode.AUTO)

    async def async_turn_off(self) -> None:
        return await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs) -> None:
        LOGGER.debug("set_temperature: %s", kwargs)
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature:
            # TeslaFi expects temp in configured units:
            #  (settings > account > measurements)
            # but we originally reported it in C
            # So if the TeslaFi API reports F is preferred,
            # we have to convert it before sending.
            
            if self.coordinator.data.get("temperature", "C") == "F":
                temperature = TemperatureConverter.convert(
                    temperature,
                    from_unit=UnitOfTemperature.CELSIUS,
                    to_unit=UnitOfTemperature.FAHRENHEIT,
                )
            await self.coordinator.execute_command("set_temps", temp=temperature)
            self.async_write_ha_state()
            self._refresh_soon()
