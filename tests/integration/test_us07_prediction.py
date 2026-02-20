"""
Integration tests for US-07: Probabilité + classe (seuil 0.47)

Tests verify that:
1. Successful API call displays probability and class
2. Probability ≥0.47 → class "grave"
3. Probability <0.47 → class "non_grave"
"""

from unittest.mock import MagicMock, patch

from briefml.ui.lib import api_client


class TestUS07Prediction:
    """Tests for US-07: Display prediction with probability and classification"""

    def test_successful_api_call_returns_probability_and_class(self):
        """
        T058: Verify successful API call returns probability and class

        Given: Valid prediction inputs
        When: API returns 200 OK with probability and prediction
        Then: Response contains probability, prediction, and threshold fields
        """
        # Arrange
        valid_inputs = {
            "dep": "59",
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "col": 2,
            "choc_mode": 1,
            "manv_mode": 1,
            "driver_age_bucket": 30,
            "driver_trajet_family": 1,
            "catv_family_4": 1,
            "lum": 1,
            "atm": 1,
            "time_bucket": "morning_06_11",
        }

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.68,
            "prediction": "grave",
            "threshold": 0.47,
        }

        # Act
        with patch("requests.post", return_value=mock_response):
            result = api_client.call_predict_api(valid_inputs)

        # Assert
        assert "probability" in result, "Response should contain 'probability' field"
        assert "prediction" in result, "Response should contain 'prediction' field"
        assert "threshold" in result, "Response should contain 'threshold' field"
        assert result["probability"] == 0.68
        assert result["prediction"] == "grave"
        assert result["threshold"] == 0.47
        assert api_client.is_success_response(result), (
            "Should be recognized as success response"
        )

    def test_probability_above_threshold_returns_grave_class(self):
        """
        T059: Verify probability ≥0.47 returns class "grave"

        Given: Valid prediction inputs
        When: API returns probability ≥0.47 (e.g., 0.68)
        Then: Prediction class is "grave"
        """
        # Arrange
        inputs = {
            "dep": "75",
            "agg": 2,
            "catr": 3,
            "vma_bucket": 90,
            "int": 4,
            "circ": 2,
            "col": 3,
            "choc_mode": 2,
            "manv_mode": 2,
            "driver_age_bucket": 18,
            "driver_trajet_family": 2,
            "catv_family_4": 2,
            "lum": 3,
            "atm": 7,
            "time_bucket": "evening_18_23",
        }

        # Mock API response with high probability
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.68,
            "prediction": "grave",
            "threshold": 0.47,
        }

        # Act
        with patch("requests.post", return_value=mock_response):
            result = api_client.call_predict_api(inputs)

        # Assert
        assert result["probability"] >= 0.47, "Probability should be above threshold"
        assert result["prediction"] == "grave", (
            "Classification should be 'grave' for high probability"
        )

    def test_probability_below_threshold_returns_non_grave_class(self):
        """
        T060: Verify probability <0.47 returns class "non_grave"

        Given: Valid prediction inputs
        When: API returns probability <0.47 (e.g., 0.23)
        Then: Prediction class is "non_grave"
        """
        # Arrange
        inputs = {
            "dep": "59",
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "col": 2,
            "choc_mode": 1,
            "manv_mode": 1,
            "driver_age_bucket": 30,
            "driver_trajet_family": 1,
            "catv_family_4": 1,
            "lum": 1,
            "atm": 1,
            "time_bucket": "morning_06_11",
        }

        # Mock API response with low probability
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.23,
            "prediction": "non_grave",
            "threshold": 0.47,
        }

        # Act
        with patch("requests.post", return_value=mock_response):
            result = api_client.call_predict_api(inputs)

        # Assert
        assert result["probability"] < 0.47, "Probability should be below threshold"
        assert result["prediction"] == "non_grave", (
            "Classification should be 'non_grave' for low probability"
        )

    def test_threshold_boundary_case_exactly_0_47(self):
        """
        Boundary test: Probability exactly 0.47 should be classified as "grave"

        Given: Valid prediction inputs
        When: API returns probability exactly 0.47
        Then: Prediction class is "grave" (threshold inclusive)
        """
        # Arrange
        inputs = {
            "dep": "59",
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "col": 2,
            "choc_mode": 1,
            "manv_mode": 1,
            "driver_age_bucket": 30,
            "driver_trajet_family": 1,
            "catv_family_4": 1,
            "lum": 1,
            "atm": 1,
            "time_bucket": "morning_06_11",
        }

        # Mock API response with probability exactly at threshold
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.47,
            "prediction": "grave",
            "threshold": 0.47,
        }

        # Act
        with patch("requests.post", return_value=mock_response):
            result = api_client.call_predict_api(inputs)

        # Assert
        assert result["probability"] == 0.47, (
            "Probability should be exactly at threshold"
        )
        assert result["prediction"] == "grave", (
            "Classification should be 'grave' at threshold (inclusive)"
        )

    def test_error_response_does_not_contain_probability(self):
        """
        Verify error responses are properly identified (no probability field)

        Given: Invalid inputs
        When: API returns error response (e.g., 422 validation error)
        Then: Response does not contain probability field and is_success_response returns False
        """
        # Arrange
        invalid_inputs = {"dep": "invalid"}

        # Mock validation error response
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [{"loc": ["body", "lum"], "msg": "field required"}]
        }

        # Act
        with patch("requests.post", return_value=mock_response):
            result = api_client.call_predict_api(invalid_inputs)

        # Assert
        assert "error" in result, "Error response should contain 'error' field"
        assert "probability" not in result, (
            "Error response should not contain 'probability'"
        )
        assert not api_client.is_success_response(result), (
            "Should be recognized as error response"
        )
