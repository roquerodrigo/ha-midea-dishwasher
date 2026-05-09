"""Cancel button: stops the running cycle."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from ..entity import MideaDishwasherEntity


class MideaDishwasherCancelButton(MideaDishwasherEntity, ButtonEntity):
    """Button that cancels the running cycle."""

    _attr_translation_key = "cancel"
    _attr_icon = "mdi:stop-circle-outline"

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_cancel"

    async def async_press(self) -> None:
        """Send the cancel command to the dishwasher."""
        await self.coordinator.config_entry.runtime_data.client.async_cancel_work()
        await self.coordinator.async_request_refresh()
