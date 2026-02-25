"""
Page 1: Contexte Route

Fields: dep, agg, catr, vma_bucket
"""

import streamlit as st

from briefml.ui.lib import reference_loader, session_state


def render():
    """Render Page 1: Contexte Route form fields."""
    # Header
    st.header("Page 1 : Contexte Route")
    st.caption("Informations sur le departement, la route et l'agglomeration")

    # Get reference data
    ref_data = session_state.get_reference_data()

    # Field 1: Departement (dep)
    st.subheader("Departement")
    dep_options = reference_loader.get_dropdown_options(ref_data, "dep")
    current_dep = session_state.get_prediction_input("dep")

    # Find index for current value
    dep_index = 0
    if current_dep:
        formatted_current = reference_loader.format_dropdown_option(
            current_dep,
            reference_loader.get_label_for_code(ref_data, "dep", current_dep),
        )
        if formatted_current in dep_options:
            dep_index = dep_options.index(formatted_current)

    dep_selected = st.selectbox(
        "Departement", options=dep_options, index=dep_index, key="dep_input"
    )
    if dep_selected:
        dep_code = reference_loader.parse_dropdown_value(dep_selected)
        session_state.set_prediction_input("dep", dep_code)

    # Help expander for dep
    dep_help = reference_loader.get_field_help(ref_data, "dep")
    if dep_help:
        with st.expander("ℹ️ Aide : Departement"):
            st.write(dep_help["definition"])

    st.divider()

    # Field 2: Agglomeration (agg)
    st.subheader("Agglomeration")
    agg_options = reference_loader.get_dropdown_options(ref_data, "agg")
    current_agg = session_state.get_prediction_input("agg")

    agg_index = 0
    if current_agg:
        formatted_current = reference_loader.format_dropdown_option(
            current_agg,
            reference_loader.get_label_for_code(ref_data, "agg", current_agg),
        )
        if formatted_current in agg_options:
            agg_index = agg_options.index(formatted_current)

    agg_selected = st.selectbox(
        "Agglomeration",
        options=agg_options,
        index=agg_index,
        key="agg_input",
        help="Accident en ou hors agglomeration",
    )
    if agg_selected:
        agg_code = reference_loader.parse_dropdown_value(agg_selected)
        session_state.set_prediction_input("agg", agg_code)

    agg_help = reference_loader.get_field_help(ref_data, "agg")
    if agg_help:
        with st.expander("ℹ️ Aide : Agglomeration"):
            st.write(agg_help["definition"])

    st.divider()

    # Field 3: Categorie de route (catr)
    st.subheader("Categorie de route")
    catr_options = reference_loader.get_dropdown_options(ref_data, "catr")
    current_catr = session_state.get_prediction_input("catr")

    catr_index = 0
    if current_catr:
        formatted_current = reference_loader.format_dropdown_option(
            current_catr,
            reference_loader.get_label_for_code(ref_data, "catr", current_catr),
        )
        if formatted_current in catr_options:
            catr_index = catr_options.index(formatted_current)

    catr_selected = st.selectbox(
        "Categorie de route", options=catr_options, index=catr_index, key="catr_input"
    )
    if catr_selected:
        catr_code = reference_loader.parse_dropdown_value(catr_selected)
        session_state.set_prediction_input("catr", catr_code)

    catr_help = reference_loader.get_field_help(ref_data, "catr")
    if catr_help:
        with st.expander("ℹ️ Aide : Categorie de route"):
            st.write(catr_help["definition"])

    st.divider()

    # Field 4: VMA bucket
    st.subheader("Vitesse maximale autorisee")
    vma_options = reference_loader.get_dropdown_options(ref_data, "vma_bucket")
    current_vma = session_state.get_prediction_input("vma_bucket")

    vma_index = 0
    if current_vma:
        formatted_current = reference_loader.format_dropdown_option(
            current_vma,
            reference_loader.get_label_for_code(ref_data, "vma_bucket", current_vma),
        )
        if formatted_current in vma_options:
            vma_index = vma_options.index(formatted_current)

    vma_selected = st.selectbox(
        "Vitesse maximale autorisee",
        options=vma_options,
        index=vma_index,
        key="vma_input",
    )
    if vma_selected:
        vma_code = reference_loader.parse_dropdown_value(vma_selected)
        session_state.set_prediction_input("vma_bucket", vma_code)

    vma_help = reference_loader.get_field_help(ref_data, "vma_bucket")
    if vma_help:
        with st.expander("ℹ️ Aide : Vitesse maximale autorisee"):
            st.write(vma_help["definition"])

    st.divider()

    # Navigation buttons
    def _go_next():
        session_state.navigate_next()
        session_state.update_form_complete_status()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.button("← Precedent", disabled=True, key="nav_prev_1")

    with col2:
        st.button("Suivant →", type="primary", key="nav_next_1", on_click=_go_next)

    st.caption("Page 1/6 • 4 champs sur cette page")


# Standalone execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="Page 1 - Contexte Route", page_icon="🛣️", layout="centered"
    )
    if "reference_data" not in st.session_state:
        reference_data = reference_loader.load_reference_data()
        session_state.initialize_state(reference_data)
    render()
