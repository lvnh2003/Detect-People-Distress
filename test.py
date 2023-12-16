from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QScrollArea, QPushButton, QHBoxLayout, QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Sample data
        trains = [
            [1, "Train1", "08:00", "10:00"],
            [2, "Train2", "12:00", "14:00"],
            [3, "Train3", "16:00", "18:00"]
        ]

        # Create widgets
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        self.table_widget = QTableWidget(self.scroll_widget)
        self.table_widget.setRowCount(len(trains))
        self.table_widget.setColumnCount(3)

        # Combine two columns into one and populate the table with data
        for row_index, row_data in enumerate(trains):
            combined_data = f"{row_data[2]} - {row_data[3]}"
            item = QTableWidgetItem(combined_data)
            self.table_widget.setItem(row_index, 0, item)
            item_name_train = QTableWidgetItem(row_data[1])
            self.table_widget.setItem(row_index, 1, item_name_train)

            # Create buttons for each row
            delete_button = QPushButton("Delete", self.table_widget)
            delete_button.clicked.connect(lambda _, i=row_index: self.delete_selected(i))
            edit_button = QPushButton("Edit", self.table_widget)
            edit_button.clicked.connect(lambda _, i=row_index: self.edit_selected(i))

            # Create a layout for buttons
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)

            # Create a container widget for the layout
            button_container = QWidget()
            button_container.setLayout(button_layout)

            # Set the container widget as the cell widget for the third column
            self.table_widget.setCellWidget(row_index, 2, button_container)

        # Set header labels for the new columns
        header_labels = ["Time", "Name Train", "Actions"]
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        # Set column width for the "Actions" column
        self.table_widget.setColumnWidth(2, 120)

        # Connect the itemClicked event
        self.table_widget.itemClicked.connect(self.row_clicked)

        # Layout
        table_layout = QVBoxLayout(self.scroll_widget)
        table_layout.addWidget(self.table_widget)
        self.scroll_widget.setLayout(table_layout)

        self.setCentralWidget(self.scroll_area)

    def edit_selected(self, row):
        # Implement your edit logic here, for example, open a dialog for editing
        print(f"Edit selected row: {row}")

    def delete_selected(self, row):
        # Implement your delete logic here, for example, show a confirmation dialog
        print(f"Delete selected row: {row}")

    def row_clicked(self, item):
        row = item.row()
        QMessageBox.information(self, "Row Clicked", f"You clicked on row {row + 1}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
