"""
Integration tests for US-02: Multi-page navigation.

User Story: As a user, I want to navigate through 6 pages with Précédent/Suivant buttons,
with my selections preserved across pages, and all fields as dropdowns.

Test scenarios:
- T021: Navigation Page 1→2→3→4→5→6 preserves selections
- T022: Précédent button disabled on Page 1
- T023: All fields are dropdowns (no text inputs)

Following TDD: These tests MUST FAIL before implementation.
"""

import pytest
from unittest.mock import MagicMock, patch

from briefml.ui.lib import session_state


class TestUS02Navigation:
    """Tests for US-02: Multi-page navigation functionality."""

    @pytest.fixture(autouse=True)
    def setup_session_state(self):
        """Setup mock session state for each test."""
        with patch('streamlit.session_state', MagicMock()) as mock_state:
            # Initialize clean state
            mock_state.current_page = 1
            mock_state.prediction_inputs = {}
            mock_state.last_prediction = None
            mock_state.validation_errors = {}
            mock_state.is_form_complete = False
            mock_state.reference_data = {}

            yield mock_state

    def test_navigation_page_1_to_6_preserves_selections(self, setup_session_state):
        """
        T021: Test navigation from Page 1 to Page 6 preserves all selections.

        Given: User fills fields on each page and navigates forward
        When: User navigates Page 1→2→3→4→5→6
        Then: All selections should be preserved in prediction_inputs
        """
        mock_state = setup_session_state

        # Simulate filling fields on each page and navigating
        pages_data = {
            1: {"dep": "59", "agg": 2, "catr": 3, "vma_bucket": "51-80"},
            2: {"int": 1, "circ": 2},
            3: {"col": 3, "choc_mode": 1, "manv_mode": 1},
            4: {"driver_age_bucket": "25-34", "driver_trajet_family": "trajet_1", "catv_family_4": "voitures_utilitaires"},
            5: {"lum": 1, "atm": 1, "time_bucket": "morning_06_11"}
        }

        with patch('streamlit.session_state', mock_state):
            for page_num in range(1, 6):
                # Set current page
                mock_state.get.return_value = page_num
                mock_state.current_page = page_num

                # Fill fields for this page
                for field, value in pages_data[page_num].items():
                    session_state.set_prediction_input(field, value)

                # Navigate to next page
                session_state.navigate_next()

            # Verify all fields are preserved
            all_inputs = session_state.get_all_prediction_inputs()

            # Check Page 1 fields
            assert all_inputs.get("dep") == "59", "dep should be preserved"
            assert all_inputs.get("agg") == 2, "agg should be preserved"
            assert all_inputs.get("catr") == 3, "catr should be preserved"
            assert all_inputs.get("vma_bucket") == "51-80", "vma_bucket should be preserved"

            # Check Page 2 fields
            assert all_inputs.get("int") == 1, "int should be preserved"
            assert all_inputs.get("circ") == 2, "circ should be preserved"

            # Check Page 3 fields
            assert all_inputs.get("col") == 3, "col should be preserved"
            assert all_inputs.get("choc_mode") == 1, "choc_mode should be preserved"
            assert all_inputs.get("manv_mode") == 1, "manv_mode should be preserved"

            # Check Page 4 fields
            assert all_inputs.get("driver_age_bucket") == "25-34", "driver_age_bucket should be preserved"
            assert all_inputs.get("driver_trajet_family") == "trajet_1", "driver_trajet_family should be preserved"
            assert all_inputs.get("catv_family_4") == "voitures_utilitaires", "catv_family_4 should be preserved"

            # Check Page 5 fields
            assert all_inputs.get("lum") == 1, "lum should be preserved"
            assert all_inputs.get("atm") == 1, "atm should be preserved"
            assert all_inputs.get("time_bucket") == "morning_06_11", "time_bucket should be preserved"

            # Verify we're on page 6
            assert mock_state.current_page == 6, "Should be on page 6 after navigation"

    def test_precedent_button_logic_page_1(self, setup_session_state):
        """
        T022: Test that Précédent button should be disabled on Page 1.

        Given: User is on Page 1
        When: User tries to go to previous page
        Then: Current page should remain 1 (cannot go below page 1)
        """
        mock_state = setup_session_state

        with patch('streamlit.session_state', mock_state):
            # User is on page 1
            mock_state.get.return_value = 1
            mock_state.current_page = 1

            # Try to navigate previous
            current = session_state.get_current_page()
            assert current == 1, "Should be on page 1"

            # Navigation to previous should keep us on page 1
            session_state.navigate_previous()

            # Verify still on page 1
            assert mock_state.current_page == 1, \
                "Précédent on page 1 should not go below page 1"

    def test_precedent_button_works_on_other_pages(self, setup_session_state):
        """
        T022 (extended): Test that Précédent button works on pages 2-6.

        Given: User is on Page 2, 3, 4, 5, or 6
        When: User clicks Précédent
        Then: Current page should decrement by 1
        """
        mock_state = setup_session_state

        for start_page in range(2, 7):  # Test pages 2-6
            with patch('streamlit.session_state', mock_state):
                mock_state.get.return_value = start_page
                mock_state.current_page = start_page

                # Navigate previous
                session_state.navigate_previous()

                # Verify page decremented
                expected_page = start_page - 1
                assert mock_state.current_page == expected_page, \
                    f"Précédent from page {start_page} should go to page {expected_page}"

    def test_suivant_button_works_on_all_pages(self, setup_session_state):
        """
        T021 (extended): Test that Suivant button works on pages 1-5.

        Given: User is on Page 1, 2, 3, 4, or 5
        When: User clicks Suivant
        Then: Current page should increment by 1
        """
        mock_state = setup_session_state

        for start_page in range(1, 6):  # Test pages 1-5
            with patch('streamlit.session_state', mock_state):
                mock_state.get.return_value = start_page
                mock_state.current_page = start_page

                # Navigate next
                session_state.navigate_next()

                # Verify page incremented
                expected_page = start_page + 1
                assert mock_state.current_page == expected_page, \
                    f"Suivant from page {start_page} should go to page {expected_page}"

    def test_suivant_button_cannot_exceed_page_6(self, setup_session_state):
        """
        T021 (boundary): Test that Suivant button cannot go beyond page 6.

        Given: User is on Page 6
        When: User tries to navigate next
        Then: Current page should remain 6 (cannot exceed page 6)
        """
        mock_state = setup_session_state

        with patch('streamlit.session_state', mock_state):
            mock_state.get.return_value = 6
            mock_state.current_page = 6

            # Try to navigate next
            session_state.navigate_next()

            # Verify still on page 6
            assert mock_state.current_page == 6, \
                "Suivant on page 6 should not exceed page 6"

    def test_field_validation_dropdown_only(self):
        """
        T023: Test that field specification requires dropdown controls.

        This test validates the data model expects dropdowns for all fields.
        The actual UI implementation will use st.selectbox for all fields.

        Given: Field definitions in reference_loader
        When: Loading field options
        Then: All fields should have discrete options (suitable for dropdowns)
        """
        from briefml.ui.lib import reference_loader

        # Load reference data
        ref_data = reference_loader.load_reference_data()

        # All 15 fields should have options
        required_fields = [
            "dep", "lum", "atm", "catr", "agg", "int", "circ", "col",
            "vma_bucket", "catv_family_4", "manv_mode", "driver_age_bucket",
            "choc_mode", "driver_trajet_family", "time_bucket"
        ]

        for field in required_fields:
            assert field in ref_data, f"Field '{field}' should have reference data"
            assert isinstance(ref_data[field], list), f"Field '{field}' should have list of options"
            assert len(ref_data[field]) > 0, f"Field '{field}' should have at least 1 option"

            # Verify each option has 'code' and 'label' (dropdown format)
            for opt in ref_data[field]:
                assert "code" in opt, f"Field '{field}' option missing 'code'"
                assert "label" in opt, f"Field '{field}' option missing 'label'"

        # time_bucket field should have 4 options
        assert len(ref_data["time_bucket"]) == 4, \
            "time_bucket field should have 4 dropdown options"

    def test_backward_forward_navigation_preserves_data(self, setup_session_state):
        """
        T021 (extended): Test backward and forward navigation preserves data.

        Given: User fills fields, navigates forward, then backward
        When: User goes Page 1→2→3 then 3→2→1
        Then: All previously entered data should be preserved
        """
        mock_state = setup_session_state

        with patch('streamlit.session_state', mock_state):
            # Page 1: Fill data
            mock_state.get.return_value = 1
            mock_state.current_page = 1
            session_state.set_prediction_input("dep", "59")
            session_state.set_prediction_input("agg", 2)

            # Navigate to page 2
            session_state.navigate_next()
            assert mock_state.current_page == 2

            # Page 2: Fill data
            mock_state.get.return_value = 2
            session_state.set_prediction_input("int", 1)

            # Navigate to page 3
            session_state.navigate_next()
            assert mock_state.current_page == 3

            # Page 3: Fill data
            mock_state.get.return_value = 3
            session_state.set_prediction_input("col", 3)

            # Navigate backward to page 2
            session_state.navigate_previous()
            assert mock_state.current_page == 2

            # Verify page 2 data still there
            assert session_state.get_prediction_input("int") == 1

            # Navigate backward to page 1
            mock_state.get.return_value = 2
            session_state.navigate_previous()
            assert mock_state.current_page == 1

            # Verify page 1 data still there
            assert session_state.get_prediction_input("dep") == "59"
            assert session_state.get_prediction_input("agg") == 2

            # Verify all data preserved
            all_inputs = session_state.get_all_prediction_inputs()
            assert len(all_inputs) == 4, "Should have 4 fields preserved"
            assert all_inputs["dep"] == "59"
            assert all_inputs["agg"] == 2
            assert all_inputs["int"] == 1
            assert all_inputs["col"] == 3


# Pytest markers
pytestmark = pytest.mark.integration
