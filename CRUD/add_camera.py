import sys
import cv2
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from NotifyMessage import NotifyMessage

class AddCam(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super(AddCam, self).__init__(parent)
        uic.loadUi("ui/add.ui", self)
        self.setWindowTitle("Add Camera")
        self.ipAddress.setStyleSheet("background-color:white")
        self.setStyleSheet("background-color: #DDDDDD")
        self.check_btn.clicked.connect(self.showVideo)
        self.add_camera.clicked.connect(self.addCamera)
        self.close_btn.clicked.connect(self.closeWindow)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.link = None
        self.video_capture = None
        self.cameras = self.getCameras()

        # Hiển thị video lên QLabel
        self.display_screen.setScaledContents(True)

    def showVideo(self):
        self.link = self.ipAddress.toPlainText()

        if self.video_capture is not None:
            self.video_capture.release()

        self.video_capture = cv2.VideoCapture(self.link)
        self.timer.start(30)

    def update_frame(self):
        if self.link:
            try:
                # Đọc khung hình tiếp theo từ video
                ret, frame = self.video_capture.read()
                if ret:
                    # Chuyển đổi khung hình từ cv2 sang QImage
                    qt_image = self.convert_cv2_to_qt(frame)

                    # Hiển thị khung hình trên QLabel
                    self.display_screen.setPixmap(QPixmap.fromImage(qt_image))
            except Exception as e:
                self.timer.stop()
                NotifyMessage("Link is undefined", 0)

    def convert_cv2_to_qt(self, cv_image):
        # Chuyển đổi hình ảnh từ cv2 sang QImage
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qt_image

    def addCamera(self):
        with open('cameras.txt', 'a') as file:
            file.write(self.link+"\n")
        lastIndex = len(self.cameras)
        open('CAMERA{}.txt'.format(lastIndex+1),'w')
        NotifyMessage("Add new camera sucessfully")
        self.parent().resetListCamera()
        self.close()
    def closeWindow(self):
        self.close()

    def getCameras(self):
        with open('cameras.txt', 'r') as file:
            cameras = [line.strip() for line in file]
        return cameras