import sys
import json
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QColor, QTextCharFormat, QIcon

class DataEntryApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.initUI()

    def initUI(self):
        # Main layout
        self.layout = QtWidgets.QGridLayout(self)
        self.setWindowTitle('Phone Portal Data Entry')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(0, 0, 500, 400)
        
        # Calendar widget
        self.calendar = QtWidgets.QCalendarWidget(self)
        self.layout.addWidget(self.calendar, 0, 0, 1, 2)
        self.loadCalendarData()

        button_size = QtCore.QSize(150, 30)
        # Headers
        self.videoHeader = QtWidgets.QLabel('Video Calls', self)
        self.layout.addWidget(self.videoHeader, 1, 1)

        # Video and Audio Input Boxes
        self.videoInput = QtWidgets.QLineEdit(self)
        self.videoInput.setFixedSize(button_size)
        self.audioInput = QtWidgets.QLineEdit(self)
        self.audioInput.setFixedSize(button_size)
        self.videoInput.setPlaceholderText('Video')
        self.audioInput.setPlaceholderText('Audio')
        self.layout.addWidget(self.videoInput, 11, 1)
        self.layout.addWidget(self.audioInput, 11, 2)
        
        # Connect signals for video and audio input boxes
        self.videoInput.textChanged.connect(self.updateSums)
        self.audioInput.textChanged.connect(self.updateSums)

        # Block labels and input fields
        block_names = ['AB-Block-1', 'AB-Block-2', 'Cellular-Block', 'HS-Block', 'A-Class', 'Quarantine', 'Hospital','Emulakath']
        # Block labels and input fields
        self.blocks = []
        for i, name in enumerate(block_names):
            block_label = QtWidgets.QLabel(name, self)
            video_input = QtWidgets.QLineEdit(self)
            video_input.setFixedSize(button_size)
            # Set maximum length for input fields
            video_input.setMaxLength(3)
            self.blocks.append((block_label, video_input))
            self.layout.addWidget(block_label, i+2, 0)
            self.layout.addWidget(video_input, i+2, 1)
        
        # Grand Total Label
        self.grandTotalLabel = QtWidgets.QLabel('Grand Total: 0', self)
        self.layout.addWidget(self.grandTotalLabel,12, 1)
        
        # Buttons
        self.saveButton = QtWidgets.QPushButton('Save Data', self)
        self.loadButton = QtWidgets.QPushButton('Load Data', self)
        self.resetButton = QtWidgets.QPushButton('Reset', self)
        #self.retrieveButton = QtWidgets.QPushButton('Retrieve Data', self)
        self.layout.addWidget(self.saveButton, 3, 2,1,1)
        self.layout.addWidget(self.loadButton, 4, 2,1,1)
        self.layout.addWidget(self.resetButton, 5, 2,1,1)
        #self.layout.addWidget(self.retrieveButton, 14, 1, 1, 3)

        # Signals
        self.saveButton.clicked.connect(self.saveData)
        self.loadButton.clicked.connect(self.loadData)
        self.resetButton.clicked.connect(self.resetFields)
        #self.retrieveButton.clicked.connect(self.retrieveData)

    def updateSums(self):
        video_total = int(self.videoInput.text() or '0')
        audio_total = int(self.audioInput.text() or '0')
        grand_total = video_total + audio_total
        self.grandTotalLabel.setText(f'Grand Total: {grand_total}')

    def loadData(self):
        # Load data for the selected date
        date_str = self.calendar.selectedDate().toString(QtCore.Qt.DateFormat.ISODate)
        try:
            with open(r'datas\data.json', 'r') as f:
                self.data = json.load(f)
            if date_str in self.data:
                # New block names mapping
                block_names = ['AB-Block-1', 'AB-Block-2', 'Cellular-Block', 'HS-Block', 'A-Class', 'Quarantine', 'Hospital']
                for i, block in enumerate(self.blocks, start=1):
                    block_name = block_names[i-1] if i <= len(block_names) else f'block_{i}'
                    block_data = self.data[date_str].get(block_name, {})
                    block[1].setText(str(block_data))

                self.videoInput.setText(str(self.data[date_str]['category']['video']))
                self.audioInput.setText(str(self.data[date_str]['category']['audio']))
                self.updateSums()
        except FileNotFoundError:
            print("Data file not found. Starting with empty data.")
        except json.JSONDecodeError:
            print("Data file is not in valid JSON format.")

    def saveData(self):
        date_str = self.calendar.selectedDate().toString(QtCore.Qt.DateFormat.ISODate)
        self.data[date_str] = {}
        
        # New block names mapping
        block_names = ['AB-Block-1', 'AB-Block-2', 'Cellular-Block', 'HS-Block', 'A-Class', 'Quarantine', 'Hospital','Emulakath']
        
        for i, block in enumerate(self.blocks, start=1):
            count = int(block[1].text() or '0')
            block_name = block_names[i-1] if i <= len(block_names) else f'block_{i}'
            self.data[date_str][block_name] = count
        
        # Save video and audio categories
        video_total = int(self.videoInput.text() or '0')
        audio_total = int(self.audioInput.text() or '0')
        self.data[date_str]['category'] = {'video': video_total, 'audio': audio_total}
        
        with open(r'datas\data.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def loadCalendarData(self):
        # Load the data to check which dates have entries
        try:
            with open(r'datas\data.json', 'r') as f:
                self.data = json.load(f)
            for date_str in self.data:
                date = QtCore.QDate.fromString(date_str, "yyyy-MM-dd")
                format = QTextCharFormat()
                format.setForeground(QColor('grey'))
                self.calendar.setDateTextFormat(date, format)
        except Exception as e:
            print(f"An error occurred: {e}")

    def resetFields(self):
        # Clear all input fields
        for _, video_input in self.blocks:
            video_input.clear()
        self.videoInput.clear()
        self.audioInput.clear()
        self.updateSums()

    def retrieveData(self):
        # Logic to retrieve data and display it in a new window
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = DataEntryApp()
    # apply_stylesheet(app, theme='dark_teal.xml')  # PyQt6 does not have the qt_material package
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()