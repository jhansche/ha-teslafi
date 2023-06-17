"""TeslaFi Object Models"""

from collections import UserDict

from .const import VIN_YEARS


NAN: float = float("NaN")


class TeslaFiVehicle(UserDict):
    """TeslaFi Vehicle Data"""

    def update_non_empty(self, data) -> None:
        """Update this object with non-empty data from `data`."""
        if not self.data:
            # Start out with all fields
            super().update(data)
        else:
            filtered = {k: v for (k, v) in data.items() if v}
            super().update(filtered)

    @property
    def id(self) -> str:
        """Vehicle id"""
        return self.get("id", None)

    @property
    def vehicle_id(self) -> str:
        """Vehicle id"""
        return self.get("vehicle_id", None)

    @property
    def odometer(self) -> float:
        """Odometer"""
        return float(self.get("odometer", NAN))

    @property
    def firmware_version(self) -> str | None:
        """Firmware version"""
        return self.get("car_version", None)

    @property
    def name(self) -> str | None:
        """Vehicle display name"""
        return self.get("display_name")

    @property
    def car_type(self) -> str | None:
        """Car type (model). E.g. 'model3', etc."""
        return self.get("car_type", None)

    @property
    def vin(self) -> str:
        """VIN"""
        return self["vin"]

    @property
    def car_state(self) -> str | None:
        """Current car state. One of: [Sleeping, Idling, Sentry, Charging, Driving]."""
        return self.get("carState", None)

    @property
    def model_year(self) -> int | None:
        """Decodes the model year from the VIN"""
        if not self.vin:
            return None
        dig = self.vin[9]
        return VIN_YEARS.get(dig, None)

    @property
    def is_in_gear(self) -> bool:
        """Whether the car is currently in gear."""
        return self.get("shift_state", None) in ["D", "R"]

    @property
    def is_locked(self) -> bool | None:
        """Whether the vehicle is locked."""
        if not (value := self.get("locked", None)):
            return None
        return value == "1"

    @property
    def is_sleeping(self) -> bool | None:
        """Whether the vehicle is sleeping."""
        if not (value := self.get("carState", None)):
            return None
        return value == "Sleeping"

    @property
    def is_plugged_in(self) -> bool | None:
        """Whether the vehicle is plugged in (either charging or completed)."""
        if not (value := self.get("charging_state", None)):
            return None
        return value in ["Charging", "Complete"]

    @property
    def is_charging(self) -> bool | None:
        """Whether the vehicle is actively charging."""
        if not (value := self.get("charging_state", None)):
            return None
        return value == "Charging"
