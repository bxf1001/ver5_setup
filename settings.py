from PyQt6.QtWidgets import QApplication, QWidget,QPushButton,QLineEdit,QLabel,QFileDialog,QGridLayout
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from json.decoder import JSONDecodeError
import sys
import json
from PyQt6.QtWidgets import QMessageBox

class Settings(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")  # Set your window title
        self.setGeometry(100,100,400,100)
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        # Create buttons

        # Define the size of the buttons
        button_size = QSize(100, 40)  # Adjust the size as needed
        icon_size = QSize(10, 10)


        self.input_select = QLineEdit()
        self.input_select.setPlaceholderText('Enter Path')
        # Create buttons and set their size
        self.save_button = QPushButton('Save')
        self.save_button.setIcon(QIcon('icons/user.png'))
        self.save_button.setFixedSize(button_size)
        self.save_button.setIconSize(icon_size)
        self.save_button.setToolTip('Save the path')
        self.save_button.clicked.connect(lambda: self.save_path_to_json(self.input_select.text(), self.input_select_data.text(), self.select_primary_db_label_input.text()))
        self.save_button.setEnabled(False)

        self.input_select_data = QLineEdit()
        self.input_select_data.setPlaceholderText('Enter Data Path')



        self.path_label = QLabel("Select recording Path:")
        self.select_button = QPushButton('Select')
        self.select_button.setIcon(QIcon('icons/folder.png'))
        self.select_button.setFixedSize(button_size)
        self.select_button.setIconSize(icon_size)
        self.select_button.setToolTip('Select the path where the recordings will be saved')
        self.select_button.clicked.connect(self.choose_file_path)

        self.path_label_data = QLabel("Select Primary Database:")
        self.select_button_data = QPushButton('Select')
        self.select_button_data.setIcon(QIcon('icons/folder.png'))
        self.select_button_data.setFixedSize(button_size)
        self.select_button_data.setIconSize(icon_size)
        self.select_button_data.setToolTip('Select the path where the data will be saved')
        self.select_button_data.clicked.connect(self.set_data_file_path)
        
        self.select_primary_db_label = QLabel('Select Secondary Database:')
        self.select_primary_db_label_input = QLineEdit()
        self.select_primary_db_label_input.setPlaceholderText('Enter Primary Database Path')
        self.select_primary_db_label_input.setReadOnly(True)
        self.select_primary_db_label.setToolTip('Select the primary database file path')
        self.select_primary_db = QPushButton('Select')
        self.select_primary_db.setIcon(QIcon('icons/folder.png'))
        self.select_primary_db.setFixedSize(button_size)
        self.select_primary_db.setIconSize(icon_size)
        self.select_primary_db.setToolTip('Select the primary database file path')
        self.select_primary_db.clicked.connect(self.set_primary_db_path)

        self.exit_button = QPushButton('Exit')
        self.exit_button.setIcon(QIcon('icons/exit.png'))
        self.exit_button.setFixedSize(button_size)
        self.exit_button.setIconSize(icon_size)
        self.exit_button.clicked.connect(self.close)



        layout.addWidget(self.path_label,0,0,1,2)
        layout.addWidget(self.select_button,1,3)
        layout.addWidget(self.input_select,1,0,1,2)
        layout.addWidget(self.save_button,8,0)
        layout.addWidget(self.path_label_data,3,0,1,2)
        layout.addWidget(self.select_button_data,4,3)
        layout.addWidget(self.input_select_data,4,0,1,2)
        layout.addWidget(self.select_primary_db_label,6,0,1,2)
        layout.addWidget(self.select_primary_db_label_input,7,0,1,2)
        layout.addWidget(self.select_primary_db,7,3)
        layout.addWidget(self.exit_button,8,3)

        self.setLayout(layout)
        
    

    def set_primary_db_path(self):
        try:
            primary_db_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
            if primary_db_path:  # Check if a file was selected
                self.select_primary_db_label_input.setText(primary_db_path)
                self.save_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"An error occurred: {e}")
        
    def choose_file_path(self): #
        try:
            file_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
            self.input_select.setText(file_path)
            self.save_button.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"An error occurred: {e}")
    
    def set_data_file_path(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
            if file_path:  # Check if a file was selected
                self.input_select_data.setText(file_path)
                self.save_button.setEnabled(True)           
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"An error occurred: {e}")


    def save_path_to_json(self, file_path, data_path, primary_db_path):
        try:
            with open(r'datas\\url.json', 'r+') as json_file:
                try:
                    data = json.load(json_file)
                except JSONDecodeError:
                    data = {}
    
                data['path'] = file_path
                json_file.seek(0)
                json.dump(data, json_file)
                json_file.truncate()
    
                data["data_path"] = data_path
                json_file.seek(0)
                json.dump(data, json_file)
                json_file.truncate()
    
                data['data_path2'] = primary_db_path
                json_file.seek(0)
                json.dump(data, json_file)
                json_file.truncate()
    
        except IOError as e:
            QMessageBox.warning(self, 'Error', f"An error occurred: {e}")
    
        QMessageBox.information(self, 'Information', 'Path saved successfully')


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    
    ex = Settings()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()