"""
Integration tests for US-04: Valeurs "Non renseigné"

Tests verify that:
1. atm "-1 — Non renseigné" selection → API receives -1
2. ref_options.json includes "-1 — Non renseigné" for atm, circ, col
"""

import pytest
from briefml.ui.lib import reference_loader


pytestmark = pytest.mark.integration


class TestUS04NotSpecified:
    """Integration tests for US-04: Non renseigné option handling"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load reference data once for all tests."""
        self.ref_data = reference_loader.load_reference_data()

    def test_atm_non_renseigne_selection_returns_minus_1(self):
        """
        T042: Verify atm "-1 — Non renseigné" selection → API receives -1

        Given: atm dropdown with "Non renseigné" option
        When: User selects "-1 — Non renseigné"
        Then: Parsed value is -1 (integer) for API payload
        """
        # Arrange
        atm_options = reference_loader.get_dropdown_options(self.ref_data, "atm")
        non_renseigne_option = [opt for opt in atm_options if opt.startswith("-1 — ")]

        # Assert option exists
        assert len(non_renseigne_option) == 1, "Should have exactly one '-1 — Non renseigné' option"

        # Act: simulate user selection and parsing
        selected = non_renseigne_option[0]
        parsed_code = reference_loader.parse_dropdown_value(selected)

        # Assert: API should receive -1
        assert parsed_code == -1, "Parsed code should be -1"
        assert isinstance(parsed_code, int), "Code should be integer for API"

    def test_ref_options_includes_non_renseigne_for_atm(self):
        """
        T043a: Verify ref_options.json includes "-1 — Non renseigné" for atm

        Given: Reference data loaded
        When: Checking atm field options
        Then: Contains option with code -1 and label "Non renseigné"
        """
        atm_options = self.ref_data["atm"]
        codes = [opt["code"] for opt in atm_options]
        labels = {opt["code"]: opt["label"] for opt in atm_options}

        assert -1 in codes, "atm should have code -1"
        assert labels[-1] == "Non renseigné", "atm code -1 should have label 'Non renseigné'"

    def test_ref_options_includes_non_renseigne_for_circ(self):
        """
        T043b: Verify ref_options.json includes "-1 — Non renseigné" for circ

        Given: Reference data loaded
        When: Checking circ field options
        Then: Contains option with code -1 and label "Non renseigné"
        """
        circ_options = self.ref_data["circ"]
        codes = [opt["code"] for opt in circ_options]
        labels = {opt["code"]: opt["label"] for opt in circ_options}

        assert -1 in codes, "circ should have code -1"
        assert labels[-1] == "Non renseigné", "circ code -1 should have label 'Non renseigné'"

    def test_ref_options_includes_non_renseigne_for_col(self):
        """
        T043c: Verify ref_options.json includes "-1 — Non renseigné" for col

        Given: Reference data loaded
        When: Checking col field options
        Then: Contains option with code -1 and label "Non renseigné"
        """
        col_options = self.ref_data["col"]
        codes = [opt["code"] for opt in col_options]
        labels = {opt["code"]: opt["label"] for opt in col_options}

        assert -1 in codes, "col should have code -1"
        assert labels[-1] == "Non renseigné", "col code -1 should have label 'Non renseigné'"

    def test_ref_options_includes_non_renseigne_for_lum(self):
        """
        Verify ref_options.json includes "-1 — Non renseigné" for lum

        Given: Reference data loaded
        When: Checking lum field options
        Then: Contains option with code -1 and label "Non renseigné"
        """
        lum_options = self.ref_data["lum"]
        codes = [opt["code"] for opt in lum_options]
        labels = {opt["code"]: opt["label"] for opt in lum_options}

        assert -1 in codes, "lum should have code -1"
        assert labels[-1] == "Non renseigné", "lum code -1 should have label 'Non renseigné'"

    def test_non_renseigne_dropdown_format_is_consistent(self):
        """
        Verify all "Non renseigné" options use consistent formatting

        Given: Fields that support "Non renseigné" (lum, atm, circ, col)
        When: Formatting dropdown options
        Then: All produce "-1 — Non renseigné" format
        """
        fields_with_non_renseigne = ["lum", "atm", "circ", "col"]

        for field in fields_with_non_renseigne:
            options = reference_loader.get_dropdown_options(self.ref_data, field)
            matching = [opt for opt in options if opt.startswith("-1 — ")]

            assert len(matching) == 1, \
                f"Field '{field}' should have exactly one '-1 — Non renseigné' option"
            assert "Non renseigné" in matching[0], \
                f"Field '{field}' -1 option should contain 'Non renseigné'"

    def test_non_renseigne_roundtrip_for_all_fields(self):
        """
        Verify "Non renseigné" values survive the full format → parse roundtrip

        Given: Fields that support "Non renseigné"
        When: Formatting then parsing the -1 option
        Then: Code -1 is recovered for all fields
        """
        fields_with_non_renseigne = ["lum", "atm", "circ", "col"]

        for field in fields_with_non_renseigne:
            # Format
            formatted = reference_loader.format_dropdown_option(-1, "Non renseigné")
            assert formatted == "-1 — Non renseigné"

            # Parse
            parsed = reference_loader.parse_dropdown_value(formatted)
            assert parsed == -1, f"Field '{field}': roundtrip should recover -1"

    def test_non_renseigne_values_are_valid_api_inputs(self):
        """
        Verify -1 values are valid for the API (included in valid codes)

        Given: Fields with "Non renseigné" support
        When: Checking valid codes
        Then: -1 is a valid code for lum, atm, circ, col
        """
        fields_with_non_renseigne = ["lum", "atm", "circ", "col"]

        for field in fields_with_non_renseigne:
            valid_codes = [opt["code"] for opt in self.ref_data[field]]
            assert -1 in valid_codes, \
                f"Field '{field}' should accept -1 as a valid API input"
