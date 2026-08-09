# CLAUDE.md

Guidance for Claude Code (claude.ai/code) agents working in this repository.

## Always read `CODE_STYLE.md` first

Before creating, renaming or restructuring any file/class/function, **read [`CODE_STYLE.md`](./CODE_STYLE.md)**. It is the single source of truth for conventions: language, file organisation, naming, typing, properties vs `__init__`, imports, docstrings, comments, coordinator pattern, repairs/diagnostics layout, translations, lint workflow.

For user-facing topics (entities, how to obtain `token`/`key`, layout diagram, useful commands, CI list), see [`README.md`](./README.md).

This file deliberately avoids restating those rules — it only adds:

1. The verification workflow agents must run after every change.
2. The architectural reasoning that is not obvious from `CODE_STYLE.md` alone.

## Verification workflow

**After every code change, always run lint then tests, in that order, before declaring the task done:**

```bash
scripts/lint
```

- `scripts/lint` chains `uv run ruff format .`, `uv run ruff check . --fix`, `uv run mypy custom_components/midea_dishwasher` and `uv run pytest` (config in `pyproject.toml`); running the four commands directly is equivalent. Fix any failure and re-run before moving on.
- `pytest` enforces a **90 % coverage gate** (config in `pyproject.toml`).

Both gates mirror CI (`.github/workflows/ci.yml`). Skip this only when the change literally cannot affect lint or tests (e.g., README-only edits).

## Architecture

The integration follows the HA `DataUpdateCoordinator` pattern over a synchronous LAN library, wrapped through the executor. Entity platforms use one class per file — `sensor/`, `binary_sensor/` and `button/` are directories, `number.py` and `switch.py` single files.

### Why a sync library wrapped in `async_add_executor_job`

[`midea-dishwasher-api`](https://pypi.org/project/midea-dishwasher-api/) is intentionally synchronous (raw TCP socket + AES-128-CBC + SHA-256). HA is asyncio-first, so every device call is wrapped in `hass.async_add_executor_job`. Each call opens a fresh `V3Transport`, performs the operation, and closes it — sturdier against NAT timeouts than holding a long-lived connection across coroutine suspensions.

### Entry typing

The `data/` package holds one file per type: `MideaDishwasherConfigEntry = ConfigEntry[MideaDishwasherData]` and the `type` aliases live in `data/__init__.py`, the `MideaDishwasherData(client, coordinator, integration)` dataclass in `data/runtime.py`, and each TypedDict in its own module. State lives on `entry.runtime_data` (auto-discarded on unload), never on `hass.data`. The coordinator's payload is the JSON-friendly `MideaDishwasherStatusData` TypedDict, projected from the library's `DishwasherStatus` dataclass by `api._to_status_data` so diagnostics serialization is free.

### Derived cycle progress

The protocol carries no elapsed time or percentage — `left_time` (minutes
remaining, only while `cycle_state == work`) is the only progress figure the
device sends. `MideaDishwasherCycleProgressSensor` therefore records the longest
`left_time` seen since the cycle started as the cycle duration and reports how
much of it has elapsed. The duration is published as the `cycle_total_minutes`
state attribute and restored via `RestoreEntity`, so a restart mid-cycle keeps
the baseline instead of restarting the percentage at zero; it is dropped as soon
as the device leaves `work`.

### Enum labels come from the library

`labels.py` derives every enum string from `midea_dishwasher_api`'s own enums:
the `StrEnum` values for cycle state and mode, the lowercased member names for
the two `IntEnum`s (wash stage, error code). `api._to_status_data` stores those
labels in the payload, the enum sensors expose them through `options`, and the
`start_cycle` schema validates against them — so an option list is never typed
out twice. `tests/test_labels.py` asserts the labels, the translation files and
`services.yaml` agree; a new program in the library surfaces there as a failing
test rather than as an untranslated state in the UI.

### Actions are registered in async_setup

`async_setup` registers `start_cycle` once per Home Assistant start, config
entry or not (the `action-setup` quality-scale rule), and
`MideaDishwasherStartCycleService` resolves the targeted entry per call. It
raises a translated `ServiceValidationError` when the entry is unknown or not
loaded — without that check, `entry.runtime_data` on an unloaded entry raises
`AttributeError` at the user.

### Device commands raise translated errors

Every command surface — the `button`/`switch`/`number` entities and the
`start_cycle` action — goes through `device_command.async_run_device_command`,
which awaits the client call, converts any `MideaDishwasherApiClientError`
into a `HomeAssistantError` with the `command_failed` translation key, and
requests a coordinator refresh only on success. Client exceptions never reach
the frontend raw.

### PARALLEL_UPDATES

Read-only platforms declare `PARALLEL_UPDATES = 0`; `button`, `number` and
`switch` declare `1`. The device serves a single LAN session at a time, so two
commands issued together (two buttons pressed in one script) would race for the
socket and one of them would fail the handshake.

### Config flow surface

`config_flow.py` implements four user-facing steps; all share one `_validate` helper, one `_normalize` helper, and one `_credentials_schema` builder:

- `async_step_user` — initial setup; sets unique_id from `device_id`, aborts on duplicate.
- `async_step_reauth` / `async_step_reauth_confirm` — fired when the coordinator raises `ConfigEntryAuthFailed` (cryptographic handshake failure). `async_update_reload_and_abort` rotates credentials in place.
- `async_step_reconfigure` — lets the user edit credentials via the integration's three-dot menu, no delete-and-re-add cycle.
- Both reauth and reconfigure set the unique id from the submitted `device_id` and abort with `wrong_device` on mismatch, so an entry can never be repointed at a different appliance.
- `async_get_options_flow` — returns `MideaDishwasherOptionsFlow` from `options_flow.py` (one class per file).

`_validate` rejects bad hex up front (token must be 128 hex chars, key 64) before attempting a network call.

### Options flow

`options_flow.py` exposes `scan_interval` (seconds; min 10, default 30). Changing it triggers `async_reload_entry`, which re-instantiates the coordinator with the new `update_interval`. The defaults are tighter than a typical cloud integration because the LAN round-trip is cheap.

### API client

`api.py` exposes `MideaDishwasherApiClient` plus the `_to_status_data` projector. Exceptions live under `exceptions/`:

- `MideaDishwasherApiClientError` (base; covers `FrameError` and other library-level malformed-frame issues)
- `MideaDishwasherApiClientCommunicationError` (`OSError` family — connection refused, timeouts, DNS failures)
- `MideaDishwasherApiClientAuthenticationError` (`V3Error` from the LAN handshake — wrong token/key, signature mismatch)

The single `_sync_run[T]` helper wraps every device call in the same try/except envelope so the same mapping rules apply to status reads and control commands.

### Diagnostics

`diagnostics.py` returns `MideaDishwasherDiagnosticsPayload`. `token`, `key` and `device_id` are redacted via `async_redact_data` (driven by `TO_REDACT: frozenset[str]`). `host` is intentionally left visible — it speeds up troubleshooting and isn't sensitive on its own. `.github/ISSUE_TEMPLATE/bug.yml` asks users to attach the dump.

### Repairs

`repairs.py` is the entry point HA calls when the user clicks **Fix** on an issue:

- `async_create_fix_flow(hass, issue_id, data)` returns a `RepairsFlow`. Branch on `issue_id` for multiple kinds; the default returns `ConfirmRepairFlow`.
- The coordinator calls `async_raise_unreachable_device_issue` after three consecutive communication failures and `async_clear_unreachable_device_issue` on the next successful poll, so the `unreachable_device` Repair card tracks the device's actual reachability.

Issue strings live under `issues.<issue_id>` in the translation files.

## Gotchas

- This repo has no `tool.uv.default-groups`, so a bare `uv sync` won't pull in `dev`/`lint`. Use `scripts/setup` (which runs `uv sync --group dev --group lint`) to bootstrap a clone or the devcontainer.
- The `midea-dishwasher-api` pin lives in **two places**: `pyproject.toml`'s `dev` group (used for tests/mypy) and `manifest.json`'s `requirements` (what HA actually installs at runtime). Dependabot's `uv`-ecosystem entry only bumps the former; `tests/test_manifest.py` fails whenever the two drift, so an SDK bump PR must update `manifest.json` in the same change.
- `api.py` imports `FrameError` from `midea_dishwasher_api.protocol` and `V3Error` from `midea_dishwasher_api.security` — submodule paths, not the top-level re-exports (`midea_dishwasher_api`'s `__init__.py`) that the SDK repo documents as its stable public surface. An internal reshuffle on the SDK side (even a patch release) can break these two imports without touching its documented public API.
