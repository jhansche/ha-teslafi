"""Constants"""

from datetime import timedelta

import logging


HTTP_CLIENT = "client.http"
DOMAIN = "teslafi"
LOGGER = logging.getLogger(__package__)
MANUFACTURER = "Tesla, Inc."

POLLING_INTERVAL_DEFAULT = timedelta(minutes=3)
# Polling interval will be switched automatically in coordinator.py
POLLING_INTERVAL_DRIVING = timedelta(minutes=1)
POLLING_INTERVAL_SLEEPING = timedelta(minutes=10)

DELAY_CLIMATE = timedelta(seconds=30)
DELAY_CMD_WAKE = timedelta(seconds=10)
DELAY_LOCKS = timedelta(seconds=15)
DELAY_WAKEUP = timedelta(seconds=30)

ATTRIBUTION = "Data provided by Tesla and TeslaFi"

SHIFTER_STATES = {
    "P": "park",
    "R": "reverse",
    "N": "neutral",
    "D": "drive",
}
VIN_YEARS = {
    "A": 2010,
    "B": 2011,
    "C": 2012,
    "D": 2013,
    "E": 2014,
    "F": 2015,
    "G": 2016,
    "H": 2017,
    "J": 2018,
    "K": 2019,
    "L": 2020,
    "M": 2021,
    "N": 2022,
    "P": 2023,
    "R": 2024,
    "S": 2025,
    "T": 2026,
}
