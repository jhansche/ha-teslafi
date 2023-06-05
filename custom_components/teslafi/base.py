"""TeslaFi base classes"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast
from typing_extensions import override
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.components.lock import LockEntityDescription
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
        self._attr_unique_id = f"{coordinator.data.vin}-{entity_description.key}"
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
        upstream = self.entity_description.value(self.coordinator.data, self.hass)
        converted = self.entity_description.convert(upstream)
        return cast(StateType, converted)

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
    value: Callable[[TeslaFiVehicle, HomeAssistant], any] = None
    """Callable to obtain the value. Defaults to `data[key]`."""
    available: Callable[[bool, TeslaFiVehicle, HomeAssistant], bool] = None
    """Optional Callable to determine if the entity is available."""
    convert: Callable[[any], any] = lambda u: u
    """Optional Callable to convert the upstream value."""

    def __post_init__(self):
        # Needs to be in post-init to reference self.key
        if not self.value:
            self.value = lambda data, hass: data.get(self.key)


@dataclass(slots=True)
class TeslaFiButtonEntityDescription(ButtonEntityDescription, TeslaFiBaseEntityDescription):
    """TeslaFi Button EntityDescription"""

    teslafi_cmd: str = None
    """The command to send to TeslaFi on button press."""


@dataclass
class TeslaFiSensorEntityDescription(SensorEntityDescription, TeslaFiBaseEntityDescription):
    """TeslaFi Sensor EntityDescription"""


@dataclass
class TeslaFiLockEntityDescription(LockEntityDescription, TeslaFiBaseEntityDescription):
    """TeslaFi Lock EntityDescription"""


@dataclass
class TeslaFiBinarySensorEntityDescription(BinarySensorEntityDescription, TeslaFiBaseEntityDescription):
    """TeslaFi BinarySensor EntityDescription"""

    # Redefine return type from TFBED
    value: Callable[[TeslaFiVehicle, HomeAssistant], bool] = None
    icons: list[str] = None
    """List of icons for `[0]=off`, `[1]=on`"""

    @staticmethod
    def convert_to_bool(value: any) -> bool:
        """Convert the TeslaFi value to a boolean"""
        if value is bool:
            return value
        if value is None:
            return None
        if not value:
            return False
        # Otherwise it might be a non-falsey string that is actually false
        if value == "0":
            return False
        return bool(value)

    convert: Callable[[any], bool] = convert_to_bool
