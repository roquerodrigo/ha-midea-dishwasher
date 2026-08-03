"""Typed top-level shape returned by async_get_config_entry_diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .diagnostics_entry import MideaDishwasherDiagnosticsEntry
    from .status_data import MideaDishwasherStatusData


class MideaDishwasherDiagnosticsPayload(TypedDict):
    """Top-level shape returned by async_get_config_entry_diagnostics."""

    entry: MideaDishwasherDiagnosticsEntry
    coordinator_data: MideaDishwasherStatusData | None
