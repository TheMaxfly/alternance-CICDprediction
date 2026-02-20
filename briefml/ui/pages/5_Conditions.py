"""
Page 5: Conditions

Fields: lum, atm, time_bucket
"""

import streamlit as st

from briefml.ui.lib import reference_loader, session_state


def render():
    """Render Page 5: Conditions form fields."""
    session_state.set_current_page(5)

    st.header("Page 5 : Conditions")
    st.caption("Conditions d'eclairage, meteorologiques et tranche horaire")

    ref_data = session_state.get_reference_data()

    # Field: Conditions d'eclairage (lum)
    st.subheader("Conditions d'eclairage")
    lum_options = reference_loader.get_dropdown_options(ref_data, "lum")
    current_lum = session_state.get_prediction_input("lum")

    lum_index = 0
    if current_lum:
        formatted_current = reference_loader.format_dropdown_option(
            current_lum,
            reference_loader.get_label_for_code(ref_data, "lum", current_lum),
        )
        if formatted_current in lum_options:
            lum_index = lum_options.index(formatted_current)

    lum_selected = st.selectbox(
        "Luminosite", options=lum_options, index=lum_index, key="lum_input"
    )
    if lum_selected:
        lum_code = reference_loader.parse_dropdown_value(lum_selected)
        session_state.set_prediction_input("lum", lum_code)

    lum_help = reference_loader.get_field_help(ref_data, "lum")
    if lum_help:
        with st.expander("ℹ️ Aide : Conditions d'eclairage"):
            st.write(lum_help["definition"])

    st.divider()

    # Field: Conditions atmospheriques (atm)
    st.subheader("Conditions atmospheriques")
    atm_options = reference_loader.get_dropdown_options(ref_data, "atm")
    current_atm = session_state.get_prediction_input("atm")

    atm_index = 0
    if current_atm:
        formatted_current = reference_loader.format_dropdown_option(
            current_atm,
            reference_loader.get_label_for_code(ref_data, "atm", current_atm),
        )
        if formatted_current in atm_options:
            atm_index = atm_options.index(formatted_current)

    atm_selected = st.selectbox(
        "Conditions atmospheriques",
        options=atm_options,
        index=atm_index,
        key="atm_input",
    )
    if atm_selected:
        atm_code = reference_loader.parse_dropdown_value(atm_selected)
        session_state.set_prediction_input("atm", atm_code)

    atm_help = reference_loader.get_field_help(ref_data, "atm")
    if atm_help:
        with st.expander("ℹ️ Aide : Conditions atmospheriques"):
            st.write(atm_help["definition"])

    st.divider()

    # Field: Tranche horaire (time_bucket)
    st.subheader("Tranche horaire")
    time_bucket_options = reference_loader.get_dropdown_options(ref_data, "time_bucket")
    current_time_bucket = session_state.get_prediction_input("time_bucket")

    time_bucket_index = 0
    if current_time_bucket is not None:
        formatted_current = reference_loader.format_dropdown_option(
            current_time_bucket,
            reference_loader.get_label_for_code(
                ref_data, "time_bucket", current_time_bucket
            ),
        )
        if formatted_current in time_bucket_options:
            time_bucket_index = time_bucket_options.index(formatted_current)

    time_bucket_selected = st.selectbox(
        "Plage horaire",
        options=time_bucket_options,
        index=time_bucket_index,
        key="time_bucket_input",
        help="Tranche horaire de l'accident",
    )
    if time_bucket_selected:
        time_bucket_code = reference_loader.parse_dropdown_value(time_bucket_selected)
        session_state.set_prediction_input("time_bucket", time_bucket_code)

    time_bucket_help = reference_loader.get_field_help(ref_data, "time_bucket")
    if time_bucket_help:
        with st.expander("ℹ️ Aide : Tranche horaire"):
            st.write(time_bucket_help["definition"])

    st.divider()

    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Precedent", width="stretch"):
            session_state.navigate_previous()
            st.rerun()
    with col2:
        if st.button("Suivant →", width="stretch", type="primary"):
            session_state.navigate_next()
            session_state.update_form_complete_status()
            st.rerun()

    st.caption("Page 5/6 • 3 champs sur cette page")


# Standalone execution
if __name__ == "__main__":
    st.set_page_config(
        page_title="Page 5 - Conditions", page_icon="🌤️", layout="centered"
    )
    if "reference_data" not in st.session_state:
        reference_data = reference_loader.load_reference_data()
        session_state.initialize_state(reference_data)
    render()
