"""
Labels projecting the library enums onto Home Assistant strings.

Every enum option the integration exposes — sensor options, service modes and
the values stored in the coordinator payload — is derived here, so the
translation files are the only other place where these strings are spelled out.
"""

from __future__ import annotations

from midea_dishwasher_api import CycleState, ErrorCode, Mode, WashStage

CYCLE_STATE_LABELS: tuple[str, ...] = tuple(state.value for state in CycleState)
MODE_LABELS: tuple[str, ...] = tuple(mode.value for mode in Mode)
WASH_STAGE_LABELS: tuple[str, ...] = tuple(stage.name.lower() for stage in WashStage)
ERROR_CODE_LABELS: tuple[str, ...] = tuple(code.name.lower() for code in ErrorCode)


def wash_stage_label(stage: WashStage | int | None) -> str | None:
    """Return the label of a wash stage, or None for a stage we don't know."""
    return stage.name.lower() if isinstance(stage, WashStage) else None


def error_code_label(code: ErrorCode | int) -> str | None:
    """Return the label of an error code, or None for a code we don't know."""
    return code.name.lower() if isinstance(code, ErrorCode) else None
