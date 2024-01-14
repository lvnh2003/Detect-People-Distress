import sys

import cv2
from PyQt5 import QtWidgets, uic, QtCore
import numpy as np

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from NotifyMessage import NotifyMessage
class DrawDetect(QtWidgets.QMainWindow):
    def __init__(self,video,camIndex,parent):
        super(DrawDetect, self).__init__(parent)
        uic.loadUi("ui/draw.ui", self)
        self.pushButton.clicked.connect(self.addNewPolygon)
        self.done.clicked.connect(self.drawed)
        # Tạo QTimer để liên tục cập nhật khung hình từ video
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Thời gian cập nhật khung hình (30ms)
        self.camIndex = camIndex
        # Mở video bằng OpenCV tỉ lê 1.6
        self.video_capture = cv2.VideoCapture(video)

        # Hiển thị video lên QLabel
        self.display_screen.setScaledContents(True)

        # Danh sách các điểm trong đa giác
        self.points = []

        # Xử lý sự kiện click chuột
        self.display_screen.mousePressEvent = self.handle_left_click

    def handle_left_click(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            label_width = self.display_screen.width()
            label_height = self.display_screen.height()
            frame_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

            x = event.pos().x()
            y = event.pos().y()

            # Calculate scaling factors
            scale_x = frame_width / label_width
            scale_y = frame_height / label_height

            # Apply scaling and transform coordinates
            frame_x = int(x * scale_x)
            frame_y = int(y * scale_y)

            self.points.append([frame_x, frame_y])

    def update_frame(self):
        # Đọc khung hình tiếp theo từ video
        ret, frame = self.video_capture.read()

        if ret:
            # Vẽ đa giác trên khung hình
            frame = self.draw_polygon(frame, self.points)

            # Chuyển đổi khung hình từ cv2 sang QImage
            qt_image = self.convert_cv2_to_qt(frame)

            # Hiển thị khung hình trên QLabel
            self.display_screen.setPixmap(QPixmap.fromImage(qt_image))

    def draw_polygon(self, frame, points):
        for point in points:
            frame = cv2.circle(frame, (point[0], point[1]), 5, (0, 0, 255), -1)
        if len(points) > 1:
            frame = cv2.polylines(frame, [np.array(points)], isClosed=False, color=(255, 0, 0), thickness=2)
        return frame

    def convert_cv2_to_qt(self, cv_image):
        # Chuyển đổi hình ảnh từ cv2 sang QImage
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qt_image
    def addNewPolygon(self):
        self.points.clear()
    def drawed(self):
        self.points.append(self.points[0])
        with open("CAMERA{}.txt".format(self.camIndex+1), "w") as file:
        #     # Iterate over the points list
            for point in self.points:
                # Convert the point coordinates to a string
                point_str = f"{point[0]}, {point[1]}"
                # Write the point string to a new line in the file
                file.write(point_str + "\n")
        NotifyMessage("Created new points success")
        self.parent().newPoint()