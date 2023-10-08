import cv2
import numpy as np
from ultralytics import YOLO
import supervision as sv

# Load the YOLOv8 model
model = YOLO('yolov8s.pt')
points = []
def handle_left_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])

def draw_polygon(frame, points):
    for point in points:
        frame = cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)
    if len(points) > 1:
        frame = cv2.polylines(frame, [np.array(points)], isClosed=False, color=(255, 0, 0), thickness=2)
    return frame
def process_frame(frame: np.ndarray, _) -> np.ndarray:
    # detect
    results = model(frame, imgsz=1280)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = detections[detections.class_id == 0]
    zone.trigger(detections=detections)

    # annotate
    box_annotator = sv.BoxAnnotator(thickness=4, text_thickness=4, text_scale=2)
    frame = box_annotator.annotate(scene=frame, detections=detections)
    frame = zone_annotator.annotate(scene=frame)

    return frame

cap = cv2.VideoCapture("mall.mp4")
# detect = False
polygon = np.array([
    [1725, 1550],
    [2725, 1550],
    [3500, 2160],
    [1250, 2160]
])
video_info = sv.VideoInfo.from_video_path("mall.mp4")
zone = sv.PolygonZone(polygon=polygon, frame_resolution_wh=video_info.resolution_wh)
box_annotator = sv.BoxAnnotator(thickness=4, text_thickness=4, text_scale=2)
zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.white(), thickness=6, text_thickness=6, text_scale=4)

# Create a named window and set its initial size
cv2.namedWindow("Intrusion Warning", cv2.WINDOW_NORMAL)
while cap.isOpened():
    success, frame = cap.read()
    # results = model.track(frame, persist=True)
    # frame = cv2.flip(frame, 1)

    frame = process_frame(frame, None)
    # annotated_frame = results[0].plot()
    # frame_with_polygon = draw_polygon(annotated_frame.copy(), points)
    cv2.imshow("Intrusion Warning", frame)

    cv2.setMouseCallback("Intrusion Warning", handle_left_click)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("d"):
        points.append(points[0])

cap.release()
cv2.destroyAllWindows()
