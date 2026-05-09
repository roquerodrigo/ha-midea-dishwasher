from __future__ import annotations

from unittest.mock import AsyncMock, patch

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.midea_dishwasher.const import DOMAIN
from custom_components.midea_dishwasher.exceptions import (
    MideaDishwasherApiClientAuthenticationError,
    MideaDishwasherApiClientCommunicationError,
    MideaDishwasherApiClientError,
)
from tests.conftest import SAMPLE_STATUS

VALID_TOKEN = "ab" * 64
VALID_KEY = "cd" * 32

USER_INPUT = {
    "host": "192.168.5.100",
    "port": 6444,
    "device_id": 151732606394621,
    "token": VALID_TOKEN,
    "key": VALID_KEY,
}
NEW_INPUT = {
    "host": "192.168.5.101",
    "port": 6444,
    "device_id": 151732606394621,
    "token": VALID_TOKEN,
    "key": VALID_KEY,
}


class _ClientPatches:
    """Patch both config_flow and setup_entry import sites simultaneously."""

    def __init__(self):
        self._patches = (
            patch(
                "custom_components.midea_dishwasher.config_flow.MideaDishwasherApiClient"
            ),
            patch("custom_components.midea_dishwasher.MideaDishwasherApiClient"),
        )

    def __enter__(self):
        mocks = [p.start() for p in self._patches]
        for m in mocks:
            m.return_value.async_get_status = AsyncMock(return_value=SAMPLE_STATUS)
        return mocks[0]

    def __exit__(self, *exc):
        for p in self._patches:
            p.stop()


def _patch_client():
    return _ClientPatches()


async def _start_user_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_step_user_shows_form(hass, enable_custom_integrations):
    result = await _start_user_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_step_user_success_creates_entry(hass, enable_custom_integrations):
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value={})
        result = await _start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=USER_INPUT
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["host"] == USER_INPUT["host"]
    assert result["data"]["device_id"] == USER_INPUT["device_id"]


async def test_step_user_success_sets_unique_id(hass, enable_custom_integrations):
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value={})
        flow = await _start_user_flow(hass)
        await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=USER_INPUT
        )
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.unique_id == str(USER_INPUT["device_id"])


async def test_step_user_duplicate_aborts(hass, enable_custom_integrations):
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value={})
        flow1 = await _start_user_flow(hass)
        await hass.config_entries.flow.async_configure(
            flow1["flow_id"], user_input=USER_INPUT
        )
        flow2 = await _start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow2["flow_id"], user_input=USER_INPUT
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_step_user_auth_error_shows_auth(hass, enable_custom_integrations):
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(
            side_effect=MideaDishwasherApiClientAuthenticationError("bad")
        )
        flow = await _start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=USER_INPUT
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "auth"


async def test_step_user_communication_error_shows_connection(
    hass, enable_custom_integrations
):
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(
            side_effect=MideaDishwasherApiClientCommunicationError("down")
        )
        flow = await _start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=USER_INPUT
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "connection"


async def test_step_user_generic_error_shows_unknown(hass, enable_custom_integrations):
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(
            side_effect=MideaDishwasherApiClientError("oops")
        )
        flow = await _start_user_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            flow["flow_id"], user_input=USER_INPUT
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


async def test_step_user_invalid_hex_shows_invalid_credentials(
    hass, enable_custom_integrations
):
    flow = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input={**USER_INPUT, "token": "not-hex"},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_credentials"


async def test_step_user_short_token_shows_invalid_credentials(
    hass, enable_custom_integrations
):
    flow = await _start_user_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input={**USER_INPUT, "token": "ab" * 4},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_credentials"


# --- .env pre-fill ---------------------------------------------------------


def test_parse_env_defaults_complete_file():
    from custom_components.midea_dishwasher.config_flow import _parse_env_defaults

    text = (
        "# comment\n"
        "DEVICE_HOST=192.168.1.50\n"
        'DEVICE_PORT="6444"\n'
        "DEVICE_ID=999\n"
        f"DEVICE_TOKEN={VALID_TOKEN}\n"
        f"DEVICE_KEY={VALID_KEY}\n"
    )
    assert _parse_env_defaults(text) == {
        "host": "192.168.1.50",
        "port": 6444,
        "device_id": 999,
        "token": VALID_TOKEN,
        "key": VALID_KEY,
    }


def test_parse_env_defaults_none_input_returns_none():
    from custom_components.midea_dishwasher.config_flow import _parse_env_defaults

    assert _parse_env_defaults(None) is None


def test_parse_env_defaults_partial_returns_none():
    from custom_components.midea_dishwasher.config_flow import _parse_env_defaults

    assert _parse_env_defaults("DEVICE_HOST=1.2.3.4\n") is None


def test_parse_env_defaults_bad_port_returns_none():
    from custom_components.midea_dishwasher.config_flow import _parse_env_defaults

    text = (
        "DEVICE_HOST=1.2.3.4\n"
        "DEVICE_PORT=not-a-number\n"
        "DEVICE_ID=1\n"
        f"DEVICE_TOKEN={VALID_TOKEN}\n"
        f"DEVICE_KEY={VALID_KEY}\n"
    )
    assert _parse_env_defaults(text) is None


def test_read_env_file_sync_returns_none_when_absent(tmp_path, monkeypatch):
    from custom_components.midea_dishwasher import config_flow

    monkeypatch.setattr(config_flow, "_ENV_PATH", tmp_path / "nope.env")
    assert config_flow._read_env_file_sync() is None


def test_read_env_file_sync_returns_text(tmp_path, monkeypatch):
    from custom_components.midea_dishwasher import config_flow

    env = tmp_path / ".env"
    env.write_text("hello\n", encoding="utf-8")
    monkeypatch.setattr(config_flow, "_ENV_PATH", env)
    assert config_flow._read_env_file_sync() == "hello\n"


async def test_step_user_form_prefills_from_env(
    hass, enable_custom_integrations, tmp_path, monkeypatch
):
    from custom_components.midea_dishwasher import config_flow

    env = tmp_path / ".env"
    env.write_text(
        "DEVICE_HOST=10.0.0.42\n"
        "DEVICE_PORT=6444\n"
        "DEVICE_ID=42\n"
        f"DEVICE_TOKEN={VALID_TOKEN}\n"
        f"DEVICE_KEY={VALID_KEY}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_flow, "_ENV_PATH", env)

    result = await _start_user_flow(hass)
    schema = result["data_schema"].schema
    host_key = next(k for k in schema if getattr(k, "schema", k) == "host")
    assert host_key.default() == "10.0.0.42"


async def test_step_user_form_has_no_prefill_when_env_missing(
    hass, enable_custom_integrations, tmp_path, monkeypatch
):
    from custom_components.midea_dishwasher import config_flow

    monkeypatch.setattr(config_flow, "_ENV_PATH", tmp_path / "absent.env")

    result = await _start_user_flow(hass)
    schema = result["data_schema"].schema
    host_key = next(k for k in schema if getattr(k, "schema", k) == "host")
    assert host_key.default is vol.UNDEFINED


async def test_load_env_defaults_uses_executor(hass, tmp_path, monkeypatch):
    """Live test that the async helper round-trips through the executor."""
    from custom_components.midea_dishwasher import config_flow

    env = tmp_path / ".env"
    env.write_text(
        "DEVICE_HOST=1.2.3.4\n"
        "DEVICE_PORT=6444\n"
        "DEVICE_ID=1\n"
        f"DEVICE_TOKEN={VALID_TOKEN}\n"
        f"DEVICE_KEY={VALID_KEY}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(config_flow, "_ENV_PATH", env)
    result = await config_flow._load_env_defaults(hass)
    assert result is not None
    assert result["host"] == "1.2.3.4"


# --- Reauth ----------------------------------------------------------------


def _existing_entry(hass) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=USER_INPUT,
        unique_id=str(USER_INPUT["device_id"]),
    )
    entry.add_to_hass(hass)
    return entry


async def test_reauth_shows_confirm_form(hass, enable_custom_integrations):
    entry = _existing_entry(hass)
    result = await entry.start_reauth_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"


async def test_reauth_success_updates_entry(hass, enable_custom_integrations):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value=SAMPLE_STATUS)
        result = await entry.start_reauth_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=NEW_INPUT
        )
        await hass.async_block_till_done()
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data["host"] == "192.168.5.101"


async def test_reauth_auth_error_shows_auth(hass, enable_custom_integrations):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(
            side_effect=MideaDishwasherApiClientAuthenticationError("nope")
        )
        result = await entry.start_reauth_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=NEW_INPUT
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "auth"


# --- Reconfigure -----------------------------------------------------------


async def test_reconfigure_shows_form(hass, enable_custom_integrations):
    entry = _existing_entry(hass)
    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"


async def test_reconfigure_success_updates_entry(hass, enable_custom_integrations):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value=SAMPLE_STATUS)
        result = await entry.start_reconfigure_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=NEW_INPUT
        )
        await hass.async_block_till_done()
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data["host"] == "192.168.5.101"


async def test_reconfigure_communication_error_shows_connection(
    hass, enable_custom_integrations
):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(
            side_effect=MideaDishwasherApiClientCommunicationError("down")
        )
        result = await entry.start_reconfigure_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=NEW_INPUT
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "connection"


async def test_reconfigure_generic_error_shows_unknown(
    hass, enable_custom_integrations
):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(
            side_effect=MideaDishwasherApiClientError("oops")
        )
        result = await entry.start_reconfigure_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=NEW_INPUT
        )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"
