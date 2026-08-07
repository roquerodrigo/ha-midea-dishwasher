from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / "custom_components" / "midea_dishwasher" / "manifest.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

SDK_NAME = "midea-dishwasher-api"


def _manifest_sdk_requirement() -> str:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return next(
        requirement
        for requirement in manifest["requirements"]
        if requirement.startswith(SDK_NAME)
    )


def _dev_group_sdk_requirement() -> str:
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return next(
        requirement
        for requirement in pyproject["dependency-groups"]["dev"]
        if requirement.startswith(SDK_NAME)
    )


def test_manifest_installs_the_sdk_version_the_tests_run_against():
    assert _manifest_sdk_requirement() == _dev_group_sdk_requirement()


def test_manifest_pins_the_sdk_exactly():
    assert f"{SDK_NAME}==" in _manifest_sdk_requirement()
