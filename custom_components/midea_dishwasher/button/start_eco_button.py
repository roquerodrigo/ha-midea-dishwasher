"""Start-ECO button: kicks off the ECO program with no extra drying."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from ..entity import MideaDishwasherEntity


class MideaDishwasherStartEcoButton(MideaDishwasherEntity, ButtonEntity):
    """Quick-start button that runs the ECO program."""

    _attr_translation_key = "start_eco"
    _attr_icon = "mdi:leaf"

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_start_eco"

    async def async_press(self) -> None:
        """Start the ECO cycle on the dishwasher."""
        await self.coordinator.config_entry.runtime_data.client.async_start_cycle(
            mode="eco",
            extra_drying=False,
        )
        await self.coordinator.async_request_refresh()
