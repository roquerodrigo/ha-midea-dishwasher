"""Salt binary sensor: signals when the water-softener salt is low."""

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


class MideaDishwasherSaltBinarySensor(MideaDishwasherEntity, BinarySensorEntity):
    """Diagnostic problem sensor that flags low water-softener salt."""

    _attr_translation_key = "salt"
    _attr_icon = "mdi:shaker-outline"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_salt"

    @property
    def is_on(self) -> bool | None:
        """Return True when the dishwasher reports softener-salt lack."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["softwater_lack"]
