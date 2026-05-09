"""
Midea Dishwasher API client.

Thin asynchronous facade over the synchronous ``midea_dishwasher_api``
package. Each call opens a fresh ``V3Transport`` LAN session, performs the
operation, and closes it — sturdier against NAT timeouts than holding a
long-lived connection across coroutine suspensions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from midea_dishwasher_api import BrightLevel, Client, Mode, V3Transport
from midea_dishwasher_api.protocol import FrameError
from midea_dishwasher_api.security import V3Error

from .exceptions import (
    MideaDishwasherApiClientAuthenticationError,
    MideaDishwasherApiClientCommunicationError,
    MideaDishwasherApiClientError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from midea_dishwasher_api.state import DishwasherStatus

    from .data import MideaDishwasherStatusData


def _to_status_data(status: DishwasherStatus) -> MideaDishwasherStatusData:
    """Project the library dataclass onto the JSON-friendly TypedDict."""
    machine_state = status.machine_state
    cycle_state = status.cycle_state
    mode = status.mode
    wash_stage = status.wash_stage
    bright = status.bright
    return {
        "machine_state": str(machine_state) if machine_state is not None else None,
        "cycle_state": str(cycle_state) if cycle_state is not None else None,
        "mode": str(mode) if isinstance(mode, str) else None,
        "extra_drying": status.extra_drying,
        "wash_stage": int(wash_stage) if wash_stage is not None else None,
        "error_code": int(status.error_code),
        "left_time": status.left_time,
        "door_closed": status.door_closed,
        "bright_lack": status.bright_lack,
        "bright": int(bright) if bright is not None else None,
    }


class MideaDishwasherApiClient:
    """Async client wrapping the synchronous LAN V3 protocol library."""

    def __init__(  # noqa: PLR0913 — five fields of one logical (host, creds) bundle.
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        device_id: int,
        token: bytes,
        key: bytes,
    ) -> None:
        """Initialize."""
        self._hass = hass
        self._host = host
        self._port = port
        self._device_id = device_id
        self._token = token
        self._key = key

    async def async_get_status(self) -> MideaDishwasherStatusData:
        """Open a session, query status, close, and return a JSON-safe dict."""
        return await self._hass.async_add_executor_job(self._sync_get_status)

    async def async_power_on(self) -> None:
        """Power on the dishwasher."""
        await self._hass.async_add_executor_job(self._sync_power_on)

    async def async_power_off(self) -> None:
        """Power off the dishwasher."""
        await self._hass.async_add_executor_job(self._sync_power_off)

    async def async_cancel_work(self) -> None:
        """Cancel the running cycle."""
        await self._hass.async_add_executor_job(self._sync_cancel_work)

    async def async_set_bright(self, level: int) -> None:
        """Set the rinse-aid brightness level (1-5)."""
        bright = BrightLevel(level)
        await self._hass.async_add_executor_job(self._sync_set_bright, bright)

    async def async_start_cycle(self, mode: str, *, extra_drying: bool = False) -> None:
        """Start a wash cycle with the given mode."""
        mode_enum = Mode(mode)
        await self._hass.async_add_executor_job(
            self._sync_start_cycle, mode_enum, extra_drying
        )

    def _sync_get_status(self) -> MideaDishwasherStatusData:
        return self._sync_run(lambda client: _to_status_data(client.query_status()))

    def _sync_power_on(self) -> None:
        self._sync_run(lambda client: client.power_on())

    def _sync_power_off(self) -> None:
        self._sync_run(lambda client: client.power_off())

    def _sync_cancel_work(self) -> None:
        self._sync_run(lambda client: client.cancel_work())

    def _sync_set_bright(self, level: BrightLevel) -> None:
        self._sync_run(lambda client: client.set_bright(level))

    def _sync_start_cycle(self, mode: Mode, extra_drying: bool) -> None:  # noqa: FBT001
        self._sync_run(
            lambda client: client.start_to_work(mode=mode, extra_drying=extra_drying),
        )

    def _sync_run[T](self, action: Callable[[Client], T]) -> T:
        try:
            with self._build_transport() as transport:
                return action(Client(send=transport))
        except V3Error as exception:
            msg = f"LAN session error - {exception}"
            raise MideaDishwasherApiClientAuthenticationError(msg) from exception
        except FrameError as exception:
            msg = f"Malformed frame from device - {exception}"
            raise MideaDishwasherApiClientError(msg) from exception
        except OSError as exception:
            msg = f"Network error talking to device - {exception}"
            raise MideaDishwasherApiClientCommunicationError(msg) from exception

    def _build_transport(self) -> V3Transport:
        return V3Transport(
            host=self._host,
            port=self._port,
            device_id=self._device_id,
            token=self._token,
            key=self._key,
        )
