import cv2
import torch
from tracker import Tracker

# Load YOLOv8 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Change model if needed

# Initialize tracker
tracker = Tracker()

# Open webcam
cap = cv2.VideoCapture(0)

# Store fallen object positions
fallen_objects = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame)  # Disable unnecessary logs

    # Get detected objects
    detections = []
    for *xyxy, conf, cls in results.xyxy[0]:  # Extract bounding box
        x1, y1, x2, y2 = map(int, xyxy)  # Convert to integers
        w, h = x2 - x1, y2 - y1
        detections.append([x1, y1, w, h])

    # Track objects
    tracked_objects = tracker.update(detections)

    # Fall detection logic
    for obj in tracked_objects:
        x, y, w, h, obj_id = obj

        if obj_id in fallen_objects:
            if y > fallen_objects[obj_id] + 50:  # Large downward movement = fall
                print(f"⚠️ ALERT: Object {obj_id} has fallen!")
                cv2.putText(frame, "FALL DETECTED!", (x, y - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

        # Update object position
        fallen_objects[obj_id] = y

        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {obj_id}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Show frame
    cv2.imshow("Fall Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
