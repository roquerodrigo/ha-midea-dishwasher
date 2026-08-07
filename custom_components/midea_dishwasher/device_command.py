"""Shared executor that maps device command failures onto translated errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .exceptions import MideaDishwasherApiClientError

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from .coordinator import MideaDishwasherDataUpdateCoordinator


async def async_run_device_command(
    coordinator: MideaDishwasherDataUpdateCoordinator,
    command: Awaitable[None],
) -> None:
    """Await a device command and refresh, translating client failures."""
    try:
        await command
    except MideaDishwasherApiClientError as exception:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="command_failed",
            translation_placeholders={"error": str(exception)},
        ) from exception
    await coordinator.async_request_refresh()
