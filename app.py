from flask import Flask, render_template, request, Response, send_file, redirect, url_for
import threading
import subprocess
import os

app = Flask(__name__)
FALL_LOG_PATH = "fall_log.txt"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_detection():
    with open("stop_alarm.txt", "w") as f:
        f.write("no")  # reset acknowledgment
    thread = threading.Thread(target=run_detection)
    thread.start()
    return 'Detection Started', 200

@app.route('/acknowledge', methods=['POST'])
def acknowledge():
    with open("stop_alarm.txt", "w") as f:
        f.write("stop")
    return 'Acknowledged', 200

@app.route("/check_ack", methods=["GET"])
def check_ack():
    try:
        with open("stop_alarm.txt", "r") as f:
            return {'acknowledged': f.read().strip() == "stop"}
    except:
        return {'acknowledged': False}

@app.route("/logs")
def show_logs():
    if os.path.exists(FALL_LOG_PATH):
        with open(FALL_LOG_PATH, "r") as f:
            logs = f.readlines()
    else:
        logs = []
    return render_template("logs.html", logs=logs)

@app.route("/download_logs")
def download_logs():
    return send_file(FALL_LOG_PATH, as_attachment=True)

@app.route("/clear_logs")
def clear_logs():
    if os.path.exists(FALL_LOG_PATH):
        os.remove(FALL_LOG_PATH)
    return redirect(url_for('show_logs'))

def run_detection():
    subprocess.run([r"venv\Scripts\python.exe", "fall_detection_yolo.py"])


from fall_detection_yolo import generate_frames  # Import the frame generator

# remove
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# remove later//

if __name__ == "__main__":
    app.run(debug=True)
