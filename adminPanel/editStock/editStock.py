from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SERVER_URL = "http://localhost:5000"

class EditStockWindow(QDialog):
    def __init__(self, item_id, quantity, unit_price, supplier, on_update):
        super().__init__()
        self.item_id = item_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.supplier = supplier
        self.on_update = on_update

        self.setWindowTitle("Inventory Management")
        # self.setContentsMargins(200, 100, 200, 100)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_widget = QWidget()
        inner_widget.setFixedSize(650, 600)  # Increased size to accommodate larger input

        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        self.Quantity_label = QLabel("Quantity:")
        self.Quantity_label.setStyleSheet("font-size: 20px")
        self.quantity_input = QLineEdit()
        self.quantity_input.setText(str(self.quantity))
        self.quantity_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.quantity_input.setPlaceholderText("Enter Quantity")
        self.quantity_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.quantity_input.setFixedSize(300, 40)  # <-- updated size

        quantity_row = QHBoxLayout()
        quantity_row.setSpacing(10)
        quantity_row.addWidget(self.Quantity_label)
        quantity_row.addWidget(self.quantity_input)
        form_layout.addLayout(quantity_row)

        self.unitprice_label = QLabel("Unit Price:")
        self.unitprice_label.setStyleSheet("font-size: 20px")
        self.unitprice_input = QLineEdit()
        self.unitprice_input.setText(str(self.unit_price))
        self.unitprice_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.unitprice_input.setPlaceholderText("Enter Unit Price")
        self.unitprice_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.unitprice_input.setFixedSize(300, 40)  # <-- updated size

        unitprice_row = QHBoxLayout()
        unitprice_row.setSpacing(10)
        unitprice_row.addWidget(self.unitprice_label)
        unitprice_row.addWidget(self.unitprice_input)
        form_layout.addLayout(unitprice_row)

        self.supplier_label = QLabel("Supplier:")
        self.supplier_label.setStyleSheet("font-size: 20px")
        self.supplier_input = QLineEdit()
        self.supplier_input.setText(str(self.supplier))
        self.supplier_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.supplier_input.setPlaceholderText("Enter Supplier Name")
        self.supplier_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.supplier_input.setFixedSize(300, 40)  # <-- updated size

        supplier_row = QHBoxLayout()
        supplier_row.setSpacing(10)
        supplier_row.addWidget(self.supplier_label)
        supplier_row.addWidget(self.supplier_input)
        form_layout.addLayout(supplier_row)

        self.Quantity_label.setFixedWidth(100)
        self.unitprice_label.setFixedWidth(100)
        self.supplier_label.setFixedWidth(100)

        # Buttons
        self.update_button = QPushButton("Update")
        self.update_button.setFixedSize(100, 40)
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.setStyleSheet("""
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
        self.update_button.clicked.connect(self.handle_update)
        button_row = QHBoxLayout()
        button_row.addWidget(self.update_button)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addLayout(button_row)

        inner_widget.setLayout(form_layout)
        outer_layout.addWidget(inner_widget)

        self.setLayout(outer_layout)

    def handle_update(self):
        if not self.quantity_input.text():
            self.show_warning("Please enter quantity!")
            return
        if not self.unitprice_input.text():
            self.show_warning("Please enter unit price!")
            return
        if not self.supplier_input.text():
            self.show_warning("Please enter supplier!")
            return
        
        self.send_updated_item_value()
    
    def show_warning(self, text):
        msg_box = HandPointerMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def send_updated_item_value(self):
        response = requests.put(
            f"{SERVER_URL}/update_value/{self.item_id}",
            json={
                "quantity": int(self.quantity_input.text()),
                "unitPrice": float(self.unitprice_input.text()),
                "supplier": self.supplier_input.text(),
            }
        )
        if response.ok:
            if self.on_update:  # 👈 call the passed function
                self.on_update()
            self.close()


class HandPointerMessageBox(QMessageBox):
    def showEvent(self, event):
        super().showEvent(event)
        for button in self.buttons():
            if isinstance(button, QPushButton):
                button.setCursor(Qt.CursorShape.PointingHandCursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditStockWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
