from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .base import TeslaFiEntity, TeslaFiNumberEntityDescription
from .coordinator import TeslaFiCoordinator
from .const import DOMAIN, LOGGER


NUMBERS = [
    TeslaFiNumberEntityDescription(
        key="charge_limit_soc",
        name="Set Charge Limit",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:ev-station",
        native_unit_of_measurement=PERCENTAGE,
        min_value=0,
        max_value=100,
        native_step=1,
        max_value_key="charge_limit_soc_max",
        cmd=lambda c, v: c.execute_command("set_charge_limit", charge_limit_soc=v),
    ),
    TeslaFiNumberEntityDescription(
        key="charge_current_request",
        name="Request Charger Current",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
        icon="mdi:current-ac",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=1,
        native_max_value=None,
        native_step=1,
        value=lambda v, h: (
            int(x)
            if (x := v.get("charge_current_request", v.charger_current))
            else None
        ),
        max_value_key="charge_current_request_max",
        cmd=lambda c, v: c.execute_command("set_charging_amps", charging_amps=v),
        available=lambda u, v, h: u and v.is_plugged_in,
    ),
]


class TeslaFiNumber(
    TeslaFiEntity[TeslaFiNumberEntityDescription],
    NumberEntity,
):
    """TeslaFi Number entity"""

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self._get_value()
        max_value = None
        if max_key := self.entity_description.max_value_key:
            max_value = (
                int(float(x)) if (x := self.coordinator.data.get(max_key, None)) else None
            )
        if not max_value:
            max_value = self.entity_description.max_value
        if max_value: 
            self._attr_native_max_value = max_value
        return super()._handle_coordinator_update()

    async def async_set_native_value(self, value: float) -> None:
        result = await self.entity_description.cmd(self.coordinator, int(value))
        if result.get("response", {}).get("result", False):
            self._attr_native_value = int(value)
            self.async_write_ha_state()
        else:
            LOGGER.warning(
                f"Unexpected response setting {self.entity_description.key}: {result}"
            )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up from config entry"""
    coordinator: TeslaFiCoordinator
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities: list[TeslaFiNumber] = []
    entities.extend(
        [TeslaFiNumber(coordinator, description) for description in NUMBERS]
    )
    async_add_entities(entities)
