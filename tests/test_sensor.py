from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.midea_dishwasher.sensor import (
    MideaDishwasherCycleProgressSensor,
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
    assert len(hass.states.async_all("sensor")) == 6


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


def _make_cycle_progress_sensor(data=None):
    sensor = MideaDishwasherCycleProgressSensor(_make_coordinator(data))
    sensor._record_cycle_total()
    return sensor


def _advance_cycle(sensor, **changes):
    sensor.coordinator.data = {**sensor.coordinator.data, **changes}
    sensor._record_cycle_total()
    return sensor


async def test_cycle_progress_sensor_state(hass, setup_integration):
    state = hass.states.get("sensor.dishwasher_cycle_progress")
    assert state is not None
    assert state.state == "0"
    assert state.attributes["unit_of_measurement"] == "%"
    assert state.attributes["cycle_total_minutes"] == 42


async def test_cycle_progress_sensor_follows_coordinator(
    hass, setup_integration, mock_api_client, sample_status
):
    mock_api_client.async_get_status.return_value = {**sample_status, "left_time": 21}
    entry = setup_integration
    await entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get("sensor.dishwasher_cycle_progress").state == "50"


async def test_cycle_progress_sensor_restores_cycle_total(
    hass, mock_api_client, enable_custom_integrations
):
    from homeassistant.core import State
    from pytest_homeassistant_custom_component.common import (
        MockConfigEntry,
        mock_restore_cache,
    )

    from custom_components.midea_dishwasher.const import DOMAIN
    from tests.conftest import USER_INPUT

    mock_restore_cache(
        hass,
        (State("sensor.dishwasher_cycle_progress", "50", {"cycle_total_minutes": 84}),),
    )
    entry = MockConfigEntry(
        domain=DOMAIN, data=USER_INPUT, unique_id=str(USER_INPUT["device_id"])
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.dishwasher_cycle_progress").state == "50"


def test_cycle_progress_starts_at_zero():
    assert _make_cycle_progress_sensor(SAMPLE_STATUS).native_value == 0


def test_cycle_progress_halfway_through_the_cycle():
    sensor = _make_cycle_progress_sensor(SAMPLE_STATUS)
    assert _advance_cycle(sensor, left_time=21).native_value == 50


def test_cycle_progress_rounds_to_whole_percent():
    sensor = _make_cycle_progress_sensor(SAMPLE_STATUS)
    assert _advance_cycle(sensor, left_time=20).native_value == 52


def test_cycle_progress_reaches_full_when_nothing_is_left():
    sensor = _make_cycle_progress_sensor(SAMPLE_STATUS)
    assert _advance_cycle(sensor, left_time=0).native_value == 100


def test_cycle_progress_grows_the_total_when_remaining_time_increases():
    sensor = _make_cycle_progress_sensor(SAMPLE_STATUS)
    _advance_cycle(sensor, left_time=60)
    assert sensor.extra_state_attributes == {"cycle_total_minutes": 60}
    assert sensor.native_value == 0


def test_cycle_progress_keeps_the_total_when_remaining_time_is_missing():
    sensor = _make_cycle_progress_sensor(SAMPLE_STATUS)
    _advance_cycle(sensor, left_time=None)
    assert sensor.extra_state_attributes == {"cycle_total_minutes": 42}
    assert sensor.native_value is None


def test_cycle_progress_drops_the_total_once_the_cycle_ends():
    sensor = _make_cycle_progress_sensor(SAMPLE_STATUS)
    _advance_cycle(sensor, cycle_state="idle", left_time=None)
    assert sensor.extra_state_attributes == {}
    assert sensor.native_value is None


def test_cycle_progress_none_when_not_running():
    data = {**SAMPLE_STATUS, "cycle_state": "idle", "left_time": None}
    assert _make_cycle_progress_sensor(data).native_value is None


def test_cycle_progress_none_before_first_refresh():
    assert _make_cycle_progress_sensor(None).native_value is None


def test_cycle_progress_none_when_the_total_is_zero():
    data = {**SAMPLE_STATUS, "left_time": 0}
    assert _make_cycle_progress_sensor(data).native_value is None


def test_cycle_progress_restore_ignores_a_missing_state():
    sensor = _make_cycle_progress_sensor(None)
    sensor._restore_cycle_total(None)
    assert sensor.extra_state_attributes == {}


def test_cycle_progress_restore_ignores_an_unusable_total():
    sensor = _make_cycle_progress_sensor(None)
    for total in ("84", 0, None):
        sensor._restore_cycle_total(
            MagicMock(attributes={"cycle_total_minutes": total})
        )
    assert sensor.extra_state_attributes == {}


def test_cycle_progress_unique_id():
    assert (
        MideaDishwasherCycleProgressSensor(_make_coordinator()).unique_id
        == "eid_cycle_progress"
    )
