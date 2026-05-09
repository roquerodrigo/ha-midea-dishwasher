from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.midea_dishwasher.sensor import (
    MideaDishwasherErrorSensor,
    MideaDishwasherModeSensor,
    MideaDishwasherProgressSensor,
    MideaDishwasherStatusSensor,
    MideaDishwasherTimeRemainingSensor,
)

SAMPLE_STATUS = {
    "machine_state": "power_on",
    "cycle_state": "work",
    "mode": "eco",
    "wash_stage": 2,
    "error_code": 0,
    "left_time": 42,
    "door_closed": True,
    "bright_lack": False,
    "bright": 3,
}


def _make_coordinator(data=None):
    coord = MagicMock()
    coord.data = data
    coord.config_entry.entry_id = "eid"
    return coord


async def test_sensor_count(hass, setup_integration):
    assert len(hass.states.async_all("sensor")) == 5


async def test_status_sensor_state(hass, setup_integration):
    state = hass.states.get("sensor.dishwasher_status")
    assert state is not None
    assert state.state == "work"


async def test_progress_sensor_state(hass, setup_integration):
    state = hass.states.get("sensor.dishwasher_progress")
    assert state is not None
    assert state.state == "main_wash"


async def test_time_remaining_sensor_state(hass, setup_integration):
    state = hass.states.get("sensor.dishwasher_time_remaining")
    assert state is not None
    assert state.state in {"42", "0.7", "0.70", "0.700"}
    assert state.attributes["device_class"] == "duration"


async def test_error_sensor_state(hass, setup_integration):
    state = hass.states.get("sensor.dishwasher_error_code")
    assert state is not None
    assert state.state == "none"


def test_status_native_value():
    sensor = MideaDishwasherStatusSensor(_make_coordinator(SAMPLE_STATUS))
    assert sensor.native_value == "work"


def test_status_native_value_none_before_first_refresh():
    sensor = MideaDishwasherStatusSensor(_make_coordinator(None))
    assert sensor.native_value is None


def test_status_unique_id():
    assert MideaDishwasherStatusSensor(_make_coordinator()).unique_id == "eid_status"


def test_progress_native_value_known():
    sensor = MideaDishwasherProgressSensor(_make_coordinator(SAMPLE_STATUS))
    assert sensor.native_value == "main_wash"


def test_progress_native_value_all_codes():
    expected = ("idle", "pre_wash", "main_wash", "rinse", "dry", "finish")
    for stage, label in enumerate(expected):
        data = {**SAMPLE_STATUS, "wash_stage": stage}
        assert (
            MideaDishwasherProgressSensor(_make_coordinator(data)).native_value == label
        )


def test_progress_native_value_unknown_stage():
    data = {**SAMPLE_STATUS, "wash_stage": 99}
    assert MideaDishwasherProgressSensor(_make_coordinator(data)).native_value is None


def test_progress_native_value_explicit_none():
    data = {**SAMPLE_STATUS, "wash_stage": None}
    assert MideaDishwasherProgressSensor(_make_coordinator(data)).native_value is None


def test_progress_native_value_no_data():
    assert MideaDishwasherProgressSensor(_make_coordinator(None)).native_value is None


def test_progress_unique_id():
    assert (
        MideaDishwasherProgressSensor(_make_coordinator()).unique_id == "eid_progress"
    )


def test_time_remaining_native_value():
    sensor = MideaDishwasherTimeRemainingSensor(_make_coordinator(SAMPLE_STATUS))
    assert sensor.native_value == 42


def test_time_remaining_native_value_none():
    sensor = MideaDishwasherTimeRemainingSensor(_make_coordinator(None))
    assert sensor.native_value is None


def test_time_remaining_suggests_hours():
    sensor = MideaDishwasherTimeRemainingSensor(_make_coordinator())
    assert sensor.suggested_unit_of_measurement == "h"


def test_time_remaining_unique_id():
    assert (
        MideaDishwasherTimeRemainingSensor(_make_coordinator()).unique_id
        == "eid_time_remaining"
    )


def test_error_native_value_none_for_zero():
    sensor = MideaDishwasherErrorSensor(_make_coordinator(SAMPLE_STATUS))
    assert sensor.native_value == "none"


def test_error_native_value_known_codes():
    for code, expected in enumerate(
        ("none", "water_supply", "heating", "overflow", "water_valve")
    ):
        data = {**SAMPLE_STATUS, "error_code": code}
        assert (
            MideaDishwasherErrorSensor(_make_coordinator(data)).native_value == expected
        )


def test_error_native_value_unknown_code_returns_none():
    data = {**SAMPLE_STATUS, "error_code": 99}
    assert MideaDishwasherErrorSensor(_make_coordinator(data)).native_value is None


def test_error_native_value_no_data_returns_none():
    assert MideaDishwasherErrorSensor(_make_coordinator(None)).native_value is None


def test_error_unique_id():
    assert MideaDishwasherErrorSensor(_make_coordinator()).unique_id == "eid_error"


async def test_mode_sensor_state(hass, setup_integration):
    state = hass.states.get("sensor.dishwasher_program")
    assert state is not None
    assert state.state == "eco"


def test_mode_native_value_known():
    sensor = MideaDishwasherModeSensor(_make_coordinator(SAMPLE_STATUS))
    assert sensor.native_value == "eco"


def test_mode_native_value_none_when_no_program():
    data = {**SAMPLE_STATUS, "mode": None}
    assert MideaDishwasherModeSensor(_make_coordinator(data)).native_value is None


def test_mode_native_value_none_for_unknown_mode():
    data = {**SAMPLE_STATUS, "mode": "weird"}
    assert MideaDishwasherModeSensor(_make_coordinator(data)).native_value is None


def test_mode_native_value_none_no_data():
    assert MideaDishwasherModeSensor(_make_coordinator(None)).native_value is None


def test_mode_unique_id():
    assert MideaDishwasherModeSensor(_make_coordinator()).unique_id == "eid_mode"
