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
# from .manageUsers import ManageUsersWindow
SERVER_URL = "http://localhost:5000"


class ViewerPanelWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management - Admin Panel")
        self.setMinimumSize(900, 700)

        self.view_inventory = QAction("View Inventory", self)
        self.view_inventory.triggered.connect(self.view_inventory_as_table)
        self.view_inventory.hovered.connect(lambda: self.setCursor(Qt.CursorShape.PointingHandCursor))
        self.view_inventory.hovered.connect(lambda: QApplication.restoreOverrideCursor())

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
                                self.view_logs 
                            ])
        
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


    def view_logs_as_table(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ViewerPanelWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())

