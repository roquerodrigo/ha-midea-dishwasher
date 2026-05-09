"""Midea Dishwasher integration for Home Assistant."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, cast

from homeassistant.const import CONF_SCAN_INTERVAL, Platform
from homeassistant.loader import async_get_loaded_integration

from .api import MideaDishwasherApiClient
from .const import DEFAULT_SCAN_INTERVAL_SECONDS
from .coordinator import MideaDishwasherDataUpdateCoordinator
from .data import MideaDishwasherData
from .services import async_register_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import MideaDishwasherConfigData, MideaDishwasherConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MideaDishwasherConfigEntry,
) -> bool:
    """Set up Midea Dishwasher from a config entry."""
    config = cast("MideaDishwasherConfigData", entry.data)
    scan_interval_seconds: int = int(
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS),
    )
    coordinator = MideaDishwasherDataUpdateCoordinator(
        hass=hass,
        scan_interval=timedelta(seconds=scan_interval_seconds),
    )
    entry.runtime_data = MideaDishwasherData(
        client=MideaDishwasherApiClient(
            hass=hass,
            host=str(config["host"]),
            port=int(config["port"]),
            device_id=int(config["device_id"]),
            token=bytes.fromhex(config["token"]),
            key=bytes.fromhex(config["key"]),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    async_register_services(hass)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MideaDishwasherConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: MideaDishwasherConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
