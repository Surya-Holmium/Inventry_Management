from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SERVER_URL = "http://13.200.108.197:5000"

class ComboBoxLoader(QThread):
    loaded = pyqtSignal(list)

    def __init__(self, oType):
        super().__init__()
        self.oType = oType

    def run(self):
        try:
            response = requests.get(f"{SERVER_URL}/options/{self.oType}")
            if response.ok:
                self.loaded.emit(response.json())
            else:
                self.loaded.emit([])
        except Exception:
            self.loaded.emit([])


class AddStocksWindow(QDialog):
    def __init__(self, on_add=None):
        super().__init__()
        self.loaders = []
        self.on_add = on_add
        self.setWindowTitle("Inventory Management")
        self.setMinimumSize(700, 700)

        # Outer layout: centers the inner form layout horizontally and vertically
        self.outer_layout = QVBoxLayout()
        self.outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a widget to hold the form layout
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.itemname_input = self.create_input_row(form_layout, "Item Name:")
        self.select_category = self.create_combobox_row(form_layout, "Category:")
        self.description_input = self.create_input_row(form_layout, "Description:")
        self.quantity_input = self.create_input_row(form_layout, "Quantity:")
        self.unitprice_input = self.create_input_row(form_layout, "Unit Price:")
        self.supplier_input = self.create_combobox_row(form_layout, "Supplier:")
        self.location_input = self.create_combobox_row(form_layout, "Location:")
        self.minstock_input = self.create_input_row(form_layout, "Min Stock:")
        self.unit_input = self.create_combobox_row(form_layout, "Unit:")

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedSize(100, 40)
        self.submit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_button.setStyleSheet("""
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
        self.submit_button.clicked.connect(self.handle_submit)
        submit_row = QHBoxLayout()
        submit_row.addStretch()
        submit_row.addWidget(self.submit_button)
        submit_row.addStretch()
        form_layout.addLayout(submit_row)

        # Add vertical spacers to center vertically
        self.outer_layout.addStretch()
        self.outer_layout.addWidget(form_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.outer_layout.addStretch()

        self.setLayout(self.outer_layout)


    def create_input_row(self, layout, label_text):
        label = QLabel(label_text)
        label.setFixedWidth(120)
        label.setStyleSheet("font-size: 18px")

        input_field = QLineEdit()
        input_field.setFixedSize(300, 40)
        input_field.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        if(label_text == "Item Name:"):
            input_field.setPlaceholderText("Enter item name")
        elif(label_text == "Description:"):
            input_field.setPlaceholderText("Enter description")
        elif(label_text == "Quantity:"):
            input_field.setPlaceholderText("Enter quantity")
        elif(label_text == "Unit Price:"):
            input_field.setPlaceholderText("Enter unit price")
        elif(label_text == "Min Stock:"):
            input_field.setPlaceholderText("Enter minimum stock value")

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(label)
        row.addWidget(input_field)
        row.addStretch()
        layout.addLayout(row)

        return input_field

    def create_combobox_row(self, layout, label_text):
        oType = label_text[:-1].lower()
        label = QLabel(label_text)
        label.setFixedWidth(120)
        label.setStyleSheet("font-size: 18px")

        combo = QComboBox()
        combo.setFixedSize(300, 40)
        combo.addItem("Loading...")  # Placeholder
        combo.setEnabled(False)      # Disable until data is fetched
        combo.setStyleSheet("QComboBox { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        # Load options in background
        loader = ComboBoxLoader(oType)
        self.loaders.append(loader) 
        loader.loaded.connect(lambda items: self.populate_combobox(combo, items))
        loader.start()

        add_button = QPushButton("+")
        add_button.setFixedSize(40, 40)
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.clicked.connect(lambda: self.open_add_dialog(combo, oType))

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(label)
        row.addWidget(combo)
        row.addWidget(add_button)
        row.addStretch()
        layout.addLayout(row)

        return combo

    def open_add_dialog(self, combo_box, oType):
        dialog = QDialog(self)
        dialog.setFixedSize(300, 150)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        input_field = QLineEdit()
        if oType == "category":
            dialog.setWindowTitle("Add New Category")
            input_field.setPlaceholderText("Enter new category")
        elif oType == "location":
            dialog.setWindowTitle("Add New Location")
            input_field.setPlaceholderText("Enter new location")
        elif oType == "supplier":
            dialog.setWindowTitle("Add New Supplier")
            input_field.setPlaceholderText("Enter new supplier")
        else:
            dialog.setWindowTitle("Add New Unit")
            input_field.setPlaceholderText("Enter new unit")

        input_field.setFixedHeight(35)
        input_field.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        add_button = QPushButton("Add")
        add_button.setFixedSize(100, 40)
        add_button.setStyleSheet("""
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
        add_button.clicked.connect(lambda: self.add_to_combobox(combo_box, input_field.text(), oType, dialog))

        # 🔽 Center the button using a horizontal layout
        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(add_button)
        button_row.addStretch()

        layout.addWidget(input_field)
        layout.addLayout(button_row)  # 👈 Replace addWidget with addLayout

        dialog.setLayout(layout)
        dialog.exec()

    def add_to_combobox(self, combo_box, new_text, option_type, dialog):
        if not new_text:
            return
        try:
            response = requests.post(
                f"{SERVER_URL}/options/{option_type}",
                json={"value": new_text}
            )
            if response.ok and new_text not in [combo_box.itemText(i) for i in range(combo_box.count())]:
                combo_box.addItem(new_text)
                combo_box.setCurrentText(new_text)
        except Exception as e:
            print(f"Failed to add new {option_type}:", e)
        dialog.close()

    def show_warning(self, text):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def handle_submit(self):
        required_fields = [
            (self.itemname_input, "Item Name"),
            (self.select_category, "Category"),
            (self.description_input, "Description"),
            (self.quantity_input, "Quantity"),
            (self.unitprice_input, "Unit Price"),
            (self.supplier_input, "Supplier"),
            (self.location_input, "Location"),
            (self.minstock_input, "Min Stock"),
            (self.unit_input, "Unit")
        ]

        for field, name in required_fields:
            if isinstance(field, QLineEdit) and not field.text():
                self.show_warning(f"Please enter {name}!")
                return
            elif isinstance(field, QComboBox) and not field.currentText():
                self.show_warning(f"Please select {name}!")
                return

        self.send_items_value()

    def send_items_value(self):
        response = requests.post(
            f"{SERVER_URL}/create_new_item",
            json={
                "itemName": self.itemname_input.text(),
                "category": self.select_category.currentText(),
                "description": self.description_input.text(),
                "quantity": int(self.quantity_input.text()),
                "unitPrice": float(self.unitprice_input.text()),
                "supplier": self.supplier_input.currentText(),
                "location": self.location_input.currentText(),
                "minStock": self.minstock_input.text(),
                "unit": self.unit_input.currentText(),
            }
        )
        if response.ok:
            if self.on_add:
                self.on_add()
            self.close()

    # ----------------------------------------------Helper Function-------------------------------------
    def populate_combobox(self, combo, items):
        combo.clear()
        combo.setEnabled(True)
        combo.addItems(items if items else ["None Available"])
        self.loaders = [l for l in self.loaders if l.isRunning()]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddStocksWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
