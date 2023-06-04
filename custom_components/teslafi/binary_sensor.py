"""TeslaFi Binary Sensors"""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TeslaFiEntity, TeslaFiBinarySensorEntityDescription
from .const import DOMAIN
from .coordinator import TeslaFiCoordinator


SENSORS = [
    # region Charging
    TeslaFiBinarySensorEntityDescription(
        key="_is_charging",
        name="Charging",
        icon="mdi:ev-station",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda d, h: d.is_charging
    ),
    TeslaFiBinarySensorEntityDescription(
        key="_is_plugged_in",
        name="Charger Plug",
        icon="mdi:ev-plug-tesla",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_category=EntityCategory.DIAGNOSTIC,
        value=lambda d, h: d.is_plugged_in
    ),
    # endregion

    # region Non-controllable openings
    TeslaFiBinarySensorEntityDescription(
        key="df",
        name="Front Driver Door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="pf",
        name="Front Passenger Door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="dr",
        name="Rear Driver Door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="pr",
        name="Rear Passenger Door",
        icon="mdi:car-door",
        device_class=BinarySensorDeviceClass.DOOR,
    ),

    TeslaFiBinarySensorEntityDescription(
        key="fd_window",
        name="Front Driver Window",
        icon="mdi:car-door", # No car-window icon
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="fp_window",
        name="Front Passenger Window",
        icon="mdi:car-door", # No car-window icon
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="rd_window",
        name="Rear Driver Window",
        icon="mdi:car-door", # No car-window icon
        device_class=BinarySensorDeviceClass.WINDOW,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="rp_window",
        name="Rear Passenger Window",
        icon="mdi:car-door", # No car-window icon
        device_class=BinarySensorDeviceClass.WINDOW,
    ),

    TeslaFiBinarySensorEntityDescription(
        key="ft",
        name="Front Trunk",
        # No meaningful icon
        device_class=BinarySensorDeviceClass.OPENING,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="rt",
        name="Rear Trunk",
        # No meaningful icon
        device_class=BinarySensorDeviceClass.OPENING,
    ),
    # endregion

    # region Others
    TeslaFiBinarySensorEntityDescription(
        key="is_user_present",
        name="Phone Key",
        icon="mdi:car-key",
        entity_registry_visible_default=False,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="homelink_nearby",
        name="HomeLink Nearby",
        icon="mdi:car-wireless",
        entity_registry_enabled_default=False,
        device_class=BinarySensorDeviceClass.PRESENCE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiBinarySensorEntityDescription(
        # TODO: convert to switch (we can turn it on/off via Fi)
        # TODO: or alarm_control_panel?
        key="sentry_mode",
        name="Sentry Mode",
        entity_registry_enabled_default=False,
        device_class=BinarySensorDeviceClass.LOCK,
        entity_category=EntityCategory.DIAGNOSTIC,
        # device class LOCK: off=locked, on=unlocked
        convert=lambda u: not TeslaFiBinarySensorEntityDescription.convert_to_bool(u),
        icons=["mdi:shield-car", "mdi:shield-lock-open"],
    ),
    TeslaFiBinarySensorEntityDescription(
        # TODO: convert to LOCK platform
        key="locked",
        name="Locks",
        device_class=BinarySensorDeviceClass.LOCK,
        # device class LOCK: off=locked, on=unlocked
        convert=lambda u: not TeslaFiBinarySensorEntityDescription.convert_to_bool(u),
        icons=["mdi:car-door-lock", "mdi:car-door"],
    ),

    TeslaFiBinarySensorEntityDescription(
        key="valet_mode",
        name="Valet Mode",
        icon="mdi:account-tie-hat",
        entity_registry_enabled_default=False,
        device_class=BinarySensorDeviceClass.OCCUPANCY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    TeslaFiBinarySensorEntityDescription(
        key="in_service",
        name="In Service Mode",
        icons=["mdi:account-off", "mdi:account-hardhat"],
        entity_registry_enabled_default=False,
        device_class=BinarySensorDeviceClass.OCCUPANCY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # endregion
]


class TeslaFiBinarySensor(TeslaFiEntity[TeslaFiBinarySensorEntityDescription], BinarySensorEntity):
    """Base TeslaFi Sensor"""

    def __init__(
        self,
        coordinator: TeslaFiCoordinator,
        description: TeslaFiBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description)
        self._attr_unique_id = f"{coordinator.data.vin}-{description.key}"

    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self._get_value()
        return super()._handle_coordinator_update()

    @property
    def icon(self) -> str:
        upstream = super().icon
        if upstream:
            return upstream
        if icons := self.entity_description.icons:
            assert len(icons) == 2
            return icons[1] if self.is_on else icons[0]



async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiBinarySensor] = []
    entities.extend([
        TeslaFiBinarySensor(coordinator, description)
        for description in SENSORS
    ])
    async_add_entities(entities)
