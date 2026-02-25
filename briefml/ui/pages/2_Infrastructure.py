"""
Page 2: Infrastructure

Fields: int, circ
"""

import streamlit as st

from briefml.ui.lib import reference_loader, session_state


def render():
    """Render Page 2: Infrastructure form fields."""
    st.header("Page 2 : Infrastructure")
    st.caption("Type d'intersection et regime de circulation")

    ref_data = session_state.get_reference_data()

    # Field: Type d'intersection (int)
    st.subheader("Type d'intersection")
    int_options = reference_loader.get_dropdown_options(ref_data, "int")
    current_int = session_state.get_prediction_input("int")

    int_index = 0
    if current_int:
        formatted_current = reference_loader.format_dropdown_option(
            current_int,
            reference_loader.get_label_for_code(ref_data, "int", current_int),
        )
        if formatted_current in int_options:
            int_index = int_options.index(formatted_current)

    int_selected = st.selectbox(
        "Type d'intersection", options=int_options, index=int_index, key="int_input"
    )
    if int_selected:
        int_code = reference_loader.parse_dropdown_value(int_selected)
        session_state.set_prediction_input("int", int_code)

    int_help = reference_loader.get_field_help(ref_data, "int")
    if int_help:
        with st.expander("ℹ️ Aide : Type d'intersection"):
            st.write(int_help["definition"])

    st.divider()

    # Field: Regime de circulation (circ)
    st.subheader("Regime de circulation")
    circ_options = reference_loader.get_dropdown_options(ref_data, "circ")
    current_circ = session_state.get_prediction_input("circ")

    circ_index = 0
    if current_circ:
        formatted_current = reference_loader.format_dropdown_option(
            current_circ,
            reference_loader.get_label_for_code(ref_data, "circ", current_circ),
        )
        if formatted_current in circ_options:
            circ_index = circ_options.index(formatted_current)

    circ_selected = st.selectbox(
        "Regime de circulation",
        options=circ_options,
        index=circ_index,
        key="circ_input",
    )
    if circ_selected:
        circ_code = reference_loader.parse_dropdown_value(circ_selected)
        session_state.set_prediction_input("circ", circ_code)

    circ_help = reference_loader.get_field_help(ref_data, "circ")
    if circ_help:
        with st.expander("ℹ️ Aide : Regime de circulation"):
            st.write(circ_help["definition"])

    st.divider()

    # Navigation
    def _go_prev():
        session_state.navigate_previous()

    def _go_next():
        session_state.navigate_next()
        session_state.update_form_complete_status()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("← Precedent", key="nav_prev_2", on_click=_go_prev)
    with col2:
        st.button("Suivant →", type="primary", key="nav_next_2", on_click=_go_next)

    st.caption("Page 2/6 • 2 champs sur cette page")


# Standalone execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="Page 2 - Infrastructure", page_icon="🚦", layout="centered"
    )
    if "reference_data" not in st.session_state:
        reference_data = reference_loader.load_reference_data()
        session_state.initialize_state(reference_data)
    render()
