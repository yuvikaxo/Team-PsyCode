import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
import csv
import os
import winsound

# --- Configuration ---
SERIAL_PORT = 'COM4'       # !!! CHANGE THIS to your Arduino's serial port !!!
BAUD_RATE = 9600           # Must match the baud rate in your Arduino sketch
MAX_DATA_POINTS = 200      # Number of data points to display on the plot
Y_LIMIT_MIN = 0
Y_LIMIT_MAX = 1024
UPDATE_INTERVAL_MS = 10    # Milliseconds between plot updates

# Drowsiness Detection Config
DROWSINESS_THRESHOLD = 200       # EMG value considered as low (drowsy)
DROWSY_DURATION_SECONDS = 3      # Time duration under threshold to trigger alert
BEEP_FREQUENCY = 1000            # Hz
BEEP_DURATION = 500              # milliseconds

# Logging Config
CSV_FILENAME = "emg_log.csv"

# --- Globals ---
ser = None
data_buffer = deque(maxlen=MAX_DATA_POINTS)
last_low_start_time = None
drowsy_alert_triggered = False

# Prepare CSV
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "EMG_Value"])

# --- Plot Setup ---
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1)
ax.set_ylim(Y_LIMIT_MIN, Y_LIMIT_MAX)
ax.set_xlim(0, MAX_DATA_POINTS)
ax.set_xlabel("Time points")
ax.set_ylabel("Analog Reading (0-1023)")
ax.set_title("Real-time EMG Waveform")
ax.grid(True)

# --- Functions ---
def connect_serial():
    global ser
    try:
        print(f"Attempting to connect to {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        ser.reset_input_buffer()
        print("✅ Serial connection established.")
        return True
    except serial.SerialException as e:
        print(f"❌ Error connecting to serial port {SERIAL_PORT}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def init_plot():
    line.set_data([], [])
    return line,

def update_plot(frame):
    global data_buffer, ser, last_low_start_time, drowsy_alert_triggered

    if ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                line_bytes = ser.readline()
                line_str = line_bytes.decode('utf-8', errors='ignore').strip()

                if line_str:
                    try:
                        value = int(line_str)
                        data_buffer.append(value)
                        line.set_data(range(len(data_buffer)), data_buffer)

                        # --- Log to CSV ---
                        with open(CSV_FILENAME, 'a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([time.time(), value])

                        # --- Drowsiness detection ---
                        current_time = time.time()
                        if value < DROWSINESS_THRESHOLD:
                            if last_low_start_time is None:
                                last_low_start_time = current_time
                            elif (current_time - last_low_start_time) >= DROWSY_DURATION_SECONDS:
                                if not drowsy_alert_triggered:
                                    print("⚠️ Drowsiness Detected! Triggering beep...")
                                    winsound.Beep(BEEP_FREQUENCY, BEEP_DURATION)
                                    drowsy_alert_triggered = True
                        else:
                            last_low_start_time = None
                            drowsy_alert_triggered = False

                    except ValueError:
                        print(f"⚠️ Received non-integer data: '{line_str}'")
        except serial.SerialException as e:
            print(f"Serial Error: {e}. Reconnecting...")
            ser.close()
            ser = None
            connect_serial()
        except Exception as e:
            print(f"Error in update loop: {e}")

    return line,

# --- Main ---
if __name__ == "__main__":
    if connect_serial():
        ani = animation.FuncAnimation(
            fig, update_plot, init_func=init_plot,
            interval=UPDATE_INTERVAL_MS,
            blit=True, cache_frame_data=False
        )

        try:
            plt.show()
        except Exception as e:
            print(f"Error displaying plot: {e}")
        finally:
            if ser and ser.is_open:
                ser.close()
                print("Serial port closed.")
    else:
        print("❌ Could not connect to serial port. Exiting.")

print("✅ Script finished.")
