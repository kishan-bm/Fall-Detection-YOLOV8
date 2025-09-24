import cv2
import time
import threading
from ultralytics import YOLO
import pygame
import os
from datetime import datetime
from sms_alert import send_sms_alert
from fall_logger import log_fall_event

# Load models
fall_model = YOLO("runs/detect/train/weights/best.pt")  # Fall detection model
pose_model = YOLO("yolov8s-pose.pt")  # Pose estimation for body parts

# Alarm setup
pygame.mixer.init()
ALARM_SOUND = os.path.join(os.path.dirname(__file__), "alarm.wav")

# Snapshot saving directory
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# Alert cooldown time
last_alert_time = 0
alert_cooldown = 5  # in seconds

# Play alarm
def play_alarm():
    pygame.mixer.music.load(ALARM_SOUND)
    pygame.mixer.music.play(-1)

# Stop alarm
def stop_alarm():
    pygame.mixer.music.stop()

# Main generator function for frames
def generate_frames():
    global last_alert_time
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run fall detection model
        fall_results = fall_model(frame)[0]
        fall_detected = False

        for result in fall_results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            class_id = int(class_id)
            if class_id == 0 and score > 0.5:  # class_id 0 = fall
                fall_detected = True
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                cv2.putText(frame, "FALL DETECTED", (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Run pose model for body parts detection
        pose_results = pose_model(frame)[0]
        for pose in pose_results.keypoints.data:
            for x, y, conf in pose:
                if conf > 0.5:
                    cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 0), -1)

        # Optional: draw lines between keypoints
        # frame = pose_results.plot()  # Uncomment this line to use Ultralytics' auto-plot

        # Handle fall alert
        if fall_detected:
            current_time = time.time()
            if current_time - last_alert_time > alert_cooldown:
                threading.Thread(target=play_alarm).start()
                threading.Thread(target=send_sms_alert).start()
                log_fall_event()
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                snapshot_path = os.path.join(SNAPSHOT_DIR, f"fall_{timestamp}.jpg")
                cv2.imwrite(snapshot_path, frame)
                last_alert_time = current_time

        # Check if stop command is triggered
        if os.path.exists("stop_alarm.txt"):
            with open("stop_alarm.txt", "r") as f:
                if f.read().strip() == "stop":
                    stop_alarm()

        # Encode frame and yield
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
