import streamlit as st
import backend_queries

def show_login_or_register_prompts():
    st.subheader("Choose Your Option")

    option = st.radio("", ("Login", "Register"), index=0, horizontal=True)
    st.markdown("---")

    if option == "Login":
        st.subheader("Login Form")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_submit_button = st.button("Login")

        if login_submit_button:
            auth_result = backend_queries.authenticate(email, password)
            if auth_result:
                st.session_state.logged_in = True
                st.session_state.user_details = auth_result
                st.success(f"Login successful as {auth_result[3]}!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    if option == "Register":
        st.subheader("Register Form")
        name = st.text_input("Name")
        email = st.text_input("Email")
        role = st.selectbox("Select Role", ["Patient", "Doctor", "Staff", "Nurse"])
        password = st.text_input("Password", type="password")
        register_submit_button = st.button("Register")

        if register_submit_button:
            if backend_queries.register(name, email, role, password):
                st.success("Successfully Registered!")
            else:
                st.error("Unable to Register... :(")

def show_dashboard():
    user_details = st.session_state.user_details

    st.sidebar.title(f"Welcome, {user_details[1]}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_details = None
        st.rerun()

    role = user_details[3]
    st.markdown(f"# *{role}* Dashboard")

    if role == "Doctor":
        st.text("")
        st.text("Welcome doctor! View your functions below.")

    elif role == "Patient":
        st.text("")
        st.text("Welcome patient! View your functions below.")

    elif role == "Staff":
        st.text("")
        st.text("Welcome staff! View your functions below.")

    elif role == "Nurse":
        st.text("")
        st.text("Welcome nurse! View your functions below.")

    else:
        st.warning("Unknown role detected.")

    st.markdown("---")
