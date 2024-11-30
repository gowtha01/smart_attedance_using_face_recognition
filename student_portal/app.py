import streamlit as st
import os
from datetime import datetime
from auth import student_login, teacher_login, register_student, register_teacher
from student_utils import get_student_attendance, get_student_marks, mark_attendance
from teacher_utils import get_student_by_barcode, update_student_marks
from face_utils import capture_photo, save_captured_photo, verify_face, capture_verification_photo

st.set_page_config(page_title="Student Portal", layout="wide")

def main():
    st.title("Student Portal")
    
    # Session state initialization
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    # Logout button
    if st.session_state.user_type:
        if st.button("Logout"):
            st.session_state.user_type = None
            st.session_state.user_id = None
            st.rerun()  # Changed from st.experimental_rerun()

    # Main navigation
    if not st.session_state.user_type:
        role = st.selectbox("Select Role", ["Student", "Teacher"])
        action = st.radio("Choose Action", ["Login", "Register"])

        if action == "Login":
            handle_login(role)
        else:
            handle_registration(role)
    else:
        if st.session_state.user_type == "student":
            show_student_dashboard()
        else:
            show_teacher_dashboard()

def handle_login(role):
    with st.form(f"{role.lower()}_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if role == "Student":
                user = student_login(username, password)
                if user:
                    st.session_state.user_type = "student"
                    st.session_state.user_id = user['id']
                    st.success("Login successful!")
                    st.rerun()  # Already updated
                else:
                    st.error("Invalid credentials")
            else:
                user = teacher_login(username, password)
                if user:
                    st.session_state.user_type = "teacher"
                    st.session_state.user_id = user['id']
                    st.success("Login successful!")
                    st.rerun()  # Change this line from st.experimental_rerun()
                else:
                    st.error("Invalid credentials")

def handle_registration(role):
    with st.form(f"{role.lower()}_registration"):
        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if role == "Student":
            uploaded_file = st.file_uploader("Upload your photo", type=['jpg', 'jpeg', 'png'])
        
        submitted = st.form_submit_button("Register")

        if submitted and role == "Student":
            if uploaded_file is not None:
                # Register student first to get ID
                student_id = register_student(name, username, password)
                if student_id:
                    # Save photo with student ID and update path
                    image_path = save_uploaded_photo(uploaded_file, student_id)
                    if update_student_image_path(student_id, image_path):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Failed to save image path")
                else:
                    st.error("Registration failed")
            else:
                st.error("Please upload your photo")
        elif submitted:
            if register_teacher(name, username, password):
                st.success("Registration successful! Please login.")

def save_uploaded_photo(uploaded_file, student_id):
    """
    Save an uploaded student photo file and return the saved path
    """
    # Create photos directory if it doesn't exist
    photos_dir = os.path.join(os.getcwd(), "student_photos")
    os.makedirs(photos_dir, exist_ok=True)
    
    # Generate filename with student ID and timestamp
    file_ext = os.path.splitext(uploaded_file.name)[1]
    filename = f"student_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    filepath = os.path.join(photos_dir, filename)
    
    try:
        # Save the uploaded file
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filepath
    except Exception as e:
        st.error(f"Error saving photo: {str(e)}")
        return None

def update_student_image_path(student_id, image_path):
    """
    Update the image_path for a student in the database
    """
    try:
        # Add your database connection and query logic here
        query = "UPDATE students SET image_path = %s WHERE id = %s"
        # Execute query with (image_path, student_id) parameters
        return True
    except Exception as e:
        print(f"Error updating image path: {str(e)}")
        return False

def show_student_dashboard():
    st.header("Student Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Attendance", "Mark Attendance", "Marks"])
    
    with tab1:
        st.subheader("Your Attendance")
        attendance_df = get_student_attendance(st.session_state.user_id)
        if not attendance_df.empty:
            st.dataframe(attendance_df)
        else:
            st.info("No attendance records found")
            
    with tab2:
        st.subheader("Mark Attendance")
        if st.button("Capture Photo"):
            captured_image = capture_verification_photo()
            if captured_image is not None:
                st.image(captured_image, caption="Captured Photo")
                
                barcode = st.text_input("Please enter your ID for verification:")
                if barcode and barcode == str(st.session_state.user_id):
                    if mark_attendance(st.session_state.user_id):
                        st.success("Attendance marked successfully!")
                    else:
                        st.error("Failed to mark attendance")
                elif barcode:
                    st.error("Invalid ID")
    
    with tab3:
        st.subheader("Your Marks")
        marks = get_student_marks(st.session_state.user_id)
        if marks:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Subject 1", marks['subject1'])
            col2.metric("Subject 2", marks['subject2'])
            col3.metric("Subject 3", marks['subject3'])
            col4.metric("Subject 4", marks['subject4'])
            col5.metric("Subject 5", marks['subject5'])
        else:
            st.info("No marks recorded yet")

def show_teacher_dashboard():
    st.header("Teacher Dashboard")
    
    barcode = st.text_input("Enter Student ID/Barcode")
    if barcode:
        student = get_student_by_barcode(barcode)
        if student:
            st.subheader(f"Student: {student['name']}")
            
            with st.form("update_marks"):
                st.subheader("Update Marks")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                marks = [
                    col1.number_input("Subject 1", value=student.get('subject1', 0), min_value=0, max_value=100),
                    col2.number_input("Subject 2", value=student.get('subject2', 0), min_value=0, max_value=100),
                    col3.number_input("Subject 3", value=student.get('subject3', 0), min_value=0, max_value=100),
                    col4.number_input("Subject 4", value=student.get('subject4', 0), min_value=0, max_value=100),
                    col5.number_input("Subject 5", value=student.get('subject5', 0), min_value=0, max_value=100)
                ]
                
                if st.form_submit_button("Update Marks"):
                    if update_student_marks(student['id'], marks):
                        st.success("Marks updated successfully!")
                    else:
                        st.error("Failed to update marks")
        else:
            st.error("Student not found")

def show_attendance_page():
    st.subheader("Attendance System")
    
    if st.button("Capture Photo for Attendance"):
        captured_image = capture_verification_photo()
        if captured_image is not None:
            st.image(captured_image, caption="Captured Photo")
            
            # Debug student ID
            student_id = st.session_state.user_id
            st.write(f"Debug - Student ID: {student_id}")
            
            barcode = st.text_input("Please enter your ID for verification:")
            
            if barcode and barcode == str(student_id):
                # Debug attendance marking
                st.write(f"Debug - Attempting to mark attendance for student {student_id}")
                if mark_attendance(student_id):
                    st.success("Attendance marked successfully!")
                else:
                    st.error("Failed to mark attendance")
            elif barcode:
                st.error("Invalid ID")

if __name__ == "__main__":
    main()