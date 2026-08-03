"""Progress sensor: the wash stage the device is currently in."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import MideaDishwasherEntity
from ..labels import WASH_STAGE_LABELS

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherProgressSensor(MideaDishwasherEntity, SensorEntity):
    """Wash-stage enum sensor (idle / pre-wash / main-wash / rinse / dry / finish)."""

    _attr_translation_key = "progress"
    _attr_icon = "mdi:progress-clock"
    _attr_device_class = SensorDeviceClass.ENUM

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_progress"

    @property
    def options(self) -> list[str]:
        """Return every wash stage the library can report."""
        return list(WASH_STAGE_LABELS)

    @property
    def native_value(self) -> str | None:
        """Return the wash stage from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["wash_stage"]
