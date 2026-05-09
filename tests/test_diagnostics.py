from __future__ import annotations

from custom_components.midea_dishwasher.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_redacts_token(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["entry"]["data"]["token"] == "**REDACTED**"


async def test_diagnostics_redacts_key(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["entry"]["data"]["key"] == "**REDACTED**"


async def test_diagnostics_keeps_host_visible(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["entry"]["data"]["host"] == "192.168.5.100"


async def test_diagnostics_redacts_device_id(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["entry"]["data"]["device_id"] == "**REDACTED**"


async def test_diagnostics_includes_entry_metadata(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["entry"]["domain"] == "midea_dishwasher"
    assert diag["entry"]["version"] == 1
    assert "title" in diag["entry"]


async def test_diagnostics_includes_coordinator_data(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert diag["coordinator_data"]["machine_state"] == "power_on"


async def test_diagnostics_options_redacted_when_present(hass, setup_integration):
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert isinstance(diag["entry"]["options"], dict)
