import streamlit as st
import hashlib
from config import get_db_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def student_login(username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        hashed_password = hash_password(password)
        cursor.execute("SELECT * FROM students WHERE username = %s AND password = %s", 
                      (username, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    return None

def teacher_login(username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        hashed_password = hash_password(password)
        cursor.execute("SELECT * FROM teachers WHERE username = %s AND password = %s", 
                      (username, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    return None

def register_student(name, username, password):
    """Register student and return new student ID"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO students (name, username, password) VALUES (%s, %s, %s)",
                (name, username, hashed_password)
            )
            conn.commit()
            # Get the ID of newly registered student
            new_id = cursor.lastrowid
            return new_id
        except Exception as e:
            st.error(f"Registration failed: {str(e)}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def register_teacher(name, username, password):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            hashed_password = hash_password(password)
            cursor.execute("INSERT INTO teachers (name, username, password) VALUES (%s, %s, %s)",
                         (name, username, hashed_password))
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Registration failed: {str(e)}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False

def update_student_image_path(student_id, image_path):
    """Update student's image path"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE students SET image_path = %s WHERE id = %s",
                (image_path, student_id)
            )
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Failed to update image path: {str(e)}")
            return False
        finally:
            cursor.close()
            conn.close()
    return False