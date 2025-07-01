import numpy as np
import cv2
import face_recognition
import sqlite3
import streamlit as st
import os
import base64
from datetime import datetime
from chatbot_tab import answer_question, load_flan_model
from liveliness import check_blink
# use your actual function

def connect_db():
    return sqlite3.connect("evalgenius.db")


def student_dashboard(name):
    st.markdown(f"## 🎓 Welcome, {name}!")

    tab1, tab2, tab3 = st.tabs([" Notes", "Exam", " Chatbot"])

    #  NOTES TAB
    with tab1:
        st.subheader("Study Materials / Notes")
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT title, filename, uploaded_by, uploaded_time FROM notes")
        notes = cursor.fetchall()
        conn.close()

        if notes:
            for idx, (title, filename, trainer, uploaded_time) in enumerate(notes):
                file_path = os.path.join("uploaded_notes", filename)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()

                    st.markdown(f"### 📘 {title}")
                    st.markdown(f" Uploaded by: **{trainer}**")
                    st.markdown(f" Date: {uploaded_time}")
                    
                    col1, col2 = st.columns(2)

                    with col1:
                        st.download_button(
                            label=" Download",
                            data=file_bytes,
                            file_name=filename,
                            mime="application/octet-stream",
                            key=f"download_{idx}"
                        )

                    with col2:
                        if filename.lower().endswith(".pdf"):
                            with st.expander(" View PDF File"):
                                base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)

                        elif filename.lower().endswith(".txt"):
                            try:
                                text_data = file_bytes.decode("utf-8")
                                with st.expander(" View Text File"):
                                    st.text_area(" Content", text_data, height=300)
                            except:
                                st.warning("Unable to preview this text file.")
                        else:
                            st.info(" File preview not supported.")
                    
                    st.markdown("---")
                else:
                    st.warning(f" File not found: {filename}")
        else:
            st.info(" No notes available yet.")


            #  EXAM TAB    
    with tab2:
        from exam_control import is_exam_active
        from exam_control import is_exam_active, create_submission_table
        create_submission_table()  #  Add this to recreate the table

        import json

        st.subheader(" Take MCQ Exam")

        if is_exam_active():
            st.success(" Exam is active. Answer all questions below:")

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d FROM exam_questions")
            questions = cursor.fetchall()
            conn.close()

            if questions:
                student_answers = {}
                for qid, question, a, b, c, d in questions:
                    selected = st.radio(
                        f"Q{qid}. {question}",
                        [a, b, c, d],
                        key=f"question_{qid}"
                    )
                    student_answers[str(qid)] = selected

                if st.button("Submit Exam"):
                    conn = connect_db()
                    cursor = conn.cursor()

                    cursor.execute('''
                        INSERT INTO submissions (student_name, student_id, submitted_at, answers)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        name,
                        st.session_state.get("student_id", "unknown"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        json.dumps(student_answers)
                    ))
                    conn.commit()
                    conn.close()

                    st.success(" Your answers have been submitted successfully!")

            else:
                st.warning(" No questions available yet.")
        else:
            st.warning("Exam has not started yet. Please wait for your trainer to start it.")

    #  CHATBOT TAB
    with tab3:
        st.subheader(" Ask Questions from Notes")
        query = st.text_input("Ask your question ")
        generator = load_flan_model()
        if st.button("Get Answer") and query:
            with st.spinner("Thinking hard ... 💡"):
                answer = answer_question(query, generator=generator)
                st.success("Here's your answer:")
                st.write(answer)


#liveliness

def student_login():
    st.subheader("Face Login")
    
    student_id = st.text_input("**Enter your ID**")  # ID taken here now

    if st.button("Login") and student_id:
        st.info("Please blink 2 times in the webcam window...")

        # Liveness Detection we call the check_blink fucntion to check liveliness
        liveness_passed = check_blink()
#if true 
        if liveness_passed:
            st.success("Verifying your face...")

            # Step 2: Face Recognition
            name = authenticate_face(student_id)

            if name:
                st.success(f"🎉 Welcome {name}!")
                st.session_state["student_name"] = name
            else:
                st.error("Face not recognized. Try again.")
#if false
        else:
            st.error("Spoof login detected!!")

#  FACE LOGIN FUNCTION
def authenticate_face(student_id):
    st.info("Accessing webcam... please look straight")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    ret, frame = cap.read()

    if not ret or frame is None:
        st.error("Could not open the webcam")
        cap.release()
        return None

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) != 1:
        st.warning(" Make sure only your face is visible!")
        cap.release()
        return None

    face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, face_encoding FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        st.error(" Student ID not found!")
        cap.release()
        return None

    name, db_encoding_blob = result
    db_encoding = np.frombuffer(db_encoding_blob, dtype=np.float64)

    match = face_recognition.compare_faces([db_encoding], face_encoding)[0]
    distance = face_recognition.face_distance([db_encoding], face_encoding)[0]

    if match and distance < 0.4:
        st.success(f" Welcome {name}!")
        st.session_state["student_logged_in"] = True
        st.session_state["student_name"] = name
        cap.release()
        return name
    else:
        st.error("Face does not match. Try again!")
        cap.release()
        return None

