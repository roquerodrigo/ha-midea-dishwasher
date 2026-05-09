"""Status sensor: cycle_state enum from the dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..coordinator import MideaDishwasherDataUpdateCoordinator
    from ..data import MideaDishwasherStatusData

_STATUS_OPTIONS: tuple[str, ...] = (
    "power_off",
    "idle",
    "order",
    "work",
    "error",
    "soft_gear",
)


class MideaDishwasherStatusSensor(MideaDishwasherEntity, SensorEntity):
    """Cycle state enum sensor (idle / running / scheduled / error / …)."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:dishwasher"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator: MideaDishwasherDataUpdateCoordinator) -> None:
        """Initialize the sensor and copy the enum options off the constant."""
        super().__init__(coordinator)
        self._attr_options = list(_STATUS_OPTIONS)

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_status"

    @property
    def native_value(self) -> str | None:
        """Return the cycle_state from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return data["cycle_state"]
