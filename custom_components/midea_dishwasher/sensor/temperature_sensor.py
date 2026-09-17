"""Temperature sensor: water temperature inside the tub."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherTemperatureSensor(MideaDishwasherEntity, SensorEntity):
    """Temperature sensor for the water inside the tub."""

    _attr_translation_key = "temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_temperature"

    @property
    def native_value(self) -> int | None:
        """Return the tub temperature from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["temperature"]
