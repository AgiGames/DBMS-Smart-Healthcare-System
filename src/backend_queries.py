import mysql.connector
from typing import List, Tuple, Dict;
from datetime import date

conn = None

def init_connection():

    global conn
    if conn is None:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="agi123",
            database="healthcaresystem"
        )

def authenticate(email: str, password: str) -> Tuple:

    global conn
    if conn is None:
        init_connection()
    
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()
    return user

def register(name: str, email: str, role: str, password: str) -> Tuple[bool, int]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "INSERT INTO users(Name, Email, Role, Password) VALUES(%s, %s, %s, %s)"

    try:
        cursor.execute(query, (name, email, role, password))
        conn.commit()
        rows_affected = cursor.rowcount
    except mysql.connector.Error as err:
        print("Error during registration:", err)
        rows_affected = 0
    finally:
        cursor.close()

    return rows_affected > 0, cursor.lastrowid;
    

def get_doctors_available_for_appointment() -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()
    
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Specialization, Contact, Email, DoctorID FROM doctors d WHERE d.Availability = 'Available';")
    results = cursor.fetchall()
    cursor.close()
    return results       

def get_doctor_id(user_id: int) -> int:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "SELECT DoctorID FROM doctors WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()
    cursor.close()
    return results[0]

def get_patient_id(user_id: int) -> int:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "SELECT PatientID FROM patients WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()
    cursor.close()
    return results[0]

def get_appointments(doctor_id: int, from_date: date, to_date: date) -> List[Tuple]:
    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = """
        SELECT *
        FROM (
            SELECT
                a.AppointmentID,
                p.PatientID,
                p.Name AS "Patient Name",
                a.DoctorID,
                d.Name AS "Doctor Name",
                a.DateTime,
                a.Status
            FROM patients p
            JOIN appointment a ON p.PatientID = a.PatientID
            JOIN doctors d ON d.DoctorID = a.DoctorID
        ) AS result
        WHERE DoctorID = %s AND DateTime BETWEEN %s AND %s;
    """
    cursor.execute(query, (doctor_id, from_date, to_date))
    result = cursor.fetchall()
    cursor.close()
    return result

def get_doctor_availability(user_id: int) -> str:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "SELECT Availability FROM doctors WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()[0]
    cursor.close()
    return result

def set_doctor_availability(user_id: int, available_state: str) -> None:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "UPDATE doctors SET Availability = %s WHERE UserID = %s"

    try:
        cursor.execute(query, (available_state, user_id))
        conn.commit()
    except mysql.connector.Error as err:
        print("Error setting availability", err)
    finally:
        cursor.close()

def set_appointment_as_completed(appointment_id: int) -> None:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "UPDATE appointment SET Status = \"Completed\" WHERE AppointmentID = %s"

    try:
        cursor.execute(query, (appointment_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print("Error setting appointment completion status", err)
    finally:
        cursor.close()

def book_appointment(patient_id: int, doctor_id: int) -> bool:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "INSERT INTO appointment (PatientID, DoctorID, Status) VALUES (%s, %s, %s)"

    flag = False

    try:
        cursor.execute(query, (patient_id, doctor_id, 'Not Completed'))
        conn.commit()
        flag = True
    except mysql.connector.Error as err:
        print("Error booking appointment status", err)
    finally:
        cursor.close()
        return flag
    
def get_medical_records(patient_id: int, medical_records_from_date: date, medical_records_to_date: date, prescriptions_from_date: date, prescriptions_to_date: date) -> List[Tuple]:

    global conn
    if conn is None:
        init_connection() #ada

    cursor = conn.cursor()
    query = """
    SELECT 
        m.RecordID,
        m.Diagnosis,
        m.Date AS Medical_Record_Date,
        m.PrescriptionID,
        pr.PatientID,
        p.Name AS Patient_Name,
        pr.DoctorID,
        d.Name AS Doctor_Name,
        pr.Date AS Prescription_Date
    FROM medicalrecords m
    INNER JOIN prescriptions pr ON m.PrescriptionID = pr.PrescriptionID
    INNER JOIN patients p ON pr.PatientID = p.PatientID
    INNER JOIN doctors d ON pr.DoctorID = d.DoctorID
    WHERE pr.PatientID = %s
    AND m.Date BETWEEN %s AND %s
    AND pr.Date BETWEEN %s AND %s
    ORDER BY m.Date DESC;
    """
    cursor.execute(query, (patient_id, medical_records_from_date, medical_records_to_date, prescriptions_from_date, prescriptions_to_date))
    result = cursor.fetchall()
    cursor.close()
    return result

def get_medicines_of_prescriptions(prescription_id: int) -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "SELECT m.MedicineID, m.Name, m.Dosage FROM prescriptionmedicines pm JOIN medicineinventory m ON pm.MedicineID = m.MedicineID WHERE pm.PrescriptionID = %s"
    cursor.execute(query, (prescription_id,))
    result = cursor.fetchall()
    cursor.close()
    return result

def register_patient(name: str, age: int, gender: str, address: str, contact: str, blood_type: str, user_id: int) -> bool:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "INSERT INTO patients (Name, Age, Gender, Address, Contact, BloodType, UserID) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    flag = False

    try:
        cursor.execute(query, (name, age, gender, address, contact, blood_type, user_id))
        conn.commit()
        flag = True
    except mysql.connector.Error as err:
        print("Error registering patients", err)
    finally:
        cursor.close()
        return flag
    
def remove_user(user_id: int) -> None:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "DELETE FROM users WHERE UserID = %s"

    try:
        cursor.execute(query, (user_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print("Error removing user", err)
    finally:
        cursor.close()

def register_doctor(name: str, specialization: str, contact: str, email: str, user_id: int) -> bool:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "INSERT INTO doctors (Name, Specialization, Contact, Email, Availability, UserID) VALUES (%s, %s, %s, %s, %s, %s)"
    flag = False

    try:
        cursor.execute(query, (name, specialization, contact, email, 'Available', user_id))
        conn.commit()
        flag = True
    except mysql.connector.Err as err:
        print("Error registering doctor", err)
    finally:
        cursor.close()
        return flag

def get_staff_id(user_id: int) -> int:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = "SELECT StaffID FROM staff WHERE UserID = %s"
    cursor.execute(query, (user_id,))
    results = cursor.fetchone()
    cursor.close()
    return results[0]

def get_shift_schedule_for_staff(staff_id) -> List[Dict]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM shiftschedule
        WHERE StaffID = %s
        ORDER BY ShiftStart, ShiftEnd
    """, (staff_id,))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_lab_tests_for_patient(patient_id: int, from_date: date, to_date: date) -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM labtests
        WHERE PatientID = %s
        AND DateTime BETWEEN %s AND %s
        ORDER BY DateTime DESC
    """, (patient_id, from_date, to_date))
    
    results = cursor.fetchall()
    cursor.close()
    return results

def get_medicine_inventory() -> List[Dict]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medicineinventory ORDER BY name ASC")
    results = cursor.fetchall()
    cursor.close()
    return results

def get_specific_appointments(doctor_id: int, from_date: date, to_date: date, status_choice: str) -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()

    query = """
        SELECT
            a.AppointmentID,
            p.PatientID,
            p.Name AS "Patient Name",
            a.DoctorID,
            d.Name AS "Doctor Name",
            a.DateTime,
            a.Status
        FROM patients p
        JOIN appointment a ON p.PatientID = a.PatientID
        JOIN doctors d ON d.DoctorID = a.DoctorID
        WHERE a.DoctorID = %s 
        AND a.DateTime BETWEEN %s AND %s
        AND a.Status = %s;
    """
    cursor.execute(query, (doctor_id, from_date, to_date, status_choice))
    result = cursor.fetchall()
    cursor.close()
    return result


def write_prescription(doctor_id: int, patient_id: int, instructions: str, date: date, medicine_ids: List[int], diagnosis: str) -> None:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    
    query = """
    INSERT INTO prescriptions (PatientID, DoctorID, Date, Instructions)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(query, (patient_id, doctor_id, date, instructions))
    conn.commit()

    prescription_id = cursor.lastrowid

    query = """
    INSERT INTO medicalrecords (PrescriptionID, Diagnosis, Date)
    VALUES (%s, %s, %s);
    """
    cursor.execute(query, (prescription_id, diagnosis, date.today()))
    conn.commit()

    for i in range(len(medicine_ids)):
        query = "INSERT INTO prescriptionmedicines (PrescriptionID, MedicineID) VALUES (%s, %s)"
        cursor.execute(query, (prescription_id, medicine_ids[i]))
        conn.commit()

    cursor.close()

def get_all_medicine_names() -> List[Tuple[int, str]]:
    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor()
    query = """
        SELECT MedicineID, Name 
        FROM medicineinventory 
        WHERE Quantity > 0
        ORDER BY Name ASC;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

def get_all_medicine(filter_date: date, time_span: str) -> List[Dict]:
    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor(dictionary=True)

    # Map time_span to SQL condition
    if time_span == "Before":
        condition = "ExpiryDate < %s"
    elif time_span == "After":
        condition = "ExpiryDate > %s"
    elif time_span == "Then":
        condition = "ExpiryDate = %s"
    else:
        # Default fallback (shouldn't happen if frontend restricts choices)
        condition = "1 = 1"  # no filtering

    query = f"""
        SELECT 
            MedicineID,
            SupplierID,
            Name,
            Type,
            Quantity,
            ExpiryDate,
            Dosage
        FROM medicineinventory
        WHERE {condition}
        ORDER BY ExpiryDate ASC;
    """

    cursor.execute(query, (filter_date,))
    results = cursor.fetchall()
    cursor.close()

    return results

def add_new_medicine(supplier_id: int, name: str, medicine_type: str, quantity: int, expiry_date: date, dosage: int) -> bool:
    global conn
    if conn is None:
        init_connection()

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO medicineinventory (SupplierID, Name, Type, Quantity, ExpiryDate, Dosage)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (supplier_id, name, medicine_type, quantity, expiry_date, dosage))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error adding new medicine: {e}")
        return False
    
def update_medicine_quantity(medicine_id: int, new_quantity: int) -> bool:
    global conn
    if conn is None:
        init_connection()

    try:
        cursor = conn.cursor()
        query = """
            UPDATE medicineinventory
            SET Quantity = %s
            WHERE MedicineID = %s;
        """
        cursor.execute(query, (new_quantity, medicine_id))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating medicine quantity: {e}")
        return False
    
def get_all_suppliers() -> List[Tuple[int, str, str, str, str]]:

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT SupplierID, Name, Email, Address, Contact 
        FROM suppliers
        ORDER BY Name ASC;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    
    return results

def get_all_hospital_rooms(status: str):

    global conn
    if conn is None:
        init_connection()

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM hospitalrooms WHERE Availabity = %s"
    cursor.execute(query, (status,))
    results = cursor.fetchall()
    cursor.close()

    return results

def assign_room_to_patient(room_id: int, patient_id: int) -> bool:

    global conn
    if conn is None:
        init_connection() 
    
    try:
        cursor = conn.cursor()

        # Insert the room assignment
        query_assign = "INSERT INTO roomassignments (RoomID, PatientID) VALUES (%s, %s)"
        cursor.execute(query_assign, (room_id, patient_id))

        # Update the room availability to 'Not Available'
        query_update_availability = "UPDATE hospitalrooms SET Availabity = 'Not Available' WHERE RoomID = %s"
        cursor.execute(query_update_availability, (room_id,))
        
        # Commit the changes
        conn.commit()
        cursor.close()
        
        return True
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"Error assigning room to patient: {e}")
        return False
    
def register_staff(name, contact, shift_timing, user_id) -> bool:
    global conn
    if conn is None:
        init_connection() 

    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO staff (UserID, Role, Contact, ShiftTiming)
            VALUES (%s, 'Staff', %s, %s);
        """
        cursor.execute(query, (user_id, contact, shift_timing))
        conn.commit()

        if shift_timing == "Morning":
            shift_start = "09:00:00"  # 9 AM
            shift_end = "17:00:00"    # 5 PM
        elif shift_timing == "Evening":
            shift_start = "17:00:00"  # 5 PM
            shift_end = "01:00:00"    # 1 AM
        else:
            shift_start = "00:00:00"  # Midnight
            shift_end = "08:00:00"    # 8 AM

        query = """
            INSERT INTO shiftschedule (StaffID, ShiftStart, ShiftEnd, AssignedDate)
            VALUES (LAST_INSERT_ID(), %s, %s, CURDATE());
        """
        cursor.execute(query, (shift_start, shift_end))
        conn.commit()

        cursor.close()
        return True
    except Exception as e:
        print(f"Error registering staff: {e}")
        return False
