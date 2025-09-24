import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)  # Use webcam

fall_detected = False
fall_start_time = None

def detect_fall(landmarks):
    global fall_detected, fall_start_time

    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

    # Average shoulder and hip coordinates
    avg_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
    avg_hip_y = (left_hip.y + right_hip.y) / 2

    # If shoulders are at nearly same Y level as hips → likely a fall
    if abs(avg_shoulder_y - avg_hip_y) < 0.1:
        if not fall_detected:
            fall_start_time = time.time()
            fall_detected = True
        elif time.time() - fall_start_time > 2:  # 2 seconds in fallen state
            return True
    else:
        fall_detected = False
        fall_start_time = None
    return False

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        if detect_fall(results.pose_landmarks.landmark):
            cv2.putText(img, "FALL DETECTED!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    cv2.imshow("Fall Detection", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
