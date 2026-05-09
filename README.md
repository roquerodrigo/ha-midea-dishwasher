# Midea Dishwasher for Home Assistant

[![HACS Validate](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/validate.yml/badge.svg)](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/validate.yml)
[![Lint](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/lint.yml/badge.svg)](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/lint.yml)
[![CodeQL](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/codeql.yml/badge.svg)](https://github.com/roquerodrigo/ha-midea-dishwasher/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration for **Midea dishwashers** (`device_type 0xE1`, plugin v5), talking to the appliance directly over the LAN — no cloud round-trips at runtime. Built on top of [`midea-dishwasher-api`](https://pypi.org/project/midea-dishwasher-api/), which implements the `AA … E1` application protocol and the LAN V3 transport (handshake 8370 + AES-128-CBC + SHA-256).

Conventions for contributors live in [`CODE_STYLE.md`](./CODE_STYLE.md); architectural notes for AI agents in [`CLAUDE.md`](./CLAUDE.md).

## Add to Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=roquerodrigo&repository=ha-midea-dishwasher&category=integration)

## What's included

- **Local polling** over LAN V3 — no cloud calls once configured.
- **Config flow** for host, port, device ID, token, key — with reauth and reconfigure flows.
- **Options flow** with a configurable `scan_interval` (default 30 s, min 10 s).
- **Entities**: power switch, door binary sensor, rinse-aid problem sensor, status / progress / time-remaining sensors.
- **Diagnostics platform** with credential redaction (`token`, `key`, `device_id`).
- **Repairs platform** wired into HA's Issue Registry, with a sample `unreachable_device` issue.
- **Translations** for English and Brazilian Portuguese (parity enforced by tests).
- **CI**: ruff lint + format, mypy type-check, `hassfest`, HACS validation, CodeQL.
- **Coverage gate** at 95 % enforced by `pytest.ini` (currently at 100 %).

## Entities

| Domain | Key | Source field |
|---|---|---|
| `switch` | `power` | `machine_state` (calls `power_on` / `power_off`) |
| `binary_sensor` | `door` | `door_closed` (inverted; device class `door`) |
| `binary_sensor` | `rinse_aid` | `bright_lack` (device class `problem`) |
| `sensor` | `status` | `cycle_state` enum (`idle`, `order`, `work`, …) |
| `sensor` | `progress` | `wash_stage` (0–5) |
| `sensor` | `time_remaining` | `left_time` (minutes) |

The set is bounded by what `midea-dishwasher-api` decodes from the device response. Mode, water-softener level, panel brightness and humidity are not currently exposed by the upstream library.

## Obtaining `token` and `key`

`token` (128 hex chars) and `key` (64 hex chars) are device-specific credentials issued by the Midea cloud. The library does not extract them — use one of the existing tools tied to your Midea account:

- [`midea-msmart`](https://github.com/mill1000/midea-msmart) — `midea-discover login`
- [`midea-beautiful-air`](https://github.com/nbogojevic/midea-beautiful-air) — `midea-beautiful-air-cli`
- The **MideaAir** mobile app extraction route described in those projects' docs

Once you have them, paste into the integration's setup form alongside the dishwasher's IP and `device_id`.

## Useful commands

```bash
scripts/setup      # install dependencies (requirements.txt)
scripts/develop    # start Home Assistant in debug mode with the integration loaded
scripts/lint       # ruff format + check + mypy
pytest             # run tests with the 95 % coverage gate
```

Each script auto-detects `./.venv` and prepends it to `PATH` — no `source .venv/bin/activate` needed. For ad-hoc commands the same trick works: `.venv/bin/pytest`, `.venv/bin/ruff …`.

HA runs with config in `config/` and `PYTHONPATH` pointing at `custom_components/` — no symlinks. To recreate entity/device IDs during development:

```bash
rm config/.storage/core.entity_registry config/.storage/core.device_registry
```

## Layout

```
custom_components/midea_dishwasher/
├── __init__.py        # async_setup_entry / unload / reload
├── api.py             # MideaDishwasherApiClient (executor-wrapped LAN client)
├── binary_sensor.py   # door, rinse_aid
├── config_flow.py     # user / reauth / reconfigure steps
├── const.py           # DOMAIN, LOGGER, defaults, hex-length constants
├── coordinator.py     # DataUpdateCoordinator polling the device
├── data.py            # typed ConfigEntry + MideaDishwasherData dataclass + TypedDicts
├── diagnostics.py     # downloadable diagnostics with credential redaction
├── entity.py          # base CoordinatorEntity
├── exceptions/        # one file per exception class
│   ├── __init__.py
│   ├── api_client_authentication_error.py
│   ├── api_client_communication_error.py
│   └── api_client_error.py
├── manifest.json
├── options_flow.py    # OptionsFlow with scan_interval
├── repairs.py         # Repair platform: async_create_fix_flow + sample issue
├── sensor.py          # status, progress, time_remaining
├── switch.py          # power
└── translations/
    ├── en.json
    └── pt-BR.json
```

The "one top-level class per file" rule (with related classes grouped under a directory) is documented in [`CODE_STYLE.md`](./CODE_STYLE.md).

## Pre-commit hooks

Install once per clone (after `scripts/setup`):

```bash
pre-commit install
```

This wires ruff + basic file hygiene checks (`.pre-commit-config.yaml`) into every commit, mirroring the CI lint job.

## CI

- **`lint.yml`** — ruff (check + format) and mypy (Python 3.14)
- **`validate.yml`** — `hassfest` + HACS validation; push/PR to `main` and a daily cron
- **`codeql.yml`** — GitHub CodeQL security scan; push/PR to `main` and a weekly cron

## Credits

This repository was bootstrapped from [`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint) and the [`@roquerodrigo`](https://github.com/roquerodrigo) HACS template that lives at [`roquerodrigo/ha-integration-blueprint`](https://github.com/roquerodrigo/ha-integration-blueprint). The LAN V3 + AA codec implementation lives in the standalone [`midea-dishwasher-api`](https://github.com/roquerodrigo/midea-dishwasher-api) package.

## License

[MIT](LICENSE)
