import serial
import time

# --- Configuration ---
SERIAL_PORT = 'COM4'  # <<<--- CHANGE THIS! Find your Arduino's port name.
                      # Examples:
                      # Windows: 'COM3', 'COM4', etc.
                      # Linux: '/dev/ttyACM0', '/dev/ttyUSB0', etc.
                      # macOS: '/dev/cu.usbmodemXXXX', '/dev/cu.usbserial-XXXX', etc.
BAUD_RATE = 115200      # Must match the baud rate in your Arduino's Serial.begin()
# --- End Configuration ---

print(f"Attempting to connect to port {SERIAL_PORT} at {BAUD_RATE} baud...")

try:
    # Establish serial connection (with timeout)
    # Using 'with' ensures the port is closed automatically
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print(f"Successfully connected to {SERIAL_PORT}.")
        print("Waiting for Arduino data... Press Ctrl+C to exit.")

        while True:
            try:
                # Read one line from the serial port
                line = ser.readline()

                # Check if any data was actually read (timeout might return empty)
                if line:
                    # Decode bytes to a string, remove leading/trailing whitespace/newlines
                    message = line.decode('utf-8', errors='ignore').strip()

                    # Optional: Print everything received from Arduino for debugging
                    # print(f"Arduino Raw: {line}") # Raw bytes
                    # print(f"Arduino Decoded: '{message}'") # Decoded string

                    # Check if the specific message was received
                    if message == "Abnormality detected!":
                        print(">>> Muscle Peaked <<<") # Print the desired output

            except serial.SerialException as e:
                print(f"Serial error: {e}")
                print("Attempting to reconnect...")
                time.sleep(3) # Wait before retrying connection implicitly by loop
                # Note: The 'with' statement might exit here, consider a loop around 'with' for robust reconnect
                break # Exit inner loop on serial error within 'with'
            except UnicodeDecodeError:
                print("Warning: Could not decode received bytes as UTF-8. Skipping line.")
            except KeyboardInterrupt:
                print("\nExiting due to Ctrl+C.")
                break # Exit the loop

except serial.SerialException as e:
    print(f"Error: Could not open serial port {SERIAL_PORT}.")
    print(f"Details: {e}")
    print("Troubleshooting:")
    print("- Is the Arduino plugged in?")
    print(f"- Is '{SERIAL_PORT}' the correct port name?")
    print("- Is another program (like the Arduino Serial Monitor) using the port?")
    print("- Do you have the necessary permissions (especially on Linux)?")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    print("Script finished.")