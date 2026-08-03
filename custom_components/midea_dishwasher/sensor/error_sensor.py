"""Error-code sensor: the fault the device is reporting, if any."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity import EntityCategory

from ..entity import MideaDishwasherEntity
from ..labels import ERROR_CODE_LABELS

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherErrorSensor(MideaDishwasherEntity, SensorEntity):
    """Diagnostic enum sensor for the dishwasher's fault code."""

    _attr_translation_key = "error"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_error"

    @property
    def options(self) -> list[str]:
        """Return every fault code the library can report."""
        return list(ERROR_CODE_LABELS)

    @property
    def native_value(self) -> str | None:
        """Return the error code from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["error_code"]
