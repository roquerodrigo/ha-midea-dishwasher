"""Runtime data stored on entry.runtime_data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.loader import Integration

    from ..api import MideaDishwasherApiClient
    from ..coordinator import MideaDishwasherDataUpdateCoordinator


@dataclass
class MideaDishwasherData:
    """Data stored on entry.runtime_data for the Midea Dishwasher."""

    client: MideaDishwasherApiClient
    coordinator: MideaDishwasherDataUpdateCoordinator
    integration: Integration
