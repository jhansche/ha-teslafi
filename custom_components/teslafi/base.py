"""TeslaFi base classes"""

from collections.abc import Callable
from dataclasses import dataclass
from numbers import Number
from typing import Generic, TypeVar, cast
from typing_extensions import override
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.components.cover import CoverEntityDescription
from homeassistant.components.lock import LockEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.update import UpdateEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityDescription
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import TeslaFiVehicle
from .const import ATTRIBUTION, DOMAIN, LOGGER, MANUFACTURER
from .coordinator import TeslaFiCoordinator
from .util import _convert_to_bool


_BaseEntityDescriptionT = TypeVar(
    "_BaseEntityDescriptionT", bound="TeslaFiBaseEntityDescription"
)


class TeslaFiBaseEntity(CoordinatorEntity[TeslaFiCoordinator]):
    """Base TeslaFi Entity"""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    @property
    def car(self) -> TeslaFiVehicle:
        """Returns the vehicle data"""
        return self.coordinator.data

    @property
    def device_info(self) -> DeviceInfo:
        car = self.coordinator.data
        return DeviceInfo(
            identifiers={(DOMAIN, car.vin)},
            configuration_url="https://www.teslafi.com/",
            manufacturer=MANUFACTURER,
            model=car.car_type,
            name=car.name,
            sw_version=car.firmware_version,
            # TODO: model year, trim? Convert car_type to sentence case?
            hw_version=f"{car.model_year} {car.car_type or 'Tesla'}",
            suggested_area="Garage",
        )


class TeslaFiEntity(TeslaFiBaseEntity, Generic[_BaseEntityDescriptionT]):
    """Base TeslaFi Entity"""

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
class TeslaFiButtonEntityDescription(
    ButtonEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Button EntityDescription"""

    teslafi_cmd: str = None
    """The command to send to TeslaFi on button press."""


@dataclass
class TeslaFiClimateEntityDescription(
    ClimateEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Climate EntityDescription"""


@dataclass
class TeslaFiCoverEntityDescription(
    CoverEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Cover"""

    value: Callable[[TeslaFiVehicle, HomeAssistant], bool] = None
    convert: Callable[[any], bool] = _convert_to_bool
    cmd: Callable[[TeslaFiCoordinator, bool], dict] = None


@dataclass
class TeslaFiSensorEntityDescription(
    SensorEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Sensor EntityDescription"""

    icons: dict[str, str] = None
    """Dictionary of state -> icon"""

    fix_unit: Callable[[TeslaFiVehicle, HomeAssistant], str] = lambda d, h: None
    """Convert the native unit of measurement. Return None to keep the original unit."""


@dataclass
class TeslaFiNumberEntityDescription(
    NumberEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Number EntityDescription"""

    convert: Callable[[any], int] = lambda v: int(v) if v else None
    cmd: Callable[[TeslaFiCoordinator, Number], dict] = None

    max_value_key: str = None
    """
    If specified, look up this key for the max value,
    otherwise fall back to max_value.
    """


@dataclass(slots=True)
class TeslaFiSwitchEntityDescription(
    SwitchEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Switch EntityDescription"""

    cmd: Callable[[TeslaFiCoordinator, bool], bool] = None
    """The command to send to TeslaFi on toggle."""

    convert: Callable[[any], bool] = _convert_to_bool


@dataclass
class TeslaFiUpdateEntityDescription(
    UpdateEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """A class that describes update entities."""


@dataclass
class TeslaFiLockEntityDescription(
    LockEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi Lock EntityDescription"""


@dataclass
class TeslaFiBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """TeslaFi BinarySensor EntityDescription"""

    # Redefine return type from TFBED
    value: Callable[[TeslaFiVehicle, HomeAssistant], bool] = None
    icons: list[str] = None
    """List of icons for `[0]=off`, `[1]=on`"""

    convert: Callable[[any], bool] = _convert_to_bool
