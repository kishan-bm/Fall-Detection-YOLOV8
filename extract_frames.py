import cv2
import pandas as pd
import os

# Paths to videos and CSV files
video_path = "urfall-cam0.avi"  # Change if needed
falls_csv = "urfall-cam0-falls.csv"
adls_csv = "urfall-cam0-adls.csv"

# Output directories
output_dir = "dataset"
fall_dir = os.path.join(output_dir, "fall")
adls_dir = os.path.join(output_dir, "non_fall")

os.makedirs(fall_dir, exist_ok=True)
os.makedirs(adls_dir, exist_ok=True)

# Load CSV files
falls = pd.read_csv(falls_csv)
adls = pd.read_csv(adls_csv)

# Open video file
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

def extract_frames(df, label):
    frame_count = 0
    for index, row in df.iterrows():
        start_frame = int(row['start'] * fps)
        end_frame = int(row['end'] * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        while cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break

            # Save frame
            frame_name = f"{label}_{frame_count}.jpg"
            save_path = os.path.join(fall_dir if label == "fall" else adls_dir, frame_name)
            cv2.imwrite(save_path, frame)
            frame_count += 1

extract_frames(falls, "fall")
extract_frames(adls, "non_fall")

cap.release()
cv2.destroyAllWindows()

print("Frames extracted successfully!")
