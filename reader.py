import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel,QVBoxLayout,QWidget
from PyQt6.QtCore import Qt,QThread,pyqtSignal
from PyQt6.QtGui import QFont
import cv2
from pyzbar.pyzbar import ZBarSymbol,decode
from pynput.mouse import Listener as MouseListener, Button
import threading
import time
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QObject
from PIL import Image
from ctypes import Structure, c_ulong, byref, windll,c_long,POINTER,WINFUNCTYPE,c_int,WinError,cast
from ctypes.wintypes import DWORD, ULONG, LPARAM, WPARAM, POINT,MSG



class MSLLHOOKSTRUCT(Structure):
    _fields_ = [("pt", c_long * 2),
                ("mouseData", c_ulong),
                ("flags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", POINTER(c_ulong))]

class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [("vkCode", DWORD),
                ("scanCode", DWORD),
                ("flags", DWORD),
                ("time", DWORD),
                ("dwExtraInfo", ULONG)]
    
WH_MOUSE_LL = 14
WH_KEYBOARD_LL = 13
LLKHF_INJECTED = 0x00000010
    
class QRCodeScanner(QThread):
    qr_code_detected = pyqtSignal()  # Define a custom signal
    qr_code_undetected = pyqtSignal()  # Define a custom signal for unlock
    change_parent_signal_detected = pyqtSignal(QObject) 
    change_parent_signal_undetected = pyqtSignal(QObject)
    
    def __init__(self):
        QThread.__init__(self)  # Initialize QThread
        self.target_data = 'central booth lock' # The target data to be scanned
        self.stop_event = threading.Event() # Event to stop the thread
        self.cap = cv2.VideoCapture(1) # Open the camera
        self.is_locked = False  # Flag to check if the input is locked
        self.allowed_keys = [0x7B, 0x09]

    def run(self):  # This method will be run when you call self.start()
        self.scan_qr_code() # Start the QR code scanning function

    def manual_lock(self):
        self.lock()
        self.is_locked = True
        self.qr_code_detected.emit()
        self.change_parent_signal_detected.emit(self)

    def manual_unlock(self):
        self.unlock()
        self.is_locked = False
        self.change_parent_signal_undetected.emit(self)

        
    def set_hook(self): # Function to set the mouse and keyboard hooks
        # Define the hook procedures for mouse and keyboard
        MouseHookProc = WINFUNCTYPE(c_int, c_int, c_int, POINTER(MSLLHOOKSTRUCT))
        KeyboardHookProc = WINFUNCTYPE(c_int, c_int, c_int, POINTER(KBDLLHOOKSTRUCT))
        mouse_hook_proc = MouseHookProc(self.low_level_mouse_proc)
        keyboard_hook_proc = KeyboardHookProc(self.low_level_keyboard_proc)
    
        # Set the mouse hook
        hMouseHook = windll.user32.SetWindowsHookExA(WH_MOUSE_LL, mouse_hook_proc, None, 0)
        if not hMouseHook:
            raise WinError()
    
        # Set the keyboard hook
        hKeyboardHook = windll.user32.SetWindowsHookExA(WH_KEYBOARD_LL, keyboard_hook_proc, None, 0)
        if not hKeyboardHook:
            raise WinError()
    
        while not self.stop_event.is_set():
            msg = MSG()
            windll.user32.GetMessageA(byref(msg), None, 0, 0)
    
        # Unhook both mouse and keyboard hooks
        windll.user32.UnhookWindowsHookEx(hMouseHook)
        windll.user32.UnhookWindowsHookEx(hKeyboardHook)
    
    def low_level_mouse_proc(self, nCode, wParam, lParam):
        if nCode >= 0 and lParam.contents.flags & LLKHF_INJECTED == 0:
            return 1  # Block mouse input
        return windll.user32.CallNextHookEx(None, nCode, wParam, lParam)
    
    def low_level_keyboard_proc(self, nCode, wParam, lParam):
        lParam_struct = cast(lParam, POINTER(KBDLLHOOKSTRUCT)).contents
        if nCode < 0 or lParam_struct.vkCode in self.allowed_keys:
            return windll.user32.CallNextHookEx(None, nCode, wParam, lParam_struct.dwExtraInfo)
        return 1  # Block keyboard input
    
    def lock(self):
        self.stop_event.clear()  # Start the lock_input function
        self.hook_thread = threading.Thread(target=self.set_hook)
        self.hook_thread.start()
        print(f"Thread started: {self.hook_thread.name}")
        self.change_parent_signal_detected.emit(self)

    def unlock(self):
        self.stop_event.set()  # Stop the lock_input function
        windll.user32.PostThreadMessageA(self.hook_thread.ident, 0, 0, 0)  # Post a dummy message to the thread
        print(f"Thread stopped: {self.hook_thread.name}")
        self.change_parent_signal_undetected.emit(self)

    def scan_qr_code(self):
        last_detection_time = 0
        detection_delay = 2  # Delay between consecutive detections in seconds
        while True:
            ret, frame = self.cap.read()
            for barcode in decode(frame, symbols=[ZBarSymbol.QRCODE]):  # Only decode QR codes
                barcode_data = barcode.data.decode('utf-8')
                current_time = time.time()
                if barcode_data == self.target_data and current_time - last_detection_time > detection_delay:
                    print('Matched QR code:', barcode_data)
                    last_detection_time = current_time
                    if self.is_locked:  # Only unlock if the system is locked
                        self.unlock()
                        self.is_locked = False
                        self.qr_code_undetected.emit()  # Emit the custom signal for unlock
                    else:
                        self.lock()
                        self.is_locked = True
                        self.qr_code_detected.emit()  # Emit the custom signal for lock
            #resized_frame = cv2.resize(frame, (150, 100))
            #cv2.imshow('QR code scanner', resized_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()

    def scan_qr_code_from_file(self, file_path):
        # Open the image file
        img = Image.open(file_path)
        # Convert the image to grayscale
        img = img.convert('L')
        # Decode the QR code from the image
        barcodes = decode(img, symbols=[ZBarSymbol.QRCODE])
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            if barcode_data == self.target_data:
                print('Matched QR code:', barcode_data)
                if self.is_locked:  # Only unlock if the system is locked
                    self.unlock()
                    self.is_locked = False
                    self.qr_code_undetected.emit()  # Emit the custom signal for unlock
                else:
                    self.lock()
                    self.is_locked = True
                    self.qr_code_detected.emit()  # Emit the custom signal for lock

class QScannerLocker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LOCKER")
        self.setGeometry(100, 100, 150, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #E8DAEF;")  # Dark background
        
        screen_rect = QApplication.primaryScreen().availableGeometry()
        self.move(screen_rect.left(), screen_rect.top())
        
        layout = QVBoxLayout()
        self.label_heading = QLabel("LOCK STATUS", self)
        font = QFont('Arial', 15)

        self.label_heading.setFont(font)
        self.status_label = QLabel("Lock Off", self)
        font = QFont('Arial', 20)
        self.status_label.setFont(font)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #50DA59;  /* Green background */
                border: none;  /* No border */
                color: white;  /* White text */
                padding: 15px 32px;  /* Padding */
                text-align: center;  /* Centered text */
                font-size: 18px;
                border-radius: 4px;  /* Rounded corners */
            }

            QLabel:hover {
                background-color: #45a049;  /* Green background on hover */
            }
        """)
        self.label_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_heading)

        # Add lock icon
        lock_icon = QLabel(self)
        pixmap = QPixmap(r"icons\\lock.png")  # Replace "lock_icon.png" with the path to your lock icon image
        resized_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        lock_icon.setPixmap(resized_pixmap)
        lock_icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(lock_icon)

        layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        
        self.scanner = QRCodeScanner()
        self.scanner.start()  # Start the QThread
        
        self.scanner.qr_code_detected.connect(self.scanner_finished)  # Connect the custom signal
        self.scanner.qr_code_undetected.connect(self.scanner_unfinished)  # Connect the custom signal for unlock
        self.scanner.change_parent_signal_detected.connect(self.scanner_finished)
        self.scanner.change_parent_signal_undetected.connect(self.scanner_unfinished)


    def scanner_finished(self):
        self.status_label.setText("Lock On")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #FF3535;  /* Green background */
                border: none;  /* No border */
                color: white;  /* White text */
                padding: 15px 32px;  /* Padding */
                text-align: center;  /* Centered text */
                font-size: 18px;
                border-radius: 4px;  /* Rounded corners */
            }

            QLabel:hover {
                background-color: #45a049;  /* Green background on hover */
            }
        """)

    def scanner_unfinished(self):
        self.status_label.setText("Lock Off")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #50DA59;  /* Green background */
                border: none;  /* No border */
                color: white;  /* White text */
                padding: 15px 32px;  /* Padding */
                text-align: center;  /* Centered text */
                font-size: 18px;
                border-radius: 4px;  /* Rounded corners */
            }

            QLabel:hover {
                background-color: #45a049;  /* Green background on hover */
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set the Fusion theme
    app.setStyle("Fusion")
    window = QScannerLocker()
    window.show()
    sys.exit(app.exec())