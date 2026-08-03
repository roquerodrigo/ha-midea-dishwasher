"""Typed shape of the LAN credentials persisted on the config entry."""

from __future__ import annotations

from typing import TypedDict


class MideaDishwasherConfigData(TypedDict):
    """Shape of the LAN credentials persisted on the config entry."""

    host: str
    port: int
    device_id: int
    token: str
    key: str
