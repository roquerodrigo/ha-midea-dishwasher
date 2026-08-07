from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.midea_dishwasher.const import DOMAIN
from custom_components.midea_dishwasher.coordinator import (
    UNREACHABLE_DEVICE_FAILURE_THRESHOLD,
    MideaDishwasherDataUpdateCoordinator,
)
from custom_components.midea_dishwasher.exceptions import (
    MideaDishwasherApiClientAuthenticationError,
    MideaDishwasherApiClientCommunicationError,
    MideaDishwasherApiClientError,
)
from custom_components.midea_dishwasher.repairs import ISSUE_UNREACHABLE_DEVICE


def _make_coordinator(hass, payload=None, scan_interval=timedelta(minutes=5)):
    coord = MideaDishwasherDataUpdateCoordinator(hass=hass, scan_interval=scan_interval)
    client = AsyncMock()
    client.async_get_status = AsyncMock(return_value=payload or {})
    runtime_data = type("D", (), {"client": client})()
    entry = type("E", (), {"entry_id": "eid", "runtime_data": runtime_data})()
    coord.config_entry = entry
    return coord, client


def test_init_sets_domain_name(hass):
    coord = MideaDishwasherDataUpdateCoordinator(
        hass=hass, scan_interval=timedelta(seconds=300)
    )
    assert coord.name == DOMAIN


def test_init_sets_update_interval(hass):
    coord = MideaDishwasherDataUpdateCoordinator(
        hass=hass, scan_interval=timedelta(seconds=42)
    )
    assert coord.update_interval == timedelta(seconds=42)


async def test_update_data_returns_payload(hass, sample_status):
    coord, _ = _make_coordinator(hass, payload=sample_status)
    result = await coord._async_update_data()
    assert result == sample_status


async def test_update_data_raises_update_failed_on_api_error(hass):
    coord, client = _make_coordinator(hass)
    client.async_get_status.side_effect = MideaDishwasherApiClientError("down")
    with pytest.raises(UpdateFailed):
        await coord._async_update_data()


async def test_update_data_raises_auth_failed_on_auth_error(hass):
    coord, client = _make_coordinator(hass)
    client.async_get_status.side_effect = MideaDishwasherApiClientAuthenticationError(
        "nope"
    )
    with pytest.raises(ConfigEntryAuthFailed):
        await coord._async_update_data()


def _unreachable_issue(hass):
    return ir.async_get(hass).async_get_issue(DOMAIN, ISSUE_UNREACHABLE_DEVICE)


async def _fail_polls(coord, count):
    for _ in range(count):
        with pytest.raises(UpdateFailed):
            await coord._async_update_data()


async def test_persistent_communication_failures_raise_the_repair_issue(hass):
    coord, client = _make_coordinator(hass)
    client.async_get_status.side_effect = MideaDishwasherApiClientCommunicationError(
        "down"
    )
    await _fail_polls(coord, UNREACHABLE_DEVICE_FAILURE_THRESHOLD)
    assert _unreachable_issue(hass) is not None


async def test_fewer_failures_than_the_threshold_raise_no_issue(hass):
    coord, client = _make_coordinator(hass)
    client.async_get_status.side_effect = MideaDishwasherApiClientCommunicationError(
        "down"
    )
    await _fail_polls(coord, UNREACHABLE_DEVICE_FAILURE_THRESHOLD - 1)
    assert _unreachable_issue(hass) is None


async def test_successful_update_clears_the_issue_and_resets_the_counter(
    hass, sample_status
):
    coord, client = _make_coordinator(hass)
    client.async_get_status.side_effect = MideaDishwasherApiClientCommunicationError(
        "down"
    )
    await _fail_polls(coord, UNREACHABLE_DEVICE_FAILURE_THRESHOLD)

    client.async_get_status.side_effect = None
    client.async_get_status.return_value = sample_status
    await coord._async_update_data()
    assert _unreachable_issue(hass) is None

    client.async_get_status.side_effect = MideaDishwasherApiClientCommunicationError(
        "down"
    )
    await _fail_polls(coord, UNREACHABLE_DEVICE_FAILURE_THRESHOLD - 1)
    assert _unreachable_issue(hass) is None


async def test_non_communication_errors_do_not_count_towards_the_issue(hass):
    coord, client = _make_coordinator(hass)
    client.async_get_status.side_effect = MideaDishwasherApiClientError("bad frame")
    await _fail_polls(coord, UNREACHABLE_DEVICE_FAILURE_THRESHOLD)
    assert _unreachable_issue(hass) is None
