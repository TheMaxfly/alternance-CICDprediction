"""
Session state management helpers for Streamlit interface.

This module provides helper functions to:
- Initialize session state
- Manage current page navigation
- Store and retrieve prediction inputs
- Handle prediction results
- Generate recap tables for display
"""

from typing import Any

import pandas as pd
import streamlit as st

from briefml.ui.lib import reference_loader, validation


def initialize_state(reference_data: dict[str, list[dict[str, Any]]]) -> None:
    """
    Initialize Streamlit session state with default values.

    Should be called once at app startup (in app.py).

    Args:
        reference_data: Loaded reference data from reference_loader
    """
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    if "prediction_inputs" not in st.session_state:
        st.session_state.prediction_inputs = {}

    if "last_prediction" not in st.session_state:
        st.session_state.last_prediction = None

    if "validation_errors" not in st.session_state:
        st.session_state.validation_errors = {}

    if "reference_data" not in st.session_state:
        st.session_state.reference_data = reference_data

    if "is_form_complete" not in st.session_state:
        st.session_state.is_form_complete = False


def get_current_page() -> int:
    """
    Get current page number.

    Returns:
        Current page (1-6)
    """
    return st.session_state.get("current_page", 1)


def set_current_page(page: int) -> None:
    """
    Set current page number.

    Args:
        page: Page number (1-6)
    """
    if page < 1:
        page = 1
    elif page > 6:
        page = 6
    st.session_state.current_page = page


def navigate_next() -> None:
    """Navigate to next page (increment current_page)."""
    current = get_current_page()
    set_current_page(current + 1)


def navigate_previous() -> None:
    """Navigate to previous page (decrement current_page)."""
    current = get_current_page()
    set_current_page(current - 1)


def reset_form() -> None:
    """
    Reset form to initial state.

    Clears:
    - prediction_inputs
    - last_prediction
    - validation_errors
    - Sets current_page to 1
    """
    st.session_state.prediction_inputs = {}
    st.session_state.last_prediction = None
    st.session_state.validation_errors = {}
    st.session_state.is_form_complete = False
    st.session_state.current_page = 1


def get_prediction_input(field_name: str) -> Any | None:
    """
    Get prediction input value for a field.

    Args:
        field_name: Name of the field (e.g., "lum", "dep")

    Returns:
        Field value if set, None otherwise
    """
    return st.session_state.prediction_inputs.get(field_name)


def set_prediction_input(field_name: str, value: Any) -> None:
    """
    Set prediction input value for a field.

    Args:
        field_name: Name of the field
        value: Value to store
    """
    st.session_state.prediction_inputs[field_name] = value


def get_all_prediction_inputs() -> dict[str, Any]:
    """
    Get all prediction inputs.

    Returns:
        Dictionary of field_name -> value
    """
    return st.session_state.prediction_inputs.copy()


def set_last_prediction(result: dict[str, Any] | None) -> None:
    """
    Store last prediction result.

    Args:
        result: Prediction result dict or None to clear
    """
    st.session_state.last_prediction = result


def get_last_prediction() -> dict[str, Any] | None:
    """
    Get last prediction result.

    Returns:
        Prediction result dict or None
    """
    return st.session_state.last_prediction


def set_validation_error(field_name: str, error_message: str) -> None:
    """
    Set validation error for a field.

    Args:
        field_name: Field name
        error_message: Error message to display
    """
    st.session_state.validation_errors[field_name] = error_message


def clear_validation_error(field_name: str) -> None:
    """
    Clear validation error for a field.

    Args:
        field_name: Field name
    """
    if field_name in st.session_state.validation_errors:
        del st.session_state.validation_errors[field_name]


def get_validation_error(field_name: str) -> str | None:
    """
    Get validation error for a field.

    Args:
        field_name: Field name

    Returns:
        Error message or None
    """
    return st.session_state.validation_errors.get(field_name)


def has_validation_errors() -> bool:
    """
    Check if there are any validation errors.

    Returns:
        True if there are validation errors, False otherwise
    """
    return len(st.session_state.validation_errors) > 0


def get_reference_data() -> dict[str, list[dict[str, Any]]]:
    """
    Get reference data from session state.

    Returns:
        Reference data dictionary
    """
    return st.session_state.reference_data


def update_form_complete_status() -> None:
    """
    Update is_form_complete flag based on current prediction_inputs.

    Checks if all 15 required fields are filled.
    """
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

    inputs = st.session_state.prediction_inputs
    st.session_state.is_form_complete = all(
        field in inputs and inputs[field] is not None for field in required_fields
    )


def is_form_complete() -> bool:
    """
    Check if form is complete (all 15 fields filled).

    Returns:
        True if all fields are filled, False otherwise
    """
    return st.session_state.get("is_form_complete", False)


def generate_recap_table(
    prediction_inputs: dict[str, Any], reference_data: dict[str, list[dict[str, Any]]]
) -> pd.DataFrame:
    """
    Generate recap table showing all filled prediction inputs.

    Args:
        prediction_inputs: Dictionary of field_name -> value
        reference_data: Loaded reference data from reference_loader

    Returns:
        DataFrame with columns: Champ, Code, Libellé, Page
        Sorted by page number for logical display
    """
    if not prediction_inputs:
        return pd.DataFrame(columns=["Champ", "Code", "Libellé", "Page"])

    rows = []

    for field_name, field_value in prediction_inputs.items():
        if field_value is None:
            continue

        field_label = validation.get_field_label(field_name)
        page_number = validation.get_field_page(field_name)

        try:
            value_label = reference_loader.get_label_for_code(
                reference_data, field_name, field_value
            )
        except (KeyError, ValueError):
            value_label = str(field_value)

        rows.append(
            {
                "Champ": field_label,
                "Code": str(field_value),
                "Libellé": value_label,
                "Page": page_number,
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(by="Page", ignore_index=True)

    return df
