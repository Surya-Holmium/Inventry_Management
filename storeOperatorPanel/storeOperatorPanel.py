from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QMainWindow, QVBoxLayout, QHBoxLayout, QMessageBox, QToolBar, QTableWidget,
    QTableWidgetItem, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import functools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SERVER_URL = "http://localhost:5000"


class StoreOperatorPanelWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management - Admin Panel")
        self.setMinimumSize(900, 700)

        self.statusbar = self.statusBar()

        self.raise_request = QAction("Raise Request", self)
        self.raise_request.triggered.connect(self.raise_request_dialog)
        self.raise_request.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.raise_request.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.view_inventory = QAction("View Inventory", self)
        self.view_inventory.triggered.connect(self.view_inventory_as_table)
        self.view_inventory.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.view_inventory.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.issue_stock = QAction("Issue Stock", self)
        self.issue_stock.triggered.connect(self.issue_stock_dialog)
        self.issue_stock.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.issue_stock.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.export_report = QAction("Export Report", self)
        self.export_report.triggered.connect(self.download_report)
        self.export_report.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.export_report.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.view_logs = QAction("Logs", self)
        self.view_logs.triggered.connect(self.view_logs_as_table)
        self.view_logs.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.view_logs.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        #Creating toolbar and adding toolbar elements
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("font-weight: bold; color: 2px solid black; font-size: 16px")
        
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)

        self.toolbar.addActions([
                                self.view_inventory,
                                self.raise_request, 
                                self.issue_stock,
                                self.export_report,
                                self.view_logs 
                            ])
        
        
    def raise_request_dialog(self):
        # manageUsers = ManageUsersWindow()
        # manageUsers.setStyleSheet("background-color: #add8e6;")
        # manageUsers.exec()
        pass

    def add_stocks_dialog(self):
        pass
    def edit_stock_dialog(self):
        pass
    def delete_stock_dialog(self):
        pass
    def view_inventory_as_table(self):
        response = requests.get(f"{SERVER_URL}/view_in")
        data = response.json()

        # Custom display headers
        display_headers = [
            "Item_ID", "Item_Name", "Category", "Description", "Quantity",
            "Unit_price", "Supplier", "Location", "Min_Stock", "Unit",
            "Created_At", "Updated_At"
        ]

        # Corresponding JSON keys
        data_keys = [
            "id", "item_name", "category", "description", "quantity",
            "unit_price", "supplier", "location", "min_stock", "unit",
            "created_at", "updated_at"
        ]

        self.table = QTableWidget()
        self.table.setColumnCount(len(display_headers))
        self.table.setHorizontalHeaderLabels(display_headers)
        self.table.setStyleSheet('font-size: 14px; background-color: white')
        # self.table.setFixedSize(1000, 600)
        self.table.setRowCount(len(data))
        self.table.verticalHeader().setVisible(False)
        # self.table.setAutoScroll(True).
        self.setCentralWidget(self.table)

        #Detecting a cell click
        # self.table.cellClicked.connect(self.getCellValue)

        for row_index, row_data in enumerate(data):
            for col_index, key in enumerate(data_keys):
                value = row_data.get(key, "")
                display_value = "" if value is None else str(value)
                self.table.setItem(row_index, col_index, QTableWidgetItem(display_value))


    def issue_stock_dialog(self):
        pass

    def download_report(self):
        pass
    def view_logs_as_table(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StoreOperatorPanelWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())

