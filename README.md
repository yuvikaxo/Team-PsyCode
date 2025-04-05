IoT-Integrated Cognitive Fatigue Detection Using EXG

Biosignals & Computer VisionThis project detects driver drowsiness using **EMG (Electromyography) signals** captured through the **BioAmp EXG Pill** sensor connected to an Arduino. Real-time data is visualized using Python, and alerts are generated (beep sounds) when muscle activity drops below a defined threshold combined with eye and face data from Raspberry camera module — indicating possible fatigue or drowsiness.

---

##  Key Features

- Real-time EMG signal visualization using Biosignals, electrodes, arduino, matplotlib
- Real time eye and face monitoring using Computer Vision, Camera Module, and Raspeberry Pi
- Real time Sleep logging systems
- Map and Fatigue Predictor – Input your journey destination, and using past sleep data, the system estimates when you are likely to experience drowsiness during the trip.
- User Friendly cost effective app for admins and Drivers
  

---

##  Hardware Used

- [BioAmp EXG Pill](https://github.com/upsidedownlabs/BioAmp-EXG-Pill)
- Arduino UNO / Nano
- Jumper wires
- Electrodes (placed on wrist and forearm)
- Raspberry Pi
- Raspberry Pi Camera Module

---

##  Software Used

- **Arduino IDE** (for firmware)
- **Python 3.x**
  - `pyserial`
  - `matplotlib`
  - `winsound` (for beeping on drowsiness detection)
  - `csv`
  - `collections` (for buffering)
- JavaScript 
- React Native(for app)

---

##  How to Run

### 1. Upload Arduino Code

Upload the Arduino sketch to your board to read analog EMG values from the BioAmp EXG Pill.

### 2. Connect Hardware

- Connect the BioAmp EXG Pill's analog output to **A0** pin on Arduino.
- Ensure electrodes are properly placed on the **wrist and forearm**.
- Plug in your Arduino via USB.
- Connect Camera module to Raspberry Pi
- Feed opencv code to Raspberry Pi: haar-cascades-raspberrypi.py

### 3. Run Python Code

- Install required Python libraries:
- Update the correct COM port in the Python script (e.g., COM4).
- Run the script emg_visualiser.py and haar-cascades-raspberrypi.py

### 4. Output
- Real-time waveform of muscle activity through EMG signals will appear.
- Blink rate will be monitored through camera
- A CSV file will be created with timestamped EMG data.
- Beep sound plays when muscle activity is too low or eyes are closed for more than threshold value(possible drowsiness).


  

