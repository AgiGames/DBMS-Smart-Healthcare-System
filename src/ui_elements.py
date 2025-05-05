import streamlit as st
import backend_queries
import pandas as pd
import datetime
from datetime import date


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
        role = st.selectbox("Select Role", ["Patient", "Doctor", "Staff"])
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

        # staff details
        contact = ""
        shift_timing = ""

        if "show_doctor_registration_form" not in st.session_state:
            st.session_state.show_doctor_registration_form = False
        if role == "Doctor":
            st.session_state.show_patient_registration_form = False
            st.session_state.show_doctor_registration_form = True
            st.session_state.show_staff_registration_from = False
        
        if "show_patient_registration_form" not in st.session_state:
            st.session_state.show_patient_registration_form = False
        if role == "Patient":
            st.session_state.show_patient_registration_form = True
            st.session_state.show_doctor_registration_form = False
            st.session_state.show_staff_registration_from = False

        if "show_staff_registration_from" not in st.session_state:
            st.session_state.show_staff_registration_from = False
        if role == "Staff":
            st.session_state.show_patient_registration_form = False
            st.session_state.show_doctor_registration_form = False
            st.session_state.show_staff_registration_from = True
        
        if st.session_state.show_doctor_registration_form:
            specialization = st.text_input("Specialization")
            contact = st.number_input("Contact Number", min_value=1000000000, max_value=9999999999, step=1, format="%d")

        if st.session_state.show_patient_registration_form:
            age = st.number_input("Age", 0, 200)
            gender = st.selectbox("Select Gender", ["Male", "Female", "Other"])
            address = st.text_input("address")
            contact = st.number_input("Contact Number", min_value=1000000000, max_value=9999999999, step=1, format="%d")
            blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

        if st.session_state.show_staff_registration_from:
            contact = st.number_input("Contact Number", min_value=1000000000, max_value=9999999999, step=1, format="%d")
            shift_timing = st.radio("Shift Time", ("Morning", "Evening"))

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

            if st.session_state.show_staff_registration_from:
                if backend_queries.register_staff(name, contact, shift_timing, user_id):
                    st.success("Successfully Registered Staff!")
                else:
                    st.error("Unable to Register Staff... :(")
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
    
    st.markdown(f"# {role} Dashboard")

    if role == "Doctor":

        doctor_id = backend_queries.get_doctor_id(user_id)

        st.text("")
        st.text("Welcome doctor! View your functions below.")

        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            availability_button = st.button("Availability")
        with col2:
            show_appointments_button = st.button("Appointments")
        with col3:
            write_prescription_button = st.button("Write Prescription")

        # Session states for forms
        if "show_availability_form" not in st.session_state:
            st.session_state.show_availability_form = False
        if availability_button:
            st.session_state.show_availability_form = True
            st.session_state.show_appointments = False
            st.session_state.show_prescription_form = False

        if "show_appointments" not in st.session_state:
            st.session_state.show_appointments = False
        if show_appointments_button:
            st.session_state.show_appointments = True
            st.session_state.show_availability_form = False
            st.session_state.show_prescription_form = False

        if "show_prescription_form" not in st.session_state:
            st.session_state.show_prescription_form = False
        if write_prescription_button:
            st.session_state.show_prescription_form = True
            st.session_state.show_appointments = False
            st.session_state.show_availability_form = False

        # Handling Availability Form
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

        # Handling Prescription Form
        if st.session_state.show_prescription_form:
            patient_id = st.number_input("Enter Patient ID", min_value=1, step=1)
            diagnosis = st.text_area("Diagnosis")
            instructions = st.text_area("Instructions")

            available_medicines = backend_queries.get_all_medicine_names()
            medicine_options = {name: med_id for med_id, name in available_medicines}
            selected_names = st.multiselect("Select medicines:", options=list(medicine_options.keys()))

            prescription_date = st.date_input("Date", value=date.today())

            if st.button("Submit Prescription"):
                if patient_id and diagnosis and selected_names:
                    selected_ids = [medicine_options[name] for name in selected_names]
                    backend_queries.write_prescription(doctor_id, patient_id, instructions, prescription_date, selected_ids, diagnosis)
                    st.success("Prescription written successfully!")
                    st.session_state.show_prescription_form = False
                    st.rerun()
                else:
                    st.warning("Please fill in all fields to write a prescription.")

        # Handling Appointments (the code you already provided)
        if st.session_state.show_appointments:
            doctor_id = backend_queries.get_doctor_id(user_id)

            from_date = st.date_input(
                "Select a from date:",
                value=date.today()
            )

            to_date = st.date_input(
                "Select a to date:",
                value=date.today()
            )

            status_choice = st.radio("Choose which appointments you want to see:", ("Completed", "Not Completed", "Both"))
            count = st.radio("Count the number of chosen appointments?", ("True", "False"))

            appointments = ()
            if status_choice == "Both":
                appointments = backend_queries.get_appointments(doctor_id, from_date, to_date)
            else:
                appointments = backend_queries.get_specific_appointments(doctor_id, from_date, to_date, status_choice)

            if appointments:
                df = pd.DataFrame(appointments, columns=[
                    "Appointment ID", "Patient ID", "Patient Name", "Doctor ID",
                    "Doctor Name", "Date & Time", "Status"
                ])
                
                st.subheader("Appointments")
                st.dataframe(df, use_container_width=True, hide_index=True)

                if count == "True":
                    st.markdown(f"Number of Appointments: {len(df)}")

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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            book_appointment_button = st.button("Book Appointment")
        with col2:
            show_medical_records_button = st.button("Show Medical Records")
        with col3:
            show_prescription_medicines_button = st.button("Show Prescription")
        with col4:
            show_lab_tests_button = st.button("Show Lab Tests")                

        if "book_appointment" not in st.session_state:
                st.session_state.book_appointment = False
        if book_appointment_button:
            st.session_state.book_appointment = True
            st.session_state.show_medical_records = False
            st.session_state.show_prescription_medicines = False
            st.session_state.show_lab_tests = False  # Ensure lab tests section is hidden when booking appointment

        if "show_medical_records" not in st.session_state:
            st.session_state.show_medical_records = False
        if show_medical_records_button:
            st.session_state.book_appointment = False
            st.session_state.show_medical_records = True
            st.session_state.show_lab_tests = False  # Ensure lab tests section is hidden when viewing records

        if "show_prescription_medicines" not in st.session_state:
            st.session_state.show_prescription_medicines = False
        if show_prescription_medicines_button:
            st.session_state.book_appointment = False
            st.session_state.show_prescription_medicines = True
            st.session_state.show_lab_tests = False  # Ensure lab tests section is hidden when viewing prescriptions

        if "show_lab_tests" not in st.session_state:
            st.session_state.show_lab_tests = False
        if show_lab_tests_button:
            st.session_state.book_appointment = False
            st.session_state.show_medical_records = False
            st.session_state.show_prescription_medicines = False
            st.session_state.show_lab_tests = True

        if st.session_state.book_appointment:
            st.text("Available Doctors and their Specializations")

            patient_id = backend_queries.get_patient_id(user_id)
            available_doctors = backend_queries.get_doctors_available_for_appointment()
            
            for doctor in available_doctors:
                name = doctor[0]
                specialization = doctor[1]
                contact = doctor[2]
                email = doctor[3]
                doctor_id = doctor[4]

                cols = st.columns([2, 2, 2, 2, 4])
                cols[0].write(name)
                cols[1].write(specialization)
                cols[2].write(contact)
                cols[3].write(email)

                with cols[4].form(key=f"form_{doctor_id}"):
                    submit = st.form_submit_button("Book Appointment")
                    if submit:
                        if backend_queries.book_appointment(patient_id, doctor_id):
                            st.success(f"Appointment booked with Dr. {name}")
                        else:
                            st.error(f"Unable to Book Appointment! :(")
        
        if st.session_state.show_medical_records:
            st.text("Your Medical Records")

            patient_id = backend_queries.get_patient_id(user_id)

            col1, col2 = st.columns(2)

            with col1:
                medical_records_from_date = st.date_input(
                    "Select a from date for medical records:",
                    value=date.today()
                )

            with col2:
                medical_records_to_date = st.date_input(
                    "Select a to date for medical records:",
                    value=date.today()
                )

            with col1:
                prescriptions_from_date = st.date_input(
                    "Select a from date for prescriptions:",
                    value=date.today()
                )

            with col2:
                prescriptions_to_date = st.date_input(
                    "Select a to date for prescriptions:",
                    value=date.today()
                )

            medical_records = backend_queries.get_medical_records(patient_id, medical_records_from_date, medical_records_to_date,
                                                                  prescriptions_from_date, prescriptions_to_date)

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

            df_medicines = pd.DataFrame(medicines, columns=["Medicine ID", "Name", "Dosage"])
            st.dataframe(df_medicines, use_container_width=True, hide_index=True)

        if st.session_state.show_lab_tests:
            st.subheader("Your Lab Test Results")

            patient_id = backend_queries.get_patient_id(user_id)

            # Add date inputs for filtering
            col1, col2 = st.columns(2)
            with col1:
                from_date = st.date_input("From Date", value=date(2024, 1, 1))
            with col2:
                to_date = st.date_input("To Date", value=date.today())

            # Ensure from_date is not after to_date
            if from_date > to_date:
                st.error("From Date cannot be after To Date.")
            else:
                # Fetch lab tests within the selected date range
                lab_tests = backend_queries.get_lab_tests_for_patient(patient_id, from_date, to_date)

                if lab_tests:
                    df_lab_tests = pd.DataFrame(lab_tests, columns=["TestID", "PatientID", "DoctorID", "TestType", "Result", "DateTime"])
                    st.dataframe(df_lab_tests, use_container_width=True, hide_index=True)
                else:
                    st.info("No lab tests found for the selected date range.")




    elif role == "Staff":
        st.text("")
        st.text("Welcome staff! View your functions below.")

        # Staff Functions: Manage patients and appointments
        st.markdown("---")

        staff_id = backend_queries.get_staff_id(user_id)

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            view_shift_schedule_button = st.button("View Shift Schedule")
        with col2:
            view_medicine_inventory_button = st.button("View Medicine Inventory")
        with col3:
            add_new_medicine_button = st.button("Add New Medicine")
        with col4:
            change_quantity_of_medicine_button = st.button("Change Medicine Quantity")
        with col5:
            assign_patient_to_room_button = st.button("Assign Patient to Room")
        with col6:
            free_room_button = st.button("Free Room")

        # Reset session states on button presses
        if "view_shift_schedule" not in st.session_state:
            st.session_state.view_shift_schedule = False
        if view_shift_schedule_button:
            st.session_state.view_shift_schedule = True
            st.session_state.view_medicine_inventory = False
            st.session_state.add_new_medicine = False
            st.session_state.change_quantity_of_medicine = False
            st.session_state.assign_patient_to_room = False
            st.session_state.free_room = False

        if "view_medicine_inventory" not in st.session_state:
            st.session_state.view_medicine_inventory = False
        if view_medicine_inventory_button:
            st.session_state.view_shift_schedule = False
            st.session_state.view_medicine_inventory = True
            st.session_state.add_new_medicine = False
            st.session_state.change_quantity_of_medicine = False
            st.session_state.assign_patient_to_room = False
            st.session_state.free_room = False

        if "add_new_medicine" not in st.session_state:
            st.session_state.add_new_medicine = False
        if add_new_medicine_button:
            st.session_state.view_shift_schedule = False
            st.session_state.view_medicine_inventory = False
            st.session_state.add_new_medicine = True
            st.session_state.change_quantity_of_medicine = False
            st.session_state.assign_patient_to_room = False
            st.session_state.free_room = False

        if "change_quantity_of_medicine" not in st.session_state:
            st.session_state.change_quantity_of_medicine = False
        if change_quantity_of_medicine_button:
            st.session_state.view_shift_schedule = False
            st.session_state.view_medicine_inventory = True
            st.session_state.add_new_medicine = False
            st.session_state.change_quantity_of_medicine = True
            st.session_state.assign_patient_to_room = False
            st.session_state.free_room = False

        if "assign_patient_to_room" not in st.session_state:
            st.session_state.assign_patient_to_room = False
        if assign_patient_to_room_button:
            st.session_state.view_shift_schedule = False
            st.session_state.view_medicine_inventory = False
            st.session_state.add_new_medicine = False
            st.session_state.change_quantity_of_medicine = False
            st.session_state.assign_patient_to_room = True
            st.session_state.free_room = False

        # New session state for freeing room
        if "free_room" not in st.session_state:
            st.session_state.free_room = False
        if free_room_button:
            st.session_state.view_shift_schedule = False
            st.session_state.view_medicine_inventory = False
            st.session_state.add_new_medicine = False
            st.session_state.change_quantity_of_medicine = False
            st.session_state.assign_patient_to_room = False
            st.session_state.free_room = True


        if st.session_state.view_shift_schedule:
            shift_schedule = backend_queries.get_shift_schedule_for_staff(staff_id)
            
            for row in shift_schedule:
                row['ShiftStart'] = (datetime.datetime.min + row['ShiftStart']).strftime('%I:%M %p')
                row['ShiftEnd'] = (datetime.datetime.min + row['ShiftEnd']).strftime('%I:%M %p')

            shift_schedule_df = pd.DataFrame(shift_schedule)
            st.dataframe(shift_schedule_df, use_container_width=True, hide_index=True)

        if st.session_state.view_medicine_inventory:
            medicine_with_expiration_date = st.date_input("Show Medicine With Expiration Date: ", date.today())
            time_span = st.radio("Time Span", ("Before", "After", "Then"))

            medicines = backend_queries.get_all_medicine(medicine_with_expiration_date, time_span)
            medicines_df = pd.DataFrame(medicines)
            st.dataframe(medicines_df, use_container_width=True, hide_index=True)

        if st.session_state.add_new_medicine:
            st.subheader("Add New Medicine")

            suppliers = backend_queries.get_all_suppliers()
            suppliers_df = pd.DataFrame(suppliers)
            st.dataframe(suppliers_df, use_container_width=True, hide_index=True)

            # Medicine form inputs
            supplier_id = st.number_input("Supplier ID", 1, step=1)
            medicine_name = st.text_input("Medicine Name")
            medicine_type = st.text_input("Medicine Type")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date", min_value=date.today())
            dosage = st.number_input("Dosage (mg)", min_value=1, step=1)

            if st.button("Add Medicine"):
                # Call backend function to add medicine
                success = backend_queries.add_new_medicine(supplier_id, medicine_name, medicine_type, quantity, expiry_date, dosage)
                if success:
                    st.success("New medicine added successfully!")
                else:
                    st.error("Failed to add new medicine!")

        if st.session_state.change_quantity_of_medicine:
            st.subheader("Change Medicine Quantity")

            # Display existing medicines
            medicines = backend_queries.get_all_medicine_names()
            medicine_options = {medicine[1]: medicine[0] for medicine in medicines}

            selected_medicine_name = st.selectbox("Select Medicine", options=list(medicine_options.keys()))
            new_quantity = st.number_input("New Quantity", min_value=0, step=1)

            if st.button("Update Quantity"):
                # Get the selected medicine ID
                selected_medicine_id = medicine_options[selected_medicine_name]
                success = backend_queries.update_medicine_quantity(selected_medicine_id, new_quantity)

                if success:
                    st.success("Medicine quantity updated successfully!")
                    st.rerun()
                else:
                    st.error("Failed to update medicine quantity!")

        if st.session_state.assign_patient_to_room:
            room_status = st.radio("Choose Room Status", ("Available", "Not Available"))
            rooms = backend_queries.get_all_hospital_rooms(room_status)
            rooms_df = pd.DataFrame(rooms)
            st.dataframe(rooms_df, use_container_width=True, hide_index=True)

            room_patient_id = st.number_input("Enter Patient ID of Patient to Assign a Room for: ", 1, step=1)
            room_id = st.number_input("Enter Room ID: ", 1, step=1)

            assign_patient_room = st.button("Assign Room")

            if assign_patient_room:
                if backend_queries.assign_room_to_patient(room_id, room_patient_id):
                    st.success(f"Room {room_id} Assigned to Patient {room_patient_id}")
                else:
                    st.error("Unable to Assign Room...")

        if st.session_state.free_room:
            room_status = st.radio("Choose Room Status", ("Available", "Not Available"))
            rooms = backend_queries.get_all_hospital_rooms(room_status)
            rooms_df = pd.DataFrame(rooms)
            st.dataframe(rooms_df, use_container_width=True, hide_index=True)
        
            room_id_to_free = st.number_input("Enter Room ID to Free: ", min_value=1, step=1)
            free_room_submit_button = st.button("Accept and Free Room")

            if free_room_submit_button:
                if backend_queries.free_room(room_id_to_free):
                    st.success(f"Room {room_id_to_free} is now available!")
                else:
                    st.error("Unable to free room. Please check the room ID and try again.")



    else:
        st.warning("Unknown role detected.")




    st.markdown("---")
