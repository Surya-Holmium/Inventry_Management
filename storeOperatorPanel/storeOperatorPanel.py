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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .showRaisedRequests import ShowStockInRequestsWindow, ShowIssuedRequestsWindow
from .issueStocks import IssueStocksWindow
from .editStock import EditStockWindow
SERVER_URL = "http://localhost:5000"


class StoreOperatorPanelWindow(QMainWindow):
    def __init__(self, userName):
        super().__init__()
        self.userName = userName
        self.setWindowTitle("Inventory Management - Store Operator Panel")
        self.setMinimumSize(900, 700)

        self.statusbar = self.statusBar()

        self.raise_request = QAction("StockIn Request", self)
        self.raise_request.triggered.connect(self.show_raised_request_dialog)
        self.raise_request.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.raise_request.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.view_inventory = QAction("View Inventory", self)
        self.view_inventory.triggered.connect(self.view_inventory_as_table)
        self.view_inventory.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.view_inventory.hovered.connect(lambda: QApplication.restoreOverrideCursor())

        self.issue_stock = QAction("StockOut Requests", self)
        self.issue_stock.triggered.connect(self.show_issued_request_dialog)
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

        self.logout_button = QAction("Logout", self)
        self.logout_button.triggered.connect(self.logout)
        self.logout_button.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.logout_button.hovered.connect(lambda: QApplication.restoreOverrideCursor())

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
                                self.view_logs,
                                self.logout_button
                            ])
        
        
    def show_raised_request_dialog(self):
        showStockInRequests = ShowStockInRequestsWindow()
        showStockInRequests.setStyleSheet("background-color: #add8e6;")
        showStockInRequests.exec()

    def edit_stock_dialog(self):
        index = self.table.currentRow()
        item_id = self.table.item(index, 1).text()
        itemName = self.table.item(index, 2).text()
        unit_price = self.table.item(index, 6).text()
        supplier = self.table.item(index, 7).text()
        editStock = EditStockWindow(item_id, itemName, unit_price, supplier, self.view_inventory_as_table)
        editStock.setStyleSheet("background-color: #add8e6;")
        editStock.exec()

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
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
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
        search_btn = QPushButton("Search")
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

    def show_issued_request_dialog(self):
        showIssuedRequests = ShowIssuedRequestsWindow()
        showIssuedRequests.setStyleSheet("background-color: #add8e6;")
        showIssuedRequests.exec()

    def download_report(self):
        pass
    def view_logs_as_table(self):
        pass
    
    def issue_stock_dialog(self):
        index = self.table.currentRow()
        item_id = self.table.item(index, 1).text()
        itemName = self.table.item(index, 2).text()
        issueStocks = IssueStocksWindow(self.userName, item_id, itemName, self.view_inventory_as_table)
        issueStocks.setStyleSheet("background-color: #add8e6;")
        issueStocks.exec()

    def getCellValue(self):
        self.issue_stock = QPushButton("Stock Out", self)

        self.issue_stock.clicked.connect(self.issue_stock_dialog)
        self.issue_stock.setCursor(Qt.CursorShape.PointingHandCursor)

        self.edit_stock = QPushButton("Stock In", self)

        self.edit_stock.clicked.connect(self.edit_stock_dialog)
        self.edit_stock.setCursor(Qt.CursorShape.PointingHandCursor)

        for btn in [self.issue_stock, self.edit_stock]:
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
            if widget and widget.text() in ["Stock Out", "Stock In"]:
                self.search_row.removeWidget(widget)

        self.search_row.addWidget(self.edit_stock),
        self.search_row.addWidget(self.issue_stock)

    def logout(self):
        from mainWindow import LoginWindow
        response = requests.post(f"{SERVER_URL}/logout/{self.userName}", json={"msg": True})
        if response.ok:
            self.logoutUsers = LoginWindow()
            self.logoutUsers.setStyleSheet("background-color: #add8e6;")
            self.logoutUsers.showMaximized()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StoreOperatorPanelWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())

