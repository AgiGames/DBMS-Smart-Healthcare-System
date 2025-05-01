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

        # patient details
        age = 0
        gender = ""
        address = ""
        contact = ""
        blood_type = ""

        # doctor details
        contact = ""
        specialization = ""

        if "show_doctor_registration_form" not in st.session_state:
            st.session_state.show_doctor_registration_form = False
        if role == "Doctor":
            st.session_state.show_patient_registration_form = False
            st.session_state.show_doctor_registration_form = True
        
        if "show_patient_registration_form" not in st.session_state:
            st.session_state.show_patient_registration_form = False
        if role == "Patient":
            st.session_state.show_patient_registration_form = True
            st.session_state.show_doctor_registration_form = False
        
        if st.session_state.show_doctor_registration_form:
            specialization = st.text_input("Specialization")
            contact = st.number_input("Contact Number", min_value=1000000000, max_value=9999999999, step=1, format="%d")

        if st.session_state.show_patient_registration_form:
            age = st.number_input("Age", 0, 200)
            gender = st.selectbox("Select Gender", ["Male", "Female", "Other"])
            address = st.text_input("address")
            contact = st.number_input("Contact Number", min_value=1000000000, max_value=9999999999, step=1, format="%d")
            blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])


        register_submit_button = st.button("Register")
        if register_submit_button:
            user_successfully_registered, user_id = backend_queries.register(name, email, role, password)
            if user_successfully_registered:
                st.success("Successfully Registered User!")
            else:
                st.error("Unable to Register User... :(")
            
            if st.session_state.show_patient_registration_form:
                if backend_queries.register_patient(name, age, gender, address, str(contact), blood_type, user_id):
                    st.success("Successfully Registered Patient!")
                else:
                    st.error("Unable to Register Patient... :(")
                    backend_queries.remove_user(user_id)

            if st.session_state.show_doctor_registration_form:
                if backend_queries.register_doctor(name, specialization, str(contact), email, user_id):
                    st.success("Successfully Registered Doctor!")
                else:
                    st.error("Unable to Register Doctor... :(")
                    backend_queries.remove_user(user_id)


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

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            book_appointment_button = st.button("Book Appointment")
        with col2:
            show_medical_records_button = st.button("Show Medical Records")
        with col3:
            show_prescription_medicines_button = st.button("Show Prescription")

        if "book_appointment" not in st.session_state:
            st.session_state.book_appointment = False
        if book_appointment_button:
            st.session_state.book_appointment = True
            st.session_state.show_medical_records = False
            st.session_state.show_prescription_medicines = False

        if "show_medical_records" not in st.session_state:
            st.session_state.show_medical_records = False
        if show_medical_records_button:
            st.session_state.book_appointment = False
            st.session_state.show_medical_records = True

        if "show_prescription_medicines" not in st.session_state:
            st.session_state.show_prescription_medicines = False
        if show_prescription_medicines_button:
            st.session_state.book_appointment = False
            st.session_state.show_prescription_medicines = True

        if st.session_state.book_appointment:
            st.text("Available Doctors and their Specializations")

            patient_id = backend_queries.get_patient_id(user_id)
            available_doctors = backend_queries.get_doctors_available_for_appointment()
            
            for doctor in available_doctors:
                name = doctor[0]
                specialization = doctor[1]
                contact = doctor[2]
                email = doctor[3]
                doctor_id = doctor[4]  # Make sure this key exists

                cols = st.columns([2, 2, 2, 2, 4])
                cols[0].write(name)
                cols[1].write(specialization)
                cols[2].write(contact)
                cols[3].write(email)

                # Use a form to handle button clicks per row
                with cols[4].form(key=f"form_{doctor_id}"):
                    submit = st.form_submit_button("Book Appointment")
                    if submit:
                        # Send to backend (custom logic here)
                        if backend_queries.book_appointment(patient_id, doctor_id):
                            st.success(f"Appointment booked with Dr. {name}")
                        else:
                            st.error(f"Unable to Book Appointment! :(")
        
        if st.session_state.show_medical_records:
            st.text("Your Medical Records")

            patient_id = backend_queries.get_patient_id(user_id)
            medical_records = backend_queries.get_medical_records(patient_id)

            df_medical_records = pd.DataFrame(medical_records, columns = [
                                                        "RecordID",
                                                        "Diagnosis",
                                                        "Medical Record Date",
                                                        "PrescriptionID",
                                                        "PatientID",
                                                        "Patient Name",
                                                        "DoctorID",
                                                        "Doctor Name",
                                                        "Prescription Date"]
                                                        )
            st.dataframe(df_medical_records, use_container_width=True, hide_index=True)

        if st.session_state.show_prescription_medicines:
            prescription_id = st.number_input("Enter Prescription ID to See Medicines", min_value=0, step=1)
            medicines = backend_queries.get_medicines_of_prescriptions(prescription_id)
            print(medicines)

            df_medicines = pd.DataFrame(medicines, columns=["Medicine ID", "Name", "Dosage"])
            st.dataframe(df_medicines, use_container_width=True, hide_index=True)



    elif role == "Staff":
        st.text("")
        st.text("Welcome staff! View your functions below.")




    elif role == "Nurse":
        st.text("")
        st.text("Welcome nurse! View your functions below.")




    else:
        st.warning("Unknown role detected.")




    st.markdown("---")
