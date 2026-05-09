"""Button platform: re-exports each entity class and wires the platform."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .cancel_button import MideaDishwasherCancelButton
from .start_eco_button import MideaDishwasherStartEcoButton
from .start_intensive_button import MideaDishwasherStartIntensiveButton

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from ..data import MideaDishwasherConfigEntry

__all__ = [
    "MideaDishwasherCancelButton",
    "MideaDishwasherStartEcoButton",
    "MideaDishwasherStartIntensiveButton",
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: MideaDishwasherConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            MideaDishwasherCancelButton(coordinator),
            MideaDishwasherStartEcoButton(coordinator),
            MideaDishwasherStartIntensiveButton(coordinator),
        ],
    )
