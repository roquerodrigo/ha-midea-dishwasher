"""Constants for midea_dishwasher."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "midea_dishwasher"
ATTRIBUTION = "Data provided by the local Midea LAN V3 protocol"

DEFAULT_PORT = 6444
DEFAULT_SCAN_INTERVAL_SECONDS = 30
MIN_SCAN_INTERVAL_SECONDS = 10

CONF_DEVICE_ID = "device_id"
CONF_TOKEN = "token"  # noqa: S105
CONF_KEY = "key"

TOKEN_HEX_LEN = 128
KEY_HEX_LEN = 64
