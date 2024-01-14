import threading
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAbstractItemView, QHeaderView
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap
import cv2,time,sys,sysinfo
import numpy as np
import random as rnd
from shapely.geometry import Point, Polygon
from ultralytics import YOLO
from playsound import playsound
import torch
from datetime import time as timeDB, datetime
from draw_detect import DrawDetect
from CRUD.add_camera import AddCam
from NotifyMessage import NotifyMessage
from Model.Train import Train
from database import insert,listTrain
from CRUD.update import UpdateForm
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = YOLO('./detect/train/weights/best.pt').float().to(device)
trains = None
camIndex = 0
if torch.cuda.is_available():
    print("run with GPU")
def getPoint():
    global camIndex
    points = []
    try:
        with open("CAMERA{}.txt".format(camIndex+1), 'r') as file:
            for line in file:
                x, y = map(int, line.strip().split(','))
                points.append([x, y])
        return np.array(points)
    except:
        return None
points = getPoint()
def getCameras():
    with open('cameras.txt', 'r') as file:
        cameras = [line.strip() for line in file]
    return cameras
cameras = getCameras()

class ThreadClass(QThread):
    ImageUpdate = pyqtSignal(np.ndarray)
    FPS = pyqtSignal(int)
    global camIndex

    def play_sound(self):
        playsound("warning.wav")
    def run(self):
        Capture = cv2.VideoCapture(cameras[camIndex])


        Capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        Capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        self.ThreadActive = True
        prev_frame_time = 0
        new_frame_time = 0
        while self.ThreadActive:
            ret,frame_cap = Capture.read()

            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            self.draw_polygon(frame_cap, points)
            if ret:
                results = model(frame_cap, conf=0.7, verbose=False)
                if len(results[0]) > 0:
                    box = results[0].boxes.xyxy[0]
                    if self.draw_prediction(box):
                        time_current = datetime.now().time()
                        for row_index, row_data in enumerate(trains):
                            start_time = datetime.combine(datetime.today(),
                                                          datetime.strptime(row_data[2], "%H:%M").time())
                            end_time = datetime.combine(datetime.today(),
                                                        datetime.strptime(row_data[3], "%H:%M").time())
                            if start_time.time() <= time_current <= end_time.time():
                                cv2.putText(frame_cap, "Fall detect!!!!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                            (0, 0, 255), 2)
                                sound_thread = threading.Thread(target=self.play_sound)
                                sound_thread.start()

                annotated_frame = results[0].plot()
                self.ImageUpdate.emit(annotated_frame)
                self.FPS.emit(fps)

    def stop(self):
        self.ThreadActive = False
        self.quit()

    def draw_polygon(self, image, points):
        if len(points) > 1:
            cv2.polylines(image, [np.array(points)], isClosed=False, color=(0, 0, 255), thickness=2)
        else:
            pass
    def draw_prediction(self, box):
        x_min, y_min, x_max, y_max = box.tolist()
        centroid = ((x_min + x_max) // 2, (y_min + y_max) // 2)
        return self.isInside(centroid)

    def isInside(self, centroid):
        polygon = Polygon(points)
        centroid = Point(centroid)
        return polygon.contains(centroid)
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

#   QLabel display
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("ui/Opencv_PiDash.ui",self)
        self.btn_start.clicked.connect(self.StartWebCam)
        self.btn_start.setStyleSheet("background-color: red; color: white;")
        self.btn_stop.clicked.connect(self.StopWebcam)

        self.resource_usage = boardInfoClass()
        self.resource_usage.start()
        self.resource_usage.cpu.connect(self.getCPU_usage)
        self.resource_usage.ram.connect(self.getRAM_usage)

        self.randomColor_usage = randomColorClass()
        self.randomColor_usage.start()
        self.randomColor_usage.color.connect(self.get_randomColors)




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

        self.btn_close.clicked.connect(self.Close_software)

        self.btn_roi_set.clicked.connect(self.addTrain)
        self.btn_stop.setEnabled(False)

        self.btn_draw.clicked.connect(self.showModal)
        self.listDataToTable()
        self.update_form = UpdateForm(self)
        self.add_camera.setFixedSize(23,23)
        self.add_camera.setStyleSheet("background-color: #FFCC33; color : white")
        self.add_camera.clicked.connect(self.open_cam)

        self.camlist.addItems(self.convertNameCamera())
    def showModal(self):
        global camIndex
        try:
            self.draw = DrawDetect(cameras[camIndex],camIndex,self)
            self.draw.show()
        except Exception as e:
            NotifyMessage("Choose camera first!!!",0)
    def open_cam(self):
        self.newCam = AddCam(self)
        self.newCam.show()
    def convertNameCamera(self):
        names = []
        if cameras is not None:
            for i in range(len(cameras)):
                names.append("CAMERA{}".format(i+1))
            return names
        return None
    def resetListCamera(self):
        global cameras
        with open('cameras.txt', 'r') as file:
            cameras = [line.strip() for line in file]
        self.camlist.clear()
        self.camlist.addItems(self.convertNameCamera())

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

    def addTrain(self):
        start_H = self.start_H.value()
        start_M = self.start_M.value()
        end_H = self.end_H.value()
        end_M = self.end_M.value()
        name = self.name_Train.toPlainText()
        if name:
            train = Train(name,timeDB(start_H,start_M),timeDB(end_H,end_M))
            insert(train)
            NotifyMessage("Add a new timeline of success")
            self.listDataToTable()
        else:
            NotifyMessage("Please enter the name!!",0)
    def listDataToTable(self):
        global trains
        trains = listTrain()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.data_action)
        self.table.setRowCount(len(trains))
        self.table.setColumnCount(3)  # Set to 2 because we will merge two columns into one
        self.table.setColumnHidden(0, True)
        # Combine two columns into one and populate the table with data
        for row_index, row_data in enumerate(trains):
            item_id = QTableWidgetItem(str(row_data[0]))
            self.table.setItem(row_index, 0, item_id)
            combined_data = f"{row_data[2]} - {row_data[3]}"  # Combine "start" and "end"
            item = QTableWidgetItem(combined_data)
            self.table.setItem(row_index, 1, item)
            item_name_train = QTableWidgetItem(row_data[1])
            self.table.setItem(row_index, 2, item_name_train)

        # Set header labels for the new columns
        header_labels = ["ID","Time", "Name Train"]
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.setStyleSheet("QTableWidget { background-color: white; }")
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: lightgray; }")

    def data_action(self):

        selected_items = self.table.selectedItems()
        if selected_items:
            selected_row = selected_items[0].row()

            # Get the ID value from the hidden column
            id_item = self.table.item(selected_row, 0)  # Assuming ID is in column 0
            if id_item:
                train_id = int(id_item.text())
                self.update_form.update_data(train_id)

                # Show the UpdateForm
                self.update_form.show()

    @pyqtSlot(np.ndarray)
    def opencv_emit(self, Image):

        #QPixmap format
        original = self.cvt_cv_qt(Image)

        self.disp_main.setPixmap(original)
        self.disp_main.setScaledContents(True)
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
            global points
            self.textEdit.append(f"{self.DateTime.toString('d MMMM yy hh:mm:ss')}: Start Webcam ({self.camlist.currentText()})")
            self.btn_stop.setEnabled(True)
            self.btn_stop.setStyleSheet("background-color: red; color: white;")
            self.btn_start.setEnabled(False)
            self.btn_start.setStyleSheet("color: grey; background-color: white")

            global camIndex
            camIndex = self.camlist.currentIndex()
            points = getPoint()
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
        self.btn_start.setStyleSheet("background-color: red; color: white;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("color: grey; background-color: white")
        self.Worker1_Opencv.stop()

    def Close_software(self):
        self.resource_usage.stop()
        sys.exit()

    def Ready_lamp(self):
        if self.Status_lamp[0]: self.Qlabel_greenlight.setStyleSheet("background-color: rgb(85, 255, 0); border-radius:30px")
        else : self.Qlabel_greenlight.setStyleSheet("background-color: rgb(184, 230, 191); border-radius:30px")
        self.Status_lamp[0] = not self.Status_lamp[0]
    def newPoint(self):
        global camIndex
        global points
        pointsNew = []
        with open("CAMERA{}.txt".format(camIndex+1), 'r') as file:
            for line in file:
                x, y = map(int, line.strip().split(','))
                pointsNew.append([x, y])
        points = pointsNew


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

