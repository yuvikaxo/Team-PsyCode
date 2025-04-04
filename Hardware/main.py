import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time

# --- Configuration ---
SERIAL_PORT = 'COM4'  # !!! CHANGE THIS to your Arduino's serial port !!!
BAUD_RATE = 9600      # Must match the baud rate in your Arduino sketch
MAX_DATA_POINTS = 200 # Number of data points to display on the plot at once
Y_LIMIT_MIN = 0       # Minimum expected analog value (adjust if needed)
Y_LIMIT_MAX = 1024    # Maximum expected analog value (adjust if needed)
UPDATE_INTERVAL_MS = 10 # How often to update the plot (milliseconds)
# ---------------------

# --- Global Variables ---
ser = None # Will hold the serial connection object
data_buffer = deque(maxlen=MAX_DATA_POINTS) # Store the latest data points

# --- Plot Setup ---
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1) # Create an empty line object
ax.set_ylim(Y_LIMIT_MIN, Y_LIMIT_MAX)
ax.set_xlim(0, MAX_DATA_POINTS)
ax.set_xlabel("Time points")
ax.set_ylabel("Analog Reading (0-1023)")
ax.set_title("Real-time ECG Waveform")
ax.grid(True)

# --- Functions ---

def connect_serial():
    """Attempts to connect to the serial port."""
    global ser
    try:
        print(f"Attempting to connect to {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Allow time for connection to establish
        ser.reset_input_buffer() # Clear any old data
        print("✅ Serial connection established.")
        return True
    except serial.SerialException as e:
        print(f"❌ Error connecting to serial port {SERIAL_PORT}: {e}")
        print("Please check:")
        print("- Is the Arduino plugged in?")
        print("- Is the correct SERIAL_PORT set in the script?")
        print("- Is the Arduino IDE Serial Monitor/Plotter closed?")
        print("- Do you have the necessary drivers installed (e.g., CH340)?")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during serial connection: {e}")
        return False

def init_plot():
    """Initializes the plot line."""
    line.set_data([], [])
    return line,

def update_plot(frame):
    """Reads data from serial and updates the plot."""
    global data_buffer, ser
    if ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                # Read line, decode, strip whitespace, convert to int
                line_bytes = ser.readline()
                line_str = line_bytes.decode('utf-8', errors='ignore').strip()

                if line_str: # Make sure we got some data
                    try:
                        value = int(line_str)
                        data_buffer.append(value)
                        # Update plot data
                        line.set_data(range(len(data_buffer)), data_buffer)
                        # Optional: Auto-adjust X limits if buffer isn't full yet
                        # ax.set_xlim(0, len(data_buffer) if len(data_buffer) > 1 else 1)

                    except ValueError:
                        print(f"Warning: Received non-integer data: '{line_str}'")
                    except Exception as e:
                         print(f"Error processing data: {e}")

        except serial.SerialException as e:
            print(f"Serial Error during read: {e}. Attempting to reconnect...")
            ser.close()
            ser = None
            connect_serial() # Try to reconnect
        except Exception as e:
            print(f"Error in update loop: {e}")
            # Consider closing serial port on generic errors too
            # if ser: ser.close(); ser = None

    # Must return the plot elements that were updated
    return line,

# --- Main Execution ---
if __name__ == "__main__":
    if connect_serial():
        # Create the animation
        ani = animation.FuncAnimation(
            fig,
            update_plot,          # Function to call for each frame
            init_func=init_plot,  # Function to call at the start
            interval=UPDATE_INTERVAL_MS, # Delay between frames in ms
            blit=True,            # Optimize redrawing (might need False on some systems)
            cache_frame_data=False # Avoid caching issues with serial data
        )

        try:
            plt.show() # Display the plot window (blocks until closed)
        except Exception as e:
            print(f"Error displaying plot: {e}")
        finally:
            # Ensure serial port is closed when plot is closed or script stops
            if ser and ser.is_open:
                ser.close()
                print("Serial port closed.")
    else:
        print("Could not connect to serial port. Exiting.")

    print("Script finished.")