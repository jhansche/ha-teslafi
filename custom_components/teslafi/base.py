"""TeslaFi base classes"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast
from typing_extensions import override
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import TeslaFiVehicle
from .const import ATTRIBUTION, DOMAIN, LOGGER,  MANUFACTURER
from .coordinator import TeslaFiCoordinator


_BaseEntityDescriptionT = TypeVar(
    "_BaseEntityDescriptionT", bound="TeslaFiBaseEntityDescription"
)


class TeslaFiEntity(CoordinatorEntity[TeslaFiCoordinator], Generic[_BaseEntityDescriptionT]):
    """Base TeslaFi Entity"""
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    entity_description: _BaseEntityDescriptionT

    def __init__(
            self,
            coordinator: TeslaFiCoordinator,
            entity_description: _BaseEntityDescriptionT,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def car(self) -> TeslaFiVehicle:
        """Returns the vehicle data"""
        return self.coordinator.data

    @property
    @override
    def available(self) -> bool:
        if self.entity_description.available:
            return self.entity_description.available(
                super().available,
                self.coordinator.data,
                self.hass,
            )
        return super().available

    def _get_value(self) -> StateType:
        LOGGER.debug("getting value for %s", self.entity_description.key)
        return cast(
            StateType, self.entity_description.value(self.coordinator.data, self.hass)
        )

    @property
    def device_info(self) -> DeviceInfo:
        car = self.coordinator.data
        return DeviceInfo(
            identifiers={
                (DOMAIN, car.vehicle_id),
                ("vin", car.vin),
                ("tesla", car.id),
            },
            configuration_url="https://www.teslafi.com/",
            default_manufacturer=MANUFACTURER,
            default_model="Tesla Vehicle",
            default_name="Tesla Vehicle",
            model=car.car_type,
            name=car.name,
            sw_version=car.firmware_version,
            # TODO: model year, trim? Convert car_type to sentence case?
            hw_version=f"{car.model_year} {car.car_type or 'Tesla'}",
            suggested_area="Garage",
        )




@dataclass
class TeslaFiBaseEntityDescription(EntityDescription):
    """Base TeslaFi EntityDescription"""
    has_entity_name = True
    value: Callable[[dict, HomeAssistant], any] = None
    """Callable to obtain the value. Defaults to `data[key]`."""
    available: Callable[[bool, dict, HomeAssistant], bool] = None
    """Optional Callable to determine if the entity is available."""

    def __post_init__(self):
        # Needs to be in post-init to reference self.key
        if not self.value:
            self.value = lambda data, hass: data.get(self.key)


@dataclass
class TeslaFiSensorEntityDescription(SensorEntityDescription, TeslaFiBaseEntityDescription):
    """TeslaFi Sensor EntityDescription"""