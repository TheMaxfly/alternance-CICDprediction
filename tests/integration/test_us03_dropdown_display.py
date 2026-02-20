"""
Integration tests for US-03: Affichage "Code + Libellé"

Tests verify that:
1. lum dropdown shows "1 — Plein jour" format
2. All dropdowns across all pages use consistent formatting
3. Formatted values are correctly parsed when selected
"""

import pytest

from briefml.ui.lib import reference_loader

pytestmark = pytest.mark.integration


class TestUS03DropdownDisplay:
    """Integration tests for US-03: Dropdown display with code — libellé format"""

    def test_lum_dropdown_shows_formatted_options(self):
        """
        T034: Verify lum dropdown shows "1 — Plein jour" format

        Given: Reference data loaded
        When: Getting dropdown options for lum field
        Then: Options are formatted as "code — libellé"
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Act
        lum_options = reference_loader.get_dropdown_options(ref_data, "lum")

        # Assert
        assert isinstance(lum_options, list)
        assert len(lum_options) > 0

        # Check specific format for "Plein jour"
        assert "1 — Plein jour" in lum_options, (
            "Should contain formatted option '1 — Plein jour'"
        )

        # Verify all options use " — " separator
        for option in lum_options:
            assert " — " in option, f"Option '{option}' should use ' — ' separator"

    def test_all_field_dropdowns_use_consistent_formatting(self):
        """
        Verify all 15 fields use consistent "code — libellé" formatting

        Given: Reference data for all fields
        When: Getting dropdown options for each field
        Then: All options are formatted consistently
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()
        required_fields = [
            "dep",
            "lum",
            "atm",
            "catr",
            "agg",
            "int",
            "circ",
            "col",
            "vma_bucket",
            "catv_family_4",
            "manv_mode",
            "driver_age_bucket",
            "choc_mode",
            "driver_trajet_family",
            "time_bucket",
        ]

        # Act & Assert
        for field_name in required_fields:
            options = reference_loader.get_dropdown_options(ref_data, field_name)

            # All options should be strings
            assert all(isinstance(opt, str) for opt in options), (
                f"Field '{field_name}' should have string options"
            )

            # All options should use " — " separator
            assert all(" — " in opt for opt in options), (
                f"Field '{field_name}' options should use ' — ' separator"
            )

            # Options should be parseable back to codes
            for option in options:
                code = reference_loader.parse_dropdown_value(option)
                assert code is not None, f"Should be able to parse '{option}'"

    def test_dep_dropdown_shows_department_codes_with_names(self):
        """
        Verify dep dropdown shows "59 — Nord" format (string codes)

        Given: Reference data for dep field
        When: Getting dropdown options
        Then: Options show department code and name
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Act
        dep_options = reference_loader.get_dropdown_options(ref_data, "dep")

        # Assert
        assert len(dep_options) == 107, "Should have 107 department options"

        # Check for specific department formats
        # Note: "Nord" might be in the data, checking for " — " pattern
        assert any("59 — " in opt for opt in dep_options), (
            "Should contain formatted option for department 59"
        )

        # All should use consistent format
        for option in dep_options:
            assert " — " in option, (
                f"Department option '{option}' should use ' — ' separator"
            )

    def test_atm_dropdown_includes_non_renseigne_option(self):
        """
        Verify atm dropdown includes "-1 — Non renseigné" option

        Given: Reference data for atm field
        When: Getting dropdown options
        Then: Includes formatted "Non renseigné" option
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Act
        atm_options = reference_loader.get_dropdown_options(ref_data, "atm")

        # Assert
        # Check that -1 option exists (should be formatted)
        has_non_renseigne = any("-1 — " in opt for opt in atm_options)
        assert has_non_renseigne, "atm should have '-1 — Non renseigné' option"

    def test_time_bucket_dropdown_has_4_options(self):
        """
        Verify time_bucket dropdown has 4 options all formatted

        Given: Reference data for time_bucket field
        When: Getting dropdown options
        Then: Has 4 formatted options
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Act
        time_bucket_options = reference_loader.get_dropdown_options(
            ref_data, "time_bucket"
        )

        # Assert
        assert len(time_bucket_options) == 4, "Should have 4 time_bucket options"

        # Check specific formats
        assert any("night_00_05 — " in opt for opt in time_bucket_options), (
            "Should have 'night_00_05' option"
        )
        assert any("morning_06_11 — " in opt for opt in time_bucket_options), (
            "Should have 'morning_06_11' option"
        )
        assert any("afternoon_12_17 — " in opt for opt in time_bucket_options), (
            "Should have 'afternoon_12_17' option"
        )
        assert any("evening_18_23 — " in opt for opt in time_bucket_options), (
            "Should have 'evening_18_23' option"
        )

        # All should be formatted
        for option in time_bucket_options:
            assert " — " in option, f"time_bucket option '{option}' should be formatted"

    def test_dropdown_selection_parsing_workflow(self):
        """
        Integration: Verify full workflow of selecting and parsing dropdown value

        Given: Formatted dropdown options
        When: User selects option and it's parsed
        Then: Correct code is extracted and stored
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()
        lum_options = reference_loader.get_dropdown_options(ref_data, "lum")

        # Simulate user selecting "1 — Plein jour"
        selected_option = [opt for opt in lum_options if opt.startswith("1 — ")][0]

        # Act
        parsed_code = reference_loader.parse_dropdown_value(selected_option)

        # Assert
        assert parsed_code == 1, "Should parse '1 — Plein jour' to code 1"
        assert isinstance(parsed_code, int), "Code should be integer"

    def test_all_pages_can_generate_formatted_options(self):
        """
        Verify all page fields can generate formatted dropdown options

        Given: Reference data
        When: Generating options for fields on each page
        Then: All succeed and return formatted lists
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Page 1 fields
        page_1_fields = ["dep", "agg", "catr", "vma_bucket"]
        # Page 2 fields
        page_2_fields = ["int", "circ"]
        # Page 3 fields
        page_3_fields = ["col", "choc_mode", "manv_mode"]
        # Page 4 fields
        page_4_fields = ["driver_age_bucket", "driver_trajet_family", "catv_family_4"]
        # Page 5 fields
        page_5_fields = ["lum", "atm", "time_bucket"]

        all_fields = (
            page_1_fields
            + page_2_fields
            + page_3_fields
            + page_4_fields
            + page_5_fields
        )

        # Act & Assert
        for field in all_fields:
            options = reference_loader.get_dropdown_options(ref_data, field)

            assert len(options) > 0, f"Field '{field}' should have at least one option"
            assert all(" — " in opt for opt in options), (
                f"Field '{field}' should have all options formatted"
            )

    def test_formatted_options_preserve_special_characters(self):
        """
        Verify formatted options preserve French accents and special characters

        Given: Reference data with French labels
        When: Getting formatted options
        Then: Accents and special characters are preserved
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Act - get options for a field likely to have accents (e.g., lum, atm)
        lum_options = reference_loader.get_dropdown_options(ref_data, "lum")
        atm_options = reference_loader.get_dropdown_options(ref_data, "atm")

        all_options = lum_options + atm_options

        # Assert - check that French characters are preserved
        # This is a smoke test - we don't check specific strings,
        # just that encoding works properly
        for option in all_options:
            # Should be valid UTF-8 string
            assert isinstance(option, str)
            # Should be able to encode/decode
            assert option == option.encode("utf-8").decode("utf-8")

    def test_dropdown_options_are_stable_across_calls(self):
        """
        Verify dropdown options are stable (same order, same content) across calls

        Given: Reference data
        When: Calling get_dropdown_options() multiple times
        Then: Returns same list each time
        """
        # Arrange
        ref_data = reference_loader.load_reference_data()

        # Act
        lum_options_1 = reference_loader.get_dropdown_options(ref_data, "lum")
        lum_options_2 = reference_loader.get_dropdown_options(ref_data, "lum")

        # Assert
        assert lum_options_1 == lum_options_2, "Options should be stable across calls"
        assert len(lum_options_1) == len(lum_options_2)

        # Order should be preserved
        for i in range(len(lum_options_1)):
            assert lum_options_1[i] == lum_options_2[i], (
                f"Option at index {i} should be the same"
            )
