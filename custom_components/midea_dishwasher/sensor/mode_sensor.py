"""Mode sensor: program currently selected on the dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import MideaDishwasherEntity
from ..labels import MODE_LABELS

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherModeSensor(MideaDishwasherEntity, SensorEntity):
    """Enum sensor for the program (Mode) currently selected on the device."""

    _attr_translation_key = "mode"
    _attr_icon = "mdi:auto-mode"
    _attr_device_class = SensorDeviceClass.ENUM

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_mode"

    @property
    def options(self) -> list[str]:
        """Return every program the library can report."""
        return list(MODE_LABELS)

    @property
    def native_value(self) -> str | None:
        """Return the current program label, or None when no program is set."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        mode = data["mode"]
        return mode if mode in MODE_LABELS else None
