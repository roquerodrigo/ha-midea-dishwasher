"""Config flow for midea_dishwasher."""

from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector

from .api import MideaDishwasherApiClient
from .const import (
    CONF_DEVICE_ID,
    CONF_KEY,
    CONF_TOKEN,
    DEFAULT_PORT,
    DOMAIN,
    KEY_HEX_LEN,
    LOGGER,
    TOKEN_HEX_LEN,
)
from .exceptions import (
    MideaDishwasherApiClientAuthenticationError,
    MideaDishwasherApiClientCommunicationError,
    MideaDishwasherApiClientError,
)
from .options_flow import MideaDishwasherOptionsFlow

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant

    from .data import MideaDishwasherConfigData, MideaDishwasherConfigEntry

# Convenience for local development: when a `.env` sits next to the HA config
# directory (i.e. in the repo root in this project), pre-fill the form so the
# devloop is "click → click → save". A regular HACS install has no `.env`
# at this path, so this is a no-op for end users.
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
_ENV_KEYS: dict[str, str] = {
    "host": "DEVICE_HOST",
    "port": "DEVICE_PORT",
    "device_id": "DEVICE_ID",
    "token": "DEVICE_TOKEN",
    "key": "DEVICE_KEY",
}


def _read_env_file_sync() -> str | None:
    """Read the local ``.env`` file synchronously, returning ``None`` if absent."""
    try:
        return _ENV_PATH.read_text(encoding="utf-8")
    except OSError:
        return None


def _parse_env_defaults(text: str | None) -> MideaDishwasherConfigData | None:
    """Parse a ``.env`` payload into pre-fill defaults, or ``None``."""
    if text is None:
        return None
    parsed: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        parsed[name.strip()] = value.strip().strip('"').strip("'")
    with suppress(KeyError, ValueError):
        return {
            "host": parsed[_ENV_KEYS["host"]],
            "port": int(parsed[_ENV_KEYS["port"]]),
            "device_id": int(parsed[_ENV_KEYS["device_id"]]),
            "token": parsed[_ENV_KEYS["token"]].lower(),
            "key": parsed[_ENV_KEYS["key"]].lower(),
        }
    return None


async def _load_env_defaults(
    hass: HomeAssistant,
) -> MideaDishwasherConfigData | None:
    """Return form pre-fill defaults from a local ``.env``, or ``None``."""
    text = await hass.async_add_executor_job(_read_env_file_sync)
    return _parse_env_defaults(text)


def _credentials_schema(
    defaults: Mapping[str, str | int] | None = None,
) -> vol.Schema:
    """Build the LAN credentials schema, optionally pre-filled."""
    src: Mapping[str, str | int] = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST,
                default=src.get("host", vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
            ),
            vol.Required(
                CONF_PORT,
                default=src.get("port", DEFAULT_PORT),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=65535,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Required(
                CONF_DEVICE_ID,
                default=src.get("device_id", vol.UNDEFINED),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Required(
                CONF_TOKEN,
                default=src.get("token", vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
            vol.Required(
                CONF_KEY,
                default=src.get("key", vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
        },
    )


def _normalize(user_input: MideaDishwasherConfigData) -> MideaDishwasherConfigData:
    """Coerce form values into the strict TypedDict shape."""
    return {
        "host": str(user_input["host"]).strip(),
        "port": int(user_input["port"]),
        "device_id": int(user_input["device_id"]),
        "token": str(user_input["token"]).strip().lower(),
        "key": str(user_input["key"]).strip().lower(),
    }


class MideaDishwasherFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Midea Dishwasher."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: MideaDishwasherConfigEntry,  # noqa: ARG004
    ) -> MideaDishwasherOptionsFlow:
        """Return the options flow handler."""
        return MideaDishwasherOptionsFlow()

    # The narrowed ``MideaDishwasherConfigData`` parameter is intentional —
    # HA's base class declares ``dict[str, Any] | None`` here, and we trade
    # strict LSP compliance for stronger typing of our own user_input schema.
    async def async_step_user(  # type: ignore[override]
        self,
        user_input: MideaDishwasherConfigData | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        normalized: MideaDishwasherConfigData | None = None

        if user_input is not None:
            normalized = _normalize(user_input)
            errors = await self._validate(normalized)
            if not errors:
                await self.async_set_unique_id(str(normalized["device_id"]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Midea Dishwasher ({normalized['host']})",
                    data=dict(normalized),
                )

        prefill = normalized or await _load_env_defaults(self.hass)
        return self.async_show_form(
            step_id="user",
            data_schema=_credentials_schema(
                defaults=cast("Mapping[str, str | int] | None", prefill),
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, str],  # noqa: ARG002
    ) -> config_entries.ConfigFlowResult:
        """Trigger reauth when the device rejects stored credentials."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: MideaDishwasherConfigData | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Prompt the user for new credentials and update the entry."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            normalized = _normalize(user_input)
            errors = await self._validate(normalized)
            if not errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=dict(normalized),
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_credentials_schema(
                defaults=cast("Mapping[str, str | int]", entry.data),
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: MideaDishwasherConfigData | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Allow editing credentials of an existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            normalized = _normalize(user_input)
            errors = await self._validate(normalized)
            if not errors:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=dict(normalized),
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_credentials_schema(
                defaults=cast("Mapping[str, str | int]", entry.data),
            ),
            errors=errors,
        )

    async def _validate(
        self,
        user_input: MideaDishwasherConfigData,
    ) -> dict[str, str]:
        """Test credentials and return an errors dict (empty on success)."""
        try:
            token = bytes.fromhex(user_input["token"])
            key = bytes.fromhex(user_input["key"])
        except ValueError as exception:
            LOGGER.warning("Token/key is not valid hex: %s", exception)
            return {"base": "invalid_credentials"}
        if len(token) * 2 != TOKEN_HEX_LEN or len(key) * 2 != KEY_HEX_LEN:
            return {"base": "invalid_credentials"}
        try:
            await self._test_credentials(user_input, token=token, key=key)
        except MideaDishwasherApiClientAuthenticationError as exception:
            LOGGER.warning(exception)
            return {"base": "auth"}
        except MideaDishwasherApiClientCommunicationError as exception:
            LOGGER.error(exception)
            return {"base": "connection"}
        except MideaDishwasherApiClientError as exception:
            LOGGER.exception(exception)
            return {"base": "unknown"}
        return {}

    async def _test_credentials(
        self,
        user_input: MideaDishwasherConfigData,
        token: bytes,
        key: bytes,
    ) -> None:
        """Validate credentials against the device by issuing a status query."""
        client = MideaDishwasherApiClient(
            hass=self.hass,
            host=user_input["host"],
            port=user_input["port"],
            device_id=user_input["device_id"],
            token=token,
            key=key,
        )
        await client.async_get_status()
