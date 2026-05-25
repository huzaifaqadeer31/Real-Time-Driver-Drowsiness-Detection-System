import os
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import time
import threading
import winsound


class DrowsinessMonitor:
    def __init__(self):
        self.MODEL_PATH = 'model/drowsiness_efficientnetb0.h5'
        self.IMG_SIZE   = 224

        self.current_status     = "Waiting..."
        self.current_confidence = 0.0

        self.drowsy_counter    = 0
        self.alert_counter     = 0
        self.DROWSY_THRESHOLD  = 15
        self.ALERT_THRESHOLD   = 8
        self.CONFIDENCE_THRESHOLD = 0.80

        self.final_state = "Waiting..."
        self.is_drowsy   = False

        self.alert_count       = 0
        self.drowsy_start_time = 0
        self.drowsy_duration   = 0
        self.session_start     = time.time()

        self.alarm_active = False
        self.alarm_thread = None

        self.last_notification_time = 0
        self.NOTIFICATION_COOLDOWN  = 30

        self.frame_count      = 0
        self.PREDICT_EVERY_N  = 3
        self.last_label       = "Alert"
        self.last_conf        = 0.0

        self.no_face_counter          = 0
        self.NO_FACE_RESET_THRESHOLD  = 10

        self._lock         = threading.Lock()
        self._latest_frame = None
        self._camera_ready = False

        self.model = None
        self.load_model()
        self.init_face_detection()

        self._cam_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self._cam_thread.start()
        print("[INFO] Background camera thread started.")

    def load_model(self):
        print(f"[INFO] Loading model from {self.MODEL_PATH}...")
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = tf.keras.models.load_model(self.MODEL_PATH)
                print("[INFO] Model loaded successfully.")
            except Exception as e:
                print(f"[ERROR] Could not load model: {e}")
                self.model = None
        else:
            print(f"[WARNING] Model not found at {self.MODEL_PATH}.")

    def init_face_detection(self):
        mp_face = mp.solutions.face_detection
        self.face_detection = mp_face.FaceDetection(min_detection_confidence=0.7)

    def trigger_alarm(self, active):
        if active and not self.alarm_active:
            self.alarm_active = True
            self.alarm_thread = threading.Thread(target=self._alarm_loop, daemon=True)
            self.alarm_thread.start()
        elif not active:
            self.alarm_active = False

    def _alarm_loop(self):
        while self.alarm_active:
            winsound.Beep(1000, 500)
            time.sleep(1.0)

    def send_notification(self):
        now = time.time()
        if now - self.last_notification_time > self.NOTIFICATION_COOLDOWN:
            print("[ALERT] Drowsiness detected.")
            self.last_notification_time = now

    def predict_drowsiness(self, face_img):
        if self.model is None:
            return "Demo", 0.0
        try:
            img       = cv2.resize(face_img, (self.IMG_SIZE, self.IMG_SIZE))
            img       = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_array = np.expand_dims(img, axis=0).astype("float32")
            img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
            prediction   = self.model.predict(img_array, verbose=0)
            alert_score  = prediction[0][0]
            drowsy_score = prediction[0][1]
            label = "Drowsy" if drowsy_score > self.CONFIDENCE_THRESHOLD else "Alert"
            conf  = drowsy_score if label == "Drowsy" else alert_score
            return label, float(conf)
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return "Error", 0.0

    def update_state(self, label):
        if label == "Drowsy":
            self.drowsy_counter += 1
            self.alert_counter   = 0
        else:
            self.alert_counter  += 1
            if self.alert_counter >= self.ALERT_THRESHOLD:
                self.drowsy_counter = 0

        if self.drowsy_counter >= self.DROWSY_THRESHOLD:
            if not self.is_drowsy:
                self.is_drowsy         = True
                self.final_state       = "Drowsy"
                self.drowsy_start_time = time.time()
                self.alert_count      += 1
                self.trigger_alarm(True)
                self.send_notification()
            self.drowsy_duration = int(time.time() - self.drowsy_start_time)
        elif self.drowsy_counter == 0 and self.is_drowsy:
            self.is_drowsy       = False
            self.final_state     = "Alert"
            self.drowsy_duration = 0
            self.trigger_alarm(False)
        elif not self.is_drowsy:
            self.final_state = "Alert" if label == "Alert" else "Waiting..."

    def handle_no_face(self):
        self.no_face_counter += 1
        if self.no_face_counter >= self.NO_FACE_RESET_THRESHOLD:
            self.drowsy_counter = 0
            self.alert_counter  = 0
            self.last_label     = "Alert"
            self.last_conf      = 0.0
            if self.is_drowsy:
                self.is_drowsy       = False
                self.drowsy_duration = 0
                self.trigger_alarm(False)
            self.final_state = "No Face Detected"
        self.current_status     = "No Face Detected"
        self.current_confidence = 0.0

    def _camera_loop(self):
        print("[INFO] Opening camera...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Could not open camera.")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS,          30)
        self._camera_ready = True
        print("[INFO] Camera opened successfully.")

        while True:
            success, frame = cap.read()
            if not success:
                time.sleep(0.05)
                continue

            frame     = cv2.flip(frame, 1)
            h, w, _   = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results   = self.face_detection.process(rgb_frame)
            self.frame_count += 1

            if results.detections:
                self.no_face_counter = 0
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    x  = max(0, int(bbox.xmin  * w))
                    y  = max(0, int(bbox.ymin  * h))
                    bw = min(w - x, int(bbox.width  * w))
                    bh = min(h - y, int(bbox.height * h))
                    if bw > 10 and bh > 10:
                        if self.frame_count % self.PREDICT_EVERY_N == 0:
                            face_img                = frame[y:y+bh, x:x+bw]
                            label, conf             = self.predict_drowsiness(face_img)
                            self.last_label         = label
                            self.last_conf          = conf
                            self.current_status     = label
                            self.current_confidence = conf
                            self.update_state(label)
                        else:
                            label = self.last_label
                            conf  = self.last_conf
                        color = (0, 0, 255) if self.final_state == "Drowsy" else (0, 255, 0)
                        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
                        cv2.putText(frame,
                                    f"{self.final_state} ({int(conf * 100)}%)",
                                    (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                self.handle_no_face()

            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                with self._lock:
                    self._latest_frame = buffer.tobytes()

        cap.release()

    def generate_frames(self):
        print("[INFO] Client connected to /video_feed")
        while True:
            with self._lock:
                frame_bytes = self._latest_frame
            if frame_bytes is None:
                time.sleep(0.05)
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.033)
