import streamlit as st
import backend_queries
import pandas as pd

def show_login_or_register_prompts():
    st.subheader("Choose Your Option")

    option = st.radio("Login or Register?", ("Login", "Register"), index=0, horizontal=True)
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

    user_id = user_details[0]
    name = user_details[1]
    email = user_details[2]
    role = user_details[3]
    st.markdown(f"# *{role}* Dashboard")




    if role == "Doctor":
        st.text("")
        st.text("Welcome doctor! View your functions below.")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            availability_button = st.button("Availability")
        with col2:
            show_appointments_button = st.button("Appointments")

        if "show_availability_form" not in st.session_state:
            st.session_state.show_availability_form = False
        if availability_button:
            st.session_state.show_availability_form = True
            st.session_state.show_appointments = False

        if "show_appointments" not in st.session_state:
            st.session_state.show_appointments = False
        if show_appointments_button:
            st.session_state.show_appointments = True
            st.session_state.show_availability_form = False

        if st.session_state.show_availability_form:
            availability = backend_queries.get_doctor_availability(user_id)
            st.write(f"Current Availability: {availability}")

            if "availability_choice" not in st.session_state:
                st.session_state.availability_choice = availability

            st.session_state.availability_choice = st.radio(
                "Change Availability",
                ("Available", "Not Available"),
                index=0 if st.session_state.availability_choice == "Available" else 1,
                horizontal=True,
                key="availability_radio"
            )

            if st.button("Submit"):
                backend_queries.set_doctor_availability(user_id, st.session_state.availability_choice)
                st.success(f"Availability changed to: {st.session_state.availability_choice}")
                import time
                time.sleep(2)
                st.session_state.show_availability_form = False
                st.rerun()

        if st.session_state.show_appointments:
            doctor_id = backend_queries.get_doctor_id(user_id)
            appointments = backend_queries.get_appointments(doctor_id)

            if appointments:
                df = pd.DataFrame(appointments, columns=[
                    "Appointment ID", "Patient ID", "Patient Name", "Doctor ID",
                    "Doctor Name", "Date & Time", "Status"
                ])
                
                st.subheader("Appointments")
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.subheader("Set Appointment Completion")
                appointment_id = st.number_input("Enter Appointment ID", min_value=0, step=1)
                submit_appointment_completion_button = st.button("Submit Appointment to Set it As Complete")
                backend_queries.set_appointment_as_completed(appointment_id)


            else:
                st.info("No appointments found.")

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
