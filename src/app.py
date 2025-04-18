import streamlit as st
import ui_elements

st.title("Smart Healthcare System")
st.markdown("---")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_details' not in st.session_state:
    st.session_state.user_details = None

if not st.session_state.logged_in:
    ui_elements.show_login_or_register_prompts()

if st.session_state.logged_in:
    ui_elements.show_dashboard()
