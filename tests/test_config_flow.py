from __future__ import annotations

from unittest.mock import AsyncMock, patch

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


async def test_reauth_with_a_different_device_id_aborts(
    hass, enable_custom_integrations
):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value=SAMPLE_STATUS)
        result = await entry.start_reauth_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={**NEW_INPUT, "device_id": 999},
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert entry.data["device_id"] == USER_INPUT["device_id"]


async def test_reconfigure_with_a_different_device_id_aborts(
    hass, enable_custom_integrations
):
    entry = _existing_entry(hass)
    with _patch_client() as mock:
        mock.return_value.async_get_status = AsyncMock(return_value=SAMPLE_STATUS)
        result = await entry.start_reconfigure_flow(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={**NEW_INPUT, "device_id": 999},
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "wrong_device"
    assert entry.data["device_id"] == USER_INPUT["device_id"]
