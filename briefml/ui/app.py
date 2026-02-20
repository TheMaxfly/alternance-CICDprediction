"""
Streamlit app for accident severity prediction.

This is the main entry point for the Streamlit interface.
It provides a multi-page form to collect 15 input variables
and call the FastAPI prediction endpoint.

Architecture:
- Uses briefml.ui.lib modules for session state, validation, and API calls
- Loads reference data from data/ref_options.json
- Implements constitution principle III (API-First)
"""

import logging

import streamlit as st

from briefml.ui.lib import reference_loader, session_state

# Configure logging (T095)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# Configure Streamlit page
st.set_page_config(
    page_title="Prediction de Gravite d'Accidents",
    page_icon="🚗",
    layout="centered",
    initial_sidebar_state="expanded",
)


# T017: Load reference data on initialization
@st.cache_data
def load_reference_data():
    """Load reference data from JSON file (cached)."""
    try:
        return reference_loader.load_reference_data()
    except Exception as e:
        st.error(f"Erreur lors du chargement des donnees de reference: {e}")
        st.stop()


# Initialize reference data
reference_data = load_reference_data()

# Initialize session state
session_state.initialize_state(reference_data)


# Sidebar: Navigation and controls
with st.sidebar:
    st.header("Navigation")

    # T019: Progress indicator showing "Page X/6"
    current_page = session_state.get_current_page()
    st.progress(current_page / 6, text=f"**Page {current_page}/6**")

    st.divider()

    # T018: "Nouvelle prediction" button that resets session state
    if st.button("Nouvelle prediction", width="stretch"):
        session_state.reset_form()
        st.rerun()

    st.divider()

    # Show completion status
    completion = session_state.is_form_complete()
    if completion:
        st.success("Formulaire complet")
    else:
        filled_count = len(
            [
                f
                for f in [
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
                if session_state.get_prediction_input(f) is not None
            ]
        )
        st.info(f"{filled_count}/15 champs remplis")


# Main content area
st.title("Prediction de Gravite d'Accidents")
st.caption(
    "Interface Streamlit pour la prediction de la gravite des accidents de la route"
)

# Import page render functions (numeric-prefixed filenames require importlib)
import importlib  # noqa: E402

_page1 = importlib.import_module("briefml.ui.pages.1_Contexte_Route")
_page2 = importlib.import_module("briefml.ui.pages.2_Infrastructure")
_page3 = importlib.import_module("briefml.ui.pages.3_Collision")
_page4 = importlib.import_module("briefml.ui.pages.4_Conducteur")
_page5 = importlib.import_module("briefml.ui.pages.5_Conditions")
_page6 = importlib.import_module("briefml.ui.pages.6_Recap_Prediction")

# Display current page content
if current_page == 1:
    _page1.render()
elif current_page == 2:
    _page2.render()
elif current_page == 3:
    _page3.render()
elif current_page == 4:
    _page4.render()
elif current_page == 5:
    _page5.render()
elif current_page == 6:
    _page6.render()
else:
    st.error(f"Page invalide : {current_page}")


# Footer
st.divider()
st.caption("Application developpee selon l'architecture Speckit")
