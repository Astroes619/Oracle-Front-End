import json
import os
import csv
import cv2
import numpy as np
from skimage.feature import hog
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponseServerError, JsonResponse
import joblib
import base64
from io import BytesIO
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml')


def eye_detection(request):
    data = json.loads(request.body)
    encoded_frame = base64.b64decode(data["frame"].split(",")[1])
    nparr = np.frombuffer(encoded_frame, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi_gray = gray[y : y + h, x : x + w]
        roi_color = frame[y : y + h, x : x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)
            eye_img = roi_gray[ey : ey + eh, ex : ex + ew]
            eye_img_resized = cv2.resize(eye_img, (100, 50))
            aspect_ratio = ew / eh
            ground_truth = get_gaze_direction(ex, ey, ew, eh, w)
            features = extract_hog_features(eye_img_resized)
            predicted = clf.predict([features])[0]
            eye_tracking_data.append(
                {
                    "x": ex,
                    "y": ey,
                    "w": ew,
                    "h": eh,
                    "aspect_ratio": aspect_ratio,
                    "ground_truth": ground_truth,
                    "predicted": predicted,
                }
            )
            write_eye_tracking_data(eye_tracking_data[-1])
            print(
                f"x: {ex}, y: {ey}, w: {ew}, h: {eh}, aspect_ratio: {aspect_ratio}, ground_truth: {ground_truth}, predicted: {predicted}"
            )
    retval, buffer = cv2.imencode(".jpg", frame)
    response = base64.b64encode(buffer).decode("utf-8")
    return JsonResponse({"result": "data:image/jpeg;base64," + response})
