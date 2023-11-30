import cv2
from ultralytics import YOLO
import torch

import numpy as np
import time
from datetime import datetime
from funtions import DetectFunction
points = []
last_alert_time = time.time()
alert_interval = 15
def handle_left_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
def draw_polygon(frame, points):
    for point in points:
        frame = cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)
    if len(points) > 1:
        frame = cv2.polylines(frame, [np.array(points)], isClosed=False, color=(255, 0, 0), thickness=2)
    return frame
# Đặt thiết bị là GPU nếu có sẵn, nếu không thì là CPU
if torch.cuda.is_available():
    print("run with GPU")
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# Load the YOLOv8 model
model = YOLO('/home/lvnh/PycharmProjects/Detect-People-Distress/detect/train/weights/best.pt').float().to(device)
functions = DetectFunction()
# Open the video file
video_path = "7.mp4"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        frame = draw_polygon(frame, points)
        # Run YOLOv8 inference on the frame
        results = model(frame, conf=0.7, verbose=False)

        if len(results[0]) > 0:
            cv2.putText(frame,"Fall detect!!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            current_time = time.time()
            if current_time - last_alert_time >= alert_interval:
                last_alert_time = current_time
                image_path = "detected_object.jpg"
                cv2.imwrite(image_path, frame)
                # Save the frame as an image
                functions.sendMessage(image_path)


        # Convert the annotated frame back to numpy array and move it to CPU for display
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        cv2.setMouseCallback("YOLOv8 Inference", handle_left_click)
        # Break the loop if 'q' is pressed
        key = cv2.waitKey(1)
        if key == ord("d"):
            points.append(points[0])
        elif key == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

        # Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()