import cv2
import numpy as np
import time
from collections import deque

# --- User Configuration ---
PI_IP_ADDRESS = "192.168.228.77"  # <<<--- CHANGE THIS to your Pi's actual IP Address!
PORT = 5001                          # Port used in libcamera-vid command on Pi

# --- Drowsiness Thresholds ---
LONG_CLOSURE_DURATION_THRESHOLD = 2.0 # Seconds eyes must be undetected for drowsy alert
BLINK_RATE_WINDOW = 30.0              # Seconds to check blink rate over
BLINK_THRESHOLD_LOW = 5               # Min blinks in window for fatigue alert
BLINK_THRESHOLD_HIGH = 20             # Max blinks in window for high-rate alert

# --- Haar Cascade Paths (Uses standard paths from opencv-python pip package) ---
try:
    HAARCASCADE_BASE_PATH = cv2.data.haarcascades
    FACE_CASCADE_PATH = HAARCASCADE_BASE_PATH + 'haarcascade_frontalface_default.xml'
    EYE_CASCADE_PATH = HAARCASCADE_BASE_PATH + 'haarcascade_eye_tree_eyeglasses.xml'
    # MOUTH_CASCADE_PATH = HAARCASCADE_BASE_PATH + 'haarcascade_smile.xml' # Optional/Experimental
except AttributeError:
    print("ERROR: Could not find cv2.data.haarcascades.")
    print("Ensure opencv-python is installed correctly via pip.")
    print("If using a different OpenCV install, you may need to provide the full path to cascade files.")
    exit()

# --- Detection Parameters (Tune these based on performance and accuracy on your PC) ---
# Processing frame width (can resize if needed, but stream is 640x480)
PROC_FRAME_WIDTH = 640
# Face Detection
FACE_SCALE_FACTOR = 1.15 # Can be lower (more sensitive) on PC than Pi Zero (e.g., 1.1 to 1.3)
FACE_MIN_NEIGHBORS = 5   # Higher reduces false positives (e.g., 3 to 6)
FACE_MIN_SIZE = (40, 40) # Minimum face size to detect (pixels)
# Eye Detection
EYE_SCALE_FACTOR = 1.1
EYE_MIN_NEIGHBORS = 3
EYE_MIN_SIZE = (20, 20)

# --- State Variables ---
blink_counter_for_rate = 0
blink_rate_start_time = time.time()
eye_closure_start_time = None
long_closure_alert_active = False
eyes_detected_last_frame = False # Assume eyes start open or undetected

# --- Load Classifiers ---
print("[INFO] Loading Haar cascades...")
face_cascade = cv2.CascadeClassifier(FACE_CASCADE_PATH)
eye_cascade = cv2.CascadeClassifier(EYE_CASCADE_PATH)
if face_cascade.empty(): print(f"ERROR: Could not load face cascade from {FACE_CASCADE_PATH}"); exit()
if eye_cascade.empty(): print(f"ERROR: Could not load eye cascade from {EYE_CASCADE_PATH}"); exit()
print("[INFO] Cascades loaded successfully.")

# --- Alert Function (Simple console print) ---
def trigger_alert(message_type):
    """Prints alert messages to the console."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("-----------------------------------------")
    print(f"ALERT ({timestamp}): ", end="")
    if message_type == "DROWSY_CLOSURE":
        print(f"Potential Drowsiness! Eyes closed > {LONG_CLOSURE_DURATION_THRESHOLD:.1f}s")
    elif message_type == "LOW_BLINK_RATE":
        print(f"Low Blink Rate! (<{BLINK_THRESHOLD_LOW} blinks/{int(BLINK_RATE_WINDOW)}s)")
    elif message_type == "HIGH_BLINK_RATE":
        print(f"High Blink Rate! (>{BLINK_THRESHOLD_HIGH} blinks/{int(BLINK_RATE_WINDOW)}s)")
    # elif message_type == "YAWN": # If you implement yawn detection
    #     print("Yawning Detected!")
    else:
        print(f"Generic Alert - {message_type}")
    print("-----------------------------------------")

# --- Connect to Pi Stream ---
stream_url = f"tcp://{PI_IP_ADDRESS}:{PORT}"
# Try this alternative if the first one struggles
# stream_url = f"tcp/h264://{PI_IP_ADDRESS}:{PORT}"

print(f"[INFO] Attempting to connect to stream: {stream_url}")
# Explicitly try FFMPEG backend which is often good for network streams
vs = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)

# Check if connection was successful
if not vs.isOpened():
    print("="*30)
    print("ERROR: Cannot open network stream.")
    print("Troubleshooting:")
    print(f"- Is the libcamera-vid command running correctly on the Pi ({PI_IP_ADDRESS})?")
    print(f"- Is the IP address '{PI_IP_ADDRESS}' and Port '{PORT}' correct?")
    print(f"- Is the Pi reachable? Try: ping {PI_IP_ADDRESS}")
    print("- Is a firewall blocking the connection on the Pi or (more likely) this PC?")
    print("- Try the alternative stream_url format in the script.")
    print("="*30)
    exit()
else:
    print("[INFO] Stream connection successful. Waiting for buffer...")
    time.sleep(2.0) # Give stream buffer a moment to fill
    print("[INFO] Starting detection loop...")

# --- Main Loop ---
last_frame_time = time.time()
frame_count_fps = 0

while True:
    # --- Grab frame from Network Stream ---
    ret, frame = vs.read()

    # --- Check if frame was received correctly ---
    if not ret or frame is None:
        print("[WARN] Failed to grab frame or frame is empty. Stream may have ended or connection lost.")
        # Optional: Implement a reconnection logic here
        time.sleep(0.5) # Pause briefly before trying again
        # Try to reopen
        vs.release()
        vs.open(stream_url, cv2.CAP_FFMPEG)
        if not vs.isOpened():
            print("[ERROR] Failed to reopen stream. Exiting.")
            break
        else:
            print("[INFO] Re-opened stream connection.")
            time.sleep(1.0) # Wait after reopen
            continue # Skip rest of loop for this iteration

    # --- Performance Measurement (Optional) ---
    frame_count_fps += 1
    current_time_fps = time.time()
    elapsed_fps = current_time_fps - last_frame_time
    if elapsed_fps >= 5.0: # Print FPS every 5 seconds
        fps = frame_count_fps / elapsed_fps
        # print(f"[INFO] Approx PC Processing FPS: {fps:.2f}") # Uncomment to see FPS
        last_frame_time = current_time_fps
        frame_count_fps = 0

    # --- Frame Preparation ---
    # Optional resizing if you want to process at a different resolution than the stream
    # current_height, current_width = frame.shape[:2]
    # if current_width != PROC_FRAME_WIDTH:
    #    ratio = PROC_FRAME_WIDTH / float(current_width)
    #    dim = (PROC_FRAME_WIDTH, int(current_height * ratio))
    #    frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Optional: gray = cv2.equalizeHist(gray) # Test if helps contrast

    # --- Face Detection ---
    faces = [] # Ensure faces is defined even if detection fails
    try:
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=FACE_SCALE_FACTOR,
            minNeighbors=FACE_MIN_NEIGHBORS,
            minSize=FACE_MIN_SIZE,
            flags=cv2.CASCADE_SCALE_IMAGE
        )
    except cv2.error as e:
        print(f"[WARN] Error during face detection: {e}")
        # Decide how to handle - skip frame?
        continue # Skip processing rest of this frame

    eyes_detected_this_frame = False
    current_closure_duration = 0.0 # Reset for this frame

    # --- Process (First Detected) Face ---
    if len(faces) > 0:
        (x, y, w, h) = faces[0] # Get coordinates of the first face
        # Optional: Draw face rectangle
        # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # --- Eye Detection within Face ROI ---
        # Create ROI (Region of Interest) for eyes in the upper part of the face
        eye_roi_gray = gray[y : y + int(h/1.8), x : x+w]
        eye_roi_color = frame[y : y + int(h/1.8), x : x+w] # For drawing rectangles in color

        eyes = [] # Ensure eyes is defined
        try:
            eyes = eye_cascade.detectMultiScale(
                eye_roi_gray,
                scaleFactor=EYE_SCALE_FACTOR,
                minNeighbors=EYE_MIN_NEIGHBORS,
                minSize=EYE_MIN_SIZE,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
        except cv2.error as e:
            print(f"[WARN] Error during eye detection: {e}")
            # Eyes will remain undetected for this frame if error occurs

        if len(eyes) > 0:
            eyes_detected_this_frame = True
            # Optional: Draw eye rectangles (adjust coordinates relative to the main frame)
            # for (ex, ey, ew, eh) in eyes:
            #     cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 1)
        # else: No eyes detected in the face ROI

    # else: No faces detected in the frame

    # --- State Machine for Blink/Closure Detection ---
    current_time = time.time()

    # 1. Eyes are currently DETECTED (or face wasn't found)
    if eyes_detected_this_frame:
        if not eyes_detected_last_frame:
             # Transition: Eyes just OPENED (was closed/undetected before)
             # Mark end of a potential blink/closure.
             if eye_closure_start_time is not None:
                 blink_duration = current_time - eye_closure_start_time
                 # Count as blink only if duration is reasonable (not a flicker, not a long closure)
                 if 0.05 < blink_duration < LONG_CLOSURE_DURATION_THRESHOLD:
                     blink_counter_for_rate += 1
                     # print(f"[DEBUG] Blink detected. Count: {blink_counter_for_rate}") # Debug
             eye_closure_start_time = None # Reset closure timer
             long_closure_alert_active = False # Can trigger alert again

        eyes_detected_last_frame = True

    # 2. Eyes are currently UNDETECTED (and a face *was* found)
    elif len(faces) > 0: # Only count closure if a face was present
        if eyes_detected_last_frame:
            # Transition: Eyes just CLOSED (was open before)
            eye_closure_start_time = current_time # Start timing the closure

        # Check for long closure if eyes are still closed
        if eye_closure_start_time is not None:
            current_closure_duration = current_time - eye_closure_start_time
            if current_closure_duration > LONG_CLOSURE_DURATION_THRESHOLD and not long_closure_alert_active:
                trigger_alert("DROWSY_CLOSURE")
                long_closure_alert_active = True # Prevent continuous alerts for this single event

        eyes_detected_last_frame = False
    # else: No face detected, don't change eye state based on lack of eyes alone

    # --- Check Blink Rate Periodically ---
    if current_time - blink_rate_start_time > BLINK_RATE_WINDOW:
        # print(f"[INFO] Blink rate check: {blink_counter_for_rate} blinks in last {BLINK_RATE_WINDOW:.0f}s") # Debug
        if blink_counter_for_rate < BLINK_THRESHOLD_LOW:
            trigger_alert("LOW_BLINK_RATE")
        elif blink_counter_for_rate > BLINK_THRESHOLD_HIGH:
            trigger_alert("HIGH_BLINK_RATE")

        # Reset for next window
        blink_counter_for_rate = 0
        blink_rate_start_time = current_time

    # --- Display Status on Frame (Optional) ---
    # Add text to the frame for visual feedback
    status_text = ""
    if long_closure_alert_active:
        status_text = f"ALERT: EYES CLOSED > {LONG_CLOSURE_DURATION_THRESHOLD:.1f}s!"
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    elif eye_closure_start_time is not None:
         status_text = f"Eyes Closed: {current_closure_duration:.1f}s"
         cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

    # cv2.putText(frame, f"Blinks (Rate Window): {blink_counter_for_rate}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)


    # --- Show Frame on PC ---
    cv2.imshow("Pi Stream Processed on PC - Press 'q' to Quit", frame)
    key = cv2.waitKey(1) & 0xFF

    # --- Quit Condition ---
    if key == ord('q'):
        print("[INFO] 'q' pressed, exiting...")
        break

# --- Cleanup ---
print("[INFO] Cleaning up resources...")
vs.release()
cv2.destroyAllWindows()
print("[INFO] Exited.")