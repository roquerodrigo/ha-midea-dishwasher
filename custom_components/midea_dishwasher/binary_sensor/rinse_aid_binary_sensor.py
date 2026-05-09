"""Rinse-aid binary sensor: signals when the rinse-aid bottle is low."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import EntityCategory

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherRinseAidBinarySensor(MideaDishwasherEntity, BinarySensorEntity):
    """Diagnostic problem sensor that flags low rinse-aid."""

    _attr_translation_key = "rinse_aid"
    _attr_icon = "mdi:bottle-tonic-outline"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_rinse_aid"

    @property
    def is_on(self) -> bool | None:
        """Return True when the dishwasher reports rinse-aid lack."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["bright_lack"]
