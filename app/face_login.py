import sqlite3 
# for sqlite database[creating a database , creating a table within a database , storing values in database , importantly connecting to the database]
import streamlit as st
#we are using streamlit which is a web app framework, which uses only python
import cv2
#we are using opencv' cv2 for capturing frames, image processing, etc
import face_recognition
#instead of building a face recognition model from scatch we are using the pretrained model which is trained with millions of data,
#we can this to save cost and time
import os
#to save database and access files with in my computer


def connect_db():
    return sqlite3.connect("evalgenius.db")
#we are connecting to our db file "evalgenius" using sqlite3.connect 
#we are creating a function for it so that each time when we want to connect the db file we can  call this function istead of writing the connect code again and again
#the above function is created so that we can call it when ever we waant to open and do something in or with the db

def create_table():
    conn=connect_db()
    cursor=conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        face_encoding BLOB NOT NULL
    )''' )
    conn.commit()
    conn.close()
# IN THE ABOVE we are creeating a table student inside our db
#using cursor we are writing inside out table
#we are creating table if if doesnot exist , in it
#we are giving a id with increaments automatically
#we are giving student name it must be text not null
#giving student id must be unique not null
#giving encoding of that students face it must be a blob (BINARY LARGE OBJECT)

def save_student(name,student_id,encoding):
    conn=connect_db()
    cursor=conn.cursor()
    try:
        cursor.execute("INSERT INTO students(name,student_id,face_encoding) VALUES (?,?,?)",(name,student_id,encoding))
        conn.commit()
        st.success("Student registered!")
    except sqlite3.IntegrityError:
        st.error("student already exists!, login using face ID")
    finally:
        conn.close()

#we are adding the student info in to the student table created in the db, when ever the students register themself, so that no duplicate id creation can be occured.
        
def capture_face_encoding():
    #this functions captured frame and detects face and converts that face to encodings
    
    st.info("Look at the webcam , the webcam is opening")
    cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
    #now we are using cv2's videocapture to capture video using live webcam and we capture frames from the webcam live video

    encoding=None
    #creating a empty numpy array, to store the embeddings of the face which we are going to detect below    
    while True:
        ret, frame=cap.read()
        #capturing frame from the live webcam and stroing it in the frame variable
        
        if not ret:
            st.error("Couldnt access the webcam,FAILED!!")
            #if ret is false or couldnt capture frames then display error using streamlit and come out of the while loop
            break
        
        rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        face_locations=face_recognition.face_locations(rgb_frame)
        #if we have captured face then we have to convert it  into rgb image
        #detecting the face using the face_recognitions face_locations function , we give the frame which we converted to rgb image
        
        cv2.imshow("Press 'S' to capture face and 'Q' to quit",frame)
        #if user wishes to capture face they enter s or wish to quirt them q
        key=cv2.waitKey(1)
        
        if key==ord('s'):
            #if user entered s
            if len(face_locations)==1:
                #we need to make sure only one face is detected in the frame , so check if the length ==1 or not
                
                face_encodings=face_recognition.face_encodings(rgb_frame,face_locations)
                #using face_recogntion's face_encoding we convert the captured face into encodings or a vector
                
                if face_encodings:
                    #if encodings is there then
                    encoding=face_encodings[0]
                    #if face encodings are loaded we have to make sure we are taking only one face's encoding and then store into the variable encodings which we created earlier
                    
                    st.success("Face Captured successfully!!")
                    #if encoding successfully captured and stored we display a success message
                    break
                else:
                    #if no encodings are able to capture

                    st.error("failed to capture! try again")
                    #we display error message to try again
            
            elif len(face_locations)==0:
                #if no face is detected in the frame
                
                st.warning("no face found , capture face again clearly!!")
                #display a warining message
            
            else:
                st.warning("mutiple faces found! make sure only your face is visible !!")
            
                            
        elif key==ord('q'):
            #while capturing frame if user enters q the webcam capture stops and shuts
            
            st.warning("cancelled webcam capture")
            #after shutting a warning message displayed
            break
        
    cap.release()
    cv2.destroyAllWindows()
    #after completing capturing and all we have to do is  release the webcam or turn off and destroy the window,
    
    if encoding is not None:
        return encoding.tobytes()
    return None
#if encoding is captures then we have to convert the numpy array into bytes object or in binary form so that its easy store in the sqlite database


def register_faces():
    #if student goes to register tab this function gets called
    st.header("Register your face")
    
    name=st.text_input("**Enter your name**")
    student_id=st.text_input("**Enter your id**")
    #creating an input area where user can enter name and their unique id
    
    create_table()
    #then we call the create_table which creates a table when calles for the first time then from next it stores the name and id in the db
    
    if st.button("Click to capture FACE") and name and student_id:
        #if user clicks capture face buttone then the text name and student_id is also filled
        
        encoding=capture_face_encoding()
        # we call the function which captures frame, detect face and convert the face to encodings and return the encoding
        #we store the encoding in the encoding array
        
        if encoding:
            save_student(name,student_id,encoding)
            #if an encoding is successfully extracted we need to store the encoding wrt their name and id in the database
        
        else:
            st.error("no face captured! try again")
            #if no encoding is extracted then display error message

#this is for registering students name and ID and capture encoding by callin the previous fucntion, saving them in database
