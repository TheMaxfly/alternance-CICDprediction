"""
Integration tests for US-09: Aide contextuelle par champ.

Tests that each page's fields have help text available via get_field_help().
"""

import pytest
from briefml.ui.lib.reference_loader import load_reference_data, get_field_help

pytestmark = pytest.mark.integration


class TestUS09HelpIntegration:
    """Integration tests for contextual help per field."""

    @pytest.fixture
    def ref_data(self):
        return load_reference_data()

    def test_page1_fields_have_help(self, ref_data):
        """Page 1 fields (dep, agg, catr, vma_bucket) have help text."""
        for field in ["dep", "agg", "catr", "vma_bucket"]:
            help_info = get_field_help(ref_data, field)
            assert help_info is not None, f"Page 1 field '{field}' missing help"
            assert "definition" in help_info
            assert "codes" in help_info
            assert len(help_info["codes"]) > 0

    def test_page2_fields_have_help(self, ref_data):
        """Page 2 fields (int, circ) have help text."""
        for field in ["int", "circ"]:
            help_info = get_field_help(ref_data, field)
            assert help_info is not None, f"Page 2 field '{field}' missing help"
            assert len(help_info["definition"]) > 0

    def test_page3_fields_have_help(self, ref_data):
        """Page 3 fields (col, choc_mode, manv_mode) have help text."""
        for field in ["col", "choc_mode", "manv_mode"]:
            help_info = get_field_help(ref_data, field)
            assert help_info is not None, f"Page 3 field '{field}' missing help"
            assert len(help_info["definition"]) > 0

    def test_page4_fields_have_help(self, ref_data):
        """Page 4 fields (driver_age_bucket, driver_trajet_family, catv_family_4) have help text."""
        for field in ["driver_age_bucket", "driver_trajet_family", "catv_family_4"]:
            help_info = get_field_help(ref_data, field)
            assert help_info is not None, f"Page 4 field '{field}' missing help"
            assert len(help_info["definition"]) > 0

    def test_page5_fields_have_help(self, ref_data):
        """Page 5 fields (lum, atm, time_bucket) have help text."""
        for field in ["lum", "atm", "time_bucket"]:
            help_info = get_field_help(ref_data, field)
            assert help_info is not None, f"Page 5 field '{field}' missing help"
            assert len(help_info["definition"]) > 0

    def test_help_codes_count_matches_reference(self, ref_data):
        """Help codes count matches reference data options count for each field."""
        for field in ref_data:
            help_info = get_field_help(ref_data, field)
            if help_info is not None:
                assert len(help_info["codes"]) == len(ref_data[field]), \
                    f"Field '{field}': help has {len(help_info['codes'])} codes but ref has {len(ref_data[field])}"

    def test_help_definition_is_in_french(self, ref_data):
        """Help definitions should be written in French."""
        # Check a sample of fields for French content
        help_lum = get_field_help(ref_data, "lum")
        # Should contain French words
        definition = help_lum["definition"].lower()
        assert any(word in definition for word in ["éclairage", "luminosité", "lumière", "conditions"]), \
            f"Definition for 'lum' doesn't appear to be in French: {help_lum['definition']}"
