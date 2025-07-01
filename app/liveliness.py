import dlib
import cv2
from imutils import face_utils
from scipy.spatial import distance

# Load detector and predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r"D:\my_projects\NexusGenius\app\shape_predictor_68_face_landmarks.dat")
#here i gave the shape predictor model i have installed 

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear
#the eye or the eye aspect ratio is captures after getting the facial landmarks, using that we identify the landmarks of the eyes
#we then use eye formula which find whether the eye is closed or not 
#when eye is closes then the value will be less and when open the value will be high
#a sudden increase in the eye value detect that a blink has occured

def check_blink(blink_target=2):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam failed to open!")
        return False
#opening webcam nad checking whether the webcam is openes or not

    EAR_THRESHOLD = 0.25 #the threshold or ear value , if ear is less than 0.25 that means eye is closed , if ear >0.25 then eye is opened
    CONSEC_FRAMES = 1 # this we are setting in how many frames eye must be closed

    blink_counter = 0 #total blink detected
    frame_counter = 0 #tracking how long the ear<0.25, eyes closed

    while True:
        ret, frame = cap.read()
        if not ret:
            break
#we are reading frame in webcam in a loop

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0) 
#we are converting frame to gray as color of the image do not matter in recongition , we focus of gradient
#using dlibs detector we detect the face in the gray scale image

        for rect in rects:
            shape = predictor(gray, rect) #we are getting the facial landmarks
            shape = face_utils.shape_to_np(shape) #convert them in to numpy array 

            leftEye = shape[42:48]
            rightEye = shape[36:42]
#we are using the landmarks of the eyes which we have extracted using facial landmark detector

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
#finding the ear ratio
            if ear < EAR_THRESHOLD:
                frame_counter += 1
            else:
                if frame_counter >= CONSEC_FRAMES:
                    blink_counter += 1
                    print(f"Blink detected! Total: {blink_counter}")
                frame_counter = 0

            cv2.polylines(frame, [leftEye], True, (0, 255, 0), 1)
            cv2.polylines(frame, [rightEye], True, (0, 255, 0), 1)
#dding the green line aroung the eyes and showing the count of blinks

        cv2.putText(frame, f"Blinks: {blink_counter}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.imshow("Liveness Detection", frame)

        if blink_counter >= blink_target:
            cap.release()
            cv2.destroyAllWindows()
            return True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False
