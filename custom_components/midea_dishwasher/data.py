"""Custom types for midea_dishwasher."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import MideaDishwasherApiClient
    from .coordinator import MideaDishwasherDataUpdateCoordinator


type JsonPrimitive = str | int | float | bool | None
type JsonValue = JsonPrimitive | list[JsonValue] | Mapping[str, JsonValue]
type JsonObject = Mapping[str, JsonValue]


class MideaDishwasherStatusData(TypedDict):
    """JSON-friendly view of a status response decoded by the library."""

    machine_state: str | None
    cycle_state: str | None
    mode: str | None
    extra_drying: bool
    wash_stage: int | None
    error_code: int
    left_time: int | None
    door_closed: bool
    bright_lack: bool
    bright: int | None


class MideaDishwasherConfigData(TypedDict):
    """Shape of the LAN credentials persisted on the config entry."""

    host: str
    port: int
    device_id: int
    token: str
    key: str


class MideaDishwasherOptionsData(TypedDict, total=False):
    """Shape of the options writable by the options flow."""

    scan_interval: NotRequired[int]


class MideaDishwasherDiagnosticsEntry(TypedDict):
    """Entry section of the diagnostics dump."""

    title: str
    version: int
    domain: str
    data: Mapping[str, str | int]
    options: Mapping[str, str | int]


class MideaDishwasherDiagnosticsPayload(TypedDict):
    """Top-level shape returned by async_get_config_entry_diagnostics."""

    entry: MideaDishwasherDiagnosticsEntry
    coordinator_data: MideaDishwasherStatusData | None


type MideaDishwasherConfigEntry = ConfigEntry[MideaDishwasherData]


@dataclass
class MideaDishwasherData:
    """Data stored on entry.runtime_data for the Midea Dishwasher."""

    client: MideaDishwasherApiClient
    coordinator: MideaDishwasherDataUpdateCoordinator
    integration: Integration
