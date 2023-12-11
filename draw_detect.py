import cv2
from PyQt5 import QtWidgets, uic, QtCore
import numpy as np

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

class DrawDetect(QtWidgets.QMainWindow):
    def __init__(self):
        super(DrawDetect, self).__init__()
        uic.loadUi("draw.ui", self)
        self.pushButton.clicked.connect(self.draw_polygon)
        self.done.clicked.connect(self.drawed)
        # Tạo QTimer để liên tục cập nhật khung hình từ video
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Thời gian cập nhật khung hình (30ms)

        # Mở video bằng OpenCV
        self.video_path = "5.mp4"
        self.video_capture = cv2.VideoCapture(self.video_path)

        # Hiển thị video lên QLabel
        self.display_screen.setScaledContents(True)

        # Danh sách các điểm trong đa giác
        self.points = []

        # Xử lý sự kiện click chuột
        self.display_screen.mousePressEvent = self.handle_left_click

    def handle_left_click(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            x = event.pos().x()
            y = event.pos().y()
            self.points.append([x, y])
            print(f"Added point: ({x}, {y})")

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
    def drawed(self):
        self.hide()