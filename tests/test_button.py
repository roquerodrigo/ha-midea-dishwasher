from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.midea_dishwasher.button import (
    MideaDishwasherCancelButton,
    MideaDishwasherStartEcoButton,
    MideaDishwasherStartIntensiveButton,
)


def _make_coordinator():
    coord = MagicMock()
    coord.config_entry.entry_id = "eid"
    coord.config_entry.runtime_data.client.async_cancel_work = AsyncMock()
    coord.config_entry.runtime_data.client.async_start_cycle = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    return coord


async def test_button_count(hass, setup_integration):
    assert len(hass.states.async_all("button")) == 3


async def test_press_cancel_calls_cancel_and_refresh():
    coord = _make_coordinator()
    await MideaDishwasherCancelButton(coord).async_press()
    coord.config_entry.runtime_data.client.async_cancel_work.assert_awaited_once()
    coord.async_request_refresh.assert_awaited_once()


async def test_press_start_eco_uses_eco_no_extra_drying():
    coord = _make_coordinator()
    await MideaDishwasherStartEcoButton(coord).async_press()
    coord.config_entry.runtime_data.client.async_start_cycle.assert_awaited_once_with(
        mode="eco", extra_drying=False
    )
    coord.async_request_refresh.assert_awaited_once()


async def test_press_start_intensive_uses_intensive_with_extra_drying():
    coord = _make_coordinator()
    await MideaDishwasherStartIntensiveButton(coord).async_press()
    coord.config_entry.runtime_data.client.async_start_cycle.assert_awaited_once_with(
        mode="intensive", extra_drying=True
    )


def test_unique_ids():
    coord = _make_coordinator()
    assert MideaDishwasherCancelButton(coord).unique_id == "eid_cancel"
    assert MideaDishwasherStartEcoButton(coord).unique_id == "eid_start_eco"
    assert MideaDishwasherStartIntensiveButton(coord).unique_id == "eid_start_intensive"
