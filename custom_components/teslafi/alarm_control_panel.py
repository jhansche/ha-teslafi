from dataclasses import dataclass
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityDescription,
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMING,
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_DISARMING,
    STATE_ALARM_DISARMED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import (
    TeslaFiBaseEntityDescription,
    TeslaFiBinarySensorEntityDescription,
    TeslaFiEntity,
)
from .const import DELAY_WAKEUP, DELAY_LOCKS, DOMAIN, LOGGER
from .coordinator import TeslaFiCoordinator


@dataclass
class TeslaFiSentryEntityDescription(
    AlarmControlPanelEntityDescription,
    TeslaFiBaseEntityDescription,
):
    """Alarm panel to control Sentry Mode"""


class TeslaFiSentryEntity(
    TeslaFiEntity[TeslaFiSentryEntityDescription],
    AlarmControlPanelEntity,
):
    _attr_code_arm_required: bool = False
    _attr_supported_features: AlarmControlPanelEntityFeature = (
        AlarmControlPanelEntityFeature.ARM_AWAY
    )
    _target_state: str | None = None

    def __init__(
        self,
        coordinator: TeslaFiCoordinator,
        entity_description: TeslaFiSentryEntityDescription,
    ) -> None:
        super().__init__(coordinator, entity_description)
        self._attr_changed_by = None
        self._target_state = None

    @property
    def icon(self) -> str | None:
        if self.state == STATE_ALARM_ARMED_AWAY:
            return "mdi:shield-car"
        return super().icon

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        LOGGER.debug("Disarming")
        response = await self.coordinator.execute_command(
            "set_sentry_mode", sentryMode=False
        )
        assert response
        # NOTE: we might run into this error:
        # > RuntimeError: Tesla Vehicle Command Protocol required, please refer to the documentation here:
        # > https://developer.tesla.com/docs/fleet-api#2023-10-09-rest-api-vehicle-commands-endpoint-deprecation-warning:

        if response:
            self._target_state = STATE_ALARM_DISARMED
            self._attr_state = STATE_ALARM_DISARMING
            self._attr_changed_by = "hass"
            self.async_write_ha_state()

            if self.coordinator.data.is_sleeping:
                LOGGER.info("Car is currently sleeping, please wait")
                self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
            else:
                self.coordinator.schedule_refresh_in(DELAY_LOCKS)

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        LOGGER.debug("Arming")
        response = await self.coordinator.execute_command(
            "set_sentry_mode", sentryMode=True
        )
        assert response
        # NOTE: we might run into this error:
        # > RuntimeError: Tesla Vehicle Command Protocol required, please refer to the documentation here:
        # > https://developer.tesla.com/docs/fleet-api#2023-10-09-rest-api-vehicle-commands-endpoint-deprecation-warning:

        if response:
            self._target_state = STATE_ALARM_ARMED_AWAY
            self._attr_state = STATE_ALARM_ARMING
            self._attr_changed_by = "hass"
            self.async_write_ha_state()

            if self.coordinator.data.is_sleeping:
                LOGGER.info("Car is currently sleeping, please wait")
                self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
            else:
                self.coordinator.schedule_refresh_in(DELAY_LOCKS)

    def _handle_coordinator_update(self) -> None:
        old_state = self.state
        new_state = self._get_value()
        target = self._target_state
        waiting = target is not None

        if waiting:
            if new_state == target:
                # It succeeded
                self._attr_state = new_state
                self._attr_changed_by = "hass"
                self._target_state = None
                LOGGER.info("Target state succeeded: %s", target)
            else:
                # still waiting
                LOGGER.debug("Still waiting for %s", target)
                return self.coordinator.schedule_refresh_in(DELAY_WAKEUP)
        elif old_state is None or new_state is None:
            self._attr_changed_by = None
            self._attr_state = new_state
        elif old_state != new_state:
            self._attr_changed_by = "remote"
            self._attr_state = new_state

        return super()._handle_coordinator_update()


ALARMS = [
    TeslaFiSentryEntityDescription(
        key="sentry_mode",
        name="Sentry Mode",
        entity_registry_enabled_default=False,
        convert=lambda v: STATE_ALARM_ARMED_AWAY
        if TeslaFiBinarySensorEntityDescription.convert_to_bool(v)
        else STATE_ALARM_DISARMED,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiSentryEntity] = []
    entities.extend(
        [TeslaFiSentryEntity(coordinator, description) for description in ALARMS]
    )
    async_add_entities(entities)
