# Code Style Guide

Style conventions for the `ha-midea-dishwasher` project. Before committing, run
`uv run ruff format .`, `uv run ruff check . --fix` and
`uv run mypy custom_components/midea_dishwasher` — they must exit cleanly.
`uv run pytest` (with the 90 % coverage gate) follows.

**Always read this file before adding or restructuring code.**

## Language

- Code is written in **English**: file names, class names, function names,
  variable names, dictionary keys, identifier strings.
- The conversation language with the user can be Portuguese or anything else;
  what is committed to disk stays English.
- User-facing strings live in `custom_components/midea_dishwasher/translations/{en,pt-BR}.json`
  only — never hardcoded in Python.

## File organization

- **One top-level class per file.** Multiple semantically related classes (e.g.
  exception families, entity classes for one platform) get grouped into a
  package directory with one class per submodule and an `__init__.py`
  re-exporting the public symbols.
  - Example: `exceptions/` contains `api_client_error.py`,
    `api_client_communication_error.py`, `api_client_authentication_error.py`,
    plus `__init__.py`.
  - Example: `sensor/` contains `status_sensor.py`, `progress_sensor.py`,
    `time_remaining_sensor.py`, `error_sensor.py`, plus `__init__.py`. Same
    pattern for `binary_sensor/` and `button/`.
- **TypedDicts and `type` aliases do not count as "classes"** for this rule —
  they live alongside related code (typically in `data.py`) and don't need
  their own file.
- **Helper functions** may live in the same file as the single class that uses
  them (e.g. `_verify_response_or_raise` in `api.py`).
- **`__init__.py` of the integration package** wires `async_setup_entry`,
  `async_unload_entry`, `async_reload_entry` and nothing else.

## Entities: one class per entity

- **One class per entity.** Every entity gets its own dedicated class — never
  share a generic class parameterized by an `EntityDescription` subclass with
  callable fields like `value_fn` or `action_fn`. Encode the entity's behaviour
  directly in its class via `@property` and class-level `_attr_*` constants
  (or a plain `EntityDescription` instance assigned at the class level).
  - Don't write a `MideaDishwasherSensorDescription` subclass with a
    `value_fn`/`action_fn` field.
  - Do write `MideaDishwasher<Name><Platform>` (e.g.
    `MideaDishwasherStatusSensor`, `MideaDishwasherCancelButton`,
    `MideaDishwasherDoorBinarySensor`, `MideaDishwasherPowerSwitch`).
- The reason: each entity is a discrete contract; mixing them through a
  generic class hides the contract behind indirection and discourages per-entity
  refinement (icons, state attributes, custom logic).

## Naming

- Public classes are prefixed with `MideaDishwasher`.
- Concrete platform entities end with the entity type: `MideaDishwasherSensor`,
  `MideaDishwasherBinarySensor`, `MideaDishwasherPowerSwitch`,
  `MideaDishwasherCancelButton`.
- Exception classes end with `Error`: `MideaDishwasherApiClientError`,
  `…CommunicationError`, `…AuthenticationError`.
- Private attributes / functions are prefixed with `_`.

## Typing

**Strict typing. No generics, no `Any`.** Mypy enforces this.

Banned: `typing.Any`, `object` as a value type, bare `dict` / `list` / `tuple` /
`set`, `dict[str, Any]`, `Mapping[str, Any]`.

Required:

- `TypedDict` for known dict / JSON shapes (see `data.py`:
  `MideaDishwasherStatusData`, `MideaDishwasherConfigData`,
  `MideaDishwasherOptionsData`, `MideaDishwasherDiagnosticsPayload`).
- `@dataclass` for structured records (`MideaDishwasherData`).
- Named `type` aliases for recursive / shared shapes — `JsonPrimitive`,
  `JsonValue`, `JsonObject` in `data.py`.
- `frozenset[str]` / `tuple[str, ...]` for fixed string collections.
- `cast("TypedDictName", value)` at HA framework boundaries that hand us a
  permissive type (e.g. `entry.data` is `MappingProxyType[str, Any]`).

When narrowing an HA-provided callback signature (e.g. `async_step_user`),
mypy reports `[override]` (Liskov violation). Add `# type: ignore[override]`
with a one-line comment explaining the deliberate narrowing — see
`config_flow.py` for the canonical example.

## Properties and `__init__`

- **Always prefer `@property`** over assigning `_attr_*` values in `__init__`.
  Properties are computed lazily from backing fields stored on the parent class
  (e.g. `self.coordinator`, `self.entity_description`).
- When the body of `__init__` would only call `super().__init__(...)`, omit
  `__init__` entirely and let Python inherit the parent.
- Class-level constants like `_attr_attribution = ATTRIBUTION` and
  `_attr_has_entity_name = True` are fine — they don't depend on instance
  state.

## Imports

- Always start every module with `from __future__ import annotations` so type
  hints become lazy strings and the runtime cost of `if TYPE_CHECKING` imports
  is zero.
- Same-package relative imports (`from .module import …`) are the default.
- Move type-only imports into a `TYPE_CHECKING` block (Ruff `TC001`/`TC003`):

  ```python
  from __future__ import annotations
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from collections.abc import Mapping
      from .data import MideaDishwasherStatusData
  ```

- `noqa` comments are reserved for unavoidable framework constraints (e.g.
  `# noqa: ARG001` for HA-framework callback parameters that must exist but go
  unused). Document the reason inline if non-obvious. Never silence to "make
  ruff happy" — fix the underlying code.

## Docstrings

- Every public class, function, method (including `@property`) and `__init__`
  has a docstring. Ruff enforces this via `D102`/`D107`.
- A single sentence is usually enough. Describe the *contract* or the *why*,
  not the obvious implementation.
- Module-level docstring at the top of every `.py` file.
- Avoid restating the type — the signature already does that.

## Comments

- Default to **no comments**. Add one only when the *why* is not obvious from
  the code: a hidden constraint, a workaround, a subtle invariant, or a
  deliberate type-system override.
- Never describe *what* the code does — well-named identifiers handle that.
- **No section dividers** like `# --- API payloads ---` to group related
  declarations. If a file has so many sections that you feel the need for
  visual separators, split it into multiple files instead.

## Logging

- Each module uses the package-level `LOGGER` from `const.py`
  (`LOGGER: Logger = getLogger(__package__)`); never call `logging.getLogger(...)`
  ad-hoc.
- Use **lazy `%`-formatting**, never f-strings — they force string interpolation
  even when the level is filtered:

  ```python
  LOGGER.warning("Refresh failed: %s", exception)   # ✓
  LOGGER.warning(f"Refresh failed: {exception}")    # ✗
  ```

- Levels:
  - `debug` — successful fetch summaries, every-poll diagnostics.
  - `info` — one-shot lifecycle (setup complete, reauth flow started).
  - `warning` — recoverable failures (transient API error, falling back).
  - `error` / `exception` — unrecoverable in current cycle.
- Never log `token`, `key` or full headers. The API-client boundary should
  swallow the original exception's string form when it could expose them.

## Error messages

- Format: `"Failed to <verb> <object>: <cause>"`. Keep them short and grep-able.
- Pre-validate inputs before the network call so user-facing errors point at
  the bad input, not a downstream traceback (`config_flow._validate` rejects
  malformed token/key hex up front).
- Custom exceptions get the same hierarchy:
  `MideaDishwasherApiClientError` (base; covers `FrameError` and other
  library-level malformed-frame issues) → `…CommunicationError` (`OSError`
  family — connection refused, timeouts, DNS failures) and
  `…AuthenticationError` (`V3Error` from the LAN handshake — wrong token/key,
  signature mismatch). Wrap raw upstream errors at the API client boundary;
  everything above only catches the custom hierarchy.

## Coordinator and runtime data

- All API state flows through `entry.runtime_data: MideaDishwasherData`
  (`data.py`). Never store integration state in `hass.data`.
- The coordinator is typed as `DataUpdateCoordinator[MideaDishwasherStatusData]`.
  `_async_update_data` returns the typed payload; client errors map to
  `UpdateFailed`, authentication errors to `ConfigEntryAuthFailed` (which
  triggers reauth).
- The `midea-dishwasher-api` library is intentionally **synchronous** (raw TCP
  + AES-128-CBC + SHA-256). HA is asyncio-first, so every device call is
  wrapped in `hass.async_add_executor_job`. Each call opens a fresh
  `V3Transport`, performs the operation, and closes it — sturdier against
  NAT timeouts than holding a long-lived connection across coroutine
  suspensions. The single `_sync_run[T]` helper in `api.py` wraps every
  device call in the same try/except envelope so the same mapping rules
  apply to status reads and control commands.

## Config / options / repairs / diagnostics

- `config_flow.py` carries `user`, `reauth`, `reauth_confirm` and `reconfigure`
  steps, all sharing one `_validate` helper, one `_normalize` helper and one
  `_credentials_schema` builder.
- `options_flow.py` exposes `scan_interval` (seconds; min 10, default 30).
  Changing it triggers `async_reload_entry`, which re-instantiates the
  coordinator with the new `update_interval`.
- `repairs.py` exposes `async_create_fix_flow`. Sample helpers like
  `async_raise_unreachable_device_issue` show how to register issues from
  anywhere in the integration.
- `diagnostics.py` returns `MideaDishwasherDiagnosticsPayload`. `token`, `key`
  and `device_id` are redacted via `async_redact_data` (driven by
  `TO_REDACT: frozenset[str]`). `host` is intentionally left visible — it
  speeds up troubleshooting and isn't sensitive on its own.

## Translations

- Two locales: `en.json` and `pt-BR.json`. `tests/test_translations.py`
  parametrizes over every locale and fails if their nested key sets diverge.
- Issue strings live under `issues.<issue_id>`; options strings under
  `options.step.init.data`; flow strings under `config.step.<step_id>`;
  entity names under `entity.<platform>.<key>.name`.

## Pre-commit hooks

`pre-commit` is a dev dependency (`pyproject.toml`) and `.pre-commit-config.yaml`
mirrors the lint commands (ruff format, ruff check). Install once per
clone:

```bash
pre-commit install
```

The hook runs the same gates as CI on every commit. Skip it only on
emergency `git commit --no-verify` and immediately re-run
`uv run ruff format .`, `uv run ruff check . --fix` and
`uv run mypy custom_components/midea_dishwasher`.

## Conventional commits

All commits follow [Conventional Commits](https://www.conventionalcommits.org/),
which `release-please` parses to bump the version and generate `CHANGELOG.md`:

| Type | Meaning | Bump |
|---|---|---|
| `feat` | New feature | minor |
| `fix` | Bug fix | patch |
| `perf` | Performance improvement | patch |
| `deps` | Dependency bump | patch |
| `docs` | Documentation only | none |
| `refactor` | Refactor without behavior change | none |
| `test` | Test-only change | none |
| `ci` | CI / tooling change | none |
| `chore` | Anything else (rarely) | none |

- Subject line: imperative mood, lowercase, no trailing period.
- Use scopes when useful: `feat(switch): expose power on/off control`.
- A `BREAKING CHANGE:` footer (or `!` after type) bumps the major version.

## Linting and verification

- Ruff configuration lives in `pyproject.toml` with `select = ["ALL"]`.
- Mypy configuration lives in `pyproject.toml`. Run both directly:
  `uv run ruff check . --fix` and `uv run mypy custom_components/midea_dishwasher`.
- After every change run `uv run ruff format .`, `uv run ruff check . --fix`,
  `uv run mypy custom_components/midea_dishwasher` and `uv run pytest`. All gates
  mirror CI (`.github/workflows/ci.yml`).
- Tests live in `tests/`, mirroring the production layout. The 90 % coverage
  gate (`pyproject.toml`) prevents untested code from sneaking in. When a test
  exercises a state that is impossible under the new types, update or remove
  it — never weaken the type to satisfy the test.
