from __future__ import annotations

import copy
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

# Pre-import the integration so submodule attribute lookups succeed even when
# only one test file is collected (fixtures patch
# ``custom_components.midea_dishwasher.MideaDishwasherApiClient`` and rely on
# the submodule being attached to the namespace package).
import custom_components.midea_dishwasher  # noqa: F401

if TYPE_CHECKING:
    from collections.abc import Generator

pytest_plugins = "pytest_homeassistant_custom_component"

SAMPLE_STATUS = {
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

VALID_TOKEN = "ab" * 64
VALID_KEY = "cd" * 32
USER_INPUT = {
    "host": "192.168.5.100",
    "port": 6444,
    "device_id": 151732606394621,
    "token": VALID_TOKEN,
    "key": VALID_KEY,
}


@pytest.fixture
def sample_status() -> dict:
    return copy.deepcopy(SAMPLE_STATUS)


@pytest.fixture
def enable_custom_integrations(hass) -> None:
    from homeassistant.loader import DATA_CUSTOM_COMPONENTS

    hass.data.pop(DATA_CUSTOM_COMPONENTS, None)


@pytest.fixture
def mock_api_client(sample_status: dict) -> Generator:
    with patch(
        "custom_components.midea_dishwasher.MideaDishwasherApiClient"
    ) as mock_class:
        instance = mock_class.return_value
        instance.async_get_status = AsyncMock(return_value=sample_status)
        instance.async_power_on = AsyncMock(return_value=None)
        instance.async_power_off = AsyncMock(return_value=None)
        instance.async_cancel_work = AsyncMock(return_value=None)
        instance.async_set_bright = AsyncMock(return_value=None)
        instance.async_start_cycle = AsyncMock(return_value=None)
        yield instance


@pytest.fixture
async def setup_integration(hass, mock_api_client, enable_custom_integrations):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.midea_dishwasher.const import DOMAIN

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=USER_INPUT,
        unique_id=str(USER_INPUT["device_id"]),
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
