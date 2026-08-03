from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from midea_dishwasher_api import CycleState, ErrorCode, Mode, WashStage

from custom_components.midea_dishwasher.labels import (
    CYCLE_STATE_LABELS,
    ERROR_CODE_LABELS,
    MODE_LABELS,
    WASH_STAGE_LABELS,
    error_code_label,
    wash_stage_label,
)

COMPONENT_DIR = Path(__file__).parent.parent / "custom_components" / "midea_dishwasher"
TRANSLATIONS_DIR = COMPONENT_DIR / "translations"

SENSOR_STATE_LABELS = {
    "status": CYCLE_STATE_LABELS,
    "mode": MODE_LABELS,
    "progress": WASH_STAGE_LABELS,
    "error": ERROR_CODE_LABELS,
}


def _translations(locale):
    path = TRANSLATIONS_DIR / f"{locale}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _locales():
    return [path.stem for path in sorted(TRANSLATIONS_DIR.glob("*.json"))]


def test_cycle_state_labels_match_the_library():
    assert tuple(state.value for state in CycleState) == CYCLE_STATE_LABELS


def test_mode_labels_match_the_library():
    assert tuple(mode.value for mode in Mode) == MODE_LABELS


def test_wash_stage_labels_match_the_library():
    assert WASH_STAGE_LABELS == (
        "idle",
        "pre_wash",
        "main_wash",
        "rinse",
        "dry",
        "finish",
    )


def test_error_code_labels_match_the_library():
    assert ERROR_CODE_LABELS == (
        "none",
        "water_supply",
        "heating",
        "overflow",
        "water_valve",
    )


def test_wash_stage_label_of_a_known_stage():
    assert wash_stage_label(WashStage.MAIN_WASH) == "main_wash"


@pytest.mark.parametrize("stage", [None, 99])
def test_wash_stage_label_of_an_unknown_stage(stage):
    assert wash_stage_label(stage) is None


def test_error_code_label_of_a_known_code():
    assert error_code_label(ErrorCode.WATER_SUPPLY) == "water_supply"


def test_error_code_label_of_an_unknown_code():
    assert error_code_label(99) is None


@pytest.mark.parametrize("locale", _locales())
@pytest.mark.parametrize(("key", "labels"), SENSOR_STATE_LABELS.items())
def test_every_label_is_translated(locale, key, labels):
    states = _translations(locale)["entity"]["sensor"][key]["state"]
    assert tuple(states) == labels


@pytest.mark.parametrize("locale", _locales())
def test_every_mode_is_translated_for_the_service_selector(locale):
    options = _translations(locale)["selector"]["mode"]["options"]
    assert tuple(options) == MODE_LABELS


def test_service_schema_offers_every_mode():
    services = yaml.safe_load(
        (COMPONENT_DIR / "services.yaml").read_text(encoding="utf-8")
    )
    options = services["start_cycle"]["fields"]["mode"]["selector"]["select"]["options"]
    assert tuple(options) == MODE_LABELS
