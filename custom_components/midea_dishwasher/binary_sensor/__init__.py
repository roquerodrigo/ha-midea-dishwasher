"""Binary-sensor platform: re-exports each entity class and wires the platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .door_binary_sensor import MideaDishwasherDoorBinarySensor
from .extra_drying_binary_sensor import MideaDishwasherExtraDryingBinarySensor
from .rinse_aid_binary_sensor import MideaDishwasherRinseAidBinarySensor

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..data import MideaDishwasherConfigEntry

__all__ = [
    "MideaDishwasherDoorBinarySensor",
    "MideaDishwasherExtraDryingBinarySensor",
    "MideaDishwasherRinseAidBinarySensor",
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MideaDishwasherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            MideaDishwasherDoorBinarySensor(coordinator),
            MideaDishwasherExtraDryingBinarySensor(coordinator),
            MideaDishwasherRinseAidBinarySensor(coordinator),
        ],
    )
