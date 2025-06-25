# Drowsiness Detection & Alert System with Arduino and Python

This project implements a real-time **driver drowsiness detection system** using computer vision (MediaPipe), hardware alerting (Arduino), and cloud logging (ThingSpeak). It monitors the driver’s eye activity through a webcam and triggers alerts if drowsiness is detected.

---

## 🚀 Features

* 👁️ Detects **eye aspect ratio (EAR)** using MediaPipe face mesh.
* ⏱️ Triggers alert if eyes are closed for **≥ 3 seconds** (prolonged blink).
* 🔔 Sends signal to **Arduino** to activate a buzzer.
* 📊 Logs data to **ThingSpeak**:

  * Total number of blinks
  * Number of prolonged closures (drowsy events)
* 🧠 Real-time face and eye tracking using OpenCV.

---

## 💠 Technologies Used

| Component     | Technology                   |
| ------------- | ---------------------------- |
| Eye Detection | MediaPipe Face Mesh + OpenCV |
| Alert System  | Arduino UNO with buzzer      |
| Communication | PySerial (Serial via USB)    |
| Data Logging  | ThingSpeak API               |
| Languages     | Python, Arduino C            |

---

## 📷 System Overview

1. **Webcam** captures real-time video.
2. **MediaPipe** processes facial landmarks, especially eyes.
3. Calculates **EAR** (Eye Aspect Ratio) to monitor blink and closure.
4. If eyes closed ≥ 3 seconds:

   * Sends `'2'` to Arduino → double beep.
   * Logs event to ThingSpeak.
5. Eyes reopen → sends `'0'` to Arduino → stop buzzer.

---

## ⚙️ Setup Instructions

### 1. 👤 Python Environment

Install dependencies:

```bash
pip install opencv-python mediapipe numpy pyserial thingspeak
```

### 2. 🔌 Hardware Setup

* Arduino UNO
* Active buzzer connected to a digital pin (e.g., pin 8)
* Connect via USB

Upload `arduino_alert_final.ino` using Arduino IDE.
The sketch listens for:

* `'2'` → double beep
* `'0'` → stop buzzer

### 3. 🧲 Run Detection Script

```bash
python drowsiness_detection_final.py
```

Make sure the correct COM port is configured in the Python file:

```python
arduino = serial.Serial('COM3', 9600)
```

Change `'COM3'` if you're on a different OS (e.g., `/dev/ttyUSB0` on Linux).

---

## 🔐 ThingSpeak Integration

Update the following lines in the Python script with your own ThingSpeak credentials:

```python
channel_id = "YOUR_CHANNEL_ID"
write_key = "YOUR_API_KEY"
```
