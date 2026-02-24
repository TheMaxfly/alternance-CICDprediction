"""
Contract tests for FastAPI /predict endpoint.

These tests validate the API contract between Streamlit UI and FastAPI backend.

Current API contract:
- Request body: {"data": {15 feature fields}}
- Success response: {"proba": float, "pred_class": int, "label": str, "threshold": float}
"""

import os
from typing import Any

import pytest
import requests
from requests.exceptions import RequestException

# API configuration - can be overridden with environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000")
PREDICT_ENDPOINT = f"{API_URL}/predict"


def _as_request_body(payload: dict[str, Any]) -> dict[str, Any]:
    """Wrap feature payload using the current API request schema."""
    return {"data": payload}


@pytest.fixture
def valid_payload() -> dict[str, Any]:
    """Valid prediction input with all 15 required fields."""
    return {
        "dep": "59",
        "lum": 1,
        "atm": 1,
        "catr": 3,
        "agg": 2,
        "int": 1,
        "circ": 2,
        "col": 3,
        "vma_bucket": "51-80",
        "catv_family_4": "voitures_utilitaires",
        "manv_mode": 1,
        "driver_age_bucket": "25-34",
        "choc_mode": 1,
        "driver_trajet_family": "trajet_1",
        "time_bucket": "morning_06_11",
    }


def test_api_reachable() -> None:
    """
    Prerequisite test: check API is running and reachable.
    """
    try:
        requests.get(f"{API_URL}/", timeout=5)
        # Any response (even 404) means the server is reachable
        assert True, "API is reachable"
    except RequestException:
        pytest.skip(
            f"API not reachable at {API_URL}. Start the API server before running tests."
        )


def test_predict_endpoint_success(valid_payload: dict[str, Any]) -> None:
    """
    T012: Valid request -> 200 OK with prediction result.
    """
    response = requests.post(
        PREDICT_ENDPOINT, json=_as_request_body(valid_payload), timeout=10
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    result = response.json()

    assert "proba" in result, "Response missing 'proba' field"
    assert "pred_class" in result, "Response missing 'pred_class' field"
    assert "label" in result, "Response missing 'label' field"
    assert "threshold" in result, "Response missing 'threshold' field"

    assert isinstance(result["proba"], int | float), "proba must be numeric"
    assert 0.0 <= result["proba"] <= 1.0, "proba must be between 0.0 and 1.0"
    assert result["pred_class"] in [0, 1], "pred_class must be 0 or 1"
    assert result["label"] in ["grave", "non_grave"], (
        f"label must be 'grave' or 'non_grave', got '{result['label']}'"
    )
    assert result["threshold"] == 0.47, (
        f"threshold must be 0.47, got {result['threshold']}"
    )

    # Validate prediction consistency with threshold
    if result["proba"] >= result["threshold"]:
        assert result["pred_class"] == 1
        assert result["label"] == "grave"
    else:
        assert result["pred_class"] == 0
        assert result["label"] == "non_grave"


def test_predict_endpoint_robustness_invalid_lum(valid_payload: dict[str, Any]) -> None:
    """
    T013: Out-of-vocabulary categorical values are handled without 5xx errors.
    """
    invalid_payload = valid_payload.copy()
    invalid_payload["lum"] = 99  # Out-of-vocabulary category

    response = requests.post(
        PREDICT_ENDPOINT, json=_as_request_body(invalid_payload), timeout=10
    )

    # Current model contract: categorical unknowns are tolerated.
    assert response.status_code == 200, (
        f"Expected 200 for robust handling, got {response.status_code}"
    )
    result = response.json()
    assert "proba" in result
    assert "pred_class" in result
    assert "label" in result


def test_predict_endpoint_missing_required_field() -> None:
    """
    T014: Missing required field in `data` -> 422 error with missing_fields detail.
    """
    incomplete_payload = {
        # "dep": "59",  # Intentionally missing
        "lum": 1,
        "atm": 1,
        "catr": 3,
        "agg": 2,
        "int": 1,
        "circ": 2,
        "col": 3,
        "vma_bucket": "51-80",
        "catv_family_4": "voitures_utilitaires",
        "manv_mode": 1,
        "driver_age_bucket": "25-34",
        "choc_mode": 1,
        "driver_trajet_family": "trajet_1",
        "time_bucket": "morning_06_11",
    }

    response = requests.post(
        PREDICT_ENDPOINT, json=_as_request_body(incomplete_payload), timeout=10
    )
    assert response.status_code == 422, (
        f"Expected 422 for missing field, got {response.status_code}"
    )

    error = response.json()
    assert "detail" in error, "Error response missing 'detail' field"
    assert isinstance(error["detail"], dict), "'detail' must be an object for this API"
    assert "missing_fields" in error["detail"], "'detail' missing 'missing_fields'"
    assert "dep" in error["detail"]["missing_fields"], (
        "Expected missing field 'dep' in error details"
    )


def test_predict_endpoint_all_fields_invalid() -> None:
    """
    Additional test: payload with many invalid categories still returns a response.
    """
    invalid_payload = {
        "dep": "",
        "lum": 99,
        "atm": 100,
        "catr": 8,
        "agg": 3,
        "int": 0,
        "circ": 5,
        "col": 10,
        "vma_bucket": "invalid",
        "catv_family_4": "invalid",
        "manv_mode": 50,
        "driver_age_bucket": "invalid",
        "choc_mode": 20,
        "driver_trajet_family": "invalid",
        "time_bucket": "invalid",
    }

    response = requests.post(
        PREDICT_ENDPOINT, json=_as_request_body(invalid_payload), timeout=10
    )
    assert response.status_code == 200, (
        f"Expected 200 for robust handling, got {response.status_code}"
    )

    result = response.json()
    assert "proba" in result
    assert "pred_class" in result
    assert "label" in result
    assert "threshold" in result


pytestmark = pytest.mark.integration
