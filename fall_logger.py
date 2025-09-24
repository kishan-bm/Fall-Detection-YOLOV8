from datetime import datetime

def log_fall_event():
    with open("fall_log.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Fall detected at {timestamp}\n")
