"""Exception classes for the midea_dishwasher API client."""

from __future__ import annotations

from .api_client_authentication_error import (
    MideaDishwasherApiClientAuthenticationError,
)
from .api_client_communication_error import (
    MideaDishwasherApiClientCommunicationError,
)
from .api_client_error import MideaDishwasherApiClientError

__all__ = [
    "MideaDishwasherApiClientAuthenticationError",
    "MideaDishwasherApiClientCommunicationError",
    "MideaDishwasherApiClientError",
]
