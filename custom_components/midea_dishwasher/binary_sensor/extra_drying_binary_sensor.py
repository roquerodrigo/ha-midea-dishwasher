"""Extra-drying binary sensor: exposes the cycle's extra-drying flag."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherExtraDryingBinarySensor(MideaDishwasherEntity, BinarySensorEntity):
    """Boolean indicator for the extra-drying flag of the current cycle."""

    _attr_translation_key = "extra_drying"
    _attr_icon = "mdi:weather-sunny"

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_extra_drying"

    @property
    def is_on(self) -> bool | None:
        """Return True when extra drying is enabled, None before first refresh."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["extra_drying"]
