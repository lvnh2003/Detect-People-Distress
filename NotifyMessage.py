import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton

class NotifyMessage(QDialog):
    def __init__(self, message, parent=None):
        super(NotifyMessage, self).__init__(parent)
        self.setWindowTitle("Notification")

        layout = QVBoxLayout()

        label = QLabel(message)
        layout.addWidget(label)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        self.setLayout(layout)
        self.exec_()


