"""Typed view of a status response decoded by the library."""

from __future__ import annotations

from typing import TypedDict


class MideaDishwasherStatusData(TypedDict):
    """JSON-friendly view of a status response decoded by the library."""

    machine_state: str | None
    cycle_state: str | None
    mode: str | None
    extra_drying: bool
    wash_stage: str | None
    error_code: str | None
    left_time: int | None
    door_closed: bool
    bright_lack: bool
    bright: int | None
