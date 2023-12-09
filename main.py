import threading
from hashlib import new
from PyQt5 import uic, sip
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer, QDateTime, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import cv2,time,sys,sysinfo
import numpy as np
import random as rnd
from Tracking_Func import Tack_Object
from ultralytics import YOLO
from playsound import playsound
import torch
from funtions import DetectFunction

functions = DetectFunction()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = YOLO('./detect/train/weights/best.pt').float().to(device)
last_alert_time = time.time()
alert_interval = 15
if torch.cuda.is_available():
    print("run with GPU")
class ThreadClass(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    FPS = pyqtSignal(int)
    global camIndex

    def play_sound(self):
        playsound("temp_part.wav")
    def run(self):
        if camIndex == 0:
            Capture = cv2.VideoCapture("5.mp4")
        if camIndex == 1:
            Capture = cv2.VideoCapture("5.mp4")

        Capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        Capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        self.ThreadActive = True
        prev_frame_time = 0
        new_frame_time = 0
        while self.ThreadActive:
            ret,frame_cap = Capture.read()
            flip_frame = cv2.flip(src=frame_cap,flipCode=1)
            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            if ret:
                results = model(flip_frame, conf=0.7, verbose=False)
                if len(results[0]) > 0:
                    cv2.putText(flip_frame, "Fall detect!!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                    # current_time = time.time()
                    # if current_time - last_alert_time >= alert_interval:
                    #     last_alert_time = current_time
                    # image_path = "detected_object.jpg"
                    # cv2.imwrite(image_path, flip_frame)
                    # # Save the frame as an image
                    # functions.sendMessage(image_path)
                    sound_thread = threading.Thread(target=self.play_sound)
                    sound_thread.start()
                annotated_frame = results[0].plot()
                self.ImageUpdate.emit(annotated_frame)
                self.FPS.emit(fps)

    def stop(self):
        self.ThreadActive = False
        self.quit()

# kiểm tra ram & cpu
class boardInfoClass(QThread):
    cpu = pyqtSignal(float)
    ram = pyqtSignal(tuple)
    temp = pyqtSignal(float)

    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            cpu = sysinfo.getCPU()
            ram = sysinfo.getRAM()
            self.cpu.emit(cpu)
            self.ram.emit(ram)

    def stop(self):
        self.ThreadActive = False
        self.quit()

class randomColorClass(QThread):
    color = pyqtSignal(tuple)
    def run(self):
        self.ThreadActive = True
        while self.ThreadActive:
            color = ([rnd.randint(0,256),rnd.randint(0,256),rnd.randint(0,256)],
                     [rnd.randint(0,256),rnd.randint(0,256),rnd.randint(0,256)],
                     [rnd.randint(0,256),rnd.randint(0,256),rnd.randint(0,256)]
                     )
            self.color.emit(color)
            time.sleep(2)

    def stop(self):
        self.ThreadActive = False
        self.quit()

class Window_ErrorAlarm(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Error.ui", self)

#   QLabel display
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("Opencv_PiDash.ui",self)

        self.online_cam = QCameraInfo.availableCameras()
        self.camlist.addItems([c.description() for c in self.online_cam])
        self.btn_start.clicked.connect(self.StartWebCam)
        self.btn_stop.clicked.connect(self.StopWebcam)

        self.resource_usage = boardInfoClass()
        self.resource_usage.start()
        self.resource_usage.cpu.connect(self.getCPU_usage)
        self.resource_usage.ram.connect(self.getRAM_usage)

        self.randomColor_usage = randomColorClass()
        self.randomColor_usage.start()
        self.randomColor_usage.color.connect(self.get_randomColors)

# Create Instance class
        self.Win_showError = Window_ErrorAlarm()

        # Track object Functions
        self.Track_Function1 = Tack_Object()
        self.Track_Function2 = Tack_Object()
        self.Track_Function3 = Tack_Object()



# QTimer Zone
        self.ready_lamp = QTimer(self, interval=1000)
        self.ready_lamp.timeout.connect(self.Ready_lamp)
        self.ready_lamp.start()


        self.lcd_timer = QTimer()
        self.lcd_timer.timeout.connect(self.clock)
        self.lcd_timer.start()

        self.flag_motor = True
        self.Status_lamp = [True,True,True]
# End QTimer Zone


        self.btn_setObject1.setCheckable(True)
        self.btn_setObject1.clicked.connect(self.GetObject_one)

        self.btn_setObject1_2.setCheckable(True)
        self.btn_setObject1.clicked.connect(self.GetObject_one)

        self.btn_close.clicked.connect(self.Close_software)

        self.btn_roi_set.setCheckable(True)
        self.btn_roi_set.clicked.connect(self.set_roi)

        self.ROI_X.valueChanged.connect(self.get_ROIX)
        self.ROI_Y.valueChanged.connect(self.get_ROIY)
        self.ROI_W.valueChanged.connect(self.get_ROIW)
        self.ROI_H.valueChanged.connect(self.get_ROIH)

        self.roi_x = 20
        self.roi_y = 20
        self.roi_w = 2000
        self.roi_h = 2000

        self.Win_showError.btn_e_close.clicked.connect(self.Close_Error)
        self.btn_stop.setEnabled(False)

        self.btn_draw.clicked.connect(self.showModal)
    def showModal(self):
        modal_dialog = QDialog(self)
        modal_dialog.setWindowTitle('Modal Dialog')

        disp_main_label = QLabel('This is a modal dialog.', modal_dialog)
        layout = QVBoxLayout()
        layout.addWidget(disp_main_label)
        modal_dialog.setLayout(layout)

        modal_dialog.exec_()
    def get_randomColors(self,color):
        self.RanColor1 = color[0]
        self.RanColor2 = color[1]
        self.RanColor3 = color[2]

    def getCPU_usage(self,cpu):
        self.Qlabel_cpu.setText(str(cpu) + " %")
        if cpu > 15: self.Qlabel_cpu.setStyleSheet("color: rgb(23, 63, 95);")
        if cpu > 25: self.Qlabel_cpu.setStyleSheet("color: rgb(32, 99, 155);")
        if cpu > 45: self.Qlabel_cpu.setStyleSheet("color: rgb(60, 174, 163);")
        if cpu > 65: self.Qlabel_cpu.setStyleSheet("color: rgb(246, 213, 92);")
        if cpu > 85: self.Qlabel_cpu.setStyleSheet("color: rgb(237, 85, 59);")

    def getRAM_usage(self,ram):
        self.Qlabel_ram.setText(str(ram[2]) + " %")
        if ram[2] > 15: self.Qlabel_ram.setStyleSheet("color: rgb(23, 63, 95);")
        if ram[2] > 25: self.Qlabel_ram.setStyleSheet("color: rgb(32, 99, 155);")
        if ram[2] > 45: self.Qlabel_ram.setStyleSheet("color: rgb(60, 174, 163);")
        if ram[2] > 65: self.Qlabel_ram.setStyleSheet("color: rgb(246, 213, 92);")
        if ram[2] > 85: self.Qlabel_ram.setStyleSheet("color: rgb(237, 85, 59);")

    def getTemp_usage(self,temp):
        self.Qlabel_temp.setText(str(temp) + " *C")
        if temp > 30: self.Qlabel_temp.setStyleSheet("color: rgb(23, 63, 95);")
        if temp > 35: self.Qlabel_temp.setStyleSheet("color: rgb(60, 174, 155);")
        if temp > 40: self.Qlabel_temp.setStyleSheet("color: rgb(246,213, 92);")
        if temp > 45: self.Qlabel_temp.setStyleSheet("color: rgb(237, 85, 59);")
        if temp > 50: self.Qlabel_temp.setStyleSheet("color: rgb(255, 0, 0);")

    def get_FPS(self,fps):
        self.Qlabel_fps.setText(str(fps))
        if fps > 5: self.Qlabel_fps.setStyleSheet("color: rgb(237, 85, 59);")
        if fps > 15: self.Qlabel_fps.setStyleSheet("color: rgb(60, 174, 155);")
        if fps > 25: self.Qlabel_fps.setStyleSheet("color: rgb(85, 170, 255);")
        if fps > 35: self.Qlabel_fps.setStyleSheet("color: rgb(23, 63, 95);")

    def clock(self):
        self.DateTime = QDateTime.currentDateTime()
        self.lcd_clock.display(self.DateTime.toString('hh:mm:ss'))


# Close Error Notification window
    def Close_Error(self):
        self.Win_error.close()

# ! Function oneclick to hsv parameter
    def GetObject_one(self):
       print("xóa tàu")

    def set_roi(self):
        print("create time change")
    #     thêm thời gian mới cho tàu

    @pyqtSlot(np.ndarray)
    def opencv_emit(self, Image):

        #QPixmap format
        original = self.cvt_cv_qt(Image)
        #Numpy Array format
        self.CopyImage =  Image[self.roi_y:self.roi_h,
                                self.roi_x:self.roi_w]
        self.disp_main.setPixmap(original)
        self.disp_main.setScaledContents(True)

    def get_ROIX(self,x):
        self.roi_x = x

    def get_ROIY(self,y):
        self.roi_y = y

    def get_ROIW(self,w):
        self.roi_w = w

    def get_ROIH(self,h):
        self.roi_h = h

    def cvt_cv_qt(self, Image):
        offset = 5
        rgb_img = cv2.cvtColor(src=Image,code=cv2.COLOR_BGR2RGB)
        h,w,ch = rgb_img.shape
        bytes_per_line = ch * w
        cvt2QtFormat = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(cvt2QtFormat)


        return pixmap #QPixmap.fromImage(cvt2QtFormat)
#----------------------------------------------------------------------------------------------------

    def StartWebCam(self,pin):
        try:
            self.textEdit.append(f"{self.DateTime.toString('d MMMM yy hh:mm:ss')}: Start Webcam ({self.camlist.currentText()})")
            self.btn_stop.setEnabled(True)
            self.btn_start.setEnabled(False)

            global camIndex
            camIndex = self.camlist.currentIndex()

        # Opencv QThread
            self.Worker1_Opencv = ThreadClass()
            self.Worker1_Opencv.ImageUpdate.connect(self.opencv_emit)
            self.Worker1_Opencv.FPS.connect(self.get_FPS)
            self.Worker1_Opencv.start()


        except Exception as error :
            pass

    def StopWebcam(self,pin):
        self.textEdit.append(f"{self.DateTime.toString('d MMMM yy hh:mm:ss')}: Stop Webcam ({self.camlist.currentText()})")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.Worker1_Opencv.stop()

    def Close_software(self):
        self.resource_usage.stop()
        sys.exit(app.exec_())

    def Ready_lamp(self):
        if self.Status_lamp[0]: self.Qlabel_greenlight.setStyleSheet("background-color: rgb(85, 255, 0); border-radius:30px")
        else : self.Qlabel_greenlight.setStyleSheet("background-color: rgb(184, 230, 191); border-radius:30px")
        self.Status_lamp[0] = not self.Status_lamp[0]
    # def Danger_lamp(self):
    #     if self.Status_lamp[0]: self.Qlabel_redlight.setStyleSheet("background-color: rgb(255,77,77); border-radius:30px")
    #     else : self.Qlabel_redlight.setStyleSheet("background-color: rgb(255,128,128); border-radius:30px")
    #     self.Status_lamp[0] = not self.Status_lamp[0]



if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

