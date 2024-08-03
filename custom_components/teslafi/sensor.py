"""Sensors"""

from datetime import datetime
from functools import cached_property
from typing import override

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiEntity, TeslaFiSensorEntityDescription
from .const import DOMAIN, SHIFTER_STATES
from .coordinator import TeslaFiCoordinator
from .model import TeslaFiTirePressure

SENSORS = [
    # region Generic car info
    TeslaFiSensorEntityDescription(
        key="odometer",
        name="Odometer",
        icon="mdi:counter",
        suggested_display_precision=1,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiSensorEntityDescription(
        key="carState",
        name="Car State",
        icon="mdi:car",
        device_class=SensorDeviceClass.ENUM,
        options=["sleeping", "idling", "sentry", "charging", "driving"],
        translation_key="car_state",
        icons={
            "sleeping": "mdi:sleep",
            "idling": "mdi:car",
            "sentry": "mdi:shield-car",
            "charging": "mdi:ev-station",
            "driving": "mdi:steering",
        },
        value=lambda d, h: d.car_state,
    ),
    TeslaFiSensorEntityDescription(
        key="speed",
        name="Speed",
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.SPEED,
        native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
        available=lambda u, d, h: u and d.is_in_gear,
    ),
    TeslaFiSensorEntityDescription(
        key="shift_state",
        name="Shift State",
        icon="mdi:car-shift-pattern",
        translation_key="shift_state",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=list(SHIFTER_STATES.values()),
        value=lambda d, h: d.shift_state,
        available=lambda u, d, h: u and d.car_state == "driving",
    ),
    # endregion
    # region Battery
    TeslaFiSensorEntityDescription(
        key="battery_level",
        name="Battery",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiSensorEntityDescription(
        key="battery_range",
        name="Battery Range",
        icon="mdi:map-marker-distance",
        suggested_display_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILES,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # endregion
    # region Charging
    TeslaFiSensorEntityDescription(
        key="time_to_full_charge",
        name="Charge Time Remaining",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        available=lambda u, d, h: u and d.is_charging,
    ),
    TeslaFiSensorEntityDescription(
        key="charger_voltage",
        name="Charger Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        available=lambda u, d, h: u and d.is_plugged_in,
    ),
    TeslaFiSensorEntityDescription(
        key="charger_actual_current",
        name="Charger Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        available=lambda u, d, h: u and d.is_plugged_in,
        value=lambda d, h: d.charger_current,
    ),
    TeslaFiSensorEntityDescription(
        key="charge_energy_added",
        name="Energy added",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=False,
        state_class=SensorStateClass.TOTAL,
        last_reset=None,
        available=lambda u, d, h: u and d.is_plugged_in,
    ),
    TeslaFiSensorEntityDescription(
        # NOTE: this field is kW as an integer, so its value is not very useful.
        # Apparent Power will be more accurate.
        key="charger_power",
        name="Charger Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        available=lambda u, d, h: u and d.is_plugged_in,
    ),
    TeslaFiSensorEntityDescription(
        # This is a synthetic entity with actual calculation of apparent power.
        key="_apparent_power",
        name="Charger Apparent Power",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value=lambda d, h: d.charger_voltage * d.charger_current,
        available=lambda u, d, h: u and d.is_plugged_in,
    ),
    TeslaFiSensorEntityDescription(
        key="_charger_level",
        name="Charger Level",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:ev-station",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        options=["level-1", "level-2", "level-3"],
        translation_key="charger_level",
        value=lambda d, h: d.charger_level,
        available=lambda u, d, h: u and d.is_charging,
    ),
    # endregion
    # region Climate
    TeslaFiSensorEntityDescription(
        key="inside_temp",
        name="Cabin Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    TeslaFiSensorEntityDescription(
        key="outside_temp",
        name="Outside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # ... climate.py
    # endregion
    # region TPMS
    TeslaFiSensorEntityDescription(
        key="tpms_front_left",
        name="TPMS Front Left",
        icon="mdi:car-tire-alert",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PSI,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        fix_unit=lambda d, h: TeslaFiTirePressure.convert_unit(d.tpms.unit),
        value=lambda d, h: d.tpms.front_left,
        available=lambda u, d, h: u and d.tpms.front_left,
    ),
    TeslaFiSensorEntityDescription(
        key="tpms_front_right",
        name="TPMS Front Right",
        icon="mdi:car-tire-alert",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PSI,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        fix_unit=lambda d, h: TeslaFiTirePressure.convert_unit(d.tpms.unit),
        value=lambda d, h: d.tpms.front_right,
        available=lambda u, d, h: u and d.tpms.front_right,
    ),
    TeslaFiSensorEntityDescription(
        key="tpms_rear_left",
        name="TPMS Rear Left",
        icon="mdi:car-tire-alert",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PSI,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        fix_unit=lambda d, h: TeslaFiTirePressure.convert_unit(d.tpms.unit),
        value=lambda d, h: d.tpms.rear_left,
        available=lambda u, d, h: u and d.tpms.rear_left,
    ),
    TeslaFiSensorEntityDescription(
        key="tpms_rear_right",
        name="TPMS Rear Right",
        icon="mdi:car-tire-alert",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PSI,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        fix_unit=lambda d, h: TeslaFiTirePressure.convert_unit(d.tpms.unit),
        value=lambda d, h: d.tpms.rear_right,
        available=lambda u, d, h: u and d.tpms.rear_right,
    ),
    # endregion
]


class TeslaFiSensor(TeslaFiEntity[TeslaFiSensorEntityDescription], SensorEntity):
    """Base TeslaFi Sensor"""

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self._get_value()
        if self.entity_description.fix_unit and (
            fixed := self.entity_description.fix_unit(self.coordinator.data, self.hass)
        ):
            self._attr_native_unit_of_measurement = fixed

        if self.entity_description.key == "charge_energy_added":
            if self.entity_description.state_class == SensorStateClass.TOTAL and (
                last_reset := self.coordinator.last_charge_reset
            ):
                self._attr_last_reset = last_reset
            else:
                self._attr_last_reset = None

        return super()._handle_coordinator_update()

    @property
    @override
    def icon(self) -> str | None:
        upstream = super().icon
        if self.entity_description.icons:
            return self.entity_description.icons.get(self.state, upstream)
        return upstream


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiSensor] = []
    entities.extend(
        [TeslaFiSensor(coordinator, description) for description in SENSORS]
    )
    async_add_entities(entities)
