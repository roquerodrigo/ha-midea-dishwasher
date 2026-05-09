"""
Repairs platform for midea_dishwasher.

Wires this integration into Home Assistant's Issue / Repair Registry. Use
``async_raise_unreachable_device_issue`` (or your own helper) from anywhere
in the integration to surface a recoverable problem to the user; the UI
exposes the "Fix" button which routes back here through
``async_create_fix_flow``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

ISSUE_UNREACHABLE_DEVICE: str = "unreachable_device"

type RepairsFixFlowData = dict[str, str | int | float | None]


async def async_create_fix_flow(
    hass: HomeAssistant,  # noqa: ARG001
    issue_id: str,  # noqa: ARG001
    data: RepairsFixFlowData | None,  # noqa: ARG001
) -> RepairsFlow:
    """
    Return the fix flow for a given issue.

    Branch on ``issue_id`` here when you have multiple kinds of issues.
    """
    return ConfirmRepairFlow()


def async_raise_unreachable_device_issue(hass: HomeAssistant) -> None:
    """
    Raise the unreachable-device issue.

    Call this from the coordinator / setup when the device is consistently
    unreachable on the LAN, so the user sees a Repair card.
    """
    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_UNREACHABLE_DEVICE,
        is_fixable=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_UNREACHABLE_DEVICE,
    )
