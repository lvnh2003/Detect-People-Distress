import cv2
import numpy as np
from yolodetect import YoloDetect
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')
points = []

# model = YoloDetect(detect_class="cell phone")

def handle_left_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])


def draw_polygon(frame, points):
    for point in points:
        frame = cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)
    if len(points) > 1:
        frame = cv2.polylines(frame, [np.array(points)], isClosed=False, color=(255, 0, 0), thickness=2)
    return frame


cap = cv2.VideoCapture(0)
detect = False
while cap.isOpened():
    success, frame = cap.read()
    results = model.track(frame, persist=True)
    frame = cv2.flip(frame, 1)

    # if detect:
    #     frame_with_polygon = YoloDetect.detect(frame_with_polygon)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()
    frame_with_polygon = draw_polygon(annotated_frame.copy(), points)
    # Display the annotated frame
    # cv2.imshow("YOLOv8 Tracking", annotated_frame)
    cv2.imshow("Intrusion Warning", frame_with_polygon)

    cv2.setMouseCallback("Intrusion Warning", handle_left_click)

    if cv2.waitKey(1) == ord("q"):
        break
    elif cv2.waitKey(1) == ord("d"):
        points.append(points[0])
    #     detect= True


cap.release()
cv2.destroyAllWindows()
