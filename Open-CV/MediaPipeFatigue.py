import cv2
import mediapipe as mp
import numpy as np
import winsound  # For Windows beep sound
from scipy.spatial import distance as dist
import time

# --- MediaPipe Initialization ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,           # Detect only one face
    refine_landmarks=True,    # Get more detailed landmarks for eyes/lips
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# --- Landmark Indices (MediaPipe - 478 Landmarks Total) ---
# These indices correspond to the points needed for eye and mouth aspect ratios.
# Verify these if MediaPipe updates its model: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png

# Points for EAR calculation (6 points per eye, similar order to dlib)
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

# Points for MAR calculation (map approximately to dlib's 60-67 range)
# We need points corresponding roughly to:
# dlib 60, 64 (mouth corners) -> mp 61, 291
# dlib 61, 67 (inner upper/lower lip vertical) -> mp 82, 14 ?? (Needs verification)
# dlib 62, 66 (inner upper/lower lip vertical) -> mp 81, 312 ?? (Needs verification)
# Let's define indices needed for the function below
# Function expects points: [upper_inner_1, lower_inner_1, upper_inner_2, lower_inner_2, corner_left, corner_right]
MOUTH_MAR_INDICES = [82, 14, 81, 312, 61, 291] # Using plausible points based on dlib mapping


# --- Calculation Functions (Identical logic, just fed different points) ---
def eye_aspect_ratio(eye):
    """Calculate the Eye Aspect Ratio (EAR) to detect blinking."""
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

def mouth_aspect_ratio(mouth_pts):
    """Calculate the Mouth Aspect Ratio (MAR) to detect yawning."""
    # Assumes mouth_pts indices correspond to [82, 14, 81, 312, 61, 291]
    # Compute vertical distances
    A = dist.euclidean(mouth_pts[0], mouth_pts[1]) # distance between point 82 and 14
    B = dist.euclidean(mouth_pts[2], mouth_pts[3]) # distance between point 81 and 312
    # Compute horizontal distance
    C = dist.euclidean(mouth_pts[4], mouth_pts[5]) # distance between corner 61 and 291

    # Compute the mouth aspect ratio
    mar = (A + B) / (2.0 * C)
    return mar

# --- Drowsiness Detection Constants ---
EYE_AR_THRESH = 0.23  # Adjusted threshold for MediaPipe (may need tuning)
EYE_AR_CONSEC_FRAMES = 15 # Number of consecutive frames the eye must be below the threshold

MOUTH_AR_THRESH = 0.4 # Adjusted threshold for MediaPipe (may need tuning)
YAWN_CONSEC_FRAMES = 20 # Number of consecutive frames mouth must be open wide

# --- Counters and Flags ---
closed_eye_frames_counter = 0 # Counts consecutive frames with low EAR
eye_closed_start = None
eye_closed_duration = 0
drowsy_alert_triggered = False # Tracks if drowsy alert is active

yawn_frames_counter = 0       # Counts consecutive frames with high MAR
yawn_alert_triggered = False  # Tracks if yawn alert is active

# --- Video Capture ---
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

if not cap.isOpened():
    print("Error: Could not open video source.")
    exit()

print("Starting drowsiness detection... Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame.")
        break

    # Flip frame horizontally for a later selfie-view display
    # and convert the BGR image to RGB.
    frame = cv2.flip(frame, 1)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and find face landmarks
    results = face_mesh.process(image_rgb)

    # Reset flags/states if no face detected
    if not results.multi_face_landmarks:
        closed_eye_frames_counter = 0
        yawn_frames_counter = 0
        drowsy_alert_triggered = False # Reset alert if face is lost
        yawn_alert_triggered = False
        eye_closed_start = None
    else:
        # Assuming only one face
        face_landmarks = results.multi_face_landmarks[0]

        # --- Extract Landmarks ---
        h, w, _ = frame.shape
        landmarks_np = np.array([(int(lm.x * w), int(lm.y * h)) for lm in face_landmarks.landmark])

        # --- Get Eye and Mouth Points ---
        left_eye = landmarks_np[LEFT_EYE_INDICES]
        right_eye = landmarks_np[RIGHT_EYE_INDICES]
        mouth = landmarks_np[MOUTH_MAR_INDICES]

        # --- Calculate Ratios ---
        left_EAR = eye_aspect_ratio(left_eye)
        right_EAR = eye_aspect_ratio(right_eye)
        ear = (left_EAR + right_EAR) / 2.0
        mouth_MAR = mouth_aspect_ratio(mouth)

        # --- Drowsiness Detection Logic ---

        # 1. Check Eye Closure (Low EAR)
        if ear < EYE_AR_THRESH:
            closed_eye_frames_counter += 1

            # Start timer when eyes first close
            if eye_closed_start is None:
                eye_closed_start = time.time()

            # If eyes closed for sufficient frames, trigger alert
            if closed_eye_frames_counter >= EYE_AR_CONSEC_FRAMES:
                cv2.putText(frame, "DROWSY ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if not drowsy_alert_triggered:
                    print("ALERT: Drowsiness detected (Eyes Closed)")
                    winsound.Beep(1000, 500)  # Beep at 1000 Hz for 500ms
                    drowsy_alert_triggered = True # Prevent continuous beeping for this closure period
        else:
            # Eyes are open, reset counter and potentially duration
            if eye_closed_start is not None:
                eye_closed_duration = time.time() - eye_closed_start
                # print(f"Eye closed duration: {eye_closed_duration:.2f}s") # Optional debug
                # Here you could potentially send `eye_closed_duration` if needed

            closed_eye_frames_counter = 0
            drowsy_alert_triggered = False # Reset alert trigger
            eye_closed_start = None

        # 2. Check Yawning (High MAR)
        if mouth_MAR > MOUTH_AR_THRESH:
            yawn_frames_counter += 1

            # If mouth open wide for sufficient frames, trigger alert
            if yawn_frames_counter >= YAWN_CONSEC_FRAMES:
                 if not yawn_alert_triggered: # Trigger only once per yawn sequence
                    print("ALERT: Yawning Detected")
                    cv2.putText(frame, "YAWNING ALERT!", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    winsound.Beep(800, 300)
                    yawn_alert_triggered = True
            # Display ongoing yawn alert text while flag is true
            if yawn_alert_triggered:
                 cv2.putText(frame, "YAWNING ALERT!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        else:
            # Mouth is not wide open, reset counter and alert flag
            yawn_frames_counter = 0
            yawn_alert_triggered = False


        # --- Display Ratios (for debugging/tuning) ---
        cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"MAR: {mouth_MAR:.2f}", (300, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # --- Optional: Draw Landmarks ---
        # Draw eye landmarks
        # for point in left_eye: cv2.circle(frame, tuple(point), 1, (0, 255, 255), -1)
        # for point in right_eye: cv2.circle(frame, tuple(point), 1, (0, 255, 255), -1)
        # Draw mouth landmarks used for MAR
        # for i in range(len(mouth)): cv2.circle(frame, tuple(mouth[i]), 1, (255, 0, 255), -1)


    # Display the resulting frame
    cv2.imshow("Drowsiness Detection (MediaPipe)", frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(5) & 0xFF == ord('q'): # Use waitKey(5) for smoother video
        break

# --- Cleanup ---
print("Exiting...")
face_mesh.close()
cap.release()
cv2.destroyAllWindows()