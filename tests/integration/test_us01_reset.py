"""
Integration tests for US-01: Start new prediction.

User Story: As a user, I want to click "Nouvelle prédiction" button to reset the form
and see a progress indicator showing "Page 1/6".

Test scenarios:
- T015: "Nouvelle prédiction" button clears all session state
- T016: Progress indicator displays "Page 1/6" after reset

Following TDD: These tests MUST FAIL before implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
import streamlit as st


# Import the modules we're testing
from briefml.ui.lib import session_state, reference_loader


class TestUS01Reset:
    """Tests for US-01: Reset functionality and progress indicator."""

    @pytest.fixture(autouse=True)
    def setup_session_state(self):
        """
        Setup mock session state for each test.

        This fixture runs before each test to ensure clean state.
        """
        # Create a mock session_state object
        with patch('streamlit.session_state', MagicMock()) as mock_state:
            # Initialize with some data to test reset
            mock_state.current_page = 3
            mock_state.prediction_inputs = {
                "dep": "59",
                "lum": 1,
                "atm": 1
            }
            mock_state.last_prediction = {"probability": 0.68, "prediction": "grave"}
            mock_state.validation_errors = {"dep": "Some error"}
            mock_state.is_form_complete = False
            mock_state.reference_data = {}

            yield mock_state

    def test_reset_clears_prediction_inputs(self, setup_session_state):
        """
        T015 (part 1): Test that reset_form() clears prediction_inputs.

        Given: User has filled some fields (prediction_inputs has 3 fields)
        When: reset_form() is called
        Then: prediction_inputs should be empty dict
        """
        mock_state = setup_session_state

        # Verify initial state has data
        assert len(mock_state.prediction_inputs) > 0, "Initial state should have data"

        # Call reset_form
        with patch('streamlit.session_state', mock_state):
            session_state.reset_form()

        # Verify prediction_inputs is cleared
        assert mock_state.prediction_inputs == {}, \
            "prediction_inputs should be empty after reset"

    def test_reset_clears_last_prediction(self, setup_session_state):
        """
        T015 (part 2): Test that reset_form() clears last_prediction.

        Given: User has a previous prediction result
        When: reset_form() is called
        Then: last_prediction should be None
        """
        mock_state = setup_session_state

        # Verify initial state has prediction
        assert mock_state.last_prediction is not None, "Initial state should have prediction"

        # Call reset_form
        with patch('streamlit.session_state', mock_state):
            session_state.reset_form()

        # Verify last_prediction is cleared
        assert mock_state.last_prediction is None, \
            "last_prediction should be None after reset"

    def test_reset_clears_validation_errors(self, setup_session_state):
        """
        T015 (part 3): Test that reset_form() clears validation_errors.

        Given: User has validation errors
        When: reset_form() is called
        Then: validation_errors should be empty dict
        """
        mock_state = setup_session_state

        # Verify initial state has errors
        assert len(mock_state.validation_errors) > 0, "Initial state should have errors"

        # Call reset_form
        with patch('streamlit.session_state', mock_state):
            session_state.reset_form()

        # Verify validation_errors is cleared
        assert mock_state.validation_errors == {}, \
            "validation_errors should be empty after reset"

    def test_reset_sets_current_page_to_1(self, setup_session_state):
        """
        T015 (part 4): Test that reset_form() sets current_page to 1.

        Given: User is on page 3
        When: reset_form() is called
        Then: current_page should be 1
        """
        mock_state = setup_session_state

        # Verify initial state is on page 3
        assert mock_state.current_page == 3, "Initial state should be on page 3"

        # Call reset_form
        with patch('streamlit.session_state', mock_state):
            session_state.reset_form()

        # Verify current_page is set to 1
        assert mock_state.current_page == 1, \
            "current_page should be 1 after reset"

    def test_reset_sets_form_complete_to_false(self, setup_session_state):
        """
        T015 (part 5): Test that reset_form() sets is_form_complete to False.

        Given: User has completed some fields
        When: reset_form() is called
        Then: is_form_complete should be False
        """
        mock_state = setup_session_state

        # Call reset_form
        with patch('streamlit.session_state', mock_state):
            session_state.reset_form()

        # Verify is_form_complete is False
        assert mock_state.is_form_complete is False, \
            "is_form_complete should be False after reset"

    def test_progress_indicator_page_1(self):
        """
        T016 (part 1): Test progress indicator shows "Page 1/6" on page 1.

        Given: User is on page 1
        When: Progress indicator is displayed
        Then: It should show "Page 1/6"
        """
        with patch('streamlit.session_state') as mock_state:
            mock_state.get.return_value = 1

            with patch('streamlit.session_state', mock_state):
                current = session_state.get_current_page()

            # Verify current page is 1
            assert current == 1, "Current page should be 1"

            # Format progress indicator string
            progress_text = f"Page {current}/6"
            assert progress_text == "Page 1/6", \
                f"Progress indicator should be 'Page 1/6', got '{progress_text}'"

    def test_progress_indicator_updates_with_page(self):
        """
        T016 (part 2): Test progress indicator updates as user navigates.

        Given: User navigates through pages
        When: Progress indicator is displayed
        Then: It should show correct "Page X/6" for each page
        """
        for page_num in range(1, 7):  # Test pages 1-6
            with patch('streamlit.session_state') as mock_state:
                mock_state.get.return_value = page_num

                with patch('streamlit.session_state', mock_state):
                    current = session_state.get_current_page()

                # Verify current page
                assert current == page_num, f"Current page should be {page_num}"

                # Format progress indicator string
                progress_text = f"Page {current}/6"
                expected = f"Page {page_num}/6"
                assert progress_text == expected, \
                    f"Progress indicator should be '{expected}', got '{progress_text}'"

    def test_progress_indicator_after_reset(self):
        """
        T016 (part 3): Test progress indicator shows "Page 1/6" after reset.

        Given: User was on page 5 and clicks reset
        When: reset_form() is called
        Then: Progress indicator should show "Page 1/6"
        """
        with patch('streamlit.session_state') as mock_state:
            # User is on page 5
            mock_state.current_page = 5
            mock_state.prediction_inputs = {"dep": "59", "lum": 1}
            mock_state.last_prediction = None
            mock_state.validation_errors = {}
            mock_state.is_form_complete = False

            # Call reset
            with patch('streamlit.session_state', mock_state):
                session_state.reset_form()

            # Verify current page is 1
            assert mock_state.current_page == 1, "Current page should be 1 after reset"

            # Format progress indicator string
            progress_text = f"Page {mock_state.current_page}/6"
            assert progress_text == "Page 1/6", \
                f"Progress indicator should be 'Page 1/6' after reset, got '{progress_text}'"

    def test_navigation_preserves_inputs(self):
        """
        Additional test: Verify that navigation (without reset) preserves inputs.

        Given: User fills fields and navigates to next page
        When: navigate_next() is called
        Then: prediction_inputs should be preserved
        """
        with patch('streamlit.session_state') as mock_state:
            mock_state.get.return_value = 1
            mock_state.current_page = 1
            mock_state.prediction_inputs = {"dep": "59", "lum": 1}

            # Navigate next
            with patch('streamlit.session_state', mock_state):
                session_state.navigate_next()

            # Verify page incremented
            assert mock_state.current_page == 2, "Current page should be 2"

            # Verify inputs preserved
            assert mock_state.prediction_inputs == {"dep": "59", "lum": 1}, \
                "prediction_inputs should be preserved during navigation"


# Pytest markers
pytestmark = pytest.mark.integration
