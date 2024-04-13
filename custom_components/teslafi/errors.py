from dataclasses import dataclass


class VehicleNotReadyError(Exception):
    """The vehicle is sleeping"""


class TeslaFiApiError(Exception):
    """API responded with an error reason"""
