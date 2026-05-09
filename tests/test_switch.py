from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.midea_dishwasher.switch import MideaDishwasherPowerSwitch

POWER_ON_DATA = {
    "machine_state": "power_on",
    "cycle_state": "work",
    "wash_stage": 2,
    "error_code": 0,
    "left_time": 42,
    "door_closed": True,
    "bright_lack": False,
}

POWER_OFF_DATA = {**POWER_ON_DATA, "machine_state": "power_off"}


def _make_switch(data=None) -> MideaDishwasherPowerSwitch:
    coord = MagicMock()
    coord.data = data
    coord.config_entry.entry_id = "eid"
    coord.config_entry.runtime_data.client.async_power_on = AsyncMock()
    coord.config_entry.runtime_data.client.async_power_off = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    return MideaDishwasherPowerSwitch(coord)


async def test_switch_count(hass, setup_integration):
    assert len(hass.states.async_all("switch")) == 1


async def test_switch_is_on_when_power_on(hass, setup_integration):
    state = hass.states.get("switch.dishwasher_power")
    assert state.state == "on"


def test_is_on_true_for_power_on():
    assert _make_switch(POWER_ON_DATA).is_on is True


def test_is_on_false_for_power_off():
    assert _make_switch(POWER_OFF_DATA).is_on is False


def test_is_on_none_before_first_refresh():
    assert _make_switch(None).is_on is None


async def test_turn_on_calls_client():
    switch = _make_switch(POWER_OFF_DATA)
    await switch.async_turn_on()
    switch.coordinator.config_entry.runtime_data.client.async_power_on.assert_awaited_once()
    switch.coordinator.async_request_refresh.assert_awaited_once()


async def test_turn_off_calls_client():
    switch = _make_switch(POWER_ON_DATA)
    await switch.async_turn_off()
    switch.coordinator.config_entry.runtime_data.client.async_power_off.assert_awaited_once()
    switch.coordinator.async_request_refresh.assert_awaited_once()


def test_unique_id_combines_entry_id_and_key():
    assert _make_switch().unique_id == "eid_power"
