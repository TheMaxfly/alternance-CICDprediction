"""
Page 4: Conducteur

Fields: driver_age_bucket, driver_trajet_family, catv_family_4
"""

import streamlit as st

from briefml.ui.lib import reference_loader, session_state


def render():
    """Render Page 4: Conducteur form fields."""
    st.header("Page 4 : Conducteur et Vehicule")
    st.caption("Informations sur le conducteur et le type de vehicule")

    ref_data = session_state.get_reference_data()

    # Field: Classe d'age conducteur
    st.subheader("Classe d'age du conducteur")
    age_options = reference_loader.get_dropdown_options(ref_data, "driver_age_bucket")
    current_age = session_state.get_prediction_input("driver_age_bucket")

    age_index = 0
    if current_age:
        formatted_current = reference_loader.format_dropdown_option(
            current_age,
            reference_loader.get_label_for_code(
                ref_data, "driver_age_bucket", current_age
            ),
        )
        if formatted_current in age_options:
            age_index = age_options.index(formatted_current)

    age_selected = st.selectbox(
        "Classe d'age", options=age_options, index=age_index, key="age_input"
    )
    if age_selected:
        age_code = reference_loader.parse_dropdown_value(age_selected)
        session_state.set_prediction_input("driver_age_bucket", age_code)

    age_help = reference_loader.get_field_help(ref_data, "driver_age_bucket")
    if age_help:
        with st.expander("ℹ️ Aide : Classe d'age du conducteur"):
            st.write(age_help["definition"])

    st.divider()

    # Field: Famille de trajet
    st.subheader("Type de trajet")
    trajet_options = reference_loader.get_dropdown_options(
        ref_data, "driver_trajet_family"
    )
    current_trajet = session_state.get_prediction_input("driver_trajet_family")

    trajet_index = 0
    if current_trajet:
        formatted_current = reference_loader.format_dropdown_option(
            current_trajet,
            reference_loader.get_label_for_code(
                ref_data, "driver_trajet_family", current_trajet
            ),
        )
        if formatted_current in trajet_options:
            trajet_index = trajet_options.index(formatted_current)

    trajet_selected = st.selectbox(
        "Type de trajet", options=trajet_options, index=trajet_index, key="trajet_input"
    )
    if trajet_selected:
        trajet_code = reference_loader.parse_dropdown_value(trajet_selected)
        session_state.set_prediction_input("driver_trajet_family", trajet_code)

    trajet_help = reference_loader.get_field_help(ref_data, "driver_trajet_family")
    if trajet_help:
        with st.expander("ℹ️ Aide : Type de trajet"):
            st.write(trajet_help["definition"])

    st.divider()

    # Field: Famille de vehicule
    st.subheader("Famille de vehicule")
    catv_options = reference_loader.get_dropdown_options(ref_data, "catv_family_4")
    current_catv = session_state.get_prediction_input("catv_family_4")

    catv_index = 0
    if current_catv:
        formatted_current = reference_loader.format_dropdown_option(
            current_catv,
            reference_loader.get_label_for_code(
                ref_data, "catv_family_4", current_catv
            ),
        )
        if formatted_current in catv_options:
            catv_index = catv_options.index(formatted_current)

    catv_selected = st.selectbox(
        "Famille de vehicule", options=catv_options, index=catv_index, key="catv_input"
    )
    if catv_selected:
        catv_code = reference_loader.parse_dropdown_value(catv_selected)
        session_state.set_prediction_input("catv_family_4", catv_code)

    catv_help = reference_loader.get_field_help(ref_data, "catv_family_4")
    if catv_help:
        with st.expander("ℹ️ Aide : Famille de vehicule"):
            st.write(catv_help["definition"])

    st.divider()

    # Navigation
    def _go_prev():
        session_state.navigate_previous()

    def _go_next():
        session_state.navigate_next()
        session_state.update_form_complete_status()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("← Precedent", key="nav_prev_4", on_click=_go_prev)
    with col2:
        st.button("Suivant →", type="primary", key="nav_next_4", on_click=_go_next)

    st.caption("Page 4/6 • 3 champs sur cette page")


# Standalone execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="Page 4 - Conducteur", page_icon="👤", layout="centered"
    )
    if "reference_data" not in st.session_state:
        reference_data = reference_loader.load_reference_data()
        session_state.initialize_state(reference_data)
    render()
