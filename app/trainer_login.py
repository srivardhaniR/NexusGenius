import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime
from exam_control import create_exam_status_table, start_exam, stop_exam, create_submission_table

# --- Connect to Database ---
def connect_db():
    return sqlite3.connect("evalgenius.db")
#we are connecting to our db file "evalgenius" using sqlite3.connect 
#we are creating a function for it so that each time when we want to connect the db file we can  call this function istead of writing the connect code again and again
#the above function is created so that we can call it when ever we waant to open and do something in or with the db

# --- Create Trainer Table ---
def create_trainer_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trainers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()

# --- Create Notes Table ---
def create_notes_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_data BLOB NOT NULL,
                uploaded_time TEXT NOT NULL,
                uploaded_by TEXT NOT NULL
            )
        ''')
        conn.commit()

def create_exam_questions_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct TEXT NOT NULL,
                uploaded_by TEXT NOT NULL
            )
        ''')
        conn.commit()


# --- Password Hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Register Trainer ---
def register_trainer(username, password):
    password_hash = hash_password(password)
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO trainers (username, password_hash) VALUES (?, ?)", (username, password_hash))
            conn.commit()
            st.success("Trainer registered successfully!")
    except sqlite3.IntegrityError:
        st.error("Trainer already exists!")

# --- Login Trainer ---
def login_trainer(username, password):
    password_hash = hash_password(password)
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trainers WHERE username = ? AND password_hash = ?", (username, password_hash))
        result = cursor.fetchone()
        return result is not None

# --- Trainer Login Page ---
def trainer_login_page():
    create_trainer_table()
    create_notes_table()
    create_exam_status_table()
    create_exam_questions_table()
    if st.session_state.get("trainer_logged_in"):
        show_trainer_dashboard()
        return

    tab1, tab2 = st.tabs(["Register Trainer", "Trainer Login"])

    with tab1:
        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")
        if st.button("Register Trainer") and username and password:
            register_trainer(username, password)

    with tab2:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login") and username and password:
            if login_trainer(username, password):
                st.success(f"Welcome {username}")
                st.session_state["trainer_logged_in"] = True
                st.session_state["trainer_username"] = username
                st.rerun()
            else:
                st.error("Invalid credentials")

# --- Trainer Dashboard ---

def show_trainer_dashboard():
    st.subheader(f"Welcome {st.session_state.get('trainer_username')}")
    st.markdown("<h1 style='text-align: center; color:#4CAF50;'>Dashboard</h1>", unsafe_allow_html=True)

    options = ["View Students", "Upload Notes", "Exam", "Logout"]
    choice = st.selectbox("Select to View", options)

    if choice == "View Students":
        view_registered_students()

    elif choice == "Upload Notes":
        st.subheader("Upload Notes")
        title = st.text_input("Title for the Notes:")
        uploaded_file = st.file_uploader("Upload File", type=["pdf", "txt", "ppt"])

        if uploaded_file is not None and title:
            notes_dir = "uploaded_notes"
            os.makedirs(notes_dir, exist_ok=True)

            filename = f"{datetime.now().strftime('%Y%m%d%H%M')}_{uploaded_file.name}"
            file_path = os.path.join(notes_dir, filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with open(file_path, "rb") as f:
                file_data = f.read()

            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO notes (title, filename, file_data, uploaded_by, uploaded_time) VALUES (?, ?, ?, ?, ?)",
                    (title, filename, file_data, st.session_state["trainer_username"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()

            st.success(" Notes uploaded successfully!")

        # --- Show Uploaded Notes ---
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, filename, uploaded_time FROM notes WHERE uploaded_by=?", (st.session_state["trainer_username"],))
            notes = cursor.fetchall()
        if notes:
            for note in notes:
                note_title = note[0]
                note_filename = note[1]
                st.markdown(f"** {note_title}**  \n *{note_filename}*")

                    # Delete button for each note
                if st.button(f"Delete", key=f"delete_{note_filename}"):
                    try:
                # 1. Remove from folder
                        file_path = os.path.join("uploaded_notes", note_filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)

                # 2. Remove from database
                        cursor.execute("DELETE FROM notes WHERE filename = ?", (note_filename,))
                        conn.commit()

                        st.success(f" Deleted '{note_title}' successfully!")
                        st.experimental_rerun()

                    except Exception as e:
                        st.error(f"⚠️ Could not delete '{note_title}': {e}")
        else:
            st.info("No notes uploaded yet.")
        

    elif choice == "Exam":
        st.subheader(" MCQ Exam Control Panel")

        create_exam_status_table()
        create_exam_questions_table()
        create_submission_table()

        # === Upload CSV-Based Exam ===
        st.markdown("###  Upload Exam (CSV Format Only)")
        exam_file = st.file_uploader("Upload CSV File", type=["csv"])

        if exam_file is not None:
            import pandas as pd
            try:
                df = pd.read_csv(exam_file)

                required_cols = ["question", "option_a", "option_b", "option_c", "option_d", "correct"]
                if all(col in df.columns for col in required_cols):
                    with connect_db() as conn:
                        cursor = conn.cursor()
                        for _, row in df.iterrows():
                            cursor.execute('''
                                INSERT INTO exam_questions (question, option_a, option_b, option_c, option_d, correct, uploaded_by)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                row["question"], row["option_a"], row["option_b"], row["option_c"],
                                row["option_d"], row["correct"].strip().lower(), st.session_state["trainer_username"]
                            ))
                        conn.commit()
                    st.success(" MCQ Exam uploaded successfully!")
                else:
                    st.error("CSV must have columns: question, option_a, option_b, option_c, option_d, correct")

            except Exception as e:
                st.error(f" Error reading file: {e}")

        # === View Submissions ===
        st.markdown("###  Student Submissions")
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT student_name, student_id, submitted_at, answers FROM submissions")
            results = cursor.fetchall()

        if results:
            import json
            for name, sid, time, answers_json in results:
                answers = json.loads(answers_json)

                    # Fetch correct answers from DB
                with connect_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, correct FROM exam_questions")
                    correct_answers = {str(row[0]): row[1].strip().lower() for row in cursor.fetchall()}

    # Compare and score
                total_questions = len(correct_answers)
                correct_count = sum(
                    1 for qid, ans in answers.items()
                    if qid in correct_answers and ans.strip().lower() == correct_answers[qid]
            )

            st.markdown(f"""
            **👤 Name:** {name}  
             **ID:** {sid}  
             **Submitted at:** {time}  
             **Score:** {correct_count} / {total_questions}
            """)
            st.markdown("---")


        else:
            st.info("No submissions yet.")

        # === Start/Stop Exam ===
        st.markdown("### 🚦 Exam Status Control")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶ Start Exam"):
                start_exam()
                st.success(" Exam is now active!")

        with col2:
            if st.button(" Stop Exam"):
                stop_exam()
                st.warning(" Exam has been stopped.")

    elif choice == "Logout":
        st.session_state["trainer_logged_in"] = False
        st.rerun()



# --- View Registered Students ---
import pandas as pd 

def view_registered_students():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, student_id FROM students")
        data = cursor.fetchall()

    st.subheader(" Registered Students")

    if data:
        df = pd.DataFrame(data, columns=["Name", "Student ID"])
        st.table(df)
    else:
        st.info("No students registered yet.")

