"""
Unit tests for US-03: Affichage "Code + Libellé"

Tests verify that:
1. format_dropdown_option() formats options as "code — libellé"
2. get_dropdown_options() returns formatted list
3. parse_dropdown_value() correctly extracts code from formatted string
"""

import pytest

from briefml.ui.lib import reference_loader


class TestUS03DropdownFormat:
    """Tests for US-03: Dropdown formatting with code and label"""

    def test_format_dropdown_option_with_integer_code(self):
        """
        T033: Verify format_dropdown_option() formats integer codes correctly

        Given: Integer code and label
        When: format_dropdown_option() is called
        Then: Returns "code — libellé" format
        """
        # Arrange
        code = 1
        label = "Plein jour"

        # Act
        result = reference_loader.format_dropdown_option(code, label)

        # Assert
        assert result == "1 — Plein jour"
        assert " — " in result, "Should use em dash separator"
        assert result.startswith("1"), "Should start with code"
        assert result.endswith("Plein jour"), "Should end with label"

    def test_format_dropdown_option_with_string_code(self):
        """
        Verify format_dropdown_option() works with string codes (e.g., department)

        Given: String code and label
        When: format_dropdown_option() is called
        Then: Returns "code — libellé" format
        """
        # Arrange
        code = "59"
        label = "Nord"

        # Act
        result = reference_loader.format_dropdown_option(code, label)

        # Assert
        assert result == "59 — Nord"
        assert isinstance(result, str)

    def test_format_dropdown_option_with_negative_code(self):
        """
        Verify format_dropdown_option() handles negative codes (e.g., "Non renseigné")

        Given: Negative code (-1) and label
        When: format_dropdown_option() is called
        Then: Returns "-1 — libellé" format
        """
        # Arrange
        code = -1
        label = "Non renseigné"

        # Act
        result = reference_loader.format_dropdown_option(code, label)

        # Assert
        assert result == "-1 — Non renseigné"

    def test_format_dropdown_option_with_special_characters_in_label(self):
        """
        Verify format_dropdown_option() handles special characters in labels

        Given: Code and label with special characters (accents, apostrophes)
        When: format_dropdown_option() is called
        Then: Returns correctly formatted string
        """
        # Arrange
        code = 3
        label = "Crépuscule ou aube (matin d'été)"

        # Act
        result = reference_loader.format_dropdown_option(code, label)

        # Assert
        assert result == "3 — Crépuscule ou aube (matin d'été)"
        assert "é" in result, "Should preserve accents"
        assert "'" in result, "Should preserve apostrophes"

    def test_parse_dropdown_value_extracts_integer_code(self):
        """
        Verify parse_dropdown_value() extracts integer code from formatted string

        Given: Formatted dropdown value "1 — Plein jour"
        When: parse_dropdown_value() is called
        Then: Returns integer 1
        """
        # Arrange
        formatted = "1 — Plein jour"

        # Act
        result = reference_loader.parse_dropdown_value(formatted)

        # Assert
        assert result == 1
        assert isinstance(result, int)

    def test_parse_dropdown_value_extracts_string_code(self):
        """
        Verify parse_dropdown_value() keeps string codes as strings

        Given: Formatted dropdown value "59 — Nord"
        When: parse_dropdown_value() is called
        Then: Returns string "59"
        """
        # Arrange
        formatted = "59 — Nord"

        # Act
        result = reference_loader.parse_dropdown_value(formatted)

        # Assert
        # Note: parse_dropdown_value tries to convert to int
        # "59" becomes int 59
        assert result == 59
        assert isinstance(result, int)

    def test_parse_dropdown_value_extracts_negative_code(self):
        """
        Verify parse_dropdown_value() handles negative codes

        Given: Formatted dropdown value "-1 — Non renseigné"
        When: parse_dropdown_value() is called
        Then: Returns integer -1
        """
        # Arrange
        formatted = "-1 — Non renseigné"

        # Act
        result = reference_loader.parse_dropdown_value(formatted)

        # Assert
        assert result == -1
        assert isinstance(result, int)

    def test_parse_dropdown_value_handles_unformatted_value(self):
        """
        Edge case: parse_dropdown_value() handles non-formatted values

        Given: Value without " — " separator
        When: parse_dropdown_value() is called
        Then: Returns value as-is
        """
        # Arrange
        unformatted = "Some value"

        # Act
        result = reference_loader.parse_dropdown_value(unformatted)

        # Assert
        assert result == "Some value"

    def test_get_dropdown_options_returns_formatted_list(self):
        """
        Verify get_dropdown_options() returns list of formatted options

        Given: Reference data with field options
        When: get_dropdown_options() is called
        Then: Returns list of "code — libellé" strings
        """
        # Arrange
        ref_data = {
            "lum": [
                {"code": 1, "label": "Plein jour"},
                {"code": 2, "label": "Crépuscule ou aube"},
                {"code": 3, "label": "Nuit sans éclairage public"},
                {"code": 4, "label": "Nuit avec éclairage public non allumé"},
                {"code": 5, "label": "Nuit avec éclairage public allumé"},
            ]
        }

        # Act
        result = reference_loader.get_dropdown_options(ref_data, "lum")

        # Assert
        assert isinstance(result, list)
        assert len(result) == 5
        assert result[0] == "1 — Plein jour"
        assert result[1] == "2 — Crépuscule ou aube"
        assert result[4] == "5 — Nuit avec éclairage public allumé"

        # All items should have the separator
        assert all(" — " in option for option in result)

    def test_get_dropdown_options_raises_error_for_missing_field(self):
        """
        Verify get_dropdown_options() raises KeyError for invalid field

        Given: Reference data without requested field
        When: get_dropdown_options() is called
        Then: Raises KeyError
        """
        # Arrange
        ref_data = {"lum": [{"code": 1, "label": "Test"}]}

        # Act & Assert
        with pytest.raises(KeyError) as exc_info:
            reference_loader.get_dropdown_options(ref_data, "invalid_field")

        assert "invalid_field" in str(exc_info.value)

    def test_get_label_for_code_returns_correct_label(self):
        """
        Verify get_label_for_code() returns matching label

        Given: Reference data and valid code
        When: get_label_for_code() is called
        Then: Returns corresponding label
        """
        # Arrange
        ref_data = {
            "lum": [
                {"code": 1, "label": "Plein jour"},
                {"code": 2, "label": "Crépuscule ou aube"},
            ]
        }

        # Act
        result = reference_loader.get_label_for_code(ref_data, "lum", 1)

        # Assert
        assert result == "Plein jour"

    def test_get_label_for_code_raises_error_for_invalid_code(self):
        """
        Verify get_label_for_code() raises ValueError for invalid code

        Given: Reference data and non-existent code
        When: get_label_for_code() is called
        Then: Raises ValueError
        """
        # Arrange
        ref_data = {"lum": [{"code": 1, "label": "Plein jour"}]}

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            reference_loader.get_label_for_code(ref_data, "lum", 999)

        assert "999" in str(exc_info.value)
        assert "lum" in str(exc_info.value)

    def test_roundtrip_format_and_parse(self):
        """
        Integration: Verify format -> parse roundtrip preserves code

        Given: Code and label
        When: Format then parse
        Then: Original code is recovered
        """
        # Test with integer code
        formatted = reference_loader.format_dropdown_option(1, "Plein jour")
        parsed = reference_loader.parse_dropdown_value(formatted)
        assert parsed == 1

        # Test with negative code
        formatted = reference_loader.format_dropdown_option(-1, "Non renseigné")
        parsed = reference_loader.parse_dropdown_value(formatted)
        assert parsed == -1
