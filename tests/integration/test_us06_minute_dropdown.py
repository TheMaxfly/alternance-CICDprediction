"""
Integration tests for US-06: Validation time_bucket dropdown

Tests verify that:
1. time_bucket field is a selectbox (not text_input or number_input)
2. time_bucket dropdown has 4 options (night_00_05, morning_06_11, afternoon_12_17, evening_18_23)
3. All time_bucket options have proper labels
"""

from pathlib import Path

import pytest

from briefml.ui.lib import reference_loader

pytestmark = pytest.mark.integration


class TestUS06TimeBucketDropdown:
    """Integration tests for US-06: time_bucket field dropdown validation"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load reference data once for all tests."""
        self.ref_data = reference_loader.load_reference_data()

    def test_time_bucket_field_uses_selectbox_in_page_5(self):
        """
        T054: Verify time_bucket field is a selectbox, not text_input

        Given: Page 5 source code
        When: Checking widget type for time_bucket field
        Then: Uses st.selectbox (not st.number_input or st.text_input)
        """
        # Read the page 5 source file
        page_path = Path("briefml/ui/pages/5_Conditions.py")
        with page_path.open(encoding="utf-8") as f:
            source = f.read()

        # Assert: time_bucket uses st.selectbox
        assert "st.selectbox" in source, "Page 5 should use st.selectbox"
        assert 'key="time_bucket_input"' in source, "Should have time_bucket_input key"

        # Assert: time_bucket does NOT use text_input or number_input
        lines = source.split("\n")
        time_bucket_lines = [line for line in lines if "time_bucket" in line.lower()]
        for line in time_bucket_lines:
            assert "st.text_input" not in line, (
                f"time_bucket should NOT use st.text_input: {line}"
            )
            assert "st.number_input" not in line, (
                f"time_bucket should NOT use st.number_input: {line}"
            )

    def test_time_bucket_dropdown_has_4_options(self):
        """
        T056: Verify data/ref_options.json includes 4 time_bucket options

        Given: Reference data for time_bucket field
        When: Counting options
        Then: Has exactly 4 options
        """
        time_bucket_options = self.ref_data["time_bucket"]
        assert len(time_bucket_options) == 4, (
            f"time_bucket should have 4 options, got {len(time_bucket_options)}"
        )

    def test_time_bucket_options_cover_expected_values(self):
        """
        Verify time_bucket options cover expected values

        Given: Reference data for time_bucket field
        When: Checking all code values
        Then: Contains exactly night_00_05, morning_06_11, afternoon_12_17, evening_18_23
        """
        time_bucket_codes = sorted(
            [opt["code"] for opt in self.ref_data["time_bucket"]]
        )
        expected_codes = sorted(
            [
                "night_00_05",
                "morning_06_11",
                "afternoon_12_17",
                "evening_18_23",
            ]
        )

        assert time_bucket_codes == expected_codes, (
            f"time_bucket codes should be {expected_codes}, got gaps or extras"
        )

    def test_time_bucket_options_have_labels(self):
        """
        Verify all time_bucket options have non-empty labels

        Given: Reference data for time_bucket field
        When: Checking labels
        Then: All options have non-empty label strings
        """
        for opt in self.ref_data["time_bucket"]:
            assert "label" in opt, f"Option {opt['code']} should have 'label' key"
            assert isinstance(opt["label"], str), (
                f"Option {opt['code']} label should be string"
            )
            assert len(opt["label"]) > 0, (
                f"Option {opt['code']} label should not be empty"
            )

    def test_time_bucket_formatted_options_are_parseable(self):
        """
        Verify all time_bucket formatted dropdown options can be parsed back

        Given: Formatted time_bucket dropdown options
        When: Parsing each option
        Then: All produce valid string codes
        """
        formatted_options = reference_loader.get_dropdown_options(
            self.ref_data, "time_bucket"
        )
        assert len(formatted_options) == 4

        for option in formatted_options:
            code = reference_loader.parse_dropdown_value(option)
            assert isinstance(code, str), (
                f"Parsed code from '{option}' should be string"
            )
            assert code in [
                "night_00_05",
                "morning_06_11",
                "afternoon_12_17",
                "evening_18_23",
            ], f"Code {code} from '{option}' should be in expected time buckets"

    def test_time_bucket_selectbox_prevents_invalid_input(self):
        """
        Verify only valid time_bucket values exist in dropdown options

        Given: time_bucket reference data
        When: Checking all codes
        Then: No values outside expected set exist
        """
        valid_codes = {
            "night_00_05",
            "morning_06_11",
            "afternoon_12_17",
            "evening_18_23",
        }
        actual_codes = {opt["code"] for opt in self.ref_data["time_bucket"]}

        # No invalid codes
        invalid = actual_codes - valid_codes
        assert len(invalid) == 0, f"Should have no invalid codes, found: {invalid}"

        # No missing codes
        missing = valid_codes - actual_codes
        assert len(missing) == 0, f"Should have no missing codes, found: {missing}"
