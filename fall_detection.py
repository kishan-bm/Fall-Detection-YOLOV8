import cv2
from ultralytics import YOLO

# Load the trained model
model = YOLO("runs/detect/train/weights/last.pt")

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Couldn't access the camera.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Run YOLO detection on the frame
    results = model(frame)

    # Process detection results
    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])  # Get detected class index
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            conf = box.conf[0]  # Confidence score

            # Draw bounding box
            color = (0, 0, 255) if cls == 0 else (0, 255, 0)  # Red for falls, green otherwise
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label the detection
            label = f"Fall {conf:.2f}" if cls == 0 else f"Person {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Display the result
    cv2.imshow("Fall Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
