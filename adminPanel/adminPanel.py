from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QToolBar, QTableWidget, QTableWidgetItem, QMessageBox, QPushButton, QHBoxLayout, QLabel, QLineEdit
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
from .issueStocks import IssueStocksWindow
# from 
SERVER_URL = "http://192.168.0.17:5000"

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
                                self.manage_request,
                                self.export_report,
                                self.view_logs, 
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
        itemName = self.table.item(index, 2).text()
        unit_price = self.table.item(index, 6).text()
        supplier = self.table.item(index, 7).text()
        editStock = EditStockWindow(item_id, itemName, unit_price, supplier, self.view_inventory_as_table)
        editStock.setStyleSheet("background-color: #add8e6;")
        editStock.exec()

    def delete_stock_item(self):
        index = self.table.currentRow()
        item_id = self.table.item(index, 1).text()
        response = requests.delete(f"{SERVER_URL}/delete_item/{item_id}")
        if response.ok:
            self.view_inventory_as_table()

    def view_inventory_as_table(self):
        data = requests.get(f"{SERVER_URL}/view_inventory").json()

        headers = ["S. No.", "Item_ID", "Item_Name", "Category", "Description", "Quantity",
                   "Unit_price", "Supplier", "Location", "Min_Stock", "Unit",
                   "Created_At", "Updated_At"]
        keys = ["id", "item_name", "category", "description", "quantity",
                "unit_price", "supplier", "location", "min_stock", "unit",
                "created_at", "updated_at"]

        # ───────── table ─────────
        table = QTableWidget(len(data), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget       { font-size:15px; background:white; }
            QHeaderView::section{ background:#E0E0E0; font-size:16px; font-weight:bold; padding:6px; }
        """)
        table.resizeColumnsToContents()
        for c in range(table.columnCount()):
            table.setColumnWidth(c, table.columnWidth(c) + 50)

        for r, row in enumerate(data):
            table.setRowHeight(r, 40)
            table.setItem(r, 0, QTableWidgetItem(str(r + 1)))
            for c, k in enumerate(keys, start=1):
                table.setItem(r, c, QTableWidgetItem(str(row.get(k, ""))))
            if row["quantity"] <= 10:
                self.show_warning(f"{row['item_name']} stock is low. Please restock.")

        self.table = table
        self.table.cellClicked.connect(self.getCellValue)

        # ───────── search bar ─────────
        search_lbl   = QLabel("Search:")
        search_lbl.setStyleSheet("font-size: 20px")
        search_input = QLineEdit()
        search_input.setFixedSize(300, 40)
        search_input.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        search_input.setPlaceholderText("Item, category, supplier …")
        search_btn   = QPushButton("Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: None;
                border-radius: 15px;
                padding: 8px 16px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #A6F1F4;
            }
        """)

        def filter_table():
            q = search_input.text().lower().strip()
            for row in range(table.rowCount()):
                visible = any(q in (table.item(row, col).text().lower())
                              for col in range(1, table.columnCount())) if q else True
                table.setRowHidden(row, not visible)

        search_btn.clicked.connect(filter_table)
        search_input.returnPressed.connect(filter_table)
        search_input.textChanged.connect(filter_table)

        self.search_row = QHBoxLayout()
        for w in (search_lbl, search_input, search_btn):
            self.search_row.addWidget(w)
        self.search_row.addStretch()

        # ───────── assemble widget ─────────
        wrap = QWidget(); layout = QVBoxLayout(wrap)
        layout.setContentsMargins(50, 30, 50, 20)
        layout.addLayout(self.search_row)
        layout.addWidget(table)

        self.setCentralWidget(wrap)

    def show_warning(self, text):
        msg_box = HandPointerMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def issue_stock_dialog(self):
        index = self.table.currentRow()
        item_id = self.table.item(index, 1).text()
        itemName = self.table.item(index, 2).text()
        issueStocks = IssueStocksWindow(item_id, itemName, self.view_inventory_as_table)
        issueStocks.setStyleSheet("background-color: #add8e6;")
        issueStocks.exec()
        
    def manage_request_dialog(self):
        pass
    def download_report(self):
        pass
    def view_logs_as_table(self):
        pass

    def getCellValue(self):
        # Create actions

        self.issue_stock = QPushButton("Stock Out", self)

        self.issue_stock.clicked.connect(self.issue_stock_dialog)
        self.issue_stock.setCursor(Qt.CursorShape.PointingHandCursor)

        self.edit_stock = QPushButton("Stock In", self)

        self.edit_stock.clicked.connect(self.edit_stock_dialog)
        self.edit_stock.setCursor(Qt.CursorShape.PointingHandCursor)

        self.delete_stock = QPushButton("Delete Stock", self)
        self.delete_stock.clicked.connect(self.delete_stock_item)
        self.delete_stock.setCursor(Qt.CursorShape.PointingHandCursor)

        for btn in [self.issue_stock, self.edit_stock, self.delete_stock]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: None;
                    border-radius: 15px;
                    padding: 8px 16px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #A6F1F4;
                }
            """)

        # Remove existing instances from the toolbar (if present)
        for i in reversed(range(self.search_row.count())):
            widget = self.search_row.itemAt(i).widget()
            if widget and widget.text() in ["Stock Out", "Stock In", "Delete Stock"]:
                self.search_row.removeWidget(widget)

        self.search_row.addWidget(self.edit_stock),
        self.search_row.addWidget(self.issue_stock)
        self.search_row.addWidget(self.delete_stock)

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

