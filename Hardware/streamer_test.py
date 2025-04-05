import cv2
import time

# --- Configuration ---
PI_IP = "192.168.228.77"  # <<<--- CHANGE THIS to your Pi's IP
PORT = 5001
# Try different URL formats if the first one fails
# stream_url = f"tcp://{PI_IP}:{PORT}"
stream_url = f"tcp://{PI_IP}:{PORT}"
# --- End Configuration ---

print(f"Attempting to connect to: {stream_url}")

# Try to open the video stream
cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG) # Specify backend explicitly sometimes helps

# Check if connection was successful
if not cap.isOpened():
    print("Error: Could not open video stream.")
    print("Troubleshooting:")
    print(f"- Is the libcamera-vid command running on the Pi ({PI_IP})?")
    print("- Is the Pi reachable? Try pinging it.")
    print("- Is the correct port ({PORT}) being used?")
    print("- Is a firewall blocking the connection on the Pi or Laptop?")
    print("- Try the alternative stream_url format in the script.")
    exit()
else:
    print("Stream opened successfully. Reading frames...")

# Read and display frames
while True:
    ret, frame = cap.read()

    # Check if frame was read successfully
    if not ret:
        print("Error: Could not read frame. Stream might have ended or connection lost.")
        # Optional: Add a delay and retry mechanism
        time.sleep(1) # Wait a second before trying again or exiting
        # Re-try opening the stream
        cap.release()
        cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
             print("Error: Failed to reopen stream. Exiting.")
             break
        else:
             print("Stream reopened...")
             continue # Skip the rest of the loop for this iteration

    # Display the frame
    cv2.imshow('Raspberry Pi Stream', frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
print("Releasing resources...")
cap.release()
cv2.destroyAllWindows()
print("Exited.")