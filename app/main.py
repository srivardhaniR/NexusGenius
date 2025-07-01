import streamlit as st
from face_login import register_faces
from face_auth import authenticate_face, student_dashboard,student_login
from trainer_login import trainer_login_page
from exam_control import create_exam_status_table, start_exam, stop_exam, create_submission_table


st.set_page_config(page_title="EvalGenius", layout="centered")
#here we are using streamlit and creating a web app , in the above line we are simply setting the name of the window and the layout of the default window

st.markdown("<h1 style='text-align: center;'>NEXUS IQ SOLUTIONS</h1>", unsafe_allow_html=True)
#markdown  is simple way to write a text with prefered text style in streamlit
#we are displaying nexusiqsolutions as h1 style, center aligned in the window
#as we are using html tags here and often markdown do not accept html tags to let it accept we give unsafe_allow_tags "TRUE"


usertype = st.sidebar.selectbox(" Hello! You are a:", ["Select", "Student", "Trainer"])
#here we are creating a side bar , example the sidebar in chatgpt where there is all our chats displayed
#we are creating sidebar using streamlit.sidebar
#in the side bar we are adding a select box with attributes student and trainer , so that the user can select and then according to the selected user type the login page would open


if usertype == "Student":
    #if the user selects usertype as student in the select box then we navigate to the student login/register page
    
    if st.session_state.get("student_logged_in"):
    #checking if the student already logged in or not , if logged in then we navigate to dashboard of that respective student.
        
        student_dashboard(st.session_state.get("student_name"))
        #when ever we click or interact in the streamlit app, it reruns entire script from top to bottom so the selection or the click we performed wont be remebered
        #and this problem creates a huge problem as the user clicks the type of login the streamlit reruns and doesnt store the users click, shows same page again
        #to avoid this we use session_state.get stores values and remembers variables
    
    else:
        st.subheader("Student Login")
        #if the student didnot login , then navigate to login/register page 
        
        tab1, tab2 = st.tabs(["Register Face", "Face Login"])
        #we are creating two tabs with in log in [1, register and 2, login]
        
        with tab1:
            register_faces()
            #if user select register face tab then we call the register_face  for further processs of registering
        
        with tab2:
            student_login()
            #if user selects face login tab then we call the student_login() for further login process

elif usertype == "Trainer":
    #if the user selects trainer then we call the trainer_login_page for further login/register process
    
    trainer_login_page()
