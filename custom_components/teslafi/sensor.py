"""Sensors"""

from collections.abc import Callable
from dataclasses import dataclass
from typing_extensions import override
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfPower,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from typing import cast

from .base import TeslaFiEntity
from .const import DOMAIN, LOGGER
from .coordinator import TeslaFiCoordinator

@dataclass
class TeslaFiSensorEntityDescription(SensorEntityDescription):
    """Base TeslaFi EntityDescription"""
    has_entity_name = True
    value: Callable[[dict, HomeAssistant], any] = None
    available: Callable[[dict, HomeAssistant], bool] = None
    """Callable to obtain the value. Defaults to `data[key]`."""

    def __post_init__(self):
        # Needs to be in post-init to reference self.key
        if not self.value:
            self.value = lambda data, hass: data.get(self.key)

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
        available=lambda x, y: x.get('shift_state', None) == 'D',
    ),
    TeslaFiSensorEntityDescription(
        key="shift_state",
        name="Shift State",
        icon="mdi:car-shift-pattern",
        device_class=SensorDeviceClass.ENUM,
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
        available=lambda x, y: x.get('charging_state', None) == 'Charging',
    ),
    TeslaFiSensorEntityDescription(
        key="charger_voltage",
        name="Charger Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        available=lambda x, y: x.get('carState', None) == 'Charging',
    ),
    TeslaFiSensorEntityDescription(
        key="charger_actual_current",
        name="Charger Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        available=lambda x, y: x.get('carState', None) == 'Charging',
    ),
    TeslaFiSensorEntityDescription(
        key="charger_power",
        name="Charger Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        available=lambda x, y: x.get('carState', None) == 'Charging',
    ),
        TeslaFiSensorEntityDescription(
        key="_apparent_power",
        name="Charger Apparent Power",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        device_class=SensorDeviceClass.APPARENT_POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value=lambda x, y: int(x.get("charger_voltage")) * int(x.get("charger_actual_current")),
        available=lambda x, y: x.get('carState', None) == 'Charging',
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

class TeslaFiSensor(TeslaFiEntity, SensorEntity):
    """Base TeslaFi Sensor"""
    entity_description: TeslaFiSensorEntityDescription

    def __init__(
        self,
        coordinator: TeslaFiCoordinator,
        description: TeslaFiSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.data.vin}-{description.key}"

    def _handle_coordinator_update(self) -> None:
        LOGGER.debug("on update for %s", self.entity_description.key)
        self._attr_native_value = cast(
            StateType, self.entity_description.value(self.coordinator.data, self.hass)
        )
        return super()._handle_coordinator_update()

    @property
    @override
    def available(self) -> bool:
        if self.entity_description.available:
            return self.entity_description.available(self.coordinator.data, self.hass)
        return super().available

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
