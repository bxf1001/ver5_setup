import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtGui import QIcon
import sqlite3
from database_test import insert_user,update_user,delete_user
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMessageBox
import os



class AddUser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the window
        self.setWindowTitle('Phone Portal User Details Manager')
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setGeometry(1500, 100, 400, 500)

        # Create layout and widgets
        layout = QVBoxLayout()
        #self.user_id_label = QLabel('User ID:', self)
        self.user_id_input = QLineEdit(self)
        self.user_id_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        self.user_id_input.setPlaceholderText('Enter User ID')
        #self.name_label = QLabel('Name:', self)
        self.name_input = QLineEdit(self)
        self.name_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        self.name_input.setPlaceholderText('NAME')
        #self.contact1_label = QLabel('Contact 1:', self)
        self.contact1_input = QLineEdit(self)
        self.contact1_input.setPlaceholderText('Enter Contact 1')
        self.contact1_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        #self.contact2_label = QLabel('Contact 2:', self)
        self.contact2_input = QLineEdit(self)
        self.contact2_input.setPlaceholderText('Enter Contact 2')
        self.contact2_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        #self.contact3_label = QLabel('Contact 3:', self)
        self.contact3_input = QLineEdit(self)
        self.contact3_input.setPlaceholderText('Enter Contact 3')
        self.contact3_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        self.save_button = QPushButton('Save', self)
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        self.save_button.setShortcut('Ctrl+S')
        #self.edit_button = QPushButton('Edit', self)
        self.delete_button = QPushButton('Delete', self)
        self.delete_button.setStyleSheet("background-color: #f44336; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        self.load_button = QPushButton('Load', self)
        self.load_button.setShortcut('Ctrl+L')
        self.load_button.setStyleSheet("background-color: #008CBA; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")
        self.reset_button = QPushButton('Reset')
        self.reset_button.setShortcut('Ctrl+R')
        self.reset_button.setStyleSheet("background-color: magenta; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")

        # Connect the Load button to the load_user function
        self.load_button.clicked.connect(self.load_user_from_db)
        # Add widgets to layout
        #layout.addWidget(self.user_id_label)
        layout.addWidget(self.user_id_input)
        #layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        #layout.addWidget(self.contact1_label)
        layout.addWidget(self.contact1_input)
        #.addWidget(self.contact2_label)
        layout.addWidget(self.contact2_input)
        #.addWidget(self.contact3_label)
        layout.addWidget(self.contact3_input)
        layout.addWidget(self.save_button)
        #layout.addWidget(self.edit_button)
        layout.addWidget(self.load_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.delete_button)
        

        # Set the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect buttons to functions
        self.save_button.clicked.connect(self.save_user)
        #self.edit_button.clicked.connect(self.edit_user)
        self.delete_button.clicked.connect(self.delete_user)
        self.reset_button.clicked.connect(self.reset_function)

    def save_user(self):
        user_id = self.user_id_input.text()
        name = self.name_input.text()
        contact1 = self.contact1_input.text()
        contact2 = self.contact2_input.text()
        contact3 = self.contact3_input.text()
        insert_user(user_id, name, contact1, contact2, contact3)
        # Load existing data
        try:
            with open(r'datas\\user_data.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        # Update data
        data[user_id] = {
            'name': name,
            '1': contact1,
            '2': contact2,
            '3': contact3
        }

        # Save data
        with open(r'datas\\user_data.json', 'w') as file:
            json.dump(data, file, indent=4)

        QMessageBox.information(self, 'Success', 'User saved successfully!')
        update_user(user_id, name, contact1, contact2, contact3)


    def load_user(self):
        user_id = self.user_id_input.text()
        # Load existing data
        try:
            with open(r'datas\\user_data.json', 'r') as file:
                data = json.load(file)

            # Check if user exists and load details
            if user_id in data:
                self.name_input.setText(data[user_id].get('name', ''))
                self.contact1_input.setText(data[user_id].get('1', ''))
                self.contact2_input.setText(data[user_id].get('2', ''))
                self.contact3_input.setText(data[user_id].get('3', ''))
            else:
                QMessageBox.warning(self, 'Error', 'User ID not found!')
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'Userdata file not found!')




    def load_user_from_db(self, user_id):
        # Define the database path
        db_path = r'D:\Ver_5_updated-main\database\\user_data.db'
        alternative_db_path = r'\\booth3\PhoneBooth_bkup\database_bkup\\user_data.db'

        # Check if the database file exists
        if not os.path.exists(db_path):
            db_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
        

        # Connect to the SQLite database
        if not os.path.exists(db_path):
            QMessageBox.warning(self, 'Error', 'Database file not found!')
            return
        
        if os.path.exists(db_path):
        # If it exists, connect to it
            conn = sqlite3.connect(db_path)
        else:
        # If it doesn't exist, connect to the alternative database file
            conn = sqlite3.connect(alternative_db_path)


        c = conn.cursor()

        # Convert the user ID to an integer
        user_id = self.user_id_input.text()

        # Query the database for the user
        c.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user_info = c.fetchone()

        # Close the connection
        conn.close()

        # If the user is found, load their data into the input fields
        if user_info is not None:
            self.name_input.setText(user_info[1])  # Adjust these indices based on your database schema
            self.contact1_input.setText(user_info[2])
            self.contact2_input.setText(user_info[3])
            self.contact3_input.setText(user_info[4])
            return user_info
        else:
            QMessageBox.warning(self, 'Error', 'User ID not found!')
            return None
    def edit_user(self):
        user_id = self.user_id_input.text()
        name = self.name_input.text()
        contact1 = self.contact1_input.text()
        contact2 = self.contact2_input.text()
        contact3 = self.contact3_input.text()

        # Load existing data
        try:
            with open(r'datas\\user_data.json', 'r+') as file:
                data = json.load(file)

                # Check if user exists
                if user_id in data:
                    # Update user details
                    data[user_id] = {
                        'name': name,
                        '1': contact1,
                        '2': contact2,
                        '3': contact3
                    }
                    # Move the file pointer to the beginning of the file
                    file.seek(0)
                    # Write the updated data back to the file
                    json.dump(data, file, indent=4)
                    # Truncate the file to the new size
                    file.truncate()
                    QMessageBox.information(self, 'Success', 'User details updated successfully!')
                else:
                    QMessageBox.warning(self, 'Error', 'User ID not found!')
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'Userdata file not found!')

    def delete_user(self):
        user_id = self.user_id_input.text()

        # Load existing data
        try:
            with open(r'datas\\user_data.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'Userdata file not found!')
            return
        delete_user(user_id)
        # Delete user
        if user_id in data:
            del data[user_id]
            with open(r'datas\\user_data.json', 'w') as file:
                json.dump(data, file, indent=4)
            QMessageBox.information(self, 'Success', 'User deleted successfully!')
        else:
            QMessageBox.warning(self, 'Error', 'User ID not found!')

    def reset_function(self):
        self.user_id_input.clear()
        self.name_input.clear()
        self.contact1_input.clear()
        self.contact2_input.clear()
        self.contact3_input.clear()
        
    def main(self):
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        ex = AddUser()
       # apply_stylesheet(app, theme='dark_teal.xml')
        ex.show()
        sys.exit(app.exec())
