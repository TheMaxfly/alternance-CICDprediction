"""
Contract tests for FastAPI /predict endpoint.

These tests validate the API contract between Streamlit UI and FastAPI backend.
Following TDD approach: these tests MUST FAIL before the API is implemented.

Test scenarios:
- T012: Valid request → 200 OK with prediction result
- T013: Invalid field value → 422 validation error
- T014: Missing required field → 422 validation error
"""

import os

import pytest
import requests
from requests.exceptions import RequestException

# API configuration - can be overridden with environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000")
PREDICT_ENDPOINT = f"{API_URL}/predict"


# Valid payload fixture for testing
@pytest.fixture
def valid_payload():
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


def test_api_reachable():
    """
    Prerequisite test: Check if API is running and reachable.

    This test should be run first to verify the API is accessible.
    """
    try:
        requests.get(f"{API_URL}/", timeout=5)
        # Any response (even 404) means the server is reachable
        assert True, "API is reachable"
    except RequestException:
        pytest.skip(
            f"API not reachable at {API_URL}. Start the API server before running tests."
        )


def test_predict_endpoint_success(valid_payload):
    """
    T012: Test successful prediction with valid inputs.

    Given: Valid prediction input with all 15 fields
    When: POST /predict is called
    Then: Response is 200 OK with prediction result

    Expected response structure:
    {
        "probability": float (0.0-1.0),
        "prediction": "grave" or "non_grave",
        "threshold": 0.47
    }
    """
    # Make request
    response = requests.post(PREDICT_ENDPOINT, json=valid_payload, timeout=10)

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Parse response
    result = response.json()

    # Validate response structure
    assert "probability" in result, "Response missing 'probability' field"
    assert "prediction" in result, "Response missing 'prediction' field"
    assert "threshold" in result, "Response missing 'threshold' field"

    # Validate probability
    assert isinstance(result["probability"], int | float), "probability must be numeric"
    assert 0.0 <= result["probability"] <= 1.0, (
        "probability must be between 0.0 and 1.0"
    )

    # Validate prediction
    assert result["prediction"] in ["grave", "non_grave"], (
        f"prediction must be 'grave' or 'non_grave', got '{result['prediction']}'"
    )

    # Validate threshold
    assert result["threshold"] == 0.47, (
        f"threshold must be 0.47, got {result['threshold']}"
    )

    # Validate prediction consistency with threshold
    if result["probability"] >= 0.47:
        assert result["prediction"] == "grave", (
            f"probability {result['probability']} >= 0.47 should predict 'grave'"
        )
    else:
        assert result["prediction"] == "non_grave", (
            f"probability {result['probability']} < 0.47 should predict 'non_grave'"
        )


def test_predict_endpoint_validation_error_invalid_lum(valid_payload):
    """
    T013: Test validation error with invalid field value.

    Given: Invalid lum code (99 instead of 1-5)
    When: POST /predict is called
    Then: Response is 422 with validation error details

    Expected response structure:
    {
        "detail": [
            {
                "loc": ["body", "lum"],
                "msg": "...",
                "type": "..."
            }
        ]
    }
    """
    # Create payload with invalid lum code
    invalid_payload = valid_payload.copy()
    invalid_payload["lum"] = 99  # Invalid - should be 1-5

    # Make request
    response = requests.post(PREDICT_ENDPOINT, json=invalid_payload, timeout=10)

    # Assert status code
    assert response.status_code == 422, (
        f"Expected 422 for invalid input, got {response.status_code}"
    )

    # Parse error response
    error = response.json()

    # Validate error structure
    assert "detail" in error, "Error response missing 'detail' field"
    assert isinstance(error["detail"], list), "'detail' must be a list"
    assert len(error["detail"]) > 0, "'detail' list must not be empty"

    # Check that error mentions 'lum' field
    lum_errors = [err for err in error["detail"] if "lum" in str(err.get("loc", []))]
    assert len(lum_errors) > 0, "Expected validation error for 'lum' field"


def test_predict_endpoint_missing_required_field():
    """
    T014: Test validation error with missing required field.

    Given: Payload missing 'dep' field
    When: POST /predict is called
    Then: Response is 422 with field required error

    Expected response structure:
    {
        "detail": [
            {
                "loc": ["body", "dep"],
                "msg": "field required" or similar,
                "type": "..."
            }
        ]
    }
    """
    # Create payload missing 'dep' field
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

    # Make request
    response = requests.post(PREDICT_ENDPOINT, json=incomplete_payload, timeout=10)

    # Assert status code
    assert response.status_code == 422, (
        f"Expected 422 for missing field, got {response.status_code}"
    )

    # Parse error response
    error = response.json()

    # Validate error structure
    assert "detail" in error, "Error response missing 'detail' field"
    assert isinstance(error["detail"], list), "'detail' must be a list"
    assert len(error["detail"]) > 0, "'detail' list must not be empty"

    # Check that error mentions 'dep' field
    dep_errors = [err for err in error["detail"] if "dep" in str(err.get("loc", []))]
    assert len(dep_errors) > 0, "Expected validation error for missing 'dep' field"


def test_predict_endpoint_all_fields_invalid():
    """
    Additional test: Multiple validation errors in single request.

    Given: Multiple invalid field values
    When: POST /predict is called
    Then: Response is 422 with multiple validation errors
    """
    invalid_payload = {
        "dep": "",  # Empty string - invalid
        "lum": 99,  # Out of range 1-5
        "atm": 100,  # Out of range -1 or 1-9
        "catr": 8,  # Invalid - should be 1-7 or 9
        "agg": 3,  # Invalid - should be 1 or 2
        "int": 0,  # Invalid - should be 1-9
        "circ": 5,  # Invalid - should be -1 or 1-4
        "col": 10,  # Invalid - should be -1 or 1-7
        "vma_bucket": "invalid",  # Not in valid buckets
        "catv_family_4": "invalid",  # Not in valid families
        "manv_mode": 50,  # Out of range -1 to 26
        "driver_age_bucket": "invalid",  # Not in valid buckets
        "choc_mode": 20,  # Out of range -1 to 9
        "driver_trajet_family": "invalid",  # Not in valid families
        "time_bucket": "invalid",  # Not in valid time buckets
    }

    # Make request
    response = requests.post(PREDICT_ENDPOINT, json=invalid_payload, timeout=10)

    # Assert status code
    assert response.status_code == 422, (
        f"Expected 422 for multiple invalid fields, got {response.status_code}"
    )

    # Parse error response
    error = response.json()

    # Validate error structure
    assert "detail" in error, "Error response missing 'detail' field"
    assert isinstance(error["detail"], list), "'detail' must be a list"

    # Expect multiple errors (at least 5 of the 15 fields should be flagged)
    assert len(error["detail"]) >= 5, (
        f"Expected multiple validation errors, got {len(error['detail'])}"
    )


# Pytest markers
pytestmark = pytest.mark.integration
