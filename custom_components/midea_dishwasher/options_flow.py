"""Options flow for midea_dishwasher."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers import selector

from .const import DEFAULT_SCAN_INTERVAL_SECONDS, MIN_SCAN_INTERVAL_SECONDS

if TYPE_CHECKING:
    from .data import MideaDishwasherOptionsData


class MideaDishwasherOptionsFlow(OptionsFlow):
    """Options flow for Midea Dishwasher."""

    async def async_step_init(
        self,
        user_input: MideaDishwasherOptionsData | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=dict(user_input))

        current_value: int = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL_SECONDS,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_value,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL_SECONDS,
                            step=5,
                            unit_of_measurement="s",
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                },
            ),
        )
