from flask import Flask, Response, jsonify
from flask_cors import CORS
import os
import time
from camera_system import DrowsinessMonitor

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
CORS(app)

monitor = DrowsinessMonitor()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    return app.send_static_file('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(monitor.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/predict')
def get_prediction():
    return jsonify({
        'status': monitor.final_state,
        'raw_status': monitor.current_status,
        'confidence': round(monitor.current_confidence * 100, 2),
        'is_drowsy': monitor.is_drowsy,
        'duration': monitor.drowsy_duration,
        'alert_count': monitor.alert_count,
        'session_time': int(time.time() - monitor.session_start),
        'drowsy_counter': monitor.drowsy_counter
    })

if __name__ == '__main__':
    os.makedirs('model', exist_ok=True)
    app.run(debug=False, threaded=True, host='127.0.0.1', port=5000, use_reloader=False)
