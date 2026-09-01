import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
sys.path.insert(0, str(APP_DIR))


class DummyModel:
    pass


class DummyScaler:
    def transform(self, values):
        return values


def load_helper():
    # prediction_helper loads persisted artifacts at import time.
    # Stub those loads so unit tests can run without model binaries.
    dummy_scaler = {
        "scaler": DummyScaler(),
        "cols_to_scale": [
            "age",
            "number_of_dependants",
            "income_level",
            "income_lakhs",
            "insurance_plan",
            "genetical_risk",
        ],
    }
    with patch("joblib.load", side_effect=[
        DummyModel(), DummyModel(), dummy_scaler, dummy_scaler
    ]):
        import prediction_helper

    return prediction_helper


def test_medical_risk_scores():
    ph = load_helper()

    assert ph.calculate_normalized_risk("No Disease") == 0.0
    assert np.isclose(ph.calculate_normalized_risk("Diabetes"), 6 / 14)
    assert np.isclose(
        ph.calculate_normalized_risk("Diabetes & Heart disease"),
        1.0,
    )


def test_medical_risk_indicator_levels():
    ph = load_helper()

    assert ph.get_medical_risk_indicator(0)["label"] == "Low"
    assert ph.get_medical_risk_indicator(0.40)["label"] == "Moderate"
    assert ph.get_medical_risk_indicator(0.80)["label"] == "High"


def test_insurance_plan_encoding():
    ph = load_helper()

    assert ph.INSURANCE_PLAN_ENCODING["Bronze"] == 1
    assert ph.INSURANCE_PLAN_ENCODING["Silver"] == 2
    assert ph.INSURANCE_PLAN_ENCODING["Gold"] == 3


def test_expected_factor_groups_are_present():
    ph = load_helper()

    expected = {
        "Age",
        "Dependants",
        "Income",
        "Insurance Plan",
        "Medical History",
        "BMI Category",
        "Smoking Status",
    }
    assert expected.issubset(ph.FACTOR_GROUPS)
