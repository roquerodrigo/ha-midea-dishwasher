# Contributing

Bug reports, ideas and pull requests are welcome.

## Reporting a bug

Open an [issue](https://github.com/roquerodrigo/ha-midea-dishwasher/issues/new/choose)
with:

- the Home Assistant version, the integration version and the dishwasher model;
- what you did, what you expected and what happened;
- the diagnostics downloaded from the integration's menu (the token, the key
  and the device ID are redacted) and the relevant debug log lines.

## Development setup

The project uses [uv](https://docs.astral.sh/uv/). A dev container
(`.devcontainer.json`) with everything installed is also provided.

```bash
scripts/setup      # install the dev and lint dependencies into .venv
scripts/develop    # run Home Assistant at http://localhost:8123 with this integration loaded
```

`scripts/develop` uses the configuration in [`config/`](config/), with debug
logging enabled for the integration. A bare `uv sync` does not install the
dev and lint groups, so use `scripts/setup`.

## Checks

Run these before opening a pull request. CI runs the same ones, plus the Home
Assistant Marketplace validation. `pre-commit install` runs the first three on
every commit, with the same tool versions.

```bash
uv run ruff format .                              # format
uv run ruff check . --fix                         # lint
uv run mypy custom_components/midea_dishwasher    # type-check
uv run pytest                                     # tests, coverage must stay at 90 % or more
```

`scripts/lint` runs all four in that order.

Read [CODE_STYLE.md](CODE_STYLE.md) before adding or restructuring code.

## Pull requests

1. Fork the repository and branch from `main`.
2. Write commit messages as [Conventional Commits](https://www.conventionalcommits.org/).
   Releases and their notes are generated from them. Mark breaking changes
   with `!` or a `BREAKING CHANGE:` footer.
3. Update `translations/en.json` and `translations/pt-BR.json` together when
   you change user-facing strings. The tests fail when the two files, the
   program list in `services.yaml` and the library's enums disagree.
4. When you bump `midea-dishwasher-api`, change the pin in `pyproject.toml`
   and in `manifest.json` in the same pull request. A test checks that they
   match.
5. Update the README when behaviour, configuration or entities change.
6. Fill in the pull request template.

## License

Contributions are released under the project's [MIT License](LICENSE).
