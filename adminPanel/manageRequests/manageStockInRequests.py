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

class ManageStockInRequestsWindow(QDialog):
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
        response = requests.get(f"{SERVER_URL}/requests/{"stock_in"}")
        data = response.json()
        print(data)
        display_headers = ["Item Name", "Quantity", "Unit Price", "Supplier", "Status", "Action"]
        data_keys = ["itemName", "quantity", "uPrice", "supplier", "sts"]

        self.table = QTableWidget()
        self.table.setColumnCount(len(display_headers))
        self.table.setHorizontalHeaderLabels(display_headers)
        self.table.setStyleSheet('font-size: 14px; background-color: white')
        self.table.setRowCount(len(data))
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(len(data_keys), 220) 

        for row_index, row_data in enumerate(data):
            for col_index, key in enumerate(data_keys):
                value = row_data.get(key, "")
                display_value = "" if value is None else str(value)
                self.table.setItem(row_index, col_index, QTableWidgetItem(display_value))

            # Inside the loop for each row
            accept_btn = QPushButton("Accept")
            accept_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            accept_btn.setFixedSize(100, 36) 
            accept_btn.setStyleSheet(self.button_style())
            accept_btn.clicked.connect(lambda _, row=row_index: self.process_request(row, "accept"))

            reject_btn = QPushButton("Reject")
            reject_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            reject_btn.setFixedSize(100, 36)  
            reject_btn.setStyleSheet(self.button_style())
            reject_btn.clicked.connect(lambda _, row=row_index: self.process_request(row, "reject"))

            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(10)
            btn_layout.addWidget(accept_btn)
            btn_layout.addWidget(reject_btn)

            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row_index, len(data_keys), btn_widget)
            self.table.setRowHeight(row_index, 50)


        self.content_layout.addWidget(self.table)

    def button_style(self):
        return f"""
            QPushButton {{
                background-color: white;
                border: 1px solid;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #A6F1F4;
            }}
        """

    def process_request(self, row, type):
        item_name = self.table.item(row, 0).text()
        quantity = self.table.item(row, 1).text()
        unit_price = self.table.item(row, 2).text()
        supplier = self.table.item(row, 3).text()

        try:
            if type == "accept":
                response = requests.post(f"{SERVER_URL}/accept_request/{"stock_in"}", json={
                    "itemName": item_name,
                    "quantity": int(quantity),
                    "unitPrice": unit_price if unit_price != "" else None,
                    "supplier": supplier
                })
            else:
                response = requests.delete(f"{SERVER_URL}/reject_request/{"stock_in"}/{item_name}")
            if response.ok:
                if type == "accept":
                    QMessageBox.information(self, "Success", f"Stock in request for '{item_name}' accepted!")
                    self.table.removeRow(row)
                else:
                    QMessageBox.information(self, "Success", f"Stock in request for '{item_name}' rejected!")
                    self.table.removeRow(row)
            else:
                QMessageBox.warning(self, "Error", "Failed to accept the request.")
        except Exception as e:
            QMessageBox.critical(self, "Network Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManageStockInRequestsWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
