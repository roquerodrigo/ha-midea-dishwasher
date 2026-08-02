"""Cycle-progress sensor: percentage of the running cycle already elapsed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.restore_state import RestoreEntity

from ..entity import MideaDishwasherEntity

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import State

    from ..coordinator import MideaDishwasherDataUpdateCoordinator
    from ..data import MideaDishwasherStatusData

ATTR_CYCLE_TOTAL_MINUTES = "cycle_total_minutes"

_RUNNING_CYCLE_STATE = "work"
_FULL_PERCENTAGE = 100


class MideaDishwasherCycleProgressSensor(
    MideaDishwasherEntity, RestoreEntity, SensorEntity
):
    """
    Percentage sensor derived from the minutes left in the running cycle.

    The device reports no elapsed time, so the cycle duration is the longest
    ``left_time`` seen since the cycle started and is restored on reload —
    otherwise a restart mid-cycle would restart the percentage at zero.
    """

    _attr_translation_key = "cycle_progress"
    _attr_icon = "mdi:percent"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MideaDishwasherDataUpdateCoordinator) -> None:
        """Initialize the sensor with no cycle duration recorded yet."""
        super().__init__(coordinator)
        self._cycle_total_minutes: int | None = None

    @property
    def unique_id(self) -> str:
        """Return a unique id derived from entry id."""
        return f"{self.coordinator.config_entry.entry_id}_cycle_progress"

    @property
    def native_value(self) -> int | None:
        """Return the elapsed percentage, or None when no cycle is running."""
        left_time = self._left_time() if self._is_running() else None
        total = self._cycle_total_minutes
        if left_time is None or total is None or total <= 0:
            return None
        elapsed_percentage = round((total - left_time) / total * 100)
        return min(max(elapsed_percentage, 0), _FULL_PERCENTAGE)

    @property
    def extra_state_attributes(self) -> Mapping[str, int]:
        """Expose the recorded cycle duration, which also survives a restart."""
        if self._cycle_total_minutes is None:
            return {}
        return {ATTR_CYCLE_TOTAL_MINUTES: self._cycle_total_minutes}

    async def async_added_to_hass(self) -> None:
        """Restore the recorded cycle duration and adopt the latest status."""
        self._restore_cycle_total(await self.async_get_last_state())
        self._record_cycle_total()
        await super().async_added_to_hass()

    def _handle_coordinator_update(self) -> None:
        """Record the cycle duration before publishing the new state."""
        self._record_cycle_total()
        super()._handle_coordinator_update()

    def _record_cycle_total(self) -> None:
        """Track the longest remaining time seen during the current cycle."""
        if not self._is_running():
            self._cycle_total_minutes = None
            return
        left_time = self._left_time()
        if left_time is None:
            return
        if self._cycle_total_minutes is None or left_time > self._cycle_total_minutes:
            self._cycle_total_minutes = left_time

    def _restore_cycle_total(self, last_state: State | None) -> None:
        """Adopt the cycle duration stored on the previous state, if any."""
        if last_state is None:
            return
        total = last_state.attributes.get(ATTR_CYCLE_TOTAL_MINUTES)
        if isinstance(total, int) and total > 0:
            self._cycle_total_minutes = total

    def _left_time(self) -> int | None:
        """Return the remaining minutes from the latest status payload."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        return data["left_time"] if data is not None else None

    def _is_running(self) -> bool:
        """Return whether the device reports a cycle in progress."""
        data: MideaDishwasherStatusData | None = self.coordinator.data
        return data is not None and data["cycle_state"] == _RUNNING_CYCLE_STATE
