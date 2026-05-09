"""Number platform for midea_dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity, NumberMode

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
    """Set up the number platform."""
    async_add_entities([MideaDishwasherBrightNumber(entry.runtime_data.coordinator)])


class MideaDishwasherBrightNumber(MideaDishwasherEntity, NumberEntity):
    """Slider that reads and sets the rinse-aid level (1-5)."""

    _attr_translation_key = "bright"
    _attr_icon = "mdi:bottle-tonic-plus"
    _attr_native_min_value = 1
    _attr_native_max_value = 5
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_bright"

    @property
    def native_value(self) -> int | None:
        """Return the current rinse-aid level reported by the device."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["bright"]

    async def async_set_native_value(self, value: float) -> None:
        """Send the requested level to the dishwasher."""
        await self.coordinator.config_entry.runtime_data.client.async_set_bright(
            int(value),
        )
        await self.coordinator.async_request_refresh()
