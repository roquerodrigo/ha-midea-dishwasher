"""Mode sensor: program currently selected on the dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..coordinator import MideaDishwasherDataUpdateCoordinator
    from ..data import MideaDishwasherStatusData

_MODE_OPTIONS: tuple[str, ...] = (
    "auto",
    "intensive",
    "normal",
    "eco",
    "glass",
    "90min",
    "1hour",
    "rapid",
    "soak",
    "3in1",
    "hygiene",
    "quiet",
    "party",
    "fruit",
)


class MideaDishwasherModeSensor(MideaDishwasherEntity, SensorEntity):
    """Enum sensor for the program (Mode) currently selected on the device."""

    _attr_translation_key = "mode"
    _attr_icon = "mdi:auto-mode"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator: MideaDishwasherDataUpdateCoordinator) -> None:
        """Initialize the sensor and copy the enum options off the constant."""
        super().__init__(coordinator)
        self._attr_options = list(_MODE_OPTIONS)

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_mode"

    @property
    def native_value(self) -> str | None:
        """Return the current program label, or None when no program is set."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        mode = data["mode"]
        if mode in _MODE_OPTIONS:
            return mode
        return None
