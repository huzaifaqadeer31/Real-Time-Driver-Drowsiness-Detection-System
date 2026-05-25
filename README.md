Introduction

SafetyGuard is an AI-based Real-Time Driver Drowsiness Detection System developed to improve road safety by monitoring driver behavior through a webcam. The system uses Deep Learning and Computer Vision techniques to detect whether the driver is alert or drowsy in real time.

The project captures live video frames, detects the driver's face, and classifies the driver's state using a trained deep learning model. If drowsiness is detected, the system can generate alerts and notifications to help prevent accidents caused by fatigue.

Features
Real-time webcam video processing
Face detection and tracking
Deep learning-based driver state classification
Multi-class classification:
Alert
Drowsy
Real-time prediction with confidence score
Live bounding box and status display
Continuous Alarm System
Flask backend API
React.js frontend dashboard

Tech Stack
Backend
Python
Flask
TensorFlow / Keras
OpenCV
MediaPipe
NumPy
Frontend
React.js
HTML
CSS
JavaScript
Deep Learning
EfficientNetB0
CNN-based image classification

Project Structure
project/
│
├── backend/
│   ├── app.py
│   ├── model/
│   ├── utils/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── dataset/
│
├── README.md
│
└── best_model.keras
