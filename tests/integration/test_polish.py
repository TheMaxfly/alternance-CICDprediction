"""
Integration tests for Polish phase: error handling and dep search.

T100: API timeout → "Service temporairement indisponible"
T101: API 422 → parse field errors and display
T102: API 500 → "Erreur serveur"
T103: dep search functionality
"""

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import Timeout

from briefml.ui.lib.api_client import (
    call_predict_api,
    format_error_message,
    is_success_response,
)
from briefml.ui.lib.reference_loader import get_dropdown_options, load_reference_data

pytestmark = pytest.mark.integration


# Sample valid inputs
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
    "time_bucket": "morning_06_11",
}


class TestT100TimeoutHandling:
    """T100: API timeout (>10s) → user-friendly message."""

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_timeout_returns_error_dict(self, mock_post):
        """Timeout returns error dict with 'timeout' type."""
        mock_post.side_effect = Timeout("Connection timed out")
        result = call_predict_api(SAMPLE_INPUTS)
        assert not is_success_response(result)
        assert result["error"] == "timeout"

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_timeout_message_is_user_friendly(self, mock_post):
        """Timeout message mentions service unavailability."""
        mock_post.side_effect = Timeout("Connection timed out")
        result = call_predict_api(SAMPLE_INPUTS)
        message = format_error_message(result)
        assert (
            "réessayer" in message.lower()
            or "indisponible" in message.lower()
            or "temps" in message.lower()
        )

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_connection_error_returns_error_dict(self, mock_post):
        """Connection error returns error dict with network/connection type."""
        from requests.exceptions import ConnectionError as RequestsConnectionError

        mock_post.side_effect = RequestsConnectionError("Connection refused")
        result = call_predict_api(SAMPLE_INPUTS)
        assert not is_success_response(result)
        assert result["error"] in ("connection", "network")


class TestT101ValidationErrorHandling:
    """T101: API 422 → parse field errors and display."""

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_422_returns_validation_error(self, mock_post):
        """422 response returns error dict with 'validation' type."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [
                {
                    "loc": ["body", "lum"],
                    "msg": "value is not a valid integer",
                    "type": "value_error",
                },
                {
                    "loc": ["body", "dep"],
                    "msg": "field required",
                    "type": "value_error.missing",
                },
            ]
        }
        mock_post.return_value = mock_response

        result = call_predict_api(SAMPLE_INPUTS)
        assert result["error"] == "validation"
        assert "formatted_errors" in result
        assert len(result["formatted_errors"]) == 2

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_422_formatted_errors_contain_field_names(self, mock_post):
        """422 formatted errors include field names."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [
                {"loc": ["body", "lum"], "msg": "invalid value", "type": "value_error"}
            ]
        }
        mock_post.return_value = mock_response

        result = call_predict_api(SAMPLE_INPUTS)
        assert any("lum" in err for err in result["formatted_errors"])

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_422_format_error_message_is_readable(self, mock_post):
        """422 formatted message is human-readable."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            "detail": [
                {"loc": ["body", "lum"], "msg": "invalid", "type": "value_error"}
            ]
        }
        mock_post.return_value = mock_response

        result = call_predict_api(SAMPLE_INPUTS)
        message = format_error_message(result)
        assert "invalide" in message.lower()
        assert "lum" in message


class TestT102ServerErrorHandling:
    """T102: API 500 → "Erreur serveur"."""

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_500_returns_server_error(self, mock_post):
        """500 response returns error dict with 'server' type."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = '{"detail": "Internal Server Error"}'
        mock_response.json.return_value = {"detail": "Internal Server Error"}
        mock_post.return_value = mock_response

        result = call_predict_api(SAMPLE_INPUTS)
        assert result["error"] == "server"
        assert result["status_code"] == 500

    @patch("briefml.ui.lib.api_client.requests.post")
    def test_500_message_mentions_server(self, mock_post):
        """500 message mentions server error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = '{"detail": "Internal Server Error"}'
        mock_response.json.return_value = {"detail": "Internal Server Error"}
        mock_post.return_value = mock_response

        result = call_predict_api(SAMPLE_INPUTS)
        message = format_error_message(result)
        assert "serveur" in message.lower()


class TestT103DepSearch:
    """T103: dep dropdown has 107+ options and can be filtered."""

    def test_dep_has_107_plus_options(self):
        """dep field has at least 107 options (all French departments)."""
        ref_data = load_reference_data()
        dep_options = get_dropdown_options(ref_data, "dep")
        assert len(dep_options) >= 107

    def test_dep_options_are_searchable_strings(self):
        """dep options are formatted strings that contain department names."""
        ref_data = load_reference_data()
        dep_options = get_dropdown_options(ref_data, "dep")
        # All should be formatted as "code — label"
        for opt in dep_options:
            assert " — " in opt

    def test_dep_contains_paris(self):
        """dep options include Paris (75)."""
        ref_data = load_reference_data()
        dep_options = get_dropdown_options(ref_data, "dep")
        paris_options = [opt for opt in dep_options if "Paris" in opt]
        assert len(paris_options) == 1
        assert "75" in paris_options[0]

    def test_dep_contains_nord(self):
        """dep options include Nord (59)."""
        ref_data = load_reference_data()
        dep_options = get_dropdown_options(ref_data, "dep")
        nord_options = [opt for opt in dep_options if "Nord" in opt]
        assert len(nord_options) >= 1
