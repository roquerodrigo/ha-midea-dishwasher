"""Error-code sensor: enum mapping the device's fault byte."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity import EntityCategory

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..coordinator import MideaDishwasherDataUpdateCoordinator
    from ..data import MideaDishwasherStatusData

_ERROR_CODE_TO_OPTION: tuple[str, ...] = (
    "none",
    "water_supply",
    "heating",
    "overflow",
    "water_valve",
)


class MideaDishwasherErrorSensor(MideaDishwasherEntity, SensorEntity):
    """Diagnostic enum sensor for the dishwasher's fault code."""

    _attr_translation_key = "error"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: MideaDishwasherDataUpdateCoordinator) -> None:
        """Initialize the sensor and copy the enum options off the constant."""
        super().__init__(coordinator)
        self._attr_options = list(_ERROR_CODE_TO_OPTION)

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_error"

    @property
    def native_value(self) -> str | None:
        """Return the error_code as a label, or None for unknown codes."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        code = data["error_code"]
        if 0 <= code < len(_ERROR_CODE_TO_OPTION):
            return _ERROR_CODE_TO_OPTION[code]
        return None
