"""TeslaFi base classes"""

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import TeslaFiVehicle
from .const import ATTRIBUTION, DOMAIN,  MANUFACTURER
from .coordinator import TeslaFiCoordinator


class TeslaFiEntity(CoordinatorEntity[TeslaFiCoordinator]):
    """Base TeslaFi Entity"""
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _coordinator: TeslaFiCoordinator

    def __init__(self, coordinator: TeslaFiCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def car(self) -> TeslaFiVehicle:
        """Returns the vehicle data"""
        return self.coordinator.data

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
