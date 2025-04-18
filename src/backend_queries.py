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
