
import cv2
import time
import threading
from ultralytics import YOLO
import pygame
import os

# Load YOLOv8 model
model = YOLO("best.pt")

# Initialize pygame for alarm
pygame.mixer.init()
ALARM_SOUND = "alarm.wav"
last_alert_time = 0
alert_cooldown = 5  # seconds

def play_alarm():
    pygame.mixer.music.load(ALARM_SOUND)
    pygame.mixer.music.play(-1)  # Loop until manually stopped

def stop_alarm():
    pygame.mixer.music.stop()

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO inference
    results = model(frame)[0]
    fall_detected = False

    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result
        class_id = int(class_id)
        if class_id == 0 and score > 0.5:  # Assuming 0 is the 'fall' class
            fall_detected = True
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            cv2.putText(frame, "FALL DETECTED", (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    if fall_detected:
        current_time = time.time()
        if current_time - last_alert_time > alert_cooldown:
            print("⚠️ YOLO Fall Detected")
            threading.Thread(target=play_alarm).start()
            last_alert_time = current_time

    # Check if alarm should stop
    if os.path.exists("stop_alarm.txt"):
        with open("stop_alarm.txt", "r") as f:
            if f.read().strip() == "stop":
                stop_alarm()

    cv2.imshow("YOLO Fall Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
stop_alarm()





# USING YOLOv8 FOR FALL DETECTION

# import cv2
# import time
# import threading
# from ultralytics import YOLO
# import pygame
# import os

# # Initialize alarm
# pygame.mixer.init()
# ALARM_SOUND = "alarm.wav"
# last_alert_time = 0
# alert_cooldown = 5  # seconds

# # Load YOLOv8 model (you can use yolov8n, yolov8s etc.)
# model = YOLO('yolov8n.pt')  # replace with custom model if available

# # Start webcam
# cap = cv2.VideoCapture(0)

# def play_alarm():
#     pygame.mixer.music.load(ALARM_SOUND)
#     pygame.mixer.music.play()

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     results = model.predict(frame, conf=0.4)
#     annotated_frame = results[0].plot()

#     fall_detected = False

#     for box in results[0].boxes.xywh:  # x, y, w, h format
#         x, y, w, h = box
#         aspect_ratio = h / w

#         # Check if the person is more horizontal than vertical
#         if aspect_ratio < 0.6:  # horizontal shape indicates lying down
#             fall_detected = True
#             break

#     if fall_detected:
#         current_time = time.time()
#         if current_time - last_alert_time > alert_cooldown:
#             print("⚠️ Fall Detected!")
#             threading.Thread(target=play_alarm).start()
#             last_alert_time = current_time

#         cv2.putText(annotated_frame, "FALL DETECTED!", (50, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

#     # Stop alarm if acknowledged via file
#     if os.path.exists("stop_alarm.txt"):
#         with open("stop_alarm.txt", "r") as f:
#             if f.read().strip() == "stop":
#                 pygame.mixer.music.stop()

#     cv2.imshow("Fall Detection (YOLOv8)", annotated_frame)

#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()












# USING MEDIAPIPE FOR FALL DETECTION


# import cv2
# import time
# import threading
# import mediapipe as mp
# import pygame
# import requests

# # Initialize pygame
# pygame.mixer.init()
# ALARM_SOUND = "alarm.wav"
# last_alert_time = 0
# alert_cooldown = 5  # seconds
# alarm_playing = False
# stop_alarm_flag = False

# # Function to check acknowledgment from server
# def is_acknowledged():
#     try:
#         res = requests.get("http://127.0.0.1:5000/check_ack")
#         return res.json().get("acknowledged", False)
#     except:
#         return False

# # Function to play alarm and stop on acknowledgment
# def play_alarm_loop():
#     global alarm_playing, stop_alarm_flag
#     alarm_playing = True
#     stop_alarm_flag = False
#     pygame.mixer.music.load(ALARM_SOUND)
#     pygame.mixer.music.play(-1)  # loop indefinitely
#     print("🔊 Alarm started")

#     while not stop_alarm_flag:
#         if is_acknowledged():
#             print("✅ Acknowledged. Stopping alarm.")
#             pygame.mixer.music.stop()
#             stop_alarm_flag = True
#         time.sleep(1)

#     alarm_playing = False

# # Pose setup
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()
# mp_drawing = mp.solutions.drawing_utils

# # Start webcam
# cap = cv2.VideoCapture(0)

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break

#     image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(image)
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#     fall_detected = False

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#         landmarks = results.pose_landmarks.landmark

#         left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
#         right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
#         left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
#         right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

#         avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
#         avg_hip_y = (left_hip.y + right_hip.y) / 2

#         if abs(avg_shoulder_y - avg_hip_y) < 0.1:
#             fall_detected = True

#         if fall_detected and (time.time() - last_alert_time > alert_cooldown):
#             print("⚠️ Fall Detected!")
#             if not alarm_playing:
#                 threading.Thread(target=play_alarm_loop).start()
#             last_alert_time = time.time()

#             cv2.putText(image, "FALL DETECTED!", (50, 50),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

#     # Optional: Show acknowledged status
#     if is_acknowledged() and not alarm_playing:
#         cv2.putText(image, "FALL ACKNOWLEDGED", (50, 100),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

#     cv2.imshow("Fall Detection", image)

#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
