"""Progress sensor: maps the device's numeric wash_stage to a labelled enum."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..coordinator import MideaDishwasherDataUpdateCoordinator
    from ..data import MideaDishwasherStatusData

_STAGE_TO_OPTION: tuple[str, ...] = (
    "idle",
    "pre_wash",
    "main_wash",
    "rinse",
    "dry",
    "finish",
)


class MideaDishwasherProgressSensor(MideaDishwasherEntity, SensorEntity):
    """Wash-stage enum sensor (idle / pre-wash / main-wash / rinse / dry / finish)."""

    _attr_translation_key = "progress"
    _attr_icon = "mdi:progress-clock"
    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, coordinator: MideaDishwasherDataUpdateCoordinator) -> None:
        """Initialize the sensor and copy the enum options off the constant."""
        super().__init__(coordinator)
        self._attr_options = list(_STAGE_TO_OPTION)

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_progress"

    @property
    def native_value(self) -> str | None:
        """Return the wash_stage as a label, or None for unknown values."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        stage = data["wash_stage"]
        if stage is None:
            return None
        if 0 <= stage < len(_STAGE_TO_OPTION):
            return _STAGE_TO_OPTION[stage]
        return None
