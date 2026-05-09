"""Start-intensive button: kicks off the intensive program with extra drying."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from ..entity import MideaDishwasherEntity


class MideaDishwasherStartIntensiveButton(MideaDishwasherEntity, ButtonEntity):
    """Quick-start button that runs the intensive program with extra drying."""

    _attr_translation_key = "start_intensive"
    _attr_icon = "mdi:lightning-bolt"

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_start_intensive"

    async def async_press(self) -> None:
        """Start the intensive cycle with extra drying on the dishwasher."""
        await self.coordinator.config_entry.runtime_data.client.async_start_cycle(
            mode="intensive",
            extra_drying=True,
        )
        await self.coordinator.async_request_refresh()
