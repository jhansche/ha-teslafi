"""Sensors"""


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
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiEntity, TeslaFiSensorEntityDescription
from .const import DOMAIN
from .coordinator import TeslaFiCoordinator


SENSORS = [
    # region Generic car info
    TeslaFiSensorEntityDescription(
        key="odometer",
        name="Odometer",
        icon="mdi:counter",
        suggested_display_precision=1,
        native_unit_of_measurement=UnitOfLength.MILES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiSensorEntityDescription(
        key="carState",
        name="Car State",
        icon="mdi:car", # TODO: icon changes by state
        device_class=SensorDeviceClass.ENUM,
        options=["Sleeping", "Idling", "Sentry", "Charging", "Driving"],
    ),
    TeslaFiSensorEntityDescription(
        key="speed",
        name="Speed",
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfSpeed.MILES_PER_HOUR,
        available=lambda u, d, h: u and d.get('shift_state', None) == 'D',
    ),
    TeslaFiSensorEntityDescription(
        key="shift_state",
        name="Shift State",
        icon="mdi:car-shift-pattern",
        device_class=SensorDeviceClass.ENUM,
        entity_category=EntityCategory.DIAGNOSTIC,
        options=["P", "R", "N", "D"],
    ),
    # endregion

    # region Battery
    TeslaFiSensorEntityDescription(
        key="battery_level",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiSensorEntityDescription(
        key="battery_range",
        name="Battery Range",
        icon="mdi:map-marker-distance",
        suggested_display_precision=1,
        native_unit_of_measurement=UnitOfLength.MILES,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    #endregion

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
    ),
     TeslaFiSensorEntityDescription(
        key="charge_energy_added",
        name="Energy added",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=False,
        state_class=SensorStateClass.TOTAL_INCREASING,
        available=lambda u, d, h: u and d.is_plugged_in,
    ),
    TeslaFiSensorEntityDescription(
        # NOTE: this field is kW as an integer, so its value is not very useful.
        # Apparent Power will be more accurate.
        key="charger_power",
        name="Charger Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        available=lambda u, d, h: u and d.is_plugged_in,
    ),
    TeslaFiSensorEntityDescription(
        # This is a synthetic entity with actual calculation of apparent power.
        key="_apparent_power",
        name="Charger Apparent Power",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        device_class=SensorDeviceClass.APPARENT_POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value=lambda d, h: int(d.get("charger_voltage")) * int(d.get("charger_actual_current")),
        available=lambda u, d, h: u and d.is_plugged_in,
    ),

    # endregion

    # region Climate
    TeslaFiSensorEntityDescription(
        key="inside_temp",
        name="Cabin Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    TeslaFiSensorEntityDescription(
        key="outside_temp",
        name="Outside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    # ... climate.py
    # endregion
]

class TeslaFiSensor(TeslaFiEntity[TeslaFiSensorEntityDescription], SensorEntity):
    """Base TeslaFi Sensor"""

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self._get_value()
        return super()._handle_coordinator_update()

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiSensor] = []
    entities.extend([
        TeslaFiSensor(coordinator, description)
        for description in SENSORS
    ])
    async_add_entities(entities)
