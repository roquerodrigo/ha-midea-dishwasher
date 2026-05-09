from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.midea_dishwasher.number import MideaDishwasherBrightNumber

SAMPLE_STATUS = {
    "machine_state": "power_on",
    "cycle_state": "work",
    "wash_stage": 2,
    "error_code": 0,
    "left_time": 42,
    "door_closed": True,
    "bright_lack": False,
    "bright": 4,
}


def _make_coordinator(data=None) -> MagicMock:
    coord = MagicMock()
    coord.data = data
    coord.config_entry.entry_id = "eid"
    coord.config_entry.runtime_data.client.async_set_bright = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    return coord


async def test_number_count(hass, setup_integration):
    assert len(hass.states.async_all("number")) == 1


def test_native_value_reads_from_status():
    assert (
        MideaDishwasherBrightNumber(_make_coordinator(SAMPLE_STATUS)).native_value == 4
    )


def test_native_value_none_before_first_refresh():
    assert MideaDishwasherBrightNumber(_make_coordinator(None)).native_value is None


def test_native_value_none_when_status_lacks_bright():
    data = {**SAMPLE_STATUS, "bright": None}
    assert MideaDishwasherBrightNumber(_make_coordinator(data)).native_value is None


async def test_set_native_value_calls_client_and_refreshes():
    coord = _make_coordinator(SAMPLE_STATUS)
    number = MideaDishwasherBrightNumber(coord)
    await number.async_set_native_value(5.0)
    coord.config_entry.runtime_data.client.async_set_bright.assert_awaited_once_with(5)
    coord.async_request_refresh.assert_awaited_once()


def test_unique_id_combines_entry_id_and_key():
    assert MideaDishwasherBrightNumber(_make_coordinator()).unique_id == "eid_bright"
