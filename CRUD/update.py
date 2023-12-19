import sys

from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QLineEdit, QVBoxLayout, QMessageBox
from PyQt5 import uic
from datetime import time as timeDB
from NotifyMessage import NotifyMessage
from database import getTrain,update,remove
class UpdateForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.train_id = None
        uic.loadUi("update.ui", self)
        self.setParent(parent)  # Set the parent after loading the UI
        self.setWindowTitle("Update Form")
        self.updateBtn.clicked.connect(self.update_train)
        self.deleteBtn.clicked.connect(self.remove_train)

    def update_data(self, train_id):
        self.train_id = train_id
        train_data = getTrain(train_id)
        self.name.setText(train_data[1])
        start = self.time_separation(train_data[2])
        end = self.time_separation(train_data[3])
        self.start_H.setValue(start[0])
        self.start_M.setValue(start[1])
        self.end_H.setValue(end[0])
        self.end_M.setValue(end[1])
    def closeEvent(self,event):
        self.accept()
    def time_separation(self,time):

        result = list(map(int, time.split(':')))

        return result
    def update_train(self):
        start_H = self.start_H.value()
        start_M = self.start_M.value()
        end_H = self.end_H.value()
        end_M = self.end_M.value()
        name = self.name.toPlainText()
        if name:
            update(self.train_id,name,timeDB(start_H,start_M),timeDB(end_H,end_M))
            self.parent().listDataToTable()
            NotifyMessage("Successfully updated!")
            self.accept()

        else:
            NotifyMessage("The name must be filled in!!", 0)
    def remove_train(self):
       confirmation = QMessageBox.question(self, "Confirmation", "Are you sure you want to delete?",
                                           QMessageBox.Yes | QMessageBox.No)

       if confirmation == QMessageBox.Yes:
           remove(self.train_id)
           self.parent().listDataToTable()
           self.accept()  # Close the dialog
       else:
           pass