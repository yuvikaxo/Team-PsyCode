import cv2
import numpy as np
import time
from collections import deque
from picamera2 import Picamera2 # <<<--- IMPORT Picamera2

# --- Constants ---
# ... (keep your existing constants) ...
LONG_CLOSURE_DURATION_THRESHOLD = 2.0
BLINK_RATE_WINDOW = 30.0
BLINK_THRESHOLD_LOW = 5
BLINK_THRESHOLD_HIGH = 20

# --- Haar Cascade Paths ---
# ... (keep your existing paths) ...
FACE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
EYE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml'

# --- Detection Parameters (CRITICAL TUNING FOR PI ZERO) ---
FRAME_WIDTH = 320 # <<<--- Keep this small for Pi Zero!
# Calculate height maintaining aspect ratio (assuming camera default ~4:3 or 16:9)
# Let picamera2 handle aspect ratio by giving it the width.
# We will resize later if needed, but capture smaller first.
FACE_SCALE_FACTOR = 1.2
FACE_MIN_NEIGHBORS = 4
FACE_MIN_SIZE = (40, 40)
EYE_SCALE_FACTOR = 1.1
EYE_MIN_NEIGHBORS = 3
EYE_MIN_SIZE = (20, 20)

# ... (keep other variables like state, alert function etc.) ...
# --- State Variables ---
blink_counter_for_rate = 0
# ... rest of state variables ...
eyes_detected_last_frame = False

# --- Load Classifiers ---
# ... (keep your cascade loading) ...
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)
if face_cascade.empty(): print("ERROR: Could not load face cascade"); exit()
if eye_cascade.empty(): print("ERROR: Could not load eye cascade"); exit()

# --- Alert Function ---
# ... (keep your alert function) ...
def trigger_alert(message_type):
    print("-----------------------------------------")
    # if message_type == "DROWSY_CLOSURE":
    #     # ... rest of alert function ...
    print("-----------------------------------------")


# --- Picamera2 Initialization --- <<<--- MODIFIED SECTION
print("[INFO] Initializing Picamera2...")
picam2 = Picamera2()
# Configure for preview (efficient) and capture numpy arrays
# Request a format OpenCV understands directly (RGB888)
config = picam2.create_preview_configuration(main={"size": (FRAME_WIDTH, int(FRAME_WIDTH * 0.75)), "format": "RGB888"}) # Adjust height ratio if needed
picam2.configure(config)
picam2.start()
# Allow camera sensor to warm up
time.sleep(2.0)
print("[INFO] Camera Initialized. Starting detection loop...")
# --- End Picamera2 Initialization ---

last_frame_time = time.time()
frame_count_fps = 0

while True:
    # --- Frame Capture using Picamera2 --- <<<--- MODIFIED
    # Capture frame as a numpy array (RGB format)
    frame_rgb = picam2.capture_array()
    # Convert RGB to BGR for OpenCV processing
    frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    # No 'ret' check needed like VideoCapture, if capture_array fails it usually throws exception

    # --- Performance Measurement ---
    # ... (keep FPS calculation) ...

    # --- Frame Preparation ---
    # Frame should already be close to FRAME_WIDTH from camera config
    # If you need exact resize (maybe slight difference):
    # height = int(frame.shape[0] * (FRAME_WIDTH / frame.shape[1]))
    # frame = cv2.resize(frame, (FRAME_WIDTH, height), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- Face Detection ---
    # ... (keep face detection logic) ...
    faces = face_cascade.detectMultiScale( ... )

    eyes_detected_this_frame = False
    current_closure_duration = 0.0

    for (x, y, w, h) in faces:
        # ... (keep eye detection logic within face ROI) ...
        eye_roi_gray = gray[y : y + int(h/1.8), x : x+w]
        eyes = eye_cascade.detectMultiScale( ... )

        if len(eyes) > 0:
            eyes_detected_this_frame = True
        break # Process only first face

    # --- State Machine for Blink/Closure Detection ---
    # ... (keep state machine logic) ...
    current_time = time.time()
    # if eyes_detected_this_frame:
    #      # ...
    # else:
    #      # ...

    # --- Check Blink Rate Periodically ---
    # ... (keep blink rate check) ...

    # --- Display Status on Frame (Optional) ---
    # ... (keep or comment out cv2.putText) ...

    # --- Show Frame (Can comment out for headless operation) ---
    cv2.imshow("Pi Zero Drowsiness Detection (Haar)", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

# --- Cleanup ---
print("[INFO] Cleaning up...")
cv2.destroyAllWindows()
picam2.stop() # <<<--- Use picam2 stop method
# if using GPIO: GPIO.cleanup()