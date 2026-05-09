from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from custom_components.midea_dishwasher.api import (
    MideaDishwasherApiClient,
    _to_status_data,
)
from custom_components.midea_dishwasher.exceptions import (
    MideaDishwasherApiClientAuthenticationError,
    MideaDishwasherApiClientCommunicationError,
    MideaDishwasherApiClientError,
)


def _client(hass) -> MideaDishwasherApiClient:
    return MideaDishwasherApiClient(
        hass=hass,
        host="1.2.3.4",
        port=6444,
        device_id=42,
        token=b"\x00" * 64,
        key=b"\x00" * 32,
    )


def _patch_transport(transport_factory):
    return patch(
        "custom_components.midea_dishwasher.api.V3Transport",
        transport_factory,
    )


def _patch_client(client_factory):
    return patch(
        "custom_components.midea_dishwasher.api.Client",
        client_factory,
    )


class _FakeTransport:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        return None


def _fake_status() -> SimpleNamespace:
    return SimpleNamespace(
        machine_state="power_on",
        cycle_state="work",
        mode="eco",
        extra_drying=True,
        wash_stage=2,
        error_code=0,
        left_time=42,
        door_closed=True,
        bright_lack=False,
        bright=3,
    )


def test_communication_error_is_api_error():
    assert issubclass(
        MideaDishwasherApiClientCommunicationError,
        MideaDishwasherApiClientError,
    )


def test_auth_error_is_api_error():
    assert issubclass(
        MideaDishwasherApiClientAuthenticationError,
        MideaDishwasherApiClientError,
    )


def test_api_error_is_exception():
    assert issubclass(MideaDishwasherApiClientError, Exception)


def test_to_status_data_maps_all_fields():
    result = _to_status_data(_fake_status())
    assert result == {
        "machine_state": "power_on",
        "cycle_state": "work",
        "mode": "eco",
        "extra_drying": True,
        "wash_stage": 2,
        "error_code": 0,
        "left_time": 42,
        "door_closed": True,
        "bright_lack": False,
        "bright": 3,
    }


def test_to_status_data_handles_none_bright():
    status = _fake_status()
    status.bright = None
    assert _to_status_data(status)["bright"] is None


def test_to_status_data_handles_none_mode():
    status = _fake_status()
    status.mode = None
    assert _to_status_data(status)["mode"] is None


def test_to_status_data_handles_int_mode_passthrough():
    status = _fake_status()
    status.mode = 0x10  # an unknown program byte
    assert _to_status_data(status)["mode"] is None


def test_to_status_data_handles_none_machine_state():
    status = _fake_status()
    status.machine_state = None
    assert _to_status_data(status)["machine_state"] is None


def test_to_status_data_handles_none_cycle_state():
    status = _fake_status()
    status.cycle_state = None
    assert _to_status_data(status)["cycle_state"] is None


def test_to_status_data_handles_none_wash_stage():
    status = _fake_status()
    status.wash_stage = None
    assert _to_status_data(status)["wash_stage"] is None


async def test_get_status_returns_typed_dict(hass):
    fake_client = MagicMock()
    fake_client.query_status = MagicMock(return_value=_fake_status())
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
    ):
        result = await _client(hass).async_get_status()
    assert result["machine_state"] == "power_on"
    assert result["left_time"] == 42


async def test_power_on_calls_library(hass):
    fake_client = MagicMock()
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
    ):
        await _client(hass).async_power_on()
    fake_client.power_on.assert_called_once()


async def test_power_off_calls_library(hass):
    fake_client = MagicMock()
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
    ):
        await _client(hass).async_power_off()
    fake_client.power_off.assert_called_once()


async def test_v3_error_maps_to_auth_error(hass):
    from midea_dishwasher_api.security import V3Error

    fake_client = MagicMock()
    fake_client.query_status = MagicMock(side_effect=V3Error("bad key"))
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
        pytest.raises(MideaDishwasherApiClientAuthenticationError),
    ):
        await _client(hass).async_get_status()


async def test_frame_error_maps_to_api_error(hass):
    from midea_dishwasher_api.protocol import FrameError

    fake_client = MagicMock()
    fake_client.query_status = MagicMock(side_effect=FrameError("bad frame"))
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
        pytest.raises(MideaDishwasherApiClientError) as exc_info,
    ):
        await _client(hass).async_get_status()
    assert not isinstance(exc_info.value, MideaDishwasherApiClientCommunicationError)
    assert not isinstance(exc_info.value, MideaDishwasherApiClientAuthenticationError)


async def test_os_error_maps_to_communication_error(hass):
    fake_client = MagicMock()
    fake_client.query_status = MagicMock(side_effect=OSError("refused"))
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
        pytest.raises(MideaDishwasherApiClientCommunicationError),
    ):
        await _client(hass).async_get_status()


async def test_power_on_propagates_v3_error(hass):
    from midea_dishwasher_api.security import V3Error

    fake_client = MagicMock()
    fake_client.power_on = MagicMock(side_effect=V3Error("nope"))
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
        pytest.raises(MideaDishwasherApiClientAuthenticationError),
    ):
        await _client(hass).async_power_on()


async def test_cancel_work_calls_library(hass):
    fake_client = MagicMock()
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
    ):
        await _client(hass).async_cancel_work()
    fake_client.cancel_work.assert_called_once()


async def test_set_bright_calls_library_with_enum(hass):
    fake_client = MagicMock()
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
    ):
        await _client(hass).async_set_bright(3)
    fake_client.set_bright.assert_called_once()
    bright = fake_client.set_bright.call_args.args[0]
    assert int(bright) == 3


async def test_set_bright_rejects_out_of_range(hass):
    with pytest.raises(ValueError, match="not a valid"):
        await _client(hass).async_set_bright(99)


async def test_start_cycle_calls_library(hass):
    fake_client = MagicMock()
    with (
        _patch_transport(_FakeTransport),
        _patch_client(MagicMock(return_value=fake_client)),
    ):
        await _client(hass).async_start_cycle("eco", extra_drying=True)
    fake_client.start_to_work.assert_called_once()
    kwargs = fake_client.start_to_work.call_args.kwargs
    assert str(kwargs["mode"]) == "eco"
    assert kwargs["extra_drying"] is True


async def test_start_cycle_rejects_unknown_mode(hass):
    with pytest.raises(ValueError, match="not a valid"):
        await _client(hass).async_start_cycle("not-a-real-mode")
