from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState

from tests.conftest import USER_INPUT


async def test_setup_entry_loads_successfully(hass, setup_integration):
    assert setup_integration.state == ConfigEntryState.LOADED


async def test_setup_entry_creates_sensor_entities(hass, setup_integration):
    assert len(hass.states.async_all("sensor")) == 5


async def test_setup_entry_creates_binary_sensor_entities(hass, setup_integration):
    assert len(hass.states.async_all("binary_sensor")) == 3


async def test_setup_entry_creates_switch_entity(hass, setup_integration):
    assert len(hass.states.async_all("switch")) == 1


async def test_setup_entry_creates_button_entity(hass, setup_integration):
    assert len(hass.states.async_all("button")) == 3


async def test_setup_entry_creates_number_entity(hass, setup_integration):
    assert len(hass.states.async_all("number")) == 1


async def test_start_cycle_service_registered(hass, setup_integration):
    from custom_components.midea_dishwasher.const import DOMAIN

    assert hass.services.has_service(DOMAIN, "start_cycle")


async def test_start_cycle_service_invokes_client(
    hass, setup_integration, mock_api_client
):
    from custom_components.midea_dishwasher.const import DOMAIN

    await hass.services.async_call(
        DOMAIN,
        "start_cycle",
        {
            "config_entry_id": setup_integration.entry_id,
            "mode": "eco",
            "extra_drying": True,
        },
        blocking=True,
    )
    mock_api_client.async_start_cycle.assert_awaited_once_with(
        mode="eco", extra_drying=True
    )


async def test_start_cycle_service_unknown_entry_raises(hass, setup_integration):
    import pytest
    from homeassistant.exceptions import ServiceValidationError

    from custom_components.midea_dishwasher.const import DOMAIN

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            "start_cycle",
            {
                "config_entry_id": "does-not-exist",
                "mode": "eco",
                "extra_drying": False,
            },
            blocking=True,
        )


async def test_setup_entry_registers_update_listener(hass, setup_integration):
    assert len(setup_integration.update_listeners) == 1


async def test_unload_entry_succeeds(hass, setup_integration):
    assert await hass.config_entries.async_unload(setup_integration.entry_id)
    assert setup_integration.state == ConfigEntryState.NOT_LOADED


async def test_unload_entry_makes_entities_unavailable(hass, setup_integration):
    await hass.config_entries.async_unload(setup_integration.entry_id)
    await hass.async_block_till_done()
    for state in hass.states.async_all("sensor"):
        assert state.state == "unavailable"


async def test_reload_entry_restores_loaded_state(
    hass, setup_integration, mock_api_client
):
    await hass.config_entries.async_reload(setup_integration.entry_id)
    await hass.async_block_till_done()
    assert setup_integration.state == ConfigEntryState.LOADED


async def test_async_reload_entry_calls_reload(
    hass, setup_integration, mock_api_client
):
    from custom_components.midea_dishwasher import async_reload_entry

    await async_reload_entry(hass, setup_integration)
    await hass.async_block_till_done()
    assert setup_integration.state == ConfigEntryState.LOADED


async def test_runtime_data_populated(hass, setup_integration):
    assert setup_integration.runtime_data.client is not None
    assert setup_integration.runtime_data.coordinator is not None
    assert setup_integration.runtime_data.integration is not None


async def test_scan_interval_defaults_to_const(hass, setup_integration):
    from datetime import timedelta

    from custom_components.midea_dishwasher.const import (
        DEFAULT_SCAN_INTERVAL_SECONDS,
    )

    assert setup_integration.runtime_data.coordinator.update_interval == timedelta(
        seconds=DEFAULT_SCAN_INTERVAL_SECONDS
    )


async def test_scan_interval_picks_up_options(
    hass, enable_custom_integrations, mock_api_client
):
    from datetime import timedelta

    from homeassistant.const import CONF_SCAN_INTERVAL
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    from custom_components.midea_dishwasher.const import DOMAIN

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=USER_INPUT,
        options={CONF_SCAN_INTERVAL: 60},
        unique_id=str(USER_INPUT["device_id"]),
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.runtime_data.coordinator.update_interval == timedelta(seconds=60)
