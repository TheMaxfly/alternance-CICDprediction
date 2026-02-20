"""
Client-side validation logic for prediction inputs.

This module provides functions to:
- Check if form is complete (all 15 fields filled)
- Validate individual fields
- Get missing fields with page numbers
"""

from typing import Any


# Required fields for prediction
REQUIRED_FIELDS = [
    "dep", "lum", "atm", "catr", "agg", "int", "circ",
    "col", "vma_bucket", "catv_family_4", "manv_mode",
    "driver_age_bucket", "choc_mode", "driver_trajet_family", "time_bucket"
]

# Field to page mapping (for navigation hints)
FIELD_TO_PAGE = {
    "dep": 1,
    "agg": 1,
    "catr": 1,
    "vma_bucket": 1,
    "int": 2,
    "circ": 2,
    "col": 3,
    "choc_mode": 3,
    "manv_mode": 3,
    "driver_age_bucket": 4,
    "driver_trajet_family": 4,
    "catv_family_4": 4,
    "lum": 5,
    "atm": 5,
    "time_bucket": 5
}

# Field labels in French (for error messages)
FIELD_LABELS = {
    "dep": "Département",
    "lum": "Conditions d'éclairage",
    "atm": "Conditions atmosphériques",
    "catr": "Catégorie de route",
    "agg": "Agglomération",
    "int": "Type d'intersection",
    "circ": "Régime de circulation",
    "col": "Type de collision",
    "vma_bucket": "Vitesse maximale autorisée",
    "catv_family_4": "Famille de véhicule",
    "manv_mode": "Manœuvre",
    "driver_age_bucket": "Classe d'âge conducteur",
    "choc_mode": "Point de choc initial",
    "driver_trajet_family": "Famille de trajet conducteur",
    "time_bucket": "Tranche horaire"
}


def is_form_complete(prediction_inputs: dict[str, Any]) -> bool:
    """
    Check if all 15 required fields are filled.

    Args:
        prediction_inputs: Dictionary of field_name -> value

    Returns:
        True if all 15 fields are present and not None, False otherwise
    """
    return all(
        field in prediction_inputs and prediction_inputs[field] is not None
        for field in REQUIRED_FIELDS
    )


def get_missing_fields(prediction_inputs: dict[str, Any]) -> list[str]:
    """
    Get list of missing or empty required fields.

    Args:
        prediction_inputs: Dictionary of field_name -> value

    Returns:
        List of missing field names
    """
    missing = []
    for field in REQUIRED_FIELDS:
        if field not in prediction_inputs or prediction_inputs[field] is None:
            missing.append(field)
    return missing


def get_missing_fields_with_pages(prediction_inputs: dict[str, Any]) -> list[tuple[int, str, str]]:
    """
    Get list of missing fields with their page numbers and labels.

    Args:
        prediction_inputs: Dictionary of field_name -> value

    Returns:
        List of tuples: [(page_number, field_name, field_label), ...]
        Sorted by page number
    """
    missing = get_missing_fields(prediction_inputs)
    result = [
        (FIELD_TO_PAGE.get(field, 0), field, FIELD_LABELS.get(field, field))
        for field in missing
    ]
    return sorted(result, key=lambda x: x[0])


def format_missing_fields_message(prediction_inputs: dict[str, Any]) -> str:
    """
    Format a user-friendly message listing missing fields by page.

    Args:
        prediction_inputs: Dictionary of field_name -> value

    Returns:
        Formatted message string, or empty string if no missing fields

    Example:
        "Champs manquants:\n- Page 1: Département\n- Page 5: Tranche horaire"
    """
    missing = get_missing_fields_with_pages(prediction_inputs)

    if not missing:
        return ""

    lines = ["Champs manquants:"]
    for page, field_name, field_label in missing:
        lines.append(f"- Page {page}: {field_label}")

    return "\n".join(lines)


def validate_field(field_name: str, value: Any, reference_data: dict[str, list[dict[str, Any]]]) -> tuple[bool, str]:
    """
    Validate a single field value against reference data.

    Args:
        field_name: Name of the field to validate
        value: Value to validate
        reference_data: Loaded reference data from reference_loader

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if value is valid, False otherwise
        - error_message: Empty string if valid, error message if invalid
    """
    # Check if field exists in reference data
    if field_name not in reference_data:
        return False, f"Champ '{field_name}' non reconnu"

    # Check if value is None or empty
    if value is None or value == "":
        return False, f"{FIELD_LABELS.get(field_name, field_name)} est requis"

    # Get valid codes from reference data
    valid_options = reference_data[field_name]
    valid_codes = [opt['code'] for opt in valid_options]

    # Check if value is in valid codes
    if value not in valid_codes:
        return False, f"Valeur invalide pour {FIELD_LABELS.get(field_name, field_name)}"

    return True, ""


def get_completion_percentage(prediction_inputs: dict[str, Any]) -> float:
    """
    Calculate form completion percentage.

    Args:
        prediction_inputs: Dictionary of field_name -> value

    Returns:
        Percentage of fields filled (0.0 to 100.0)
    """
    filled_count = sum(
        1 for field in REQUIRED_FIELDS
        if field in prediction_inputs and prediction_inputs[field] is not None
    )
    return (filled_count / len(REQUIRED_FIELDS)) * 100


def get_field_label(field_name: str) -> str:
    """
    Get French label for a field name.

    Args:
        field_name: Technical field name

    Returns:
        French label
    """
    return FIELD_LABELS.get(field_name, field_name)


def get_field_page(field_name: str) -> int:
    """
    Get page number where a field is located.

    Args:
        field_name: Technical field name

    Returns:
        Page number (1-6), or 0 if not found
    """
    return FIELD_TO_PAGE.get(field_name, 0)
