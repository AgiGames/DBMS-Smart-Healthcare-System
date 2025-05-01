import mysql.connector
from typing import List, Tuple;

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

def get_appointments(doctor_id: int) -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()

    '''
    SELECT * FROM (
    SELECT a.AppointmentID, p.PatientID, p.Name AS "Patient Name", a.DoctorID, d.Name AS "Doctor Name", a.DateTime, a.Status
    FROM patients p
    JOIN appointment a ON p.PatientID = a.PatientID
    JOIN doctors d ON d.DoctorID = a.DoctorID
    ) AS result
    WHERE DoctorID = 2;
    '''

    cursor = conn.cursor()
    query = "SELECT * FROM (SELECT a.AppointmentID, p.PatientID, p.Name AS \"Patient Name\", a.DoctorID, d.Name AS \"Doctor Name\", a.DateTime, a.Status FROM patients p JOIN appointment a ON p.PatientID = a.PatientID JOIN doctors d ON d.DoctorID = a.DoctorID) AS result WHERE DoctorID = %s;"
    cursor.execute(query, (doctor_id,))
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
    
def get_medical_records(patient_id: int) -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()

    '''
    SELECT RecordID, Diagnosis, m.Date as Medical_Record_Date, m.PrescriptionID, pr.PatientID, p.Name, pr.DoctorID, d.Name, pr.Date as Prescription_Date FROM
    medicalrecords m
    INNER JOIN
    prescriptions pr
    ON m.PrescriptionID = pr.PrescriptionID
    INNER JOIN
    patients p
    ON pr.PatientID = p.PatientID
    INNER JOIN
    doctors d
    ON pr.DoctorID = d.DoctorID
    WHERE pr.PatientID = 1;
    '''

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
    WHERE pr.PatientID = %s;
    """
    cursor.execute(query, (patient_id,))
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
