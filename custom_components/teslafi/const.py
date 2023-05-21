"""Constants"""

from datetime import timedelta

import logging


HTTP_CLIENT = "client.http"
DOMAIN = "teslafi"
LOGGER = logging.getLogger(__package__)
MANUFACTURER = "Tesla, Inc."

POLLING_INTERVAL = timedelta(minutes=5)

ATTRIBUTION = "Data provided by Tesla and TeslaFi"


VIN_YEARS = {
    'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013,
    'E': 2014, 'F': 2015, 'G': 2016, 'H': 2017,
    'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021,
    'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025,
    'T': 2026,
}
