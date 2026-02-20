"""
Reference data loader for dropdown options.

This module provides functions to:
- Load reference data from data/ref_options.json
- Validate reference data against schema
- Format dropdown options as "code — libellé"
"""

import json
from pathlib import Path
from typing import Any


def load_reference_data(json_path: str = "data/ref_options.json") -> dict[str, list[dict[str, Any]]]:
    """
    Load and validate reference data from JSON file.

    Args:
        json_path: Path to ref_options.json file (default: data/ref_options.json)

    Returns:
        Dictionary with field names as keys and lists of option dicts as values.
        Each option dict has 'code' and 'label' keys.

    Raises:
        FileNotFoundError: If JSON file does not exist
        ValueError: If JSON is invalid or missing required fields
    """
    json_file = Path(json_path)

    if not json_file.exists():
        raise FileNotFoundError(
            f"Reference data file not found: {json_path}\n"
            f"Expected location: {json_file.absolute()}"
        )

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {json_path}: {e}")

    # Validate required fields
    required_fields = [
        "dep", "lum", "atm", "catr", "agg", "int", "circ", "col",
        "vma_bucket", "catv_family_4", "manv_mode", "driver_age_bucket",
        "choc_mode", "driver_trajet_family", "time_bucket"
    ]

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(
            f"Reference data is missing required fields: {', '.join(missing_fields)}\n"
            f"Expected 15 fields: {', '.join(required_fields)}"
        )

    # Validate each field has options
    for field in required_fields:
        if not isinstance(data[field], list):
            raise ValueError(f"Field '{field}' must be a list, got {type(data[field])}")
        if len(data[field]) == 0:
            raise ValueError(f"Field '{field}' must have at least one option")

        # Validate each option has 'code' and 'label'
        for idx, option in enumerate(data[field]):
            if not isinstance(option, dict):
                raise ValueError(f"Field '{field}' option {idx} must be a dict, got {type(option)}")
            if 'code' not in option:
                raise ValueError(f"Field '{field}' option {idx} is missing 'code' key")
            if 'label' not in option:
                raise ValueError(f"Field '{field}' option {idx} is missing 'label' key")

    return data


def format_dropdown_option(code: int | str, label: str) -> str:
    """
    Format dropdown option as "code — libellé".

    Args:
        code: Option code (int or string)
        label: Option label (French description)

    Returns:
        Formatted string: "code — libellé"

    Example:
        >>> format_dropdown_option(1, "Plein jour")
        "1 — Plein jour"
        >>> format_dropdown_option("59", "Nord")
        "59 — Nord"
    """
    return f"{code} — {label}"


def get_dropdown_options(reference_data: dict[str, list[dict[str, Any]]], field_name: str) -> list[str]:
    """
    Get formatted dropdown options for a specific field.

    Args:
        reference_data: Loaded reference data from load_reference_data()
        field_name: Name of the field (e.g., "lum", "dep", "atm")

    Returns:
        List of formatted option strings: ["code — libellé", ...]

    Raises:
        KeyError: If field_name not found in reference_data
    """
    if field_name not in reference_data:
        raise KeyError(f"Field '{field_name}' not found in reference data")

    options = reference_data[field_name]
    return [format_dropdown_option(opt['code'], opt['label']) for opt in options]


def parse_dropdown_value(formatted_value: str) -> str | int:
    """
    Parse selected dropdown value back to code.

    Args:
        formatted_value: Formatted dropdown value "code — libellé"

    Returns:
        Extracted code (string or int)

    Example:
        >>> parse_dropdown_value("1 — Plein jour")
        1
        >>> parse_dropdown_value("59 — Nord")
        "59"
    """
    if " — " not in formatted_value:
        # Fallback: return as-is if not formatted
        return formatted_value

    code_str = formatted_value.split(" — ")[0]

    # Try to convert to int only if it roundtrips cleanly (e.g. "1" -> 1 -> "1")
    # This preserves leading zeros like "01" and non-numeric strings like "<=30"
    try:
        int_val = int(code_str)
        if str(int_val) == code_str:
            return int_val
        return code_str
    except ValueError:
        return code_str


def get_label_for_code(reference_data: dict[str, list[dict[str, Any]]], field_name: str, code: int | str) -> str:
    """
    Get label for a specific code in a field.

    Args:
        reference_data: Loaded reference data
        field_name: Field name (e.g., "lum")
        code: Code to look up

    Returns:
        Label for the code

    Raises:
        KeyError: If field_name not found
        ValueError: If code not found in field options
    """
    if field_name not in reference_data:
        raise KeyError(f"Field '{field_name}' not found in reference data")

    options = reference_data[field_name]
    for opt in options:
        if opt['code'] == code or str(opt['code']) == str(code):
            return opt['label']

    raise ValueError(f"Code '{code}' not found in field '{field_name}'")


def get_field_help(reference_data: dict[str, list[dict[str, Any]]], field_name: str) -> dict[str, Any] | None:
    """
    Get contextual help for a field: definition + code table.

    Args:
        reference_data: Loaded reference data from load_reference_data()
        field_name: Name of the field (e.g., "lum", "dep")

    Returns:
        Dictionary with keys:
        - "definition": str - French description of the field
        - "codes": list[dict] - List of {"code": ..., "label": ...} options
        Returns None if field_name is not found.
    """
    if field_name not in reference_data:
        return None

    help_texts = reference_data.get("help_texts", {})
    definition = help_texts.get(field_name, "")

    if not definition:
        return None

    return {
        "definition": definition,
        "codes": reference_data[field_name]
    }
