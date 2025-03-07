import streamlit as st

def init_session_state():
    """Initialize shared session state variables if they are not already set."""
    if "pdf_data" not in st.session_state:
        st.session_state.pdf_data = None
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = ""
    if "resume_content" not in st.session_state:
        st.session_state.resume_content = ""
    if "application_id" not in st.session_state:
        st.session_state.application_id = None
    if "pdf_downloaded" not in st.session_state:
        st.session_state.pdf_downloaded = False
