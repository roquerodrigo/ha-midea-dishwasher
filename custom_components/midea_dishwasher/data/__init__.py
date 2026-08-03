"""Custom types for midea_dishwasher."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from .config_data import MideaDishwasherConfigData
from .diagnostics_entry import MideaDishwasherDiagnosticsEntry
from .diagnostics_payload import MideaDishwasherDiagnosticsPayload
from .options_data import MideaDishwasherOptionsData
from .runtime import MideaDishwasherData
from .status_data import MideaDishwasherStatusData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | Mapping[str, JsonValue]
type JsonObject = Mapping[str, JsonValue]

type MideaDishwasherConfigEntry = ConfigEntry[MideaDishwasherData]

__all__ = [
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "MideaDishwasherConfigData",
    "MideaDishwasherConfigEntry",
    "MideaDishwasherData",
    "MideaDishwasherDiagnosticsEntry",
    "MideaDishwasherDiagnosticsPayload",
    "MideaDishwasherOptionsData",
    "MideaDishwasherStatusData",
]
