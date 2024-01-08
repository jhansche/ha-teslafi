"""TeslaFi Object Models"""

from collections import UserDict
from typing_extensions import deprecated

from .const import SHIFTER_STATES, VIN_YEARS


NAN: float = float("NaN")

CHARGER_CONNECTED_STATES = [
    "charging",
    "complete",
    "nopower",
    "starting",
    "stopped",
]


def _is_state(src: str | None, expect: str) -> bool | None:
    return None if src is None else src == expect


def _is_state_in(src: str | None, expect: list[str]) -> bool | None:
    return None if src is None else src in expect


def _lower_or_none(src: str | None) -> str | None:
    return None if src is None else src.lower()


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
    @deprecated("Use .vin instead")
    def id(self) -> str:
        """Vehicle id"""
        return self.get("id", self.vin)

    @property
    @deprecated("Use .vin instead")
    def vehicle_id(self) -> str:
        """Vehicle id"""
        return self.get("vehicle_id", self.vin)

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
        car_type = self.get("car_type", None)
        if not car_type and self.vin:
            # Decode model from VIN
            dig = self.vin[3]
            if dig in ["S", "3", "X", "Y"]:
                car_type = "model%s" % dig
        return car_type

    @property
    def vin(self) -> str:
        """VIN"""
        return self["vin"]

    @property
    def car_state(self) -> str | None:
        """Current car state. One of: [sleeping, idling, sentry, charging, driving]."""
        return _lower_or_none(self.get("carState", None))

    @property
    def model_year(self) -> int | None:
        """Decodes the model year from the VIN"""
        if not self.vin:
            return None
        dig = self.vin[9]
        return VIN_YEARS.get(dig, None)

    @property
    def is_in_gear(self) -> bool | None:
        """Whether the car is currently in gear."""
        return _is_state_in(self.shift_state, ["drive", "reverse"])

    @property
    def shift_state(self) -> str | None:
        """The car shifter state (P, R, N, D)"""
        if not (state := self.car_state):
            return None
        shifter = self.get("shift_state", "P") if state == "driving" else "P"
        return SHIFTER_STATES[shifter]

    @property
    def is_locked(self) -> bool | None:
        """Whether the vehicle is locked."""
        if not (value := self.get("locked", None)):
            return None
        return value == "1"

    @property
    def is_sleeping(self) -> bool | None:
        """Whether the vehicle is sleeping."""
        return _is_state(self.car_state, "sleeping")

    @property
    def charging_state(self) -> str | None:
        """The current charging state.

        One of:
        - 'charging'
        - 'complete'
        - 'disconnected'
        - 'starting'
        - 'stopped'
        - 'nopower'
        """
        return _lower_or_none(self.get("charging_state", None))

    @property
    def is_plugged_in(self) -> bool | None:
        """Whether the vehicle is plugged in."""
        return _is_state_in(self.charging_state, CHARGER_CONNECTED_STATES)

    @property
    def is_charging(self) -> bool | None:
        """Whether the vehicle is actively charging."""
        return _is_state(self.charging_state, "charging")

    @property
    def is_defrosting(self) -> bool | None:
        """Whether the defroster is on"""
        return (
            self.get("is_front_defroster_on") == "1"
            or self.get("is_rear_defroster_on") == "1"
            or self.get("defrost_mode", "0") != "0"
        )
