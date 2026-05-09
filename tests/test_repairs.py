from __future__ import annotations

from homeassistant.components.repairs import ConfirmRepairFlow
from homeassistant.helpers import issue_registry as ir

from custom_components.midea_dishwasher.const import DOMAIN
from custom_components.midea_dishwasher.repairs import (
    ISSUE_UNREACHABLE_DEVICE,
    async_create_fix_flow,
    async_raise_unreachable_device_issue,
)


async def test_create_fix_flow_returns_confirm_flow(hass):
    flow = await async_create_fix_flow(hass, ISSUE_UNREACHABLE_DEVICE, None)
    assert isinstance(flow, ConfirmRepairFlow)


async def test_raise_unreachable_device_issue_registers_issue(hass):
    async_raise_unreachable_device_issue(hass)
    registry = ir.async_get(hass)
    issue = registry.async_get_issue(DOMAIN, ISSUE_UNREACHABLE_DEVICE)
    assert issue is not None
    assert issue.is_fixable is True
    assert issue.severity == ir.IssueSeverity.WARNING
    assert issue.translation_key == ISSUE_UNREACHABLE_DEVICE


async def test_raise_unreachable_device_issue_idempotent(hass):
    async_raise_unreachable_device_issue(hass)
    async_raise_unreachable_device_issue(hass)
    registry = ir.async_get(hass)
    matching = [
        i
        for i in registry.issues.values()
        if i.domain == DOMAIN and i.issue_id == ISSUE_UNREACHABLE_DEVICE
    ]
    assert len(matching) == 1
