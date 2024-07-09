import datetime
import subprocess
import sys
from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QThreadPool,QObject ,Qt,QSize
from PyQt6.QtGui import QIcon,QKeySequence ,QDoubleValidator ,QFont,QCursor
from PyQt6.QtWidgets import QApplication, QStyleFactory, QMainWindow, QWidget, QLabel, QLineEdit, QListWidget,QListWidgetItem, QPushButton, QHBoxLayout, QGridLayout, QProgressBar,QMessageBox
import warnings
import uuid
from queue import Queue
from pywinauto import Application
from pywinauto.keyboard import send_keys
import keyboard
from add_user import AddUser
from time import sleep
import json
from queue import Queue
import sqlite3
import os
from reader import QScannerLocker ,QRCodeScanner

os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'


warnings.simplefilter("ignore", UserWarning)
import cv2
from pyzbar.pyzbar import decode
import threading
from pynput.keyboard import Key, Listener, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import time






class WorkerSignals(QObject): # Create a class to hold the
    error = pyqtSignal(tuple) # Create an error signal with a tuple parameter
    progress = pyqtSignal(int) # Create a progress signal with an additional string parameter
    finished = pyqtSignal(str) # Create a finished signal
    show_error_message = pyqtSignal(str, str)
    progress_report = pyqtSignal(str)

class WhatsApp(QRunnable): # Inherit from QRunnable 


    def __init__(self, number, timer): # Add the timer parameter and contact parameter
        super().__init__()
        self.setAutoDelete(True) # Automatically delete the thread when it finishes
        self.timer = timer # Convert the timer to seconds
        self.number = number  
        self.aborted = False       # Store the contact number
        self.uuid = uuid.uuid4().hex          # Generate a unique identifier for the worker
        self.signals = WorkerSignals() # Create an instance of the WorkerSignals class


    @pyqtSlot(int)        
    def run(self):          # Override the run method
        tasks_list = [self._precheck_events, self._postcheck_events] # Create a list of tasks
        try:    
            for task in tasks_list:
                if self.aborted:
                    break
                else:
                    task()
        except Exception as e:
            self.signals.error.emit((self.uuid, str(e)))
            raise Exception('Aborted Request')
        #self.signals.finished.emit(self.uuid) # Emit the finished signal with the uuid parameter

    def abort(self): # Add an abort method to stop the worker
        print("Aborting worker") 
        self.aborted = True
        self.signals.progress_report.emit("Call Aborted")

    def _precheck_events(self):
        self.start_applications() # Start the applications
        self.get_phonenumber()  # Get the phone number  
        sleep(2)
        self.click_call_button()   # Click the call button
        self.start_recording() # Start the recording
        self.lock_screen() # Lock the screen

    def _postcheck_events(self):
        self.timer_count()  # Start the timer_count function
        sleep(1)
        self.click_end_button() # Click the end button
        sleep(1)
        self.unlock_screen() # Unlock the screen
        sleep(1)
        self.stop_recording() # Stop the recording
        sleep(1)
        self.lock_screen()  # Lock the screen
        self.signals.finished.emit(self.uuid) # Emit the finished signal with the uuid parameter

    def start_applications(self): # Start the applications whatsapp using pywinauto
        try:
            sleep(3)
            self.startapp = Application(backend='uia').start(r"cmd.exe /c start shell:appsFolder\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App", create_new_console=True, wait_for_idle=False)
            sleep(2)
            self.appwhatsapp = Application(backend='uia').connect(title_re="WhatsApp", timeout=3)
        except :
            self.signals.show_error_message.emit('Error', 'Please Restart The WhatsApp and Try Running The Application Again.')
            raise Exception('Error starting WhatsApp')
        self.signals.progress_report.emit('WhatsApp started successfully.')
        
    def get_phonenumber(self):  # Get the phone number from the user and open the whatsapp chat window
        sleep(0.25)
        self.url = f"whatsapp://send?phone=+91{self.number}"
        self.subwhatsapp = subprocess.Popen(["cmd", "/C", f"start {self.url}"], shell=True)
        sleep(0.25)
        self.url = f"whatsapp://send?phone=+91{self.number}"
        self.subwhatsapp = subprocess.Popen(["cmd", "/C", f"start {self.url}"], shell=True)
        self.signals.progress_report.emit(f"Opening WhatsApp chat window for {self.number}...")

    def click_call_button(self): # Click the call button in the WhatsApp chat window
        while True and not self.aborted: # Loop until the call button is clicked
            try:
                self.appwhatsapp.WhatsAppDialog.child_window(title="Video call", auto_id="VideoCallButton", control_type="Button").click()
                break
            except:
                sleep(1)
                continue
        self.signals.progress_report.emit("Call button clicked successfully.")

    def start_recording(self): # Start the recording of the video call once the call is connected
        if self.aborted:
            return
        self.dialog = self.appwhatsapp.window(title="Video call ‎- WhatsApp")
        sleep(2)
        try:
            self.dialog.maximize()
        except:
            pass
        self.button = self.dialog.child_window(title="Start screen sharing", auto_id="ScreenShareButton", control_type="Button")
        self.panel = self.dialog.child_window(title="Device settings", auto_id="MoreButton", control_type="Button").wait('visible', timeout=30, retry_interval=0.5)
        self.panel.set_focus()
        while True and not self.aborted: # Loop until the button is enabled
            send_keys("{TAB}") # Press the TAB key to focus the button
            try:
                if  self.button.is_enabled():
                    send_keys("{VK_F12}")   # Press the F12 key to start recording
                    break
            except:
                sleep(3)
                continue
        self.signals.progress_report.emit("Recording started successfully.")

    def lock_screen(self): # Lock the screen to prevent any interruptions
        if self.aborted:
            return
        sleep(1)
        send_keys("^+a")
        self.signals.progress_report.emit("Screen locked successfully.")


    def click_end_button(self):  # Click the end call button to end the call
        if self.aborted:
            return
        for _ in range(3):  # Try to click the button 3 times
            try:
                sleep(2)
                button = self.appwhatsapp.Dialog.child_window(title="End call", auto_id="EndCallButton", control_type="Button")
                if button.exists():  # Check if the button exists before attempting to click it
                    button.set_focus()
                    sleep(0.5)
                    button.click()
                    #send_keys("{VK_F12}")
                    return True  # Return True if the button was clicked successfully
            except Exception as e:
                    print("ERROR:", e)
                    return False  # Return False if the button could not be clicked after 3 attempts
        self.signals.progress_report.emit("Call ended successfully.")

    def stop_recording(self): # terminate whatsapp if the end button is not clicked
        sleep(1)
        if self.aborted:
            return
        if not self.click_end_button():  # Check if the call was successfully ended
            print("Call could not be ended, attempting emergency shutdown...")
            try:
                subprocess.call("TASKKILL /F /IM WhatsApp.exe", shell=True) # Terminate the WhatsApp process
                print("WhatsApp process terminated successfully.")
                sleep(1)
                send_keys("{VK_F12}")  # Press the F12 key to stop recording
            except Exception as e:
                print("Error:", e)
                return False  # Return False if the WhatsApp process could not be terminated
        else:
            print("Call ended successfully.")
            sleep(1)
            send_keys("{VK_F12}")  # Press the F12 key to stop recording
            return True  # Return True if the recording was stopped successfully
        self.signals.progress_report.emit("Recording stopped successfully.")

    def unlock_screen(self): # Unlock the screen after the call has ended
        if self.aborted:
            return
        sleep(1)
        send_keys("^+a")
        self.signals.progress_report.emit("Screen unlocked successfully.")

    def timer_count(self): # Timer function to count down the call duration
        count_down = 0
        self.signals.progress_report.emit("Timer started successfully.")
        while count_down < self.timer and not self.aborted: 
            if keyboard.is_pressed("space"):
                print("you breaked the process")
                break
            else:
                sleep(1)
                count_down += 1
                progress_percentage = int((count_down / self.timer) * 100) # Calculate the progress percentage 
                self.signals.progress.emit(progress_percentage) # Emit the progress signal with uuid parameter
                minutes_count_down, seconds_count_down = divmod(count_down, 60)
                minutes_timer, seconds_timer = divmod(self.timer, 60)
                self.signals.progress_report.emit(f"Timer: {minutes_count_down}:{seconds_count_down}/{minutes_timer}:{seconds_timer}")
        self.signals.progress_report.emit("Timer completed successfully.")
            
    def pause_recording(self): # Start the recording of the video call once the call is connected
        if self.aborted:
            return
        self.dialog = self.appwhatsapp.window(title="Video call ‎- WhatsApp")
        sleep(2)
        try:
            self.dialog.maximize()
        except:
            pass
        self.button = self.dialog.child_window(title="Add members", auto_id="ParticipantSideBarTriggerButton", control_type="Button")
        self.panel = self.dialog.child_window(title="Device settings", auto_id="MoreButton", control_type="Button").wait('visible', timeout=30, retry_interval=0.5)
        self.panel.set_focus()
        while True and not self.aborted: # Loop until the button is enabled
            send_keys("{TAB}") # Press the TAB key to focus the button
            try:
                if  self.button.is_enabled():
                    send_keys("{VK_F11}")   # Press the F12 key to start recording
                    break
            except:
                sleep(3)
                continue
        self.signals.progress_report.emit("Recording started successfully.")

class PhonePortal(QMainWindow): # Inherit from QMainWindow

    def __init__(self, *args, **kwargs): # Add *args and **kwargs
        super().__init__(*args, **kwargs) # Pass *args and **kwargs to the super class 

        self.setWindowTitle("Phone Portal Connect V5") # Set the window title
        self.setGeometry(100, 100, 800, 400)
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        

        self.user_id_input = QLineEdit(self)
        self.user_id_input.setPlaceholderText("Enter User ID")
        self.search_button = QPushButton("Search", self)
        self.search_button.setShortcut(QKeySequence('Enter')) # Set the shortcut key for the search button to Enter
        self.result_label = QLabel(self)
        self.result_label.setFont(QFont('', 15))
        self.progress_label = QLabel('')
        self.progress_label.setFont(QFont('Pirulen Rg', 10))
        #self.progress_label.setStyleSheet("color : magenta ")
        self.result_text_browser = QListWidget(self)  # Three Contacts load from user_data.json
        self.result_text_browser.itemDoubleClicked.connect(self.add_contact_from_result)
        self.contact_text_browser = QListWidget(self)    # Selected contacts will be displayed here
        self.contact_text_browser.itemDoubleClicked.connect(self.remove_contact_from_result)
        self.add_button = QPushButton("Add Contact", self)
        self.btn_add_user = QPushButton('Add User', self) # Add User button
        self.remove_button = QPushButton("Remove Contact", self) # Remove selected contact from the contact_text_browser
        self.connect_button = QPushButton("Connect", self) # Connect button
        self.connect_button.setShortcut(QKeySequence('Ctrl+Enter')) # Set the shortcut key for the connect button to Ctrl+Return
        self.swap_button = QPushButton("Swap", self) # Swap button to swap the selected contacts
        self.abort_button = QPushButton("Abort", self)
        self.abort_button.setShortcut(QKeySequence('End')) # Abort button to abort the current operation
        self.abort_button.setEnabled(False)
        self.reset_button = QPushButton("Reset", self)  # Reset button to reset the UI elements
        self.timer1_input = QLineEdit(self) # Timer input fields
        self.timer1_input.setValidator(QDoubleValidator(0, 99.99, 2))
        self.timer2_input = QLineEdit(self) # Timer input fields
        self.timer2_input.setValidator(QDoubleValidator(0, 99.99, 2)) # Set validator to accept float values
        self.timer3_input = QLineEdit(self) # Timer input fields
        self.timer3_input.setValidator(QDoubleValidator(0, 99.99, 2)) # Set validator to accept float values
        self.progress_bar = QProgressBar(self) # Create new progress bar
        self.progress_bar.setAutoFillBackground(True)
        self.progress_bar.setValue(0) # Set the initial value of the progress bar to 0 
        self.progress_bar.setValue(0) # Set the initial value of the progress bar to 0
        self.connect_button.setEnabled(False)
        # Set the icons for the buttons
        self.search_button.setIcon(QIcon(r"icons\\search_icon.png")) # Set the icon for the search button
        self.search_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.connect_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.add_button.setIcon(QIcon(r"icons\\add_icon.png")) # Set the icon for the add button
        self.add_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.btn_add_user.setIcon(QIcon(r"icons\\adduser_icon.png")) # Set the icon for the add user button
        self.btn_add_user.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.remove_button.setIcon(QIcon(r"icons\\remove_icon.png")) # Set the icon for the remove button
        self.remove_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.connect_button.setIcon(QIcon(r"icons\\connect_icon.png")) # Set the icon for the connect button
        self.swap_button.setIcon(QIcon(r"icons\\swap_icon.png"))  # Set the icon for the swap button
        self.swap_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.abort_button.setIcon(QIcon(r"icons\\abort_icon.png"))    # Set the icon for the abort button
        self.abort_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height
        self.reset_button.setIcon(QIcon(r"icons\\reset_icon.png")) # Set the icon for the reset button
        self.reset_button.setIconSize(QSize(32, 32))  # Change 32, 32 to the desired width and height

        # Set the placeholder text for the timer input fields
        self.timer1_input.setPlaceholderText("Timer 1")
        self.timer2_input.setPlaceholderText("Timer 2")
        self.timer3_input.setPlaceholderText("Timer 3")

        # Set the maximum length for the timer input fields
        self.timer1_input.setMaxLength(3)
        self.timer2_input.setMaxLength(3)
        self.timer3_input.setMaxLength(3)

        # Disable the timer input fields by default
        self.timer1_input.setEnabled(False)
        self.timer2_input.setEnabled(False)
        self.timer3_input.setEnabled(False)
        
        # Set the style for the widgets
        self.user_id_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;font-size: 16px; margin: 4px 2px; ")
        self.search_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ;")
        self.add_button.setStyleSheet("background-color: #C39BD3; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ")
        self.btn_add_user.setStyleSheet("background-color: #ff6666; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; font-size: 16px; margin: 4px 2px; ")  # Set the font color of the add user button to red
        self.remove_button.setStyleSheet("background-color: #9999ff; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ")
        self.connect_button.setStyleSheet("""
    QPushButton {
        background-color: #05B8CC;  /* Green background */
        border: none;  /* No border */
        color: white;  /* White text */
        padding: 15px 32px;  /* Padding */
        text-align: center;  /* Centered text */
        text-decoration: none;  /* No underline */
        font-size: 18px;
        margin: 4px 2px;
          /* Mouse pointer changes when over button */
        border-radius: 4px;  /* Rounded corners */
    }

    QPushButton:hover {
        background-color: #45a049;  /* Green background on hover */
    }

    QPushButton:pressed {
        background-color: #2e7d32;  /* Darker green background when pressed */
    }
""")
        self.swap_button.setStyleSheet("background-color: #884EA0; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none; font-size: 16px; margin: 4px 2px; ") # Set the font color of the swap button to blue
        self.abort_button.setStyleSheet("background-color: #cc0000; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ") # Set the font color of the abort button to red
        self.reset_button.setStyleSheet("background-color: #148F77; color: white; border: none; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ") # Set the font color of the reset button to green
        self.timer1_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ")
        self.timer2_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px; ")
        self.timer3_input.setStyleSheet("background-color: #f2f2f2; color: black; border: 1px solid black; border-radius: 5px; padding: 10px 24px; text-align: center; text-decoration: none;  font-size: 16px; margin: 4px 2px;")
        self.result_text_browser.setStyleSheet("""
        QListWidget {
        background-color: #ffe6f0
; 
        color: #000000; 
        border: 1px solid #ff0066; 
        border-radius: 5px; 
        padding: 10px; 
        font-size: 16px; 
        }
        QListWidget::item:selected {
            background-color: #808080;
        }
        """)
        self.contact_text_browser.setStyleSheet("""
        QListWidget {
            background-color: #BB8FCE; 
            color: #000000; 
            border: 1px solid #000000; 
            border-radius: 5px; 
            padding: 10px; 
            font-size: 16px; 
        }
        QListWidget::item:selected {
            background-color: #808080;
        }
        """)

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 40px; 
                width: 200px;
            }
        
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
        """)



        # Create a layout for the widgets
        layout = QHBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.user_id_input, 0, 0, 1, 1)
        grid_layout.addWidget(self.swap_button, 6, 1)
        grid_layout.addWidget(self.btn_add_user,0,2)
        grid_layout.addWidget(self.search_button, 0, 1)
        grid_layout.addWidget(self.result_label, 1, 0, 1, 3)
        grid_layout.addWidget(self.result_text_browser, 2, 0, 1, 3)
        grid_layout.addWidget(self.contact_text_browser, 3, 0, 1, 3)
        grid_layout.addWidget(self.add_button, 5, 0)
        grid_layout.addWidget(self.remove_button, 5, 1)
        grid_layout.addWidget(self.reset_button, 5, 2)
        grid_layout.addWidget(self.connect_button, 6, 0)
        grid_layout.addWidget(self.abort_button, 6, 2)
        grid_layout.addWidget(self.timer1_input, 4, 0)
        grid_layout.addWidget(self.timer2_input, 4, 1)
        grid_layout.addWidget(self.timer3_input, 4, 2)
        grid_layout.addWidget(self.progress_label,7,0,1,3)
        grid_layout.addWidget(self.progress_bar, 8, 0,1,3)
        layout.addLayout(grid_layout)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect the buttons to the respective functions
        self.search_button.clicked.connect(self.search_user) # Connect the search button to the search_user function
        self.add_button.clicked.connect(self.add_contact) # Connect the add button to the add_contact function 
        self.remove_button.clicked.connect(self.remove_contact) # Connect the remove button to the remove_contact function
        self.connect_button.clicked.connect(self.connect_function) # Connect the connect button to the connect_function
        self.swap_button.clicked.connect(self.swap_contacts) # Connect the swap button to the swap_contacts function
        self.abort_button.clicked.connect(self.abort_function)  # Connect the abort button to the abort_function
        self.reset_button.clicked.connect(self.reset_function) # Connect the reset button to the reset_function
        self.btn_add_user.clicked.connect(self.addUser) # Connect the add user button to the addUser function


        self.threadpool = QThreadPool.globalInstance() # Create a QThreadPool instance
        self.threadpool.setMaxThreadCount(3) # Set the maximum number of threads to 3
        self.worker_progress = {} # Create a dictionary to store the progress of each worker
        self.selected_contacts = [] # List to store the selected contacts
        self.worker_queue = Queue() # Create a queue to store the workers
        self.user_data = {}

    def addUser(self): # This is the slot function for the "Add User" button
        # This is the slot function for the "Add User" button
        self.ex = AddUser()
        #apply_stylesheet(self.ex, theme='dark_blue.xml')
        self.ex.show()
    
    
    def search_user(self):
        self.timer1_input.clear()
        self.timer2_input.clear()
        self.timer3_input.clear()
        self.contact_text_browser.clear()
        self.selected_contacts.clear()
        self.progress_label.setText("Call Not in Progress")
        self.timer1_input.setEnabled(False)
        self.timer2_input.setEnabled(False)
        self.timer3_input.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.connect_button.setStyleSheet("""
    QPushButton {
        background-color: #50DA59;  /* Green background */
        border: none;  /* No border */
        color: white;  /* White text */
        padding: 15px 32px;  /* Padding */
        text-align: center;  /* Centered text */
        text-decoration: none;  /* No underline */
        font-size: 18px;
        margin: 4px 2px;
          /* Mouse pointer changes when over button */
        border-radius: 4px;  /* Rounded corners */
    }

    QPushButton:hover {
        background-color: #45a049;  /* Green background on hover */
    }

    QPushButton:pressed {
        background-color: #2e7d32;  /* Darker green background when pressed */
    }
""")
        
        # Define the primary and alternative database file paths
        with open('datas/url.json') as f:
            url = json.load(f)
    
        primary_db = url['data_path']
        alternative_db = url['data_path2']


        # Connect to the database
        if os.path.exists(primary_db):
            conn = sqlite3.connect(primary_db)
        else:
            conn = sqlite3.connect(alternative_db)

        c = conn.cursor()
    
        # Get the user ID from the input field
        user_id = self.user_id_input.text()
    
        # Select the user's details from the users table
        c.execute("SELECT name, phone1, phone2, phone3 FROM users WHERE id = ?", (user_id,))
    
        # Fetch the first row from the result
        row = c.fetchone()
    
        # Close the connection
        conn.close()
    
    
        if row is not None:
            # The user was found in the database
            name, contact1, contact2, contact3 = row
            self.result_label.setText(f"NAME: {name.upper()}")
            self.result_text_browser.clear()
            for contact in (contact1, contact2, contact3):
                if contact:
                    self.result_text_browser.addItem(contact)  # Use addItem instead of append
        else:
            # The user was not found in the database
            self.result_label.setText("User not found.")
            self.result_text_browser.clear()

    def add_contact(self):
        selected_contact = self.result_text_browser.currentItem()
        if selected_contact is not None:
            selected_contact = selected_contact.text()
        else:
            # Handle the case where there is no selected contact
            # For example, you might want to show an error message
            QMessageBox.information(self, 'Error', 'Please Add Contact.')
            return
        # Rest of your code...

        if len(self.selected_contacts) == 1:
            self.timer1_input.setEnabled(True)
        elif len(self.selected_contacts) == 2:
            self.timer2_input.setEnabled(True)
        elif len(self.selected_contacts) == 3:
            self.timer3_input.setEnabled(True)
    
    def add_contact_from_result(self, item): # This is the slot function for the double-click event on the result_text_browser
        # Get the text of the double-clicked item
        contact = item.text()
        
        # Add the contact to the contact text browser
        self.selected_contacts.append(contact)
        self.update_contact_text_browser()
        
        # Enable timer inputs as needed
        if len(self.selected_contacts) == 1:
            self.timer1_input.setEnabled(True)
        elif len(self.selected_contacts) == 2:
            self.timer2_input.setEnabled(True)
        elif len(self.selected_contacts) == 3:
            self.timer3_input.setEnabled(True)

    def remove_contact(self): # This is the slot function for the "Remove Contact" button
        selected_contact = self.contact_text_browser.selectedItems()
        if selected_contact:
            for item in selected_contact:
                row = self.contact_text_browser.row(item)
                self.contact_text_browser.takeItem(row)
                del self.selected_contacts[row]
    
            # Update the input fields
            if len(self.selected_contacts) < 1:
                self.timer1_input.setEnabled(False)
                self.timer1_input.setText('')
            if len(self.selected_contacts) < 2:
                self.timer2_input.setEnabled(False)
                self.timer2_input.setText('')
            if len(self.selected_contacts) < 3:
                self.timer3_input.setEnabled(False)
                self.timer3_input.setText('')

    def swap_contacts(self): # This is the slot function for the "Swap" button , to swap the selected contacts
        if len(self.selected_contacts) >= 2:
            self.selected_contacts[0], self.selected_contacts[1] = self.selected_contacts[1], self.selected_contacts[0]
            temp = self.timer1_input.text()
            self.timer1_input.setText(self.timer2_input.text())
            self.timer2_input.setText(temp)
            self.update_contact_text_browser()
        elif len(self.selected_contacts) >= 3:
            self.selected_contacts[0], self.selected_contacts[1], self.selected_contacts[2] = self.selected_contacts[2], self.selected_contacts[1], self.selected_contacts[0]
            self.update_contact_text_browser()

    def update_contact_text_browser(self): # This function updates the contact_text_browser with the selected contacts
        self.contact_text_browser.clear()
        for contact in self.selected_contacts:
            item = QListWidgetItem(contact)
            self.contact_text_browser.addItem(item)

    @pyqtSlot(str, str)
    def show_error_message(self, title, text):
        QMessageBox.information(self, title, text)

    
    def remove_contact_from_result(self, item): # This is the slot function for the double-click event on the result_text_browser
        # Get the text of the double-clicked item
        contact = item.text()
        
        # Remove the contact from the selected contacts
        if contact in self.selected_contacts:
            self.selected_contacts.remove(contact)
                    # Update the input fields
            if len(self.selected_contacts) < 1:
                self.timer1_input.setEnabled(False)
                self.timer1_input.setText('')
            if len(self.selected_contacts) < 2:
                self.timer2_input.setEnabled(False)
                self.timer2_input.setText('')
            if len(self.selected_contacts) < 3:
                self.timer3_input.setEnabled(False)
                self.timer3_input.setText('')
        
            # Update the contact text browser
            self.update_contact_text_browser()

    def connect_function(self): # This is the slot function for the "Connect" button
        timer1 = self.timer1_input.text()
        timer2 = self.timer2_input.text()
        timer3 = self.timer3_input.text()
        #condition to check if the timer fields are empty
        if not self.selected_contacts:
            QMessageBox.information(self, 'Error', 'Please add contact in List')
            return
        if (self.timer1_input.isEnabled() and not timer1) or \
            (self.timer2_input.isEnabled() and not timer2) or \
            (self.timer3_input.isEnabled() and not timer3):
             QMessageBox.information(self, 'Error', 'Please enter the timer values for enabled timers.')
             return
        total_time = 0
        if self.timer1_input.isEnabled() and timer1:
            total_time += float(timer1)
        if self.timer2_input.isEnabled() and timer2:
            total_time += float(timer2)
        if self.timer3_input.isEnabled() and timer3:
            total_time += float(timer3)
        
        if total_time > 12:
            QMessageBox.information(self, 'Error', 'The total time exceeds 12 minutes.')
            return
        self.abort_button.setEnabled(True)
        self.connect_button.setStyleSheet("color: green")
        self.add_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.swap_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.progress_bar.setValue(0)  # Reset progress bar
        self.progress_bar.setMaximum(100) # Set maximum value for progress bar
        self.progress_label.setText("Call In Progress")
        self.progress_label.setStyleSheet("color: green")
        self.start_workers(self.selected_contacts, [timer1, timer2, timer3]) # Start the workers


            
        

    def start_workers(self, contacts, timers): # This function starts the workers
      # Create a worker for each contact and timer
        for contact, timer in zip(contacts, timers):
            worker = WhatsApp(contact,float(timer) * 60)
            worker.setAutoDelete(True) # Automatically delete the worker when it finishes
            worker.signals.progress.connect(self.progress_bar.setValue) # Connect the progress signal to the progress bar
            worker.signals.progress_report.connect(self.progress_label.setText)
            worker.signals.finished.connect(lambda: self.worker_completed(worker.uuid, contact)) # Connect the finished signal to the worker_completed function
            worker.signals.show_error_message.connect(self.show_error_message)
            self.worker_queue.put(worker) # Put the worker in the queue

            
        self.start_next_worker() # Start the next worker in the queue



    def timestamped_data(self, contact):
            user_id = self.user_id_input.text()
            add_timer1 = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
            # Check if user_id exists in user_data
            if user_id not in self.user_data:
                # If user_id does not exist, create a new dictionary for it
                self.user_data[user_id] = {}
        
            self.user_data[user_id]['number'] = contact  # Use 'number' instead of ['number']
            print(f"{self.user_data[user_id]['number']} (Called at {add_timer1})")
        
            # Rest of your code...
            # Get the path to the last recording

            try:
                with open(r'datas\url.json', 'r') as f:
                    path_data = json.load(f)
                    recordings_folder =  r"{}".format(path_data.get('path', 'recordings'))  # Use get method to avoid KeyError
                    print(f"Recordings folder: {recordings_folder}")
            except FileNotFoundError:
                QMessageBox.information(self, 'Error', 'Please set the path to the recordings folder in the settings.')


            recording_files = os.listdir(recordings_folder)
            last_recording = sorted(recording_files)[-1]  # Assumes files are named in a way that allows sorting
            
            timestamped_data = {
                "user_id": user_id,
                "name" : self.user_data[user_id].get('name', 'Unknown'),  # Use get method to avoid KeyError
                "number": self.user_data[user_id]['number'],
                "timestamp": add_timer1,
                "recording": os.path.join(recordings_folder, last_recording)
            }
            
            with open(r'datas\timestamped_data.json', 'a') as f:
                json.dump(timestamped_data, f)
                f.write('\n')  # Add a newline for readability

    def start_next_worker(self): # This function starts the next worker in the queue
        
        if not self.worker_queue.empty(): # Check if the queue is not empty
            self.worker = self.worker_queue.get() # Get the next worker from the queue
            print(f"Starting worker with UUID {self.worker.uuid}") # Print the UUID of the worker
            self.threadpool.start(self.worker) # Start the worker
            

    def worker_completed(self, uuid,contact): # This function is called when a worker has completed
        if len(self.selected_contacts) > 1: # If there are more contacts to process
            self.worker.lock_screen() # Lock the screen to prevent any interruptions
        if len(self.selected_contacts) > 1: # If there are no more contacts to process
            self.abort_button.setEnabled(True) # Enable the abort button
        else:
            self.abort_button.setEnabled(False)
        self.timestamped_data(contact)   
        print(f"Worker with UUID {uuid} has completed") # Print the UUID of the completed worker
        self.worker_progress[uuid] = 100 # Set the progress of the worker to 100
        self.refresh_progress(len(self.worker_progress)) # Refresh the progress bar
        self.start_next_worker() # Start the next worker in the queue
        self.connect_button.setEnabled(True) # Enable the connect button
        self.add_button.setEnabled(True) # Enable the add button
        self.remove_button.setEnabled(True)
        self.swap_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.connect_button.setStyleSheet("color: blue")
        self.progress_label.setText("Call Completed ")
        self.progress_label.setStyleSheet("color : purple")

    def refresh_progress(self, num_workers):
    # This function calculates the overall progress
        if num_workers == 0:
            return
        total_progress = sum(self.worker_progress.values()) / num_workers
        self.progress_bar.setValue(int(total_progress))

    def abort_function(self): # This is the slot function for the "Abort" button
        if self.worker:
            self.worker.abort()
        self.worker_queue. queue.clear()
        self.connect_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.worker_progress.clear()
        self.add_button.setEnabled(True) # Enable the add button
        self.remove_button.setEnabled(True)
        self.swap_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.connect_button.setStyleSheet("""
    QPushButton {
        background-color: #05B8CC;  /* Green background */
        border: none;  /* No border */
        color: white;  /* White text */
        padding: 15px 32px;  /* Padding */
        text-align: center;  /* Centered text */
        text-decoration: none;  /* No underline */
        font-size: 18px;
        margin: 4px 2px;
          /* Mouse pointer changes when over button */
        border-radius: 4px;  /* Rounded corners */
    }

    QPushButton:hover {
        background-color: #45a049;  /* Green background on hover */
    }

    QPushButton:pressed {
        background-color: #2e7d32;  /* Darker green background when pressed */
    }
""")
        self.abort_button.setEnabled(False)
        self.progress_label.setText("Call Not in Progress ")
        self.progress_label.setStyleSheet("color : magenta ")

    def reset_function(self): # This is the slot function for the "Reset" button
        self.user_id_input.clear()
        self.result_label.clear()
        self.result_text_browser.clear()
        self.contact_text_browser.clear()
        self.selected_contacts.clear()
        self.timer1_input.clear()
        self.timer2_input.clear()
        self.timer3_input.clear()
        self.timer1_input.setEnabled(False)
        self.timer2_input.setEnabled(False)
        self.timer3_input.setEnabled(False)
        self.progress_bar.setValue(0)
        self.connect_button.setEnabled(True)
        self.connect_button.setStyleSheet("""
    QPushButton {
        background-color: #05B8CC;  /* Green background */
        border: none;  /* No border */
        color: white;  /* White text */
        padding: 15px 32px;  /* Padding */
        text-align: center;  /* Centered text */
        text-decoration: none;  /* No underline */
        font-size: 18px;
        margin: 4px 2px;
          /* Mouse pointer changes when over button */
        border-radius: 4px;  /* Rounded corners */
    }

    QPushButton:hover {
        background-color: #45a049;  /* Green background on hover */
    }

    QPushButton:pressed {
        background-color: #2e7d32;  /* Darker green background when pressed */
    }
""")
        self.progress_label.setText("Call Not in Progress")
        self.progress_label.setStyleSheet("color : magenta ")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stylesheet = """

    """
    app.setStyle(QStyleFactory.create('Fusion'))
    window = PhonePortal()
    window.show()
    sys.exit(app.exec())