import cv2
import dlib
import numpy as np
import winsound  # For Windows beep sound
from scipy.spatial import distance as dist
import time

# Load dlib’s face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Indices for facial landmarks in dlib's 68-point model
LEFT_EYE = list(range(42, 48))
RIGHT_EYE = list(range(36, 42))
MOUTH = list(range(60, 68))

# Initialize blink counters
blink_counter = 0
blink_start_time = time.time()
eye_closed_start = None
eye_closed_duration = 0

BLINK_THRESHOLD_LOW = 5   # If blinks < 5 in 30 sec → Warning (fatigue)
BLINK_THRESHOLD_HIGH = 20  # If blinks > 20 in 30 sec → Drowsiness

def eye_aspect_ratio(eye):
    """Calculate the Eye Aspect Ratio (EAR) to detect blinking."""
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def mouth_aspect_ratio(mouth):
    """Calculate the Mouth Aspect Ratio (MAR) to detect yawning."""
    A = dist.euclidean(mouth[1], mouth[7])  # Vertical distance
    B = dist.euclidean(mouth[2], mouth[6])
    C = dist.euclidean(mouth[0], mouth[4])  # Horizontal distance
    return (A + B) / (2.0 * C)

def check_blink_rate():
    global blink_counter, blink_start_time

    # Check every 30 seconds
    if time.time() - blink_start_time > 30:
        if blink_counter < BLINK_THRESHOLD_LOW:
            print("⚠️ Low Blink Rate! Fatigue Warning!")  
            cv2.putText(frame, "LOW BLINK RATE ALERT!", (50, 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
        elif blink_counter > BLINK_THRESHOLD_HIGH:
            print("⚠️ High Blink Rate! Possible Drowsiness!")  
            cv2.putText(frame, "HIGH BLINK RATE ALERT!", (50, 250), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

        # Reset blink counter
        blink_start_time = time.time()
        blink_counter = 0

# Constants for detecting drowsiness
EYE_AR_THRESH = 0.25  # EAR threshold for closed eyes
EYE_AR_CONSEC_FRAMES = 15  # Frames before triggering alert
MOUTH_AR_THRESH = 0.6  # MAR threshold for yawning
YAWN_CONSEC_FRAMES = 20  # Frames before yawning alert triggers

# Initialize counters
yawn_counter = 0
yawn_flag = False  # To prevent repeated alerts
drowsy_alert_triggered = False  # To track if beep has been played
yawn_alert_start = None  # Track when yawning alert started

# Start video capture
cap = cv2.VideoCapture(0)  # Use webcam

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        landmarks = np.array([(p.x, p.y) for p in landmarks.parts()])

        # Extract eye and mouth regions
        left_eye = landmarks[LEFT_EYE]
        right_eye = landmarks[RIGHT_EYE]
        mouth = landmarks[MOUTH]

        # Compute EAR and MAR
        left_EAR = eye_aspect_ratio(left_eye)
        right_EAR = eye_aspect_ratio(right_eye)
        mouth_MAR = mouth_aspect_ratio(mouth)

        ear = (left_EAR + right_EAR) / 2.0  # Average EAR

        # Check if eyes are closed
        if ear < EYE_AR_THRESH:
            if eye_closed_start is None:
                eye_closed_start = time.time()
            blink_counter += 1
            print(f"[DEBUG] Blink Count: {blink_counter}")  # Debugging
            if blink_counter >= EYE_AR_CONSEC_FRAMES:
                cv2.putText(frame, "DROWSY ALERT!", (50, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                if not drowsy_alert_triggered:
                    winsound.Beep(1000, 500)  # Beep at 1000 Hz for 500ms (Windows)
                    drowsy_alert_triggered = True  # Prevent continuous beeping
        else:
            if eye_closed_start is not None:
                eye_closed_duration = time.time() - eye_closed_start
                print(f"[DEBUG] Eye Closed for: {eye_closed_duration:.2f} sec")  

                # Send eye closure duration to ML model
                # send_data_to_ml_model(eye_closed_duration)  # Uncomment when ML model is ready

            eye_closed_start = None  # Reset eye closure timer
            blink_counter = 0  # Reset counter if eyes are open
            drowsy_alert_triggered = False  # Reset beep trigger

        # Check for yawning
        if mouth_MAR > MOUTH_AR_THRESH:
            yawn_counter += 1
            if yawn_counter >= YAWN_CONSEC_FRAMES and not yawn_flag:
                print("⚠️ YAWNING ALERT!")
                yawn_flag = True  # Prevent multiple alerts
                yawn_alert_start = time.time()  # Start timer for yawn alert
                winsound.Beep(800, 500)  # Beep at 800 Hz for 500ms
        else:
            yawn_counter = 0  # Reset if not yawning
            if yawn_alert_start and time.time() - yawn_alert_start > 2:  # Keep alert visible for 2 sec
                yawn_flag = False  # Allow new detection

        # Display Yawning Alert if needed
        if yawn_flag:
            cv2.putText(frame, "YAWNING ALERT!", (50, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

        # Draw facial landmarks
        for (x, y) in landmarks:
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    cv2.imshow("Fatigue Detection", frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
