"""Time-remaining sensor: minutes left in the running cycle."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTime

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherTimeRemainingSensor(MideaDishwasherEntity, SensorEntity):
    """Duration sensor for minutes remaining in the running cycle."""

    _attr_translation_key = "time_remaining"
    _attr_icon = "mdi:timer-sand"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_suggested_unit_of_measurement = UnitOfTime.HOURS

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_time_remaining"

    @property
    def native_value(self) -> int | None:
        """Return the left_time minutes from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["left_time"]
