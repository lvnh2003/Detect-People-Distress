import sys
import cv2
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from NotifyMessage import NotifyMessage

class AddCam(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super(AddCam, self).__init__(parent)
        # load ui from ui folder
        uic.loadUi("ui/add.ui", self)
        self.setWindowTitle("Add Camera")
        self.ipAddress.setStyleSheet("background-color:white")
        self.setStyleSheet("background-color: #DDDDDD")
        # show video button
        self.check_btn.clicked.connect(self.showVideo)
        # add camera after success
        self.add_camera.clicked.connect(self.addCamera)
        self.close_btn.clicked.connect(self.closeWindow)
        # setTimeOut display video throung open-cv
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.link = None
        self.video_capture = None
        self.cameras = self.getCameras()

        # Display into QLabel
        self.display_screen.setScaledContents(True)
    # function after click "OK" for check camera's link is exist 
    def showVideo(self):
        self.link = self.ipAddress.toPlainText()

        if self.video_capture is not None:
            self.video_capture.release()
        # change value video_capture
        self.video_capture = cv2.VideoCapture(self.link)
        self.timer.start(30)

    def update_frame(self):
        if self.link:
            try:
                # Read the next frame in video
                ret, frame = self.video_capture.read()
                if ret:
                    # Convert frame from cv2 to QImage
                    qt_image = self.convert_cv2_to_qt(frame)

                    # Display into QLabel
                    self.display_screen.setPixmap(QPixmap.fromImage(qt_image))
            except Exception as e:
                self.timer.stop()
                NotifyMessage("Link is undefined", 0)

    def convert_cv2_to_qt(self, cv_image):
        # Convert frame from cv2 to QImage
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        # get height, width, ch is color tuple (no color convert RGB)
        h, w, ch = rgb_image.shape
        # bytes needs each image line 
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return qt_image
    # add camera link into resource/cameras.txt
    def addCamera(self):
        with open('resource/cameras.txt', 'a') as file:
            file.write(self.link+"\n")
        lastIndex = len(self.cameras)
        open('CAMERA{}.txt'.format(lastIndex+1),'w')
        NotifyMessage("Add new camera sucessfully")
        self.parent().resetListCamera()
        self.close()
    def closeWindow(self):
        self.close()

    def getCameras(self):
        with open('resource/cameras.txt', 'r') as file:
            cameras = [line.strip() for line in file]
        return cameras