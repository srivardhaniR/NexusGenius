import sqlite3

def connect_db():
    return sqlite3.connect("evalgenius.db")
#we are connecting to our db file "evalgenius" using sqlite3.connect 
#we are creating a function for it so that each time when we want to connect the db file we can  call this function istead of writing the connect code again and again
#the above function is created so that we can call it when ever we waant to open and do something in or with the db


def create_exam_status_table():
    #we are creaitng table to store the trainers upload or exam details in the database 
    with connect_db() as conn:
        cursor = conn.cursor()
        #cursor is like a pen with which we can write or read in the database
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exam_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_exam_active INTEGER NOT NULL DEFAULT 0
            )
        ''')
        #we use execute to perform  sql commands
        #here for the first run we will be creating a table and with the columns like is_exam_active and all
        
        cursor.execute("SELECT COUNT(*) FROM exam_status")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO exam_status (is_exam_active) VALUES (0)")
        conn.commit()
#here  create_exam_status_table created in the db file connected 
#we are creating a table to check exam status

def start_exam():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE exam_status SET is_exam_active = 1 WHERE id = 1")
        conn.commit()
#the block will run to start the exam and the status of the exam will be active in db if this fucntion is called

def stop_exam():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE exam_status SET is_exam_active = 0 WHERE id = 1")
        conn.commit()
#the block will run to start the exam and the status of the exam will be active in db if this fucntion is called

def is_exam_active():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_exam_active FROM exam_status WHERE id = 1")
        return cursor.fetchone()[0] == 1
#this block will store the exam status as active in the database if called

def create_submission_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                answers TEXT NOT NULL
            )
        ''')
        conn.commit()
#creating a table where to store the exam submission of the student , the name, id, time of submission, and answers
