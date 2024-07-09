import sys 
import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon

class TimestampedDataSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText('Enter User ID or Number')
        layout.addWidget(self.search_input)

        search_button = QPushButton('Search', self)
        search_button.clicked.connect(self.search_data)
        search_button.setShortcut(Qt.Key.Key_Enter)
        layout.addWidget(search_button)

        self.results_table = QTableWidget(self)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(['User ID', 'Name', 'Number', 'Timestamp', 'Recordings'])
        self.results_table.setColumnWidth(0, 100)
        self.results_table.setColumnWidth(1, 100)
        self.results_table.setColumnWidth(2, 100)
        self.results_table.setColumnWidth(3, 200)
        self.results_table.setColumnWidth(4, 200)
        layout.addWidget(self.results_table)

        self.setLayout(layout)
        self.setWindowTitle('Phone Portal Search Data')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(100, 100, 800, 600)

    def search_data(self):
        search_term = self.search_input.text()
        try:
            with open(r'datas\timestamped_data.json', 'r') as f:
                self.results_table.setRowCount(0)
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if search_term in (entry.get('user_id', ''), entry.get('number', ''), entry.get('name', '')):
                            row_position = self.results_table.rowCount()
                            self.results_table.insertRow(row_position)
                            self.results_table.setItem(row_position, 0, QTableWidgetItem(entry['user_id']))
                            self.results_table.setItem(row_position, 1, QTableWidgetItem(entry.get('name', 'Unknown')))
                            self.results_table.setItem(row_position, 2, QTableWidgetItem(entry['number']))
                            self.results_table.setItem(row_position, 3, QTableWidgetItem(entry['timestamp']))
                            recording_link = QTableWidgetItem('Open Recording' if entry.get('recording') else 'No Recording')
                            recording_link.setData(1000, entry.get('recording', ''))
                            self.results_table.setItem(row_position, 4, recording_link)
        except FileNotFoundError:
            QMessageBox.information(self, 'File Not Found', 'No timestamped data file found.')

    def cellClicked(self, row, column):
        if column == 4:
            recording_path = self.results_table.item(row, column).data(1000)
            if recording_path != 'Not Available' and os.path.exists(recording_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(recording_path))
            elif recording_path == 'Not Available':
                QMessageBox.information(self, 'Recording Not Available', 'No recording file is associated with this entry.')
            else:
                QMessageBox.information(self, 'File Not Found', 'The recording file does not exist.')

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = TimestampedDataSearch()
    ex.results_table.cellClicked.connect(ex.cellClicked)
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()