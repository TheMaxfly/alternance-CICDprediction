"""
Integration tests for US-08: Récapitulatif des 15 champs

Tests verify that:
1. Page 6 displays all 15 field selections in a table format
2. Table shows field name, code, and label
3. Table is generated correctly from session state
"""

import pytest
import pandas as pd
from briefml.ui.lib import session_state, reference_loader


pytestmark = pytest.mark.integration


class TestUS08RecapTable:
    """Integration tests for US-08: Summary table display"""

    def test_page_6_displays_all_15_field_selections_in_table(self):
        """
        T067: Verify Page 6 displays all 15 field selections in table format

        Given: All 15 prediction inputs are filled
        When: Generating recap table
        Then: Table contains 15 rows with field name, code, and label columns
        """
        # Arrange: Complete prediction inputs
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
            "time_bucket": "morning_06_11"
        }

        # Load reference data
        ref_data = reference_loader.load_reference_data()

        # Act: Generate recap table
        recap_table = session_state.generate_recap_table(complete_inputs, ref_data)

        # Assert: Table structure
        assert isinstance(recap_table, pd.DataFrame), "Should return a pandas DataFrame"
        assert len(recap_table) == 15, "Should have exactly 15 rows (one per field)"

        # Assert: Required columns exist
        expected_columns = ["Champ", "Code", "Libellé", "Page"]
        for col in expected_columns:
            assert col in recap_table.columns, f"Table should have '{col}' column"

        # Assert: All field names are present
        field_names = recap_table["Champ"].tolist()
        assert "Département" in field_names
        assert "Conditions d'éclairage" in field_names
        assert "Tranche horaire" in field_names

    def test_recap_table_shows_correct_codes_and_labels(self):
        """
        Verify recap table displays correct codes and labels for each field

        Given: Prediction inputs with specific values
        When: Generating recap table
        Then: Table shows matching codes and labels from reference data
        """
        # Arrange
        inputs = {
            "dep": "59",
            "lum": 1,
            "atm": 1,
            "catr": 1,
            "agg": 1,
            "int": 1,
            "circ": 1,
            "col": 2,
            "vma_bucket": 50,
            "catv_family_4": 1,
            "manv_mode": 1,
            "driver_age_bucket": 30,
            "choc_mode": 1,
            "driver_trajet_family": 1,
            "time_bucket": "morning_06_11"
        }
        ref_data = reference_loader.load_reference_data()

        # Act
        recap_table = session_state.generate_recap_table(inputs, ref_data)

        # Assert: Check specific field values
        # Find row for "lum" field
        lum_row = recap_table[recap_table["Champ"] == "Conditions d'éclairage"]
        assert len(lum_row) == 1, "Should have exactly one row for lum"
        assert lum_row["Code"].values[0] == "1", "lum code should be '1'"

        # Find row for "dep" field
        dep_row = recap_table[recap_table["Champ"] == "Département"]
        assert len(dep_row) == 1, "Should have exactly one row for dep"
        assert dep_row["Code"].values[0] == "59", "dep code should be '59'"

    def test_recap_table_is_sorted_by_page_number(self):
        """
        Verify recap table rows are sorted by page number for logical display

        Given: Complete prediction inputs
        When: Generating recap table
        Then: Rows are ordered by page number (1-6)
        """
        # Arrange
        inputs = {
            "dep": "59", "agg": 1, "catr": 1, "vma_bucket": 50,  # Page 1
            "int": 1, "circ": 1,  # Page 2
            "col": 2, "choc_mode": 1, "manv_mode": 1,  # Page 3
            "driver_age_bucket": 30, "driver_trajet_family": 1, "catv_family_4": 1,  # Page 4
            "lum": 1, "atm": 1, "time_bucket": "morning_06_11"  # Page 5
        }
        ref_data = reference_loader.load_reference_data()

        # Act
        recap_table = session_state.generate_recap_table(inputs, ref_data)

        # Assert: Pages should be in order
        pages = recap_table["Page"].tolist()
        assert pages == sorted(pages), "Table should be sorted by page number"

        # First rows should be from page 1
        first_4_pages = recap_table.head(4)["Page"].tolist()
        assert all(p == 1 for p in first_4_pages), "First 4 rows should be from page 1"

        # Last rows should be from page 5
        last_3_pages = recap_table.tail(3)["Page"].tolist()
        assert all(p == 5 for p in last_3_pages), "Last 3 rows should be from page 5"

    def test_recap_table_handles_partial_inputs(self):
        """
        Verify recap table only shows filled fields (not missing ones)

        Given: Prediction inputs with only 10/15 fields filled
        When: Generating recap table
        Then: Table contains only 10 rows (filled fields)
        """
        # Arrange: Partial inputs (10 fields)
        partial_inputs = {
            "dep": "59",
            "agg": 1,
            "catr": 1,
            "vma_bucket": 50,
            "int": 1,
            "circ": 1,
            "col": 2,
            "choc_mode": 1,
            "manv_mode": 1,
            "driver_age_bucket": 30
            # Missing: driver_trajet_family, catv_family_4, lum, atm, time_bucket
        }
        ref_data = reference_loader.load_reference_data()

        # Act
        recap_table = session_state.generate_recap_table(partial_inputs, ref_data)

        # Assert
        assert len(recap_table) == 10, "Should only show 10 rows for 10 filled fields"

        # Missing fields should not appear
        field_names = recap_table["Champ"].tolist()
        assert "Conditions d'éclairage" not in field_names, "lum should not appear (missing)"
        assert "Tranche horaire" not in field_names, "time_bucket should not appear (missing)"

    def test_recap_table_includes_page_column_for_navigation(self):
        """
        Verify recap table includes page number column for navigation

        Given: Complete prediction inputs
        When: Generating recap table
        Then: Table includes "Page" column with correct page numbers
        """
        # Arrange
        inputs = {
            "dep": "59", "agg": 1, "catr": 1, "vma_bucket": 50,
            "int": 1, "circ": 1,
            "col": 2, "choc_mode": 1, "manv_mode": 1,
            "driver_age_bucket": 30, "driver_trajet_family": 1, "catv_family_4": 1,
            "lum": 1, "atm": 1, "time_bucket": "morning_06_11"
        }
        ref_data = reference_loader.load_reference_data()

        # Act
        recap_table = session_state.generate_recap_table(inputs, ref_data)

        # Assert
        assert "Page" in recap_table.columns, "Should have 'Page' column"

        # Check specific page mappings
        dep_page = recap_table[recap_table["Champ"] == "Département"]["Page"].values[0]
        assert dep_page == 1, "dep should be on page 1"

        lum_page = recap_table[recap_table["Champ"] == "Conditions d'éclairage"]["Page"].values[0]
        assert lum_page == 5, "lum should be on page 5"

    def test_recap_table_uses_french_labels(self):
        """
        Verify recap table uses French labels for better UX

        Given: Prediction inputs with technical field names
        When: Generating recap table
        Then: Table displays French labels, not technical names
        """
        # Arrange
        inputs = {
            "dep": "59", "lum": 1, "atm": 1, "catr": 1, "agg": 1,
            "int": 1, "circ": 1, "col": 2, "vma_bucket": 50,
            "catv_family_4": 1, "manv_mode": 1, "driver_age_bucket": 30,
            "choc_mode": 1, "driver_trajet_family": 1, "time_bucket": "morning_06_11"
        }
        ref_data = reference_loader.load_reference_data()

        # Act
        recap_table = session_state.generate_recap_table(inputs, ref_data)

        # Assert: Should use French labels
        field_names = recap_table["Champ"].tolist()

        # Should NOT contain technical names
        assert "dep" not in field_names, "Should not show technical name 'dep'"
        assert "lum" not in field_names, "Should not show technical name 'lum'"

        # Should contain French labels
        assert "Département" in field_names, "Should show French label"
        assert "Conditions d'éclairage" in field_names, "Should show French label"
        assert "Tranche horaire" in field_names, "Should show French label"

    def test_recap_table_handles_empty_inputs(self):
        """
        Edge case: Empty inputs should return empty table

        Given: Empty prediction inputs
        When: Generating recap table
        Then: Returns empty DataFrame with correct columns
        """
        # Arrange
        empty_inputs = {}
        ref_data = reference_loader.load_reference_data()

        # Act
        recap_table = session_state.generate_recap_table(empty_inputs, ref_data)

        # Assert
        assert isinstance(recap_table, pd.DataFrame), "Should return DataFrame even if empty"
        assert len(recap_table) == 0, "Should have 0 rows for empty inputs"

        # Columns should still exist
        expected_columns = ["Champ", "Code", "Libellé", "Page"]
        for col in expected_columns:
            assert col in recap_table.columns, f"Should have '{col}' column even when empty"
