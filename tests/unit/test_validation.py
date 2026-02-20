"""
Unit tests for US-05: Validation "15 champs requis"

Tests verify that:
1. is_form_complete() returns False with 14/15 fields
2. is_form_complete() returns True with all 15 fields
3. Missing fields messages are properly formatted
"""

from briefml.ui.lib import validation


class TestUS05Validation:
    """Tests for US-05: Validation of required fields"""

    def test_is_form_complete_returns_false_with_14_of_15_fields(self):
        """
        T046: Verify is_form_complete() returns False with 14/15 fields

        Given: Prediction inputs with 14 out of 15 required fields
        When: is_form_complete() is called
        Then: Returns False (form is not complete)
        """
        # Arrange: Complete form minus one field (time_bucket)
        inputs_14_fields = {
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
            # time_bucket is missing (14/15)
        }

        # Act
        result = validation.is_form_complete(inputs_14_fields)

        # Assert
        assert result is False, "Form with 14/15 fields should not be complete"
        assert len(inputs_14_fields) == 14, "Should have exactly 14 fields"

    def test_is_form_complete_returns_true_with_all_15_fields(self):
        """
        T047: Verify is_form_complete() returns True with all 15 fields

        Given: Prediction inputs with all 15 required fields filled
        When: is_form_complete() is called
        Then: Returns True (form is complete)
        """
        # Arrange: Complete form with all 15 fields
        inputs_15_fields = {
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
        result = validation.is_form_complete(inputs_15_fields)

        # Assert
        assert result is True, "Form with all 15 fields should be complete"
        assert len(inputs_15_fields) == 15, "Should have exactly 15 fields"

    def test_is_form_complete_returns_false_with_empty_dict(self):
        """
        Edge case: Empty dictionary should not be complete

        Given: Empty prediction inputs
        When: is_form_complete() is called
        Then: Returns False
        """
        # Arrange
        empty_inputs = {}

        # Act
        result = validation.is_form_complete(empty_inputs)

        # Assert
        assert result is False, "Empty form should not be complete"

    def test_is_form_complete_returns_false_with_none_values(self):
        """
        Edge case: Fields with None values should not count as filled

        Given: All 15 fields present but one has None value
        When: is_form_complete() is called
        Then: Returns False
        """
        # Arrange: All fields present, but time_bucket is None
        inputs_with_none = {
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
            "time_bucket": None,  # None value
        }

        # Act
        result = validation.is_form_complete(inputs_with_none)

        # Assert
        assert result is False, "Field with None value should not count as filled"

    def test_get_missing_fields_returns_correct_list(self):
        """
        Verify get_missing_fields() returns list of missing field names

        Given: Prediction inputs with 3 missing fields
        When: get_missing_fields() is called
        Then: Returns list with 3 missing field names
        """
        # Arrange: Missing time_bucket, lum, atm
        inputs_12_fields = {
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
        }

        # Act
        missing = validation.get_missing_fields(inputs_12_fields)

        # Assert
        assert len(missing) == 3, "Should have 3 missing fields"
        assert "lum" in missing, "lum should be missing"
        assert "atm" in missing, "atm should be missing"
        assert "time_bucket" in missing, "time_bucket should be missing"

    def test_get_missing_fields_with_pages_returns_sorted_list(self):
        """
        Verify get_missing_fields_with_pages() returns sorted list with page numbers

        Given: Prediction inputs with missing fields on different pages
        When: get_missing_fields_with_pages() is called
        Then: Returns list sorted by page number with (page, field, label) tuples
        """
        # Arrange: Missing fields on pages 1, 3, 5
        inputs = {
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "choc_mode": 1,
            "manv_mode": 1,
            "driver_age_bucket": 30,
            "driver_trajet_family": 1,
            "catv_family_4": 1,
            "lum": 1,
            "atm": 1,
            # Missing: dep (page 1), col (page 3), time_bucket (page 5)
        }

        # Act
        result = validation.get_missing_fields_with_pages(inputs)

        # Assert
        assert len(result) == 3, "Should have 3 missing fields"

        # Verify structure: list of (page, field_name, field_label)
        pages = [item[0] for item in result]
        fields = [item[1] for item in result]

        # Should be sorted by page
        assert pages == sorted(pages), "Results should be sorted by page number"

        # Check specific missing fields
        assert "dep" in fields, "dep should be in missing fields"
        assert "col" in fields, "col should be in missing fields"
        assert "time_bucket" in fields, "time_bucket should be in missing fields"

    def test_format_missing_fields_message_returns_formatted_string(self):
        """
        Verify format_missing_fields_message() returns user-friendly message

        Given: Prediction inputs with 2 missing fields
        When: format_missing_fields_message() is called
        Then: Returns formatted message with "Page X: Field label" format
        """
        # Arrange: Missing lum (page 5) and dep (page 1)
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

        # Assert
        assert "Champs manquants:" in message, "Message should have header"
        assert "Page 1:" in message, "Should mention page 1"
        assert "Page 5:" in message, "Should mention page 5"
        assert "Département" in message, "Should use French label for dep"
        assert "Conditions d'éclairage" in message, "Should use French label for lum"

    def test_format_missing_fields_message_returns_empty_string_when_complete(self):
        """
        Verify format_missing_fields_message() returns empty string for complete form

        Given: Prediction inputs with all 15 fields filled
        When: format_missing_fields_message() is called
        Then: Returns empty string
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
        message = validation.format_missing_fields_message(complete_inputs)

        # Assert
        assert message == "", "Complete form should return empty message"

    def test_get_completion_percentage_calculates_correctly(self):
        """
        Verify get_completion_percentage() calculates correct percentage

        Given: Prediction inputs with various completion levels
        When: get_completion_percentage() is called
        Then: Returns correct percentage (0-100)
        """
        # Test 0%
        empty = {}
        assert validation.get_completion_percentage(empty) == 0.0

        # Test 50% (7.5/15 rounded)
        half = {
            "dep": "59",
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "col": 2,
        }
        percentage = validation.get_completion_percentage(half)
        expected = (7 / 15) * 100  # ~46.67%
        assert abs(percentage - expected) < 0.01, (
            f"Expected ~{expected}%, got {percentage}%"
        )

        # Test 100%
        complete = {
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
        assert validation.get_completion_percentage(complete) == 100.0

    def test_get_field_label_returns_french_labels(self):
        """
        Verify get_field_label() returns correct French labels

        Given: Technical field names
        When: get_field_label() is called
        Then: Returns French label
        """
        assert validation.get_field_label("dep") == "Département"
        assert validation.get_field_label("lum") == "Conditions d'éclairage"
        assert validation.get_field_label("time_bucket") == "Tranche horaire"

    def test_get_field_page_returns_correct_page_numbers(self):
        """
        Verify get_field_page() returns correct page numbers

        Given: Field names
        When: get_field_page() is called
        Then: Returns correct page number (1-6)
        """
        # Page 1 fields
        assert validation.get_field_page("dep") == 1
        assert validation.get_field_page("agg") == 1

        # Page 2 fields
        assert validation.get_field_page("int") == 2
        assert validation.get_field_page("circ") == 2

        # Page 5 fields
        assert validation.get_field_page("lum") == 5
        assert validation.get_field_page("atm") == 5
        assert validation.get_field_page("time_bucket") == 5

        # Unknown field
        assert validation.get_field_page("unknown_field") == 0
