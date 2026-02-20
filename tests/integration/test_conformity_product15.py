"""
Conformity tests: verify ref_options.json matches the product15 reference specification.

Validates:
- All 15 fields present with exact expected codes
- Format "code — libelle" for all dropdowns
- "Non renseigné" (-1) present where specified
- dep has 107+ departments including DOM-TOM
"""

import pytest
from briefml.ui.lib.reference_loader import load_reference_data, get_dropdown_options

pytestmark = pytest.mark.integration


@pytest.fixture
def ref_data():
  return load_reference_data()


class TestProduct15Conformity:
  """Verify ref_options.json matches the product15 data dictionary."""

  def test_all_15_fields_present(self, ref_data):
    """All 15 required fields exist in ref_options.json."""
    required = [
      "dep", "lum", "atm", "agg", "catr", "int", "circ",
      "col", "choc_mode", "manv_mode", "vma_bucket",
      "catv_family_4", "driver_age_bucket", "driver_trajet_family", "time_bucket"
    ]
    for field in required:
      assert field in ref_data, f"Missing field: {field}"

  def test_dep_codes(self, ref_data):
    """dep: all French department codes present (01-95, 2A, 2B, DOM-TOM)."""
    codes = [opt["code"] for opt in ref_data["dep"]]
    expected_metro = [f"{i:02d}" for i in range(1, 20)] + \
             [f"{i:02d}" for i in range(21, 96)] + \
             ["2A", "2B"]
    expected_dom = ["971", "972", "973", "974", "975", "976", "977", "978", "986", "987", "988"]

    for code in expected_metro:
      assert code in codes, f"dep missing metro code: {code}"
    for code in expected_dom:
      assert code in codes, f"dep missing DOM-TOM code: {code}"

    assert len(codes) >= 107

  def test_lum_codes(self, ref_data):
    """lum: codes -1, 1-5."""
    codes = [opt["code"] for opt in ref_data["lum"]]
    assert set(codes) == {-1, 1, 2, 3, 4, 5}

  def test_lum_labels(self, ref_data):
    """lum: correct French labels."""
    labels = {opt["code"]: opt["label"] for opt in ref_data["lum"]}
    assert labels[1] == "Plein jour"
    assert labels[2] == "Crépuscule ou aube"
    assert labels[3] == "Nuit sans éclairage public"
    assert labels[4] == "Nuit avec éclairage public non allumé"
    assert labels[5] == "Nuit avec éclairage public allumé"
    assert labels[-1] == "Non renseigné"

  def test_atm_codes(self, ref_data):
    """atm: codes -1, 1-9."""
    codes = [opt["code"] for opt in ref_data["atm"]]
    assert set(codes) == {-1, 1, 2, 3, 4, 5, 6, 7, 8, 9}

  def test_agg_codes(self, ref_data):
    """agg: codes 1, 2."""
    codes = [opt["code"] for opt in ref_data["agg"]]
    assert set(codes) == {1, 2}

  def test_catr_codes(self, ref_data):
    """catr: codes 1-7, 9."""
    codes = [opt["code"] for opt in ref_data["catr"]]
    assert set(codes) == {1, 2, 3, 4, 5, 6, 7, 9}

  def test_int_codes(self, ref_data):
    """int: codes 1-9."""
    codes = [opt["code"] for opt in ref_data["int"]]
    assert set(codes) == {1, 2, 3, 4, 5, 6, 7, 8, 9}

  def test_circ_codes(self, ref_data):
    """circ: codes -1, 1-4."""
    codes = [opt["code"] for opt in ref_data["circ"]]
    assert set(codes) == {-1, 1, 2, 3, 4}

  def test_col_codes(self, ref_data):
    """col: codes -1, 1-7."""
    codes = [opt["code"] for opt in ref_data["col"]]
    assert set(codes) == {-1, 1, 2, 3, 4, 5, 6, 7}

  def test_choc_mode_codes(self, ref_data):
    """choc_mode: codes -1, 0-9."""
    codes = [opt["code"] for opt in ref_data["choc_mode"]]
    assert set(codes) == {-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9}

  def test_manv_mode_codes(self, ref_data):
    """manv_mode: codes -1, 0-26."""
    codes = [opt["code"] for opt in ref_data["manv_mode"]]
    expected = {-1} | set(range(27))
    assert set(codes) == expected

  def test_vma_bucket_codes(self, ref_data):
    """vma_bucket: 8 speed buckets."""
    codes = [opt["code"] for opt in ref_data["vma_bucket"]]
    expected = ["<=30", "31-50", "51-80", "81-90", "91-110", "111-130", ">130", "inconnue"]
    assert codes == expected

  def test_catv_family_4_codes(self, ref_data):
    """catv_family_4: 4 vehicle families."""
    codes = [opt["code"] for opt in ref_data["catv_family_4"]]
    expected = ["voitures_utilitaires", "2rm_3rm", "lourds_tc_agri_autres", "vulnerables"]
    assert set(codes) == set(expected)

  def test_driver_age_bucket_codes(self, ref_data):
    """driver_age_bucket: 9 age buckets including ."""
    codes = [opt["code"] for opt in ref_data["driver_age_bucket"]]
    expected = ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65-74", "75+", "unknown"]
    assert set(codes) == set(expected)

  def test_driver_trajet_family_codes(self, ref_data):
    """driver_trajet_family: 7 trip families."""
    codes = [opt["code"] for opt in ref_data["driver_trajet_family"]]
    expected = ["trajet_1", "trajet_2", "trajet_3", "trajet_4", "trajet_5", "trajet_9", "unknown"]
    assert set(codes) == set(expected)

  def test_time_bucket_codes(self, ref_data):
    """time_bucket: night_00_05, morning_06_11, afternoon_12_17, evening_18_23 (4 options)."""
    codes = [opt["code"] for opt in ref_data["time_bucket"]]
    expected = {"night_00_05", "morning_06_11", "afternoon_12_17", "evening_18_23"}
    assert set(codes) == expected
    assert len(codes) == 4

  def test_all_dropdowns_use_code_libelle_format(self, ref_data):
    """All 15 fields produce 'code — libelle' formatted dropdown options."""
    for field in ref_data:
      if field == "help_texts":
        continue
      options = get_dropdown_options(ref_data, field)
      for opt in options:
        assert " — " in opt, \
          f"Field '{field}' option '{opt}' missing 'code — libelle' format"

  def test_non_renseigne_fields(self, ref_data):
    """Fields with -1 Non renseigne: lum, atm, circ, col, choc_mode, manv_mode."""
    fields_with_nr = ["lum", "atm", "circ", "col", "choc_mode", "manv_mode"]
    for field in fields_with_nr:
      codes = [opt["code"] for opt in ref_data[field]]
      assert -1 in codes, f"Field '{field}' should have -1 (Non renseigné)"
