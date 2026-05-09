"""DataUpdateCoordinator for midea_dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER
from .exceptions import (
    MideaDishwasherApiClientAuthenticationError,
    MideaDishwasherApiClientError,
)

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from .data import MideaDishwasherConfigEntry, MideaDishwasherStatusData


class MideaDishwasherDataUpdateCoordinator(
    DataUpdateCoordinator["MideaDishwasherStatusData"]
):
    """Coordinator that polls dishwasher status over the LAN."""

    config_entry: MideaDishwasherConfigEntry

    def __init__(self, hass: HomeAssistant, scan_interval: timedelta) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )

    async def _async_update_data(self) -> MideaDishwasherStatusData:
        """Fetch the latest status from the dishwasher."""
        try:
            return await self.config_entry.runtime_data.client.async_get_status()
        except MideaDishwasherApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MideaDishwasherApiClientError as exception:
            raise UpdateFailed(exception) from exception
