import cv2
import mediapipe as mp
import serial
import time
import numpy as np
import thingspeak  

# Initialize MediaPipe Face Mesh.
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils  # Drawing utilities
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# Initialize the video capture.
cap = cv2.VideoCapture(0)

# Initialize the Arduino connection.
arduino = None
try:
    arduino = serial.Serial('COM3', 9600)
    time.sleep(2)  # gives the connection a second to settle
    print("Connected to Arduino successfully")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")

# ThinkSpeak channel settings
channel_id = "2748329"  #channel ID
write_key = "SYK8G39884K5RJ9G"  #channel's API Key
ts_channel = thingspeak.Channel(id=channel_id, api_key=write_key)

def calculate_EAR(eye_points):
    # Compute the euclidean distances between the horizontal and vertical eye landmarks.
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    C = np.linalg.norm(eye_points[0] - eye_points[3])
    # Compute the eye aspect ratio.
    ear = (A + B) / (2.0 * C)
    return ear

# Indices of facial landmarks for the left and right eye.
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

# Thresholds and counters.
EAR_THRESHOLD = 0.25
EAR_CONSEC_FRAMES = 90  # 3 seconds at 30 fps
counter = 0
total_blinks = 0
prolonged_closures = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Failed to read frame")
        continue

    # Get the dimensions of the frame
    h, w, _ = frame.shape

    # Convert the BGR image to RGB and process it.
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    # Convert the image color back so it can be displayed.
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Draw the face mesh annotations on the image.
            mp_drawing.draw_landmarks(
                image, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
            )

            # Get the landmarks/pixels for the left and right eye.
            l_eye = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in LEFT_EYE_IDX])
            r_eye = np.array([(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) for i in RIGHT_EYE_IDX])

            # Calculate EAR for both eyes.
            left_EAR = calculate_EAR(l_eye)
            right_EAR = calculate_EAR(r_eye)
            ear = (left_EAR + right_EAR) / 2.0

            # Inside the loop, after calculating EAR
            print(f"EAR: {ear}")
            if ear < EAR_THRESHOLD:
                counter += 1
                total_blinks += 1  # Increment total blink count whenever the EAR is below the threshold
                if counter >= EAR_CONSEC_FRAMES:
                    prolonged_closures += 1  # Increment prolonged closures count
                    print("Eyes have been closed for 3 seconds - Triggering double beep")
                    if arduino:
                        arduino.write(b'2')  # Send signal to Arduino to double beep
                    # Update ThinkSpeak channel with blink frequency and prolonged closures
                    try:
                        response = ts_channel.update({
                            'field1': total_blinks,
                            'field2': prolonged_closures
                        })
                        print(f"Data sent to ThingSpeak: {response}")
                    except Exception as e:
                        print(f"Failed to send data to ThingSpeak: {e}")
            else:
                if counter >= EAR_CONSEC_FRAMES:
                    print("Eyes are now open - Stopping buzzer")
                    if arduino:
                        print("Sending '0' to Arduino")
                        arduino.write(b'0')  # Send signal to stop buzzing
                counter = 0

    # Display the resulting frame
    cv2.imshow('MediaPipe Face Mesh', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
