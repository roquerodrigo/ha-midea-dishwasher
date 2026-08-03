"""Status sensor: cycle_state enum from the dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import MideaDishwasherEntity
from ..labels import CYCLE_STATE_LABELS

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherStatusSensor(MideaDishwasherEntity, SensorEntity):
    """Cycle state enum sensor (idle / running / scheduled / error / ...)."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:dishwasher"
    _attr_device_class = SensorDeviceClass.ENUM

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_status"

    @property
    def options(self) -> list[str]:
        """Return every cycle state the library can report."""
        return list(CYCLE_STATE_LABELS)

    @property
    def native_value(self) -> str | None:
        """Return the cycle_state from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["cycle_state"]
