from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, QMessageBox, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .manageUsers import ManageUsersWindow
from .addStocks import AddStocksWindow
from .editStock import EditStockWindow
# from 
SERVER_URL = "http://13.200.108.197:5000"

class AdminPanelWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management - Admin Panel")
        self.setMinimumSize(900, 700)

        self.statusbar = self.statusBar()

        self.manage_users = QAction("Manage Users", self)
        self.manage_users.triggered.connect(self.manage_users_dialog)
        self.manage_users.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.manage_users.hovered.connect(lambda: QApplication.restoreOverrideCursor())


        self.add_stocks = QAction("Create New Stock", self)
        self.add_stocks.triggered.connect(self.add_stocks_dialog)
        self.add_stocks.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.add_stocks.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.view_inventory = QAction("View Inventory", self)
        self.view_inventory.triggered.connect(self.view_inventory_as_table)
        self.view_inventory.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.view_inventory.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.issue_stock = QAction("Outbound Stock", self)
        self.issue_stock.triggered.connect(self.issue_stock_dialog)
        self.issue_stock.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.issue_stock.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.manage_request = QAction("Manage Request", self)
        self.manage_request.triggered.connect(self.manage_request_dialog)
        self.manage_request.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.manage_request.hovered.connect(lambda: QApplication.restoreOverrideCursor())

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
                                self.add_stocks, 
                                self.manage_users, 
                                self.issue_stock,
                                self.manage_request,
                                self.export_report,
                                self.view_logs 
                            ])
        
        
    def manage_users_dialog(self):
        manageUsers = ManageUsersWindow()
        manageUsers.setStyleSheet("background-color: #add8e6;")
        manageUsers.exec()

    def add_stocks_dialog(self):
        addStocks = AddStocksWindow(self.view_inventory_as_table)
        addStocks.setStyleSheet("background-color: #add8e6;")
        addStocks.exec()
        
    def edit_stock_dialog(self):
        index = self.table.currentRow()
        item_id = self.table.item(index, 1).text()
        quntity = self.table.item(index, 5).text()
        unit_price = self.table.item(index, 6).text()
        supplier = self.table.item(index, 7).text()
        editStock = EditStockWindow(item_id, quntity, unit_price, supplier, self.view_inventory_as_table)
        editStock.setStyleSheet("background-color: #add8e6;")
        editStock.exec()

    def delete_stock_item(self):
        index = self.table.currentRow()
        item_id = self.table.item(index, 1).text()
        response = requests.delete(f"{SERVER_URL}/delete_item/{item_id}")
        if response.ok:
            self.view_inventory_as_table()

    def view_inventory_as_table(self):
        response = requests.get(f"{SERVER_URL}/view_inventory")
        data = response.json()
        display_headers = [
            "S. No.", "Item_ID", "Item_Name", "Category", "Description", "Quantity",
            "Unit_price", "Supplier", "Location", "Min_Stock", "Unit",
            "Created_At", "Updated_At"
        ]
        data_keys = [
            "id", "item_name", "category", "description", "quantity",
            "unit_price", "supplier", "location", "min_stock", "unit",
            "created_at", "updated_at"
        ]

        table = QTableWidget()
        table.setColumnCount(len(display_headers))
        table.setHorizontalHeaderLabels(display_headers)
        table.setRowCount(len(data))
        table.verticalHeader().setVisible(False)

        table.setStyleSheet("""
            QTableWidget {
                font-size: 15px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                font-size: 16px;
                font-weight: bold;
                padding: 6px;
            }
        """)

        table.resizeColumnsToContents()
        for col in range(table.columnCount()):
            table.setColumnWidth(col, table.columnWidth(col) + 30)

        for row_index, row_data in enumerate(data):
            table.setRowHeight(row_index, 40)
            # Add S. No. manually
            table.setItem(row_index, 0, QTableWidgetItem(str(row_index + 1)))
            for col_index, key in enumerate(data_keys):
                value = row_data.get(key, "")
                table.setItem(row_index, col_index + 1, QTableWidgetItem(str(value)))
            if(row_data["quantity"] <= 10):
                self.show_warning(f"{row_data["item_name"]} stock is minimum amount. Please add more stock")

        self.table = table
        self.table.cellClicked.connect(self.getCellValue)

        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(50, 30, 50, 20)
        container_layout.addWidget(table)

        self.setCentralWidget(container_widget)

    def show_warning(self, text):
        msg_box = HandPointerMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def issue_stock_dialog(self):
        pass
    def manage_request_dialog(self):
        pass
    def download_report(self):
        pass
    def view_logs_as_table(self):
        pass

    def getCellValue(self):
        # Create actions
        self.edit_stock = QAction("Inbound Stock", self)
        self.edit_stock.triggered.connect(self.edit_stock_dialog)
        self.edit_stock.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.edit_stock.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.delete_stock = QAction("Delete Stock", self)
        self.delete_stock.triggered.connect(self.delete_stock_item)
        self.delete_stock.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_stock.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        # Remove existing instances from the toolbar (if present)
        for action in self.toolbar.actions():
            if action.text() in ["Inbound Stock", "Delete Stock"]:
                self.toolbar.removeAction(action)

        # Add fresh actions
        self.toolbar.addAction(self.edit_stock)
        self.toolbar.addAction(self.delete_stock)

class HandPointerMessageBox(QMessageBox):
    def showEvent(self, event):
        super().showEvent(event)
        for button in self.buttons():
            if isinstance(button, QPushButton):
                button.setCursor(Qt.CursorShape.PointingHandCursor)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminPanelWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())

