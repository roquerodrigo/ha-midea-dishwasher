"""Integration-level service registration for midea_dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import voluptuous as vol
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .data import MideaDishwasherData

SERVICE_START_CYCLE: str = "start_cycle"

_VALID_MODES: tuple[str, ...] = (
    "auto",
    "intensive",
    "normal",
    "eco",
    "glass",
    "90min",
    "1hour",
    "rapid",
    "soak",
    "3in1",
    "hygiene",
    "quiet",
    "party",
    "fruit",
)

_START_CYCLE_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required("config_entry_id"): cv.string,
        vol.Required("mode"): vol.In(_VALID_MODES),
        vol.Optional("extra_drying", default=False): cv.boolean,
    },
)


def async_register_services(hass: HomeAssistant) -> None:
    """Register integration-level services (idempotent across config entries)."""
    if hass.services.has_service(DOMAIN, SERVICE_START_CYCLE):
        return

    async def _start_cycle(call: ServiceCall) -> None:
        entry_id: str = call.data["config_entry_id"]
        entry = hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            msg = f"Config entry {entry_id} is not a Midea Dishwasher entry"
            raise ServiceValidationError(msg)
        data = cast("MideaDishwasherData", entry.runtime_data)
        await data.client.async_start_cycle(
            mode=call.data["mode"],
            extra_drying=call.data["extra_drying"],
        )
        await data.coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_START_CYCLE,
        _start_cycle,
        schema=_START_CYCLE_SCHEMA,
    )
