import sys
import json
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QIcon
from datetime import datetime, timedelta
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from reportlab.lib.pagesizes import letter 
from reportlab.pdfgen import canvas 
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter,landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from PyQt6 import QtWidgets
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QPageSize, QPageLayout
from PyQt6.QtWidgets import QDialog

# Headers for the table
headers = ['Date', 'AB-Block-1', 'AB-Block-2', 'Cellular-Block', 'HS-Block', 'A-Class', 'Quarantine', 'Hospital', 'Emulakath', 'Video', 'Audio', 'Total']

class TableWidget(QTableWidget):
    def __init__(self, headers):
        super().__init__()
        self.headers = headers
        self.init_ui()

    def init_ui(self):
        self.setColumnCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.setColumnWidth(3, 150)
        self.setColumnWidth(6, 150)
        self.setColumnWidth(7, 150)
        self.setColumnWidth(8, 150)
        

    def loadData(self, from_date, to_date):
        try:
            with open(r'datas\data.json', 'r') as f:
                all_data = json.load(f)
            
            # Filter data within the date range
            filtered_data = {date: all_data[date] for date in all_data if from_date <= date <= to_date}
            
            # Sort the filtered data by date in ascending order
            sorted_data = dict(sorted(filtered_data.items()))
            
            self.setRowCount(len(sorted_data) + 1)  # +1 for the grand total row
            grand_totals = [0] * (len(self.headers) - 1)  # Initialize grand totals list

            for i, (date, values) in enumerate(sorted_data.items()):
                self.setItem(i, 0, QTableWidgetItem(date))
                row_total = 0  # Initialize row total
                for j, key in enumerate(self.headers[1:], 1):  # Skip the 'Date' column
                    if key in ['Video', 'Audio']:
                        value = values['category'][key.lower()]
                    else:
                        value = values.get(key, 0)
                    self.setItem(i, j, QTableWidgetItem(str(value)))
                    row_total += value
                    grand_totals[j - 1] += value  # Update grand total for the column
                self.setItem(i, len(self.headers) - 1, QTableWidgetItem(str(row_total)))  # Set row total

            # Set grand totals in the last row
            self.setItem(len(sorted_data), 0, QTableWidgetItem('Grand Total'))
            for j, total in enumerate(grand_totals, 1):
                self.setItem(len(sorted_data), j, QTableWidgetItem(str(total)))

            return True
        except FileNotFoundError:
            print("Data file not found.")
            return False
        except json.JSONDecodeError:
            print("Data file is not in valid JSON format.")
            return False

class DataView(QWidget):
    def __init__(self, headers):
        super().__init__()
        self.setWindowTitle("Phone Portal Data View")
        self.setWindowIcon(QIcon("logo.png"))
        self.setGeometry(100, 100, 1400, 600)
        self.table = TableWidget(headers)
        self.layout = QVBoxLayout()
        
        # Date range selection layout
        date_range_layout = QtWidgets.QHBoxLayout()
        self.from_label = QtWidgets.QLabel('From:', self)
        self.to_label = QtWidgets.QLabel('To:', self)
        self.from_date = QtWidgets.QDateEdit(self)
        self.to_date = QtWidgets.QDateEdit(self)
        self.from_date.setCalendarPopup(True)
        self.to_date.setCalendarPopup(True)
        # Set "from" date to 30 days before current date
        thirty_days_ago = datetime.now() - timedelta(days=30)
        self.from_date.setDate(QtCore.QDate(thirty_days_ago.year, thirty_days_ago.month, thirty_days_ago.day))
        # Set "to" date to current date
        self.to_date.setDate(QtCore.QDate.currentDate())
        date_range_layout.addWidget(self.from_label)
        date_range_layout.addWidget(self.from_date)
        date_range_layout.addWidget(self.to_label)
        date_range_layout.addWidget(self.to_date)

        # Retrieve button
        self.retrieve_button = QPushButton('Retrieve Data')
        self.retrieve_button.clicked.connect(self.retrieve_data)

        # Add layouts to the main layout
        self.layout.addLayout(date_range_layout)
        self.layout.addWidget(self.retrieve_button)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

    def retrieve_data(self):
        from_date = self.from_date.date().toString('yyyy-MM-dd')
        to_date = self.to_date.date().toString('yyyy-MM-dd')
        if self.table.loadData(from_date, to_date):
            print(f'Data retrieved for dates between {from_date} and {to_date}')
    
    def setup_export_buttons(self):
        # Export to PDF button
        self.export_pdf_button = QPushButton('Export to PDF')
        self.export_pdf_button.clicked.connect(self.export_to_pdf)

        # Save as Excel button
        self.save_excel_button = QPushButton('Save as Excel')
        self.save_excel_button.clicked.connect(self.save_as_excel)

        # Print button
        self.print_button = QPushButton('Print')
        self.print_button.clicked.connect(self.print_table)

        # Add buttons to layout
        self.layout.addWidget(self.export_pdf_button)
        self.layout.addWidget(self.save_excel_button)
        self.layout.addWidget(self.print_button)

    def export_to_pdf(self):
        # Prompt user for location and name of the PDF file
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save as PDF",
            "",
            "PDF Files (*.pdf)"
        )
        filename = 'Block_Phone_List_Details.pdf'  # Name of the PDF file
        pdf = SimpleDocTemplate(filename, pagesize=landscape(letter))
        elements = []
        # Define the style for the heading
        styles = getSampleStyleSheet()
        heading_style = styles['Heading1']
        heading_style.alignment = 1  # Center align

        # Create the heading
        heading_text = "Block List Phone Data Details"
        heading = Paragraph(heading_text, heading_style)

        # Add the heading to the elements list
        elements.append(heading)
        elements.append(Spacer(1, 12))  # Add some space after the heading

        # Define the headers for the table
        headers = ['Date', 'AB-Block-1', 'AB-Block-2', 'Cellular-Block', 'HS-Block', 'A-Class', 'Quarantine', 'Hospital', 'Emulakath', 'Video', 'Audio', 'Total']

        # Include headers as the first row of the data
        data = [headers]  # Start with the headers
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item is not None else '')
            data.append(row_data)  # Add the row data to the data array

        # Create a table for the data
        table = Table(data)

        # Add style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Add the table to the elements list
        elements.append(table)

        # Build the PDF
        pdf.build(elements)

        print(f"Table data has been exported to '{filename}'")


    def save_as_excel(self):
        # Prompt user for location and name of the Excel file
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save as Excel",
            "",
            "Excel Files (*.xlsx)"
        )
        filename = 'Block_Phone_List_Details.xlsx'  # Name of the Excel file
        # Rest of your code...
        
        if filename:
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            # Create a workbook and add a worksheet
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()

            # Start from the first cell
            row = 0
            col = 0

            # Iterate over the headers and write them to the first row
            for header in headers:
                worksheet.write(row, col, header)
                col += 1

            # Reset the column index and increment the row index
            col = 0
            row += 1

            # Iterate over the data and write it to the worksheet
            for table_row in range(self.table.rowCount()):
                for table_col in range(self.table.columnCount()):
                    item = self.table.item(table_row, table_col)
                    worksheet.write(row, col, item.text() if item is not None else '')
                    col += 1
                # Reset the column index and increment the row index
                col = 0
                row += 1

            # Close the workbook
            workbook.close()

            print(f"Table data has been exported to '{filename}'")
        else:
            print("Save as Excel cancelled.")


    
    def print_table(self):
        # Create a QPrinter object
        printer = QPrinter()
        printer.setResolution(1200)
    
        # Set the printer to landscape mode
        layout = printer.pageLayout()
        layout.setOrientation(QPageLayout.Orientation.Landscape)
        printer.setPageLayout(layout)
    
        # Set the paper size to Letter
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))
    
        # Create a QPrintDialog
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # The user accepted the dialog; start printing process
            # You will need to implement the actual painting/printing of the table here
            pass

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    demo = DataView(headers)
    demo.setup_export_buttons()
    demo.show()
    sys.exit(app.exec())