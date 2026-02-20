"""
Unit tests for api_client - US-12 (Observability logging).

Tests:
- call_predict_api() logs request metadata (timestamp, status, latency)
- No user input data is logged (only metadata)
- Logging format is correct
"""

import logging
import json
from unittest.mock import patch, MagicMock

import pytest
from briefml.ui.lib.api_client import call_predict_api


# Sample valid inputs for testing
SAMPLE_INPUTS = {
    "dep": "59",
    "lum": 1,
    "atm": 1,
    "catr": 3,
    "agg": 1,
    "int": 1,
    "circ": 2,
    "col": 1,
    "vma_bucket": "51-80",
    "catv_family_4": "voitures_utilitaires",
    "manv_mode": 1,
    "driver_age_bucket": "25-34",
    "choc_mode": 1,
    "driver_trajet_family": "trajet_1",
    "time_bucket": "morning_06_11"
}


class TestUS12Logging:
    """Tests for prediction API logging (metadata only)."""

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_successful_call_logs_metadata(self, mock_post, caplog):
        """Successful API call logs status_code and response_time_ms."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.68,
            "prediction": "grave",
            "threshold": 0.47
        }
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO, logger="briefml.ui.lib.api_client"):
            call_predict_api(SAMPLE_INPUTS)

        # Should log at least one message with status and timing
        assert len(caplog.records) >= 1
        log_message = caplog.text
        assert "200" in log_message
        assert "ms" in log_message.lower()

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_error_call_logs_error_metadata(self, mock_post, caplog):
        """Error API call logs status_code."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = '{"detail": "Internal error"}'
        mock_response.json.return_value = {"detail": "Internal error"}
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO, logger="briefml.ui.lib.api_client"):
            call_predict_api(SAMPLE_INPUTS)

        assert len(caplog.records) >= 1
        log_message = caplog.text
        assert "500" in log_message

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_timeout_logs_timeout_error(self, mock_post, caplog):
        """Timeout is logged as an error."""
        from requests.exceptions import Timeout
        mock_post.side_effect = Timeout("Connection timed out")

        with caplog.at_level(logging.INFO, logger="briefml.ui.lib.api_client"):
            call_predict_api(SAMPLE_INPUTS)

        assert len(caplog.records) >= 1
        log_message = caplog.text.lower()
        assert "timeout" in log_message

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_no_user_data_in_logs(self, mock_post, caplog):
        """Logs must NOT contain user input data (field values)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.68,
            "prediction": "grave",
            "threshold": 0.47
        }
        mock_post.return_value = mock_response

        with caplog.at_level(logging.DEBUG, logger="briefml.ui.lib.api_client"):
            call_predict_api(SAMPLE_INPUTS)

        log_text = caplog.text
        # Should not contain any actual field values from inputs
        for field_name, field_value in SAMPLE_INPUTS.items():
            # Skip generic values that might appear as part of other content
            if isinstance(field_value, int) and field_value in (1, 2, 3):
                continue
            assert str(field_value) not in log_text or field_name not in log_text, \
                f"User data '{field_name}={field_value}' found in logs"

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_log_contains_response_time(self, mock_post, caplog):
        """Log includes response time in milliseconds."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "probability": 0.68,
            "prediction": "grave",
            "threshold": 0.47
        }
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO, logger="briefml.ui.lib.api_client"):
            call_predict_api(SAMPLE_INPUTS)

        log_message = caplog.text
        # Should mention response time
        assert "response_time" in log_message.lower() or "ms" in log_message.lower()

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_422_logs_validation_error(self, mock_post, caplog):
        """422 validation error is logged with status code."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [{"loc": ["body", "lum"], "msg": "invalid", "type": "value_error"}]
        }
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO, logger="briefml.ui.lib.api_client"):
            call_predict_api(SAMPLE_INPUTS)

        log_message = caplog.text
        assert "422" in log_message
