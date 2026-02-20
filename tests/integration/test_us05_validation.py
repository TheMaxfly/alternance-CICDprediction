"""
Integration tests for US-05: Validation "15 champs requis"

Tests verify that:
1. "Prédire" button is disabled when fields are missing
2. Missing fields message is displayed correctly
3. Form completion status is tracked properly
"""

import pytest

from briefml.ui.lib import validation

pytestmark = pytest.mark.integration


class TestUS05ValidationIntegration:
    """Integration tests for US-05: Form validation with missing fields"""

    def test_disabled_predict_button_when_fields_missing(self):
        """
        T048: Verify "Prédire" button logic is disabled when fields are missing

        Given: Prediction inputs with only 10/15 fields filled
        When: Checking form completion status
        Then: Form is marked as incomplete (button should be disabled in UI)
        """
        # Arrange: Incomplete form (10/15 fields)
        incomplete_inputs = {
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
            # Missing: driver_trajet_family, catv_family_4, lum, atm, time_bucket
        }

        # Act
        is_complete = validation.is_form_complete(incomplete_inputs)
        missing_fields = validation.get_missing_fields(incomplete_inputs)

        # Assert
        assert is_complete is False, "Form with 10/15 fields should not be complete"
        assert len(missing_fields) == 5, "Should have 5 missing fields"
        assert "lum" in missing_fields
        assert "atm" in missing_fields
        assert "time_bucket" in missing_fields
        assert "driver_trajet_family" in missing_fields
        assert "catv_family_4" in missing_fields

    def test_enabled_predict_button_when_all_fields_filled(self):
        """
        Verify form completion status is True when all 15 fields are filled

        Given: Prediction inputs with all 15 required fields
        When: Checking form completion status
        Then: Form is marked as complete (button should be enabled in UI)
        """
        # Arrange: Complete form
        complete_inputs = {
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

        # Act
        is_complete = validation.is_form_complete(complete_inputs)
        missing_fields = validation.get_missing_fields(complete_inputs)

        # Assert
        assert is_complete is True, "Form with all 15 fields should be complete"
        assert len(missing_fields) == 0, "Should have no missing fields"

    def test_missing_fields_message_displays_page_numbers(self):
        """
        Verify missing fields message includes page numbers for navigation

        Given: Prediction inputs with missing fields on different pages
        When: Generating missing fields message
        Then: Message includes page numbers and field labels
        """
        # Arrange: Missing fields on pages 1, 3, 5
        inputs_with_gaps = {
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "choc_mode": 1,
            "driver_age_bucket": 30,
            "driver_trajet_family": 1,
            "catv_family_4": 1,
            "atm": 1,
            # Missing: dep (page 1), col + manv_mode (page 3), lum + time_bucket (page 5)
        }

        # Act
        message = validation.format_missing_fields_message(inputs_with_gaps)
        missing_with_pages = validation.get_missing_fields_with_pages(inputs_with_gaps)

        # Assert
        assert "Champs manquants:" in message
        assert "Page 1:" in message  # dep is on page 1
        assert "Page 3:" in message  # col, manv_mode on page 3
        assert "Page 5:" in message  # lum, time_bucket on page 5

        # Verify page mapping is correct
        pages = {item[1]: item[0] for item in missing_with_pages}
        assert pages["dep"] == 1
        assert pages["col"] == 3
        assert pages["manv_mode"] == 3
        assert pages["lum"] == 5
        assert pages["time_bucket"] == 5

    def test_form_completion_tracks_progress(self):
        """
        Verify form completion percentage tracks user progress correctly

        Given: Prediction inputs at different completion stages
        When: Calculating completion percentage
        Then: Returns accurate percentage for each stage
        """
        # Stage 1: 0% (empty form)
        empty = {}
        assert validation.get_completion_percentage(empty) == 0.0

        # Stage 2: ~20% (3/15 fields)
        stage_2 = {"dep": "59", "agg": 1, "catr": 1}
        percentage_2 = validation.get_completion_percentage(stage_2)
        assert percentage_2 == pytest.approx(20.0, abs=0.1)

        # Stage 3: ~40% (6/15 fields)
        stage_3 = {**stage_2, "vma_bucket": 50, "int": 1, "circ": 1}
        percentage_3 = validation.get_completion_percentage(stage_3)
        assert percentage_3 == pytest.approx(40.0, abs=0.1)

        # Stage 4: ~93% (14/15 fields)
        stage_4 = {
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
            # Missing only time_bucket
        }
        percentage_4 = validation.get_completion_percentage(stage_4)
        assert percentage_4 == pytest.approx(93.33, abs=0.1)

        # Stage 5: 100% (all 15 fields)
        stage_5 = {**stage_4, "time_bucket": "morning_06_11"}
        percentage_5 = validation.get_completion_percentage(stage_5)
        assert percentage_5 == 100.0

    def test_validation_message_is_user_friendly(self):
        """
        Verify validation messages use French labels and are user-friendly

        Given: Missing fields with technical names
        When: Generating missing fields message
        Then: Message uses French labels instead of technical names
        """
        # Arrange: Missing some technical field names
        inputs = {
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
            "atm": 1,
            "time_bucket": "morning_06_11",
        }

        # Act
        message = validation.format_missing_fields_message(inputs)

        # Assert: Should use French labels, not technical names
        assert "dep" not in message, "Should not show technical name 'dep'"
        assert "lum" not in message, "Should not show technical name 'lum'"
        assert "Département" in message, "Should use French label"
        assert "Conditions d'éclairage" in message, "Should use French label"

    def test_validation_handles_edge_case_all_none_values(self):
        """
        Edge case: Form with all fields present but all None values

        Given: All 15 fields present but set to None
        When: Checking form completion
        Then: Form is not complete (None values don't count)
        """
        # Arrange: All fields present but None
        all_none = dict.fromkeys(validation.REQUIRED_FIELDS)

        # Act
        is_complete = validation.is_form_complete(all_none)
        missing = validation.get_missing_fields(all_none)

        # Assert
        assert is_complete is False, "Form with None values should not be complete"
        assert len(missing) == 15, "All 15 fields should be considered missing"

    def test_validation_identifies_specific_missing_fields_for_user_guidance(self):
        """
        Verify validation provides specific guidance on which fields to fill

        Given: Partially filled form
        When: Getting missing fields with pages
        Then: Returns specific list that can guide user to correct pages
        """
        # Arrange: User filled first 2 pages but stopped
        first_two_pages = {
            "dep": "59",
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            # All of pages 3, 4, 5 are missing
        }

        # Act
        missing_with_pages = validation.get_missing_fields_with_pages(first_two_pages)

        # Assert
        # Should identify fields from pages 3, 4, 5
        missing_pages = [item[0] for item in missing_with_pages]
        assert 3 in missing_pages, "Should identify missing fields on page 3"
        assert 4 in missing_pages, "Should identify missing fields on page 4"
        assert 5 in missing_pages, "Should identify missing fields on page 5"

        # Should not mention pages 1-2 (already complete)
        assert all(page > 2 for page in missing_pages), (
            "Should only mention incomplete pages"
        )
