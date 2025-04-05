import serial
import time

# Replace with your correct COM port (Check in Arduino IDE or Device Manager)
ser = serial.Serial('COM3', 9600)  # For Windows
# ser = serial.Serial('/dev/ttyUSB0', 9600)  # For Linux

time.sleep(2)  # wait for Arduino to reset

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            emg_value = int(line)
            print("EMG Value:", emg_value)
    except ValueError:
        continue
