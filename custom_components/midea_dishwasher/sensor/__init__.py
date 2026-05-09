"""Sensor platform: re-exports each sensor entity class and wires the platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .error_sensor import MideaDishwasherErrorSensor
from .mode_sensor import MideaDishwasherModeSensor
from .progress_sensor import MideaDishwasherProgressSensor
from .status_sensor import MideaDishwasherStatusSensor
from .time_remaining_sensor import MideaDishwasherTimeRemainingSensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..data import MideaDishwasherConfigEntry

__all__ = [
    "MideaDishwasherErrorSensor",
    "MideaDishwasherModeSensor",
    "MideaDishwasherProgressSensor",
    "MideaDishwasherStatusSensor",
    "MideaDishwasherTimeRemainingSensor",
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MideaDishwasherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            MideaDishwasherStatusSensor(coordinator),
            MideaDishwasherModeSensor(coordinator),
            MideaDishwasherProgressSensor(coordinator),
            MideaDishwasherTimeRemainingSensor(coordinator),
            MideaDishwasherErrorSensor(coordinator),
        ],
    )
