from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QMessageBox, QTableWidgetItem, QTableWidget
)
from PyQt6.QtCore import Qt
import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
SERVER_URL = "http://192.168.0.23:5000"

class ShowIssuedRequestsWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Management - Manage Requests")
        self.setMinimumSize(900, 600)

        # ------------------- Main Layout -------------------
        self.outer_layout = QVBoxLayout()
        self.outer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.outer_layout.addWidget(self.content_widget)

        self.setLayout(self.outer_layout)

        # Fetch request data
        response = requests.get(f"{SERVER_URL}/requests/{"stock_out"}")
        data = response.json()
        display_headers = ["Transaction ID", "Item Id", "Item Name", "Quantity", "Issued By", "Issued To", "Issued At", "Status"]
        data_keys = ["tran_id", "item_id", "itemName", "quantity", "issued_by", "issued_to", "issued_at", "sts"]

        self.table = QTableWidget()
        self.table.setColumnCount(len(display_headers))
        self.table.setHorizontalHeaderLabels(display_headers)
        self.table.setStyleSheet('font-size: 14px; background-color: white')
        self.table.setRowCount(len(data))
        self.table.verticalHeader().setVisible(False)

        for row_index, row_data in enumerate(data):
            for col_index, key in enumerate(data_keys):
                value = row_data.get(key, "")
                display_value = "" if value is None else str(value)
                self.table.setItem(row_index, col_index, QTableWidgetItem(display_value))

        self.content_layout.addWidget(self.table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShowIssuedRequestsWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
