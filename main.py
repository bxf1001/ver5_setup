import sys
from time import sleep
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout,QDialog, QPushButton, QSplashScreen,QLabel
from PyQt6.QtGui import QPixmap, QIcon
from run_me_queuing import PhonePortal
from settings import Settings
from add_user import AddUser
from data_entry import DataEntryApp
from rt_data import DataView
from search_data import TimestampedDataSearch
from PyQt6.QtWidgets import QGridLayout,QTextBrowser
from PyQt6.QtCore import QSize,QThread,QCoreApplication
from PyQt6.QtCore import Qt  # Import the Qt module from the PyQt5.QtCore package
# from qt_material import apply_stylesheet  # PyQt6 does not have the qt_material package


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone Potral")  # Set your window title
        self.setWindowIcon(QIcon('icons/logo.png'))
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        # Create buttons
        # Define the size of the buttons
        button_size = QSize(100, 100)  # Adjust the size as needed
        icon_size = QSize(80, 80)

        # Create buttons and set their size
        self.btn_add_user_label = QLabel("ADD USER")
        self.btn_add_user = QPushButton('')
        self.btn_add_user.setIcon(QIcon('icons/user.png'))
        self.btn_add_user.setFixedSize(button_size)
        self.btn_add_user.setIconSize(icon_size)
        
        self.btn_connect_label = QLabel("CONNECT")
        self.btn_connect = QPushButton('')
        self.btn_connect.setIcon(QIcon('icons/connect_main.png'))
        self.btn_connect.setFixedSize(button_size)
        self.btn_connect.setIconSize(icon_size)
        
        self.btn_data_entry_label = QLabel('DATA ENTRY')
        self.btn_data_entry = QPushButton('')
        self.btn_data_entry.setIcon(QIcon('icons/data_entry.png'))
        self.btn_data_entry.setFixedSize(button_size)
        self.btn_data_entry.setIconSize(icon_size)
        
        self.btn_data_view_label = QLabel('DATA VIEW')
        self.btn_data_view = QPushButton('')
        self.btn_data_view.setIcon(QIcon('icons/data_view.png'))
        self.btn_data_view.setFixedSize(button_size)
        self.btn_data_view.setIconSize(icon_size)

        self.btn_call_logs_label = QLabel('CALL LOGS')
        self.btn_call_logs = QPushButton('')
        self.btn_call_logs.setIcon(QIcon('icons/call_logs.png'))
        self.btn_call_logs.setFixedSize(button_size)
        self.btn_call_logs.setIconSize(icon_size)

        self.btn_settings_label = QLabel('SETTINGS')
        self.settings_button = QPushButton('')
        self.settings_button.setFixedSize(button_size)
        self.settings_button.setIcon(QIcon('icons/settings_icon.png'))
        self.settings_button.setIconSize(icon_size)


        self.btn_about_label = QLabel('ABOUT')  # Add an "About" button 
        self.btn_about = QPushButton('')
        self.btn_about.setIcon(QIcon('icons/about_icon.png'))
        self.btn_about.setFixedSize(button_size)
        self.btn_about.setIconSize(icon_size)

        self.btn_exit_label = QLabel('EXIT')
        self.btn_exit = QPushButton('')
        self.btn_exit.setFixedSize(button_size)
        self.btn_exit.setIcon(QIcon('icons/exit_icon.png'))
        self.btn_exit.setIconSize(icon_size)

        # Add the buttons to the layout
        layout.addWidget(self.btn_add_user, 0, 0)
        layout.addWidget(self.btn_add_user_label,1,0)
        layout.addWidget(self.btn_connect, 0, 1)
        layout.addWidget(self.btn_connect_label,1,1)
        layout.addWidget(self.btn_data_entry, 2, 0)
        layout.addWidget(self.btn_data_entry_label, 3, 0)
        layout.addWidget(self.btn_data_view, 2, 1)
        layout.addWidget(self.btn_data_view_label, 3, 1)
        layout.addWidget(self.btn_call_logs, 4, 0)
        layout.addWidget(self.btn_call_logs_label, 5, 0)
        layout.addWidget(self.settings_button, 4, 1)
        layout.addWidget(self.btn_settings_label, 5, 1)
        layout.addWidget(self.btn_about, 6, 0)
        layout.addWidget(self.btn_about_label, 7, 0)
        layout.addWidget(self.btn_exit, 6, 1)
        layout.addWidget(self.btn_exit_label, 7, 1)
        
        # Set the layout on the application's window
        self.setLayout(layout)
        #connect buttons to functions
        self.btn_add_user.clicked.connect(self.addUser)
        self.btn_connect.clicked.connect(self.connect)
        self.btn_data_entry.clicked.connect(self.dataEntry)
        self.btn_data_view.clicked.connect(self.dataView)
        self.btn_call_logs.clicked.connect(self.callLogs)
        self.settings_button.clicked.connect(self.settings)
        self.btn_about.clicked.connect(self.about)
        self.btn_exit.clicked.connect(self.exitApp)
        

        self.setWindowTitle('Phone Portal V5')
        self.setGeometry(300, 300, 300, 400)
        self.show()

    def settings(self):
        self.settings_dialog = Settings()
        self.settings_dialog.show()
        

    def addUser(self):
        self.ex = AddUser()
        self.ex.show()

    def connect(self):
        self.ex_4 = PhonePortal()
        self.ex_4.show()

    def dataEntry(self):
        self.ex_2 = DataEntryApp()
        # apply_stylesheet(self.ex_2, theme='dark_blue.xml')  # PyQt6 does not have the qt_material package
        self.ex_2.show()

    def dataView(self):
        headers = ['Date', 'AB-Block-1', 'AB-Block-2', 'Cellular-Block', 'HS-Block', 'A-Class', 'Quarantine', 'Hospital', 'Emulakath', 'Video', 'Audio', 'Total']
        self.app_demo = DataView(headers)  # Create an instance of the AppDemo class
        # apply_stylesheet(self.app_demo, theme='dark_blue.xml')  # PyQt6 does not have the qt_material package
        self.app_demo.setup_export_buttons()
        self.app_demo.show() 

    def callLogs(self):
        self.ex_3 = TimestampedDataSearch()
        self.ex_3.results_table.cellClicked.connect(self.ex_3.cellClicked)
        # apply_stylesheet(self.ex_3, theme='dark_blue.xml')  # PyQt6 does not have the qt_material package
        self.ex_3.show()
    


    def about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(400, 300)

        layout = QVBoxLayout()

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setHtml("<h2>Phone Portal V5</h2>"
                             "<p>This software is designed to provide a user-friendly interface for managing phone data.</p>"
                             "<p>Features:</p>"
                             "<ul>"
                             "<li>Add User: Allows you to add new users to the system.</li>"
                             "<li>Connect: Connects WhatsApp Video Calls.</li>"
                             "<li>Data Entry: Allows you to enter data into the system.</li>"
                             "<li>Data View: Displays the data in a tabular format.</li>"
                             "<li>Call Logs: Searches and displays timestamped call logs.</li>"
                             "<li>Settings: Provides options to customize the software.</li>"
                             "<li>Credits: 10200 Bhanu.</li>"
        )
        
        layout.addWidget(text_browser)
        dialog.setLayout(layout)

        dialog.exec()


    def exitApp(self):
        # Empty function for "Exit" button
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    pixmap = QPixmap('icons/logo.png')
    
    # Create and show the splash screen
    splash = QSplashScreen(pixmap)
    splash.setWindowState(Qt.WindowState.WindowActive)
    splash.show()
    sleep(2)
    ex = MyApp()
    ex.show()
    # apply_stylesheet(ex, theme='dark_blue.xml')  # PyQt6 does not have the qt_material package
    splash.finish(ex)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


