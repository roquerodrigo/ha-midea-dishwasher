"""Integration-level service registration for midea_dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .labels import MODE_LABELS

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

    from .data import MideaDishwasherData

SERVICE_START_CYCLE: str = "start_cycle"

ATTR_CONFIG_ENTRY_ID: str = "config_entry_id"
ATTR_MODE: str = "mode"
ATTR_EXTRA_DRYING: str = "extra_drying"

_START_CYCLE_SCHEMA: vol.Schema = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_MODE): vol.In(MODE_LABELS),
        vol.Optional(ATTR_EXTRA_DRYING, default=False): cv.boolean,
    },
)


class MideaDishwasherStartCycleService:
    """Handler for the ``midea_dishwasher.start_cycle`` action."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Store the hass instance used to resolve the targeted config entry."""
        self._hass = hass

    async def async_handle(self, call: ServiceCall) -> None:
        """Start the requested cycle on the targeted dishwasher."""
        data = self._loaded_entry_data(call.data[ATTR_CONFIG_ENTRY_ID])
        await data.client.async_start_cycle(
            mode=call.data[ATTR_MODE],
            extra_drying=call.data[ATTR_EXTRA_DRYING],
        )
        await data.coordinator.async_request_refresh()

    def _loaded_entry_data(self, entry_id: str) -> MideaDishwasherData:
        """Return the runtime data of a loaded entry, or raise for the user."""
        entry = self._hass.config_entries.async_get_entry(entry_id)
        if entry is None or entry.domain != DOMAIN:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entry_not_found",
                translation_placeholders={"entry_id": entry_id},
            )
        if entry.state is not ConfigEntryState.LOADED:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="entry_not_loaded",
                translation_placeholders={"entry_id": entry_id},
            )
        return cast("MideaDishwasherData", entry.runtime_data)


def async_register_services(hass: HomeAssistant) -> None:
    """Register the integration-level actions."""
    service = MideaDishwasherStartCycleService(hass)
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_CYCLE,
        service.async_handle,
        schema=_START_CYCLE_SCHEMA,
    )
