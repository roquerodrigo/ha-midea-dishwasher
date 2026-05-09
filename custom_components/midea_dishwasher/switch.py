"""Switch platform for midea_dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity

from .entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import MideaDishwasherConfigEntry, MideaDishwasherStatusData


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MideaDishwasherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities([MideaDishwasherPowerSwitch(entry.runtime_data.coordinator)])


class MideaDishwasherPowerSwitch(MideaDishwasherEntity, SwitchEntity):
    """Power switch that toggles the dishwasher's POWER_ON / POWER_OFF state."""

    _attr_translation_key = "power"
    _attr_icon = "mdi:power"
    _attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_power"

    @property
    def is_on(self) -> bool | None:
        """Return True when the machine reports POWER_ON, None before refresh."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["machine_state"] == "power_on"

    async def async_turn_on(self, **kwargs: object) -> None:  # noqa: ARG002
        """Power on the dishwasher."""
        await self.coordinator.config_entry.runtime_data.client.async_power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: object) -> None:  # noqa: ARG002
        """Power off the dishwasher."""
        await self.coordinator.config_entry.runtime_data.client.async_power_off()
        await self.coordinator.async_request_refresh()
