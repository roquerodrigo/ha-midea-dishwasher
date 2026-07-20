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
uv run ruff format . && uv run ruff check . --fix && uv run mypy custom_components/midea_dishwasher && uv run pytest
```

- The lint commands run `ruff format`, `ruff check --fix` and `mypy` (config in `pyproject.toml`). Fix any failure and re-run before moving on.
- `pytest` enforces a **90 % coverage gate** (config in `pyproject.toml`).

Both gates mirror CI (`.github/workflows/ci.yml`). Skip this only when the change literally cannot affect lint or tests (e.g., README-only edits).

## Architecture

The integration follows the HA `DataUpdateCoordinator` pattern over a synchronous LAN library, wrapped through the executor. Entity platforms (`sensor/`, `binary_sensor/`, `button/`) use one class per file.

### Why a sync library wrapped in `async_add_executor_job`

[`midea-dishwasher-api`](https://pypi.org/project/midea-dishwasher-api/) is intentionally synchronous (raw TCP socket + AES-128-CBC + SHA-256). HA is asyncio-first, so every device call is wrapped in `hass.async_add_executor_job`. Each call opens a fresh `V3Transport`, performs the operation, and closes it — sturdier against NAT timeouts than holding a long-lived connection across coroutine suspensions.

### Entry typing

`data.py` defines `MideaDishwasherConfigEntry = ConfigEntry[MideaDishwasherData]` and the `MideaDishwasherData(client, coordinator, integration)` dataclass. State lives on `entry.runtime_data` (auto-discarded on unload), never on `hass.data`. The coordinator's payload is the JSON-friendly `MideaDishwasherStatusData` TypedDict, projected from the library's `DishwasherStatus` dataclass by `api._to_status_data` so diagnostics serialization is free.

### Config flow surface

`config_flow.py` implements four user-facing steps; all share one `_validate` helper, one `_normalize` helper, and one `_credentials_schema` builder:

- `async_step_user` — initial setup; sets unique_id from `device_id`, aborts on duplicate.
- `async_step_reauth` / `async_step_reauth_confirm` — fired when the coordinator raises `ConfigEntryAuthFailed` (cryptographic handshake failure). `async_update_reload_and_abort` rotates credentials in place.
- `async_step_reconfigure` — lets the user edit credentials via the integration's three-dot menu, no delete-and-re-add cycle.
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
- `async_raise_unreachable_device_issue(hass)` is the sample helper that registers an issue. Call helpers like this from the coordinator/setup when you detect a recoverable problem (e.g., consistent connection failures).

Issue strings live under `issues.<issue_id>` in the translation files.

## Gotchas

- `scripts/setup` and `.devcontainer.json`'s `postCreateCommand` still run `pip install --requirement requirements.txt`, but `requirements.txt` was deleted when the repo migrated to `uv` (see `git log -- requirements.txt`) and the scripts were never updated. Bootstrapping a fresh clone or devcontainer via `scripts/setup` fails; run `uv sync --all-groups` instead (this repo has no `tool.uv.default-groups`, so a bare `uv sync` won't pull in `dev`/`lint`).
- The `midea-dishwasher-api` pin lives in **two places** that must be kept in sync by hand: `pyproject.toml`'s `dev` group (used for tests/mypy) and `manifest.json`'s `requirements` (what HA actually installs at runtime). Dependabot's `uv`-ecosystem entry only bumps the former, and nothing in CI checks the latter — a SDK version bump PR needs `manifest.json` updated manually too, or the shipped integration silently stays on the old SDK release.
- `api.py` imports `FrameError` from `midea_dishwasher_api.protocol` and `V3Error` from `midea_dishwasher_api.security` — submodule paths, not the top-level re-exports (`midea_dishwasher_api`'s `__init__.py`) that the SDK repo documents as its stable public surface. An internal reshuffle on the SDK side (even a patch release) can break these two imports without touching its documented public API.
