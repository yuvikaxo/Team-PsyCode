import cv2
import numpy as np
import time
from collections import deque

# --- Constants ---
# Drowsiness Thresholds (Adapted from your dlib script)
LONG_CLOSURE_DURATION_THRESHOLD = 2.0 # Seconds eyes must be *undetected* for drowsy alert
BLINK_RATE_WINDOW = 30.0           # Seconds to check blink rate over
BLINK_THRESHOLD_LOW = 5              # Min blinks in window for fatigue alert
BLINK_THRESHOLD_HIGH = 20            # Max blinks in window for high-rate alert
# YAWN_CONSEC_FRAMES = 10 # Experimental: Frames mouth needs to be 'open' (if using mouth cascade)

# --- Haar Cascade Paths ---
FACE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
EYE_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml'
# MOUTH_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_smile.xml' # Optional/Experimental

# --- Detection Parameters (CRITICAL TUNING FOR PI ZERO) ---
FRAME_WIDTH = 320   # Start small for Pi Zero
FACE_SCALE_FACTOR = 1.2 # Adjust between 1.1 (sensitive, slow) and 1.4 (less sensitive, faster)
FACE_MIN_NEIGHBORS = 4  # Adjust: Higher = fewer false positives, might miss faces
FACE_MIN_SIZE = (40, 40)# Minimum face size (adjust based on distance)

EYE_SCALE_FACTOR = 1.1
EYE_MIN_NEIGHBORS = 3   # Often needs to be lower than face
EYE_MIN_SIZE = (20, 20) # Adjust

# MOUTH_SCALE_FACTOR = 1.3 # If using mouth cascade
# MOUTH_MIN_NEIGHBORS = 10
# MOUTH_MIN_SIZE = (25, 25)
# MOUTH_YAWN_HEIGHT_THRESHOLD = 30 # Pixels - VERY EXPERIMENTAL

# --- State Variables ---
# Blink Rate Tracking
blink_counter_for_rate = 0
blink_rate_start_time = time.time()

# Eye Closure Tracking
eye_closure_start_time = None
long_closure_alert_active = False

# General Blink Detection (State Machine)
eyes_detected_last_frame = False # Assume eyes start open or undetected initially

# Yawn Tracking (Experimental)
# yawn_open_counter = 0
# yawn_alert_active = False

# --- Load Classifiers ---
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)
# mouth_cascade = cv2.CascadeClassifier(MOUTH_CASCADE_PATH) # Optional

if face_cascade.empty(): print("ERROR: Could not load face cascade"); exit()
if eye_cascade.empty(): print("ERROR: Could not load eye cascade"); exit()
# if mouth_cascade.empty(): print("WARNING: Could not load mouth cascade. Yawn detection disabled.")

# --- Alert Function (Replaces winsound) ---
def trigger_alert(message_type):
    """Prints alert messages to the console."""
    print("-----------------------------------------")
    if message_type == "DROWSY_CLOSURE":
        print(f"ALERT: Potential Drowsiness! Eyes closed > {LONG_CLOSURE_DURATION_THRESHOLD:.1f}s")
    elif message_type == "LOW_BLINK_RATE":
        print(f"ALERT: Low Blink Rate! (<{BLINK_THRESHOLD_LOW} blinks/{int(BLINK_RATE_WINDOW)}s)")
    elif message_type == "HIGH_BLINK_RATE":
        print(f"ALERT: High Blink Rate! (>{BLINK_THRESHOLD_HIGH} blinks/{int(BLINK_RATE_WINDOW)}s)")
    elif message_type == "YAWN":
        print("ALERT: Yawning Detected!")
    else:
        print(f"ALERT: {message_type}") # Generic
    print("-----------------------------------------")
    # --- Add GPIO Trigger Here (Optional) ---
    # import RPi.GPIO as GPIO
    # WARNING_PIN = 18 # Example
    # GPIO.setmode(GPIO.BCM) # Ensure setup somewhere
    # GPIO.setup(WARNING_PIN, GPIO.OUT)
    # GPIO.output(WARNING_PIN, GPIO.HIGH)
    # time.sleep(0.5) # Beep duration
    # GPIO.output(WARNING_PIN, GPIO.LOW)
    # --- End GPIO Trigger ---


# --- Main Loop ---
print("[INFO] Initializing camera...")
vs = cv2.VideoCapture(0)
if not vs.isOpened(): print("ERROR: Cannot open camera"); exit()
time.sleep(2.0)

print("[INFO] Starting video stream loop...")
last_frame_time = time.time()
frame_count_fps = 0

while True:
    ret, frame = vs.read()
    if not ret: print("[WARN] Failed to grab frame"); continue

    # --- Performance Measurement ---
    frame_count_fps += 1
    current_time_fps = time.time()
    elapsed_fps = current_time_fps - last_frame_time
    if elapsed_fps >= 5.0: # Print FPS every 5 seconds
        fps = frame_count_fps / elapsed_fps
        print(f"[INFO] Approx FPS: {fps:.2f}")
        last_frame_time = current_time_fps
        frame_count_fps = 0

    # --- Frame Preparation ---
    height = int(frame.shape[0] * (FRAME_WIDTH / frame.shape[1]))
    frame = cv2.resize(frame, (FRAME_WIDTH, height), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # gray = cv2.equalizeHist(gray) # Optional: Test if helps contrast

    # --- Face Detection ---
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=FACE_SCALE_FACTOR, minNeighbors=FACE_MIN_NEIGHBORS,
        minSize=FACE_MIN_SIZE, flags=cv2.CASCADE_SCALE_IMAGE
    )

    eyes_detected_this_frame = False
    current_closure_duration = 0.0

    for (x, y, w, h) in faces:
        # Draw face box (optional - comment out for speed)
        # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 1)

        # --- Eye Detection within Face ROI ---
        eye_roi_gray = gray[y : y + int(h/1.8), x : x+w] # Upper part of face
        eyes = eye_cascade.detectMultiScale(
            eye_roi_gray, scaleFactor=EYE_SCALE_FACTOR, minNeighbors=EYE_MIN_NEIGHBORS,
            minSize=EYE_MIN_SIZE, flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(eyes) > 0:
            eyes_detected_this_frame = True
            # Draw eye boxes (optional - comment out for speed)
            # for (ex, ey, ew, eh) in eyes:
            #     cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 1)

        # --- Yawn Detection (Experimental) ---
        # if not mouth_cascade.empty():
        #    mouth_roi_gray = gray[y + int(h/1.8) : y + h, x : x+w] # Lower part
        #    mouths = mouth_cascade.detectMultiScale(...) # Add params
        #    if len(mouths) > 0:
        #        # Check height or just presence
        #        # ... update yawn_open_counter ...
        #    else:
        #        # ... reset yawn_open_counter ...
        # --- End Yawn ---

        break # Process only first detected face

    # --- State Machine for Blink/Closure Detection ---
    current_time = time.time()

    # 1. Eyes are currently DETECTED
    if eyes_detected_this_frame:
        if not eyes_detected_last_frame:
             # Transition: Eyes just OPENED (was closed before)
             # This marks the *end* of a closure. If it was a short one, count it as a blink.
             if eye_closure_start_time is not None:
                 blink_duration = current_time - eye_closure_start_time
                 # Count as blink only if it wasn't a long closure (avoids double counting)
                 # And only if duration is reasonable (not an instant flicker)
                 if 0.05 < blink_duration < LONG_CLOSURE_DURATION_THRESHOLD:
                     blink_counter_for_rate += 1
                     # print(f"[DEBUG] Blink detected, duration: {blink_duration:.2f}s, Count: {blink_counter_for_rate}") # Debug
             eye_closure_start_time = None # Reset closure timer
             long_closure_alert_active = False # Can trigger alert again if eyes close long enough

        eyes_detected_last_frame = True

    # 2. Eyes are currently UNDETECTED
    else:
        if eyes_detected_last_frame:
            # Transition: Eyes just CLOSED (was open before)
            eye_closure_start_time = current_time # Start timing the closure

        # Check for long closure if eyes are still closed
        if eye_closure_start_time is not None:
            current_closure_duration = current_time - eye_closure_start_time
            if current_closure_duration > LONG_CLOSURE_DURATION_THRESHOLD and not long_closure_alert_active:
                trigger_alert("DROWSY_CLOSURE")
                long_closure_alert_active = True # Prevent continuous alerts for this closure event

        eyes_detected_last_frame = False

    # --- Check Blink Rate Periodically ---
    if current_time - blink_rate_start_time > BLINK_RATE_WINDOW:
        print(f"[INFO] Blink rate check: {blink_counter_for_rate} blinks in last {BLINK_RATE_WINDOW:.0f}s")
        if blink_counter_for_rate < BLINK_THRESHOLD_LOW:
            trigger_alert("LOW_BLINK_RATE")
        elif blink_counter_for_rate > BLINK_THRESHOLD_HIGH:
            trigger_alert("HIGH_BLINK_RATE")

        # Reset for next window
        blink_counter_for_rate = 0
        blink_rate_start_time = current_time

    # --- Check Yawn Alert (If Enabled & Logic Added) ---
    # if yawn_open_counter >= YAWN_CONSEC_FRAMES and not yawn_alert_active:
    #     trigger_alert("YAWN")
    #     yawn_alert_active = True
    # elif yawn_open_counter == 0: # Reset if mouth not detected as 'yawning'
    #     yawn_alert_active = False

    # --- Display Status on Frame (Optional) ---
    # cv2.putText(frame, f"Blinks (Rate): {blink_counter_for_rate}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    # if eye_closure_start_time:
    #     cv2.putText(frame, f"Eyes Closed: {current_closure_duration:.1f}s", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
    # if long_closure_alert_active:
    #      cv2.putText(frame, "ALERT: LONG CLOSURE!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    # Add text for other alerts if needed

    # --- Show Frame (Comment out for headless operation) ---
    cv2.imshow("Pi Zero Drowsiness Detection (Haar)", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    # --- Add small delay? Not usually needed if FPS is low ---
    # time.sleep(0.01)

# --- Cleanup ---
print("[INFO] Cleaning up...")
cv2.destroyAllWindows()
vs.release()
# if using GPIO: GPIO.cleanup()