"""Door binary sensor: reflects the dishwasher's door state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from ..data import MideaDishwasherStatusData


class MideaDishwasherDoorBinarySensor(MideaDishwasherEntity, BinarySensorEntity):
    """Door open/closed (inverted from ``door_closed``)."""

    _attr_translation_key = "door"
    _attr_icon = "mdi:door"
    _attr_device_class = BinarySensorDeviceClass.DOOR

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_door"

    @property
    def is_on(self) -> bool | None:
        """Return True when the door is open, None before first refresh."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        if data is None:
            return None
        return not data["door_closed"]
