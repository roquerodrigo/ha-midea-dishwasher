from __future__ import annotations

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from voluptuous import Invalid

from custom_components.midea_dishwasher.const import DOMAIN
from custom_components.midea_dishwasher.exceptions import (
    MideaDishwasherApiClientCommunicationError,
)
from custom_components.midea_dishwasher.services import SERVICE_START_CYCLE


async def test_service_is_registered_without_a_config_entry(
    hass, enable_custom_integrations
):
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, DOMAIN, {})
    assert hass.services.has_service(DOMAIN, SERVICE_START_CYCLE)


async def test_service_invokes_client(hass, setup_integration, mock_api_client):
    await hass.services.async_call(
        DOMAIN,
        SERVICE_START_CYCLE,
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


async def test_service_defaults_extra_drying_to_false(
    hass, setup_integration, mock_api_client
):
    await hass.services.async_call(
        DOMAIN,
        SERVICE_START_CYCLE,
        {"config_entry_id": setup_integration.entry_id, "mode": "rapid"},
        blocking=True,
    )
    mock_api_client.async_start_cycle.assert_awaited_once_with(
        mode="rapid", extra_drying=False
    )


async def test_service_rejects_an_unknown_entry(hass, setup_integration):
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_START_CYCLE,
            {"config_entry_id": "does-not-exist", "mode": "eco"},
            blocking=True,
        )


async def test_service_rejects_an_unloaded_entry(hass, setup_integration):
    await hass.config_entries.async_unload(setup_integration.entry_id)
    await hass.async_block_till_done()

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_START_CYCLE,
            {"config_entry_id": setup_integration.entry_id, "mode": "eco"},
            blocking=True,
        )


async def test_service_rejects_an_unknown_mode(hass, setup_integration):
    with pytest.raises(Invalid):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_START_CYCLE,
            {"config_entry_id": setup_integration.entry_id, "mode": "not-a-program"},
            blocking=True,
        )


async def test_service_translates_a_client_failure(
    hass, setup_integration, mock_api_client
):
    mock_api_client.async_start_cycle.side_effect = (
        MideaDishwasherApiClientCommunicationError("down")
    )
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_START_CYCLE,
            {"config_entry_id": setup_integration.entry_id, "mode": "eco"},
            blocking=True,
        )
