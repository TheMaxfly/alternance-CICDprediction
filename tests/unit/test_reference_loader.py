"""
Unit tests for reference_loader - US-09 (get_field_help) and US-10 (schema validation).

Tests:
- get_field_help() returns definition + code table for each field
- get_field_help() returns None for unknown field
- All 15 fields have help text defined
"""

import pytest
from briefml.ui.lib.reference_loader import load_reference_data, get_field_help


class TestUS09FieldHelp:
    """Tests for get_field_help() - contextual help per field."""

    @pytest.fixture
    def ref_data(self):
        """Load reference data once for all tests."""
        return load_reference_data()

    def test_get_field_help_returns_dict_for_known_field(self, ref_data):
        """get_field_help('lum') returns a dict with 'definition' and 'codes' keys."""
        help_info = get_field_help(ref_data, "lum")
        assert help_info is not None
        assert isinstance(help_info, dict)
        assert "definition" in help_info
        assert "codes" in help_info

    def test_get_field_help_definition_is_nonempty_string(self, ref_data):
        """Definition must be a non-empty string describing the field."""
        help_info = get_field_help(ref_data, "lum")
        assert isinstance(help_info["definition"], str)
        assert len(help_info["definition"]) > 10  # meaningful description

    def test_get_field_help_codes_is_list_of_dicts(self, ref_data):
        """Codes must be a list of dicts with 'code' and 'label' keys."""
        help_info = get_field_help(ref_data, "lum")
        assert isinstance(help_info["codes"], list)
        assert len(help_info["codes"]) > 0
        for item in help_info["codes"]:
            assert "code" in item
            assert "label" in item

    def test_get_field_help_codes_match_reference_data(self, ref_data):
        """Codes returned by help must match the reference data options."""
        help_info = get_field_help(ref_data, "lum")
        ref_codes = [opt["code"] for opt in ref_data["lum"]]
        help_codes = [item["code"] for item in help_info["codes"]]
        assert help_codes == ref_codes

    def test_get_field_help_returns_none_for_unknown_field(self, ref_data):
        """get_field_help('unknown_field') returns None."""
        help_info = get_field_help(ref_data, "unknown_field")
        assert help_info is None

    def test_all_15_fields_have_help(self, ref_data):
        """Every one of the 15 required fields has help text."""
        required_fields = [
            "dep", "lum", "atm", "catr", "agg", "int", "circ",
            "col", "vma_bucket", "catv_family_4", "manv_mode",
            "driver_age_bucket", "choc_mode", "driver_trajet_family", "time_bucket"
        ]
        for field in required_fields:
            help_info = get_field_help(ref_data, field)
            assert help_info is not None, f"Field '{field}' has no help text"
            assert len(help_info["definition"]) > 0, f"Field '{field}' has empty definition"

    def test_get_field_help_dep_has_definition(self, ref_data):
        """dep field help contains meaningful definition."""
        help_info = get_field_help(ref_data, "dep")
        assert "département" in help_info["definition"].lower() or "departement" in help_info["definition"].lower()

    def test_get_field_help_atm_includes_non_renseigne(self, ref_data):
        """atm help codes include -1 (Non renseigné)."""
        help_info = get_field_help(ref_data, "atm")
        codes = [item["code"] for item in help_info["codes"]]
        assert -1 in codes
