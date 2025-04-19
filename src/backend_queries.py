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

def register(name: str, email: str, role: str, password: str) -> bool:

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

    return rows_affected > 0
    

def get_all_doctors() -> List[Tuple]:

    global conn
    if conn is None:
        init_connection()
    
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors")
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
        rows_affected = 0
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
        rows_affected = 0
    finally:
        cursor.close()
