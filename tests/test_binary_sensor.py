from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.midea_dishwasher.binary_sensor import (
    MideaDishwasherDoorBinarySensor,
    MideaDishwasherExtraDryingBinarySensor,
    MideaDishwasherRinseAidBinarySensor,
)

CLOSED_OK = {
    "machine_state": "power_on",
    "cycle_state": "work",
    "wash_stage": 2,
    "error_code": 0,
    "left_time": 42,
    "door_closed": True,
    "bright_lack": False,
    "extra_drying": True,
}

OPEN_LOW = {
    **CLOSED_OK,
    "door_closed": False,
    "bright_lack": True,
    "extra_drying": False,
}


def _make_coordinator(data=None):
    coord = MagicMock()
    coord.data = data
    coord.config_entry.entry_id = "eid"
    return coord


async def test_binary_sensor_count(hass, setup_integration):
    assert len(hass.states.async_all("binary_sensor")) == 3


async def test_door_state_when_closed(hass, setup_integration):
    state = hass.states.get("binary_sensor.dishwasher_door")
    assert state.state == "off"


async def test_rinse_aid_state_when_full(hass, setup_integration):
    state = hass.states.get("binary_sensor.dishwasher_rinse_aid")
    assert state.state == "off"


async def test_extra_drying_state_when_enabled(hass, setup_integration):
    state = hass.states.get("binary_sensor.dishwasher_extra_drying")
    assert state.state == "on"


def test_door_inverts_door_closed_true():
    sensor = MideaDishwasherDoorBinarySensor(_make_coordinator(CLOSED_OK))
    assert sensor.is_on is False


def test_door_inverts_door_closed_false():
    sensor = MideaDishwasherDoorBinarySensor(_make_coordinator(OPEN_LOW))
    assert sensor.is_on is True


def test_door_returns_none_before_first_refresh():
    sensor = MideaDishwasherDoorBinarySensor(_make_coordinator(None))
    assert sensor.is_on is None


def test_rinse_aid_passes_through_bright_lack():
    sensor = MideaDishwasherRinseAidBinarySensor(_make_coordinator(OPEN_LOW))
    assert sensor.is_on is True


def test_rinse_aid_returns_none_before_first_refresh():
    sensor = MideaDishwasherRinseAidBinarySensor(_make_coordinator(None))
    assert sensor.is_on is None


def test_extra_drying_passes_through_true():
    sensor = MideaDishwasherExtraDryingBinarySensor(_make_coordinator(CLOSED_OK))
    assert sensor.is_on is True


def test_extra_drying_passes_through_false():
    sensor = MideaDishwasherExtraDryingBinarySensor(_make_coordinator(OPEN_LOW))
    assert sensor.is_on is False


def test_extra_drying_returns_none_before_first_refresh():
    sensor = MideaDishwasherExtraDryingBinarySensor(_make_coordinator(None))
    assert sensor.is_on is None


def test_unique_ids():
    coord = _make_coordinator()
    assert MideaDishwasherDoorBinarySensor(coord).unique_id == "eid_door"
    assert MideaDishwasherRinseAidBinarySensor(coord).unique_id == "eid_rinse_aid"
    assert MideaDishwasherExtraDryingBinarySensor(coord).unique_id == "eid_extra_drying"
