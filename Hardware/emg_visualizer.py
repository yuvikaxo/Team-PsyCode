import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
import sys # To exit gracefully

# --- Configuration ---
SERIAL_PORT = 'COM4'  # !!! CHANGE THIS to your Arduino's serial port !!!
BAUD_RATE = 9600      # Must match the baud rate in your Arduino sketch
MAX_DATA_POINTS = 300 # Number of data points to display (adjust for desired time window)
Y_LIMIT_MIN = 0       # Min expected analog value (0 for Arduino Uno/Nano)
Y_LIMIT_MAX = 1024    # Max expected analog value (1024 for Arduino Uno/Nano)
UPDATE_INTERVAL_MS = 10 # Plot update frequency (milliseconds) - controls animation speed
# ---------------------

# --- Global Variables ---
ser = None
data_buffer = deque(maxlen=MAX_DATA_POINTS) # Fixed-size buffer for plotting

# --- Plot Setup ---
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=1, color='cyan') # Create line object, maybe cyan color
ax.set_ylim(Y_LIMIT_MIN, Y_LIMIT_MAX)
ax.set_xlim(0, MAX_DATA_POINTS)
ax.set_xlabel("Time points")
ax.set_ylabel("Raw EMG Reading (0-1023)")
ax.set_title("Real-time EMG Signal Visualization")
ax.grid(True)
fig.patch.set_facecolor('#2d3748') # Dark background like slate-800
ax.set_facecolor('#1a202c')      # Darker axes background like slate-900
ax.spines['top'].set_color('gray')
ax.spines['bottom'].set_color('gray')
ax.spines['left'].set_color('gray')
ax.spines['right'].set_color('gray')
ax.xaxis.label.set_color('gray')
ax.yaxis.label.set_color('gray')
ax.title.set_color('white')
ax.tick_params(axis='x', colors='gray')
ax.tick_params(axis='y', colors='gray')


# --- Functions ---

def connect_serial():
    """Attempts to connect to the serial port."""
    global ser
    try:
        print(f"Attempting connection to {SERIAL_PORT} at {BAUD_RATE} baud...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Allow time for Arduino reset and connection
        ser.reset_input_buffer()
        print("✅ Serial connection established.")
        return True
    except serial.SerialException as e:
        print(f"❌ Error connecting to serial port {SERIAL_PORT}: {e}")
        print("Troubleshooting tips:")
        print("- Is the Arduino plugged in and running the correct sketch?")
        print("- Is the SERIAL_PORT variable set correctly in this script?")
        print("- Is the Arduino IDE Serial Monitor/Plotter (or other software) CLOSED?")
        print("- Are the necessary drivers (e.g., CH340) installed?")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during serial connection: {e}")
        return False

def init_plot():
    """Initializes the plot line data."""
    line.set_data(range(MAX_DATA_POINTS), [Y_LIMIT_MIN] * MAX_DATA_POINTS) # Start flat
    return line,

def update_plot(frame):
    """Reads data from serial and updates the plot."""
    global data_buffer, ser
    if ser and ser.is_open:
        try:
            # Read multiple lines if available for smoother plotting, but process one logical value
            value = None
            while ser.in_waiting > 0:
                try:
                    line_bytes = ser.readline()
                    line_str = line_bytes.decode('utf-8', errors='ignore').strip()
                    if line_str: # Check if line is not empty
                         value = int(line_str) # Convert the latest valid line to int
                except UnicodeDecodeError:
                    print(f"Warning: Unicode decode error, skipping line: {line_bytes}")
                    continue # Skip this line
                except ValueError:
                    print(f"Warning: Received non-integer data: '{line_str}', skipping.")
                    continue # Skip this line
                except Exception as read_err:
                    print(f"Error reading/processing line: {read_err}")
                    continue # Skip this line

            # If we got a valid value in this update cycle, add it to the buffer
            if value is not None:
                 data_buffer.append(value)
                 # Update plot data (use the current content of deque)
                 y_data = list(data_buffer)
                 # Pad with previous value if buffer not full, for consistent x-axis
                 if len(y_data) < MAX_DATA_POINTS:
                     padding = [y_data[0] if y_data else Y_LIMIT_MIN] * (MAX_DATA_POINTS - len(y_data))
                     y_data = padding + y_data
                 line.set_ydata(y_data) # Only update ydata since x is fixed range

        except serial.SerialException as e:
            print(f"Serial communication error: {e}. Closing port.")
            if ser: ser.close()
            ser = None
            # Attempting reconnect might be added here, or just let it stop.
            plt.close(fig) # Close the plot window on serial error
        except Exception as e:
            print(f"Error in update loop: {e}")
            if ser: ser.close() # Ensure port closure on unexpected errors
            ser = None
            plt.close(fig) # Close the plot window

    # Must return the plot elements that were updated
    return line,

# --- Main Execution ---
if __name__ == "__main__":
    if connect_serial():
        print("Starting visualization... Close the plot window to stop.")
        # Set up the animation
        ani = animation.FuncAnimation(
            fig,
            update_plot,        # Function to call repeatedly
            init_func=init_plot, # Function to set initial plot state
            interval=UPDATE_INTERVAL_MS, # Update frequency
            blit=True,           # Use blitting for faster redraws (might need False on some systems/backends)
            cache_frame_data=False # Important for dynamic data source
        )

        try:
            plt.show() # Display the plot and block until closed
        except Exception as e:
            # Handle cases where plot window might be closed unexpectedly
            print(f"Plot display error or window closed: {e}")
        finally:
            # Ensure serial port is closed when script finishes or plot is closed
            print("Cleaning up...")
            if ser and ser.is_open:
                ser.close()
                print("Serial port closed.")
    else:
        print("Could not connect to serial port. Exiting.")

    print("Script finished.")
    sys.exit() # Ensure script exits cleanly