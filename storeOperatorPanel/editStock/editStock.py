from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SERVER_URL = "http://192.168.0.23:5000"

class EditStockWindow(QDialog):
    def __init__(self, item_id, itemName, unit_price, supplier, on_update):
        super().__init__()
        self.item_id = item_id
        self.itemName = itemName
        self.unit_price = unit_price
        self.supplier = supplier
        self.on_update = on_update

        self.setWindowTitle("Inventory Management")
        # self.setContentsMargins(200, 100, 200, 100)

        # Outer layout: centers the inner form layout horizontally and vertically
        self.outer_layout = QVBoxLayout()
        self.outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a widget to hold the form layout
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.itemname_input = self.create_input_row(form_layout, "Item Name:", self.itemName)
        self.quantity_input = self.create_input_row(form_layout, "Quantity:", value=None)
        self.unitprice_input = self.create_input_row(form_layout, "Unit Price:", self.unit_price)

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

        # Add vertical spacers to center vertically
        self.outer_layout.addStretch()
        self.outer_layout.addWidget(form_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.outer_layout.addStretch()

        self.setLayout(self.outer_layout)

    def create_input_row(self, layout, label_text, value):
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet("font-size: 18px")

        input_field = QLineEdit()
        input_field.setFixedSize(300, 40)
        input_field.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        if(label_text == "Item Name:"):
            input_field.setText(value)
        elif(label_text == "Quantity:"):
            input_field.setPlaceholderText("Enter quantity")
        elif(label_text == "Unit Price:"):
            input_field.setText(value)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(label)
        row.addWidget(input_field)
        row.addStretch()
        layout.addLayout(row)

        return input_field

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
        response = requests.post(
            f"{SERVER_URL}/raise_request/{"stock_in"}",
            json={
                "itemName": self.itemname_input.text(),
                "quantity": int(self.quantity_input.text()),
                "unitPrice": float(self.unitprice_input.text()),
                "supplier": self.supplier_input.text(),
            }
        )
        if response.ok:
            if self.on_update:
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
