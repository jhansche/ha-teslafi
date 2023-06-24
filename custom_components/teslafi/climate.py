"""TeslaFi Climate controls"""

from config.custom_components.teslafi.base import TeslaFiClimateEntityDescription
from config.custom_components.teslafi.coordinator import TeslaFiCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_OFF,
    PRESET_NONE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)

from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_conversion import TemperatureConverter

from .coordinator import TeslaFiCoordinator
from .base import TeslaFiBinarySensorEntityDescription, TeslaFiClimateEntityDescription, TeslaFiEntity
from .const import DELAY_CLIMATE, DELAY_WAKEUP, DOMAIN, LOGGER

CLIMATES = [
    TeslaFiClimateEntityDescription(
        key="climate",
        name="HVAC",
        entity_registry_enabled_default=False,
    ),
]

PRESET_DOG_MODE = "dog"
PRESET_CAMP_MODE = "camp"
PRESET_KEEP_ON = "on"
BASE_PRESETS = [
    PRESET_CAMP_MODE,
    PRESET_DOG_MODE,
    PRESET_KEEP_ON,
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tesla climate by config_entry."""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiClimate] = []
    entities.extend([
        TeslaFiClimate(coordinator, description)
        for description in CLIMATES
    ])
    async_add_entities(entities)

class TeslaFiClimate(TeslaFiEntity[TeslaFiClimateEntityDescription], ClimateEntity):
    """TeslaFi Climate"""

    _attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature(
        ClimateEntityFeature.TARGET_TEMPERATURE |
        ClimateEntityFeature.PRESET_MODE |
        # TODO: Use Aux Heat for Defrost? Or Preset?
        ClimateEntityFeature.AUX_HEAT
    )

    _attr_fan_modes = [FAN_AUTO, FAN_OFF]
    _attr_preset_modes = [PRESET_NONE] + BASE_PRESETS

    # FIXME: why isn't this inherited?
    _attr_hvac_mode = None
    _attr_preset_mode = None
    _attr_is_aux_heat = False

    def _handle_coordinator_update(self) -> None:
        # These are in Celsius, despite user settings
        self._attr_target_temperature = float(temp) if (temp := self.coordinator.data.get("driver_temp_setting")) else None
        self._attr_current_temperature = float(temp) if (temp := self.coordinator.data.get("inside_temp")) else None

        is_on = TeslaFiBinarySensorEntityDescription.convert_to_bool(
            self.coordinator.data.get("is_climate_on") # 0, 1
        )
        if not is_on:
            self._attr_hvac_mode = HVACMode.OFF
        else:
            self._attr_hvac_mode = HVACMode.AUTO

        self._attr_fan_mode = FAN_AUTO if self.coordinator.data.get("fan_status") == "2" else FAN_OFF

        # TODO preset modes by climate_keeper_mode
        keeper_mode = self.coordinator.data.get("climate_keeper_mode")
        if keeper_mode == "dog":
            self._attr_preset_mode = PRESET_DOG_MODE
        elif keeper_mode == "camp":
            self._attr_preset_mode = PRESET_CAMP_MODE
        elif keeper_mode == "on":
            self._attr_preset_mode = PRESET_KEEP_ON
        else:
            self._attr_preset_mode = None

        # TODO defrost? or switch
        # defrost_mode=0, is_front_defroster_on=0, is_rear_defroster_on=0

        # TODO seat heaters? or switches
        # seat_heater_left, seat_heater_rear_right_back, seat_heater_rear_left,
        # seat_heater_right, rear_seat_heaters,
        # TODO others: side_mirror_heaters, wiper_blade_heater, steering_wheel_heater,
        #  not_enough_power_to_heat (cannot turn on heater because battery low...)

        return super()._handle_coordinator_update()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.AUTO:
            cmd = "auto_conditioning_start"
        elif hvac_mode == HVACMode.OFF:
            cmd = "auto_conditioning_stop"
        else:
            raise f"Mode '{hvac_mode}' not supported."

        await self.coordinator.execute_command(cmd)
        self.async_write_ha_state()

        if self.coordinator.data.is_sleeping:
            LOGGER.info("Car is currently sleeping, please wait")
            self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
        else:
            self.coordinator.schedule_refresh_in(DELAY_CLIMATE)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        # We show dog/camp/keep as presets, but we can't change them...

        if preset_mode == PRESET_NONE:
            await self.coordinator.execute_command("auto_conditioning_stop")
            self.async_write_ha_state()
            self.coordinator.schedule_refresh_in(DELAY_CLIMATE)
        elif preset_mode in BASE_PRESETS:
            raise NotImplementedError(f"TeslaFi does not support setting preset {preset_mode}")
        else:
            # User presets are configurable at https://teslafi.com/climates.php
            # But we cannot discover those presets automatically. We could put these into an Options Flow?
            raise NotImplementedError(f"Unknown preset {preset_mode}")

    async def async_set_temperature(self, **kwargs) -> None:
        LOGGER.info("Setting temperature, args=%s", kwargs)
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature:
            # TeslaFi expects temp in configured units:
            #  (settings > account > measurements)
            # but we original reported it in C
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
            self.coordinator.schedule_refresh_in(DELAY_CLIMATE)
