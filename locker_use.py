import sys
import cv2
from pyzbar.pyzbar import decode
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lock Button Window")

        self.lock_button = QPushButton("Lock", self)
        self.lock_button.clicked.connect(self.lock_button_clicked)

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_qr_code)

        self.cap = cv2.VideoCapture(0)  # Open the webcam

    def lock_button_clicked(self):
        if self.timer.isActive():
            self.timer.stop()
            self.cap.release()  # Release the webcam
            self.lock_button.setText("Lock")
        else:
            self.timer.start(1000)  # Start reading QR codes every second
            self.lock_button.setText("Unlock")

    def read_qr_code(self):
        target_data = "My Lock"  # Replace with your target data
    
        while True:
            ret, frame = self.cap.read()  # Read a frame from the webcam
            for barcode in decode(frame):  # Decode the frame
                barcode_data = barcode.data.decode('utf-8')
                if barcode_data == target_data:
                    print("QR code data: Matched")
                    self.timer.stop()
                    self.cap.release()  # Release the webcam
                    self.lock_button.setText("Lock")
                else:
                    print("QR code data: Not Matched")
    
            cv2.imshow('QR Code Reader', frame)  # Show the frame in a window
    
            # Check for a key press to close the window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())