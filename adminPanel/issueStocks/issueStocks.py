from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SERVER_URL = "http://192.168.0.17:5000"

class ComboBoxLoader(QThread):
    loaded = pyqtSignal(list)

    def __init__(self, itemOrEmpl):
        super().__init__()
        self.itemOrEmpl = itemOrEmpl

    def run(self):
        try:
            response = requests.get(f"{SERVER_URL}/{self.itemOrEmpl}")
            if response.ok:
                self.loaded.emit(response.json())
            else:
                self.loaded.emit([])
        except Exception:
            self.loaded.emit([])


class IssueStocksWindow(QDialog):
    def __init__(self, item_id, itemName, on_issue=None):
        super().__init__()
        self.loaders = []
        self.item_id = item_id
        self.itemName = itemName
        self.on_issue = on_issue
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
        self.quantity_input = self.create_input_row(form_layout, "Quantity:")
        self.issuedby_input = self.create_combobox_row(form_layout, "Issued By:")
        self.issuedto_input = self.create_combobox_row(form_layout, "Issued To:")

        # issue button
        self.issue_button = QPushButton("Issue")
        self.issue_button.setFixedSize(100, 40)
        self.issue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.issue_button.setStyleSheet("""
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
        self.issue_button.clicked.connect(self.handle_issue)
        issue_row = QHBoxLayout()
        issue_row.addStretch()
        issue_row.addWidget(self.issue_button)
        issue_row.addStretch()
        form_layout.addLayout(issue_row)

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
        if label_text == "Item Name:":
            input_field.setText(self.itemName)
        else:
            input_field.setPlaceholderText("Enter quantity to assign")
        input_field.setFixedSize(300, 40)
        input_field.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        input_field.setPlaceholderText("Enter quantity")

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(label)
        row.addWidget(input_field)
        row.addStretch()
        layout.addLayout(row)

        return input_field

    def create_combobox_row(self, layout, label_text):
        if label_text == "Item Name:":
            itemOrEmpl = "item_name"
        elif label_text == "Issued By:":
            itemOrEmpl = "issued_by"
        else:
            itemOrEmpl = "issued_to"
        label = QLabel(label_text)
        label.setFixedWidth(120)
        label.setStyleSheet("font-size: 18px")

        combo = QComboBox()
        combo.setFixedSize(300, 40)
        combo.addItem("Loading...")  # Placeholder
        combo.setEnabled(False)      # Disable until data is fetched
        combo.setStyleSheet("QComboBox { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        # Load options in background
        loader = ComboBoxLoader(itemOrEmpl)
        self.loaders.append(loader) 
        loader.loaded.connect(lambda items: self.populate_combobox(combo, items))
        loader.start()

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(label)
        row.addWidget(combo)
        row.addStretch()
        layout.addLayout(row)

        return combo

    def show_warning(self, text):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def handle_issue(self):
        required_fields = [
            (self.itemname_input, "Item Name"),
            (self.quantity_input, "Quantity"),
            (self.issuedby_input, "Issued By"),
            (self.issuedto_input, "Issued To"),
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
            f"{SERVER_URL}/issue_stock",
            json={
                "itemName": self.itemname_input.text(),
                "quantity": int(self.quantity_input.text()),
                "issued_by": self.issuedby_input.currentText(),
                "issued_to": self.issuedto_input.currentText(),
            }
        )
        if response.ok:
            if self.on_issue:
                self.on_issue()
            self.close()

    # ----------------------------------------------Helper Function-------------------------------------
    def populate_combobox(self, combo, items):
        combo.clear()
        combo.setEnabled(True)
        combo.addItems(items if items else ["None Available"])
        self.loaders = [l for l in self.loaders if l.isRunning()]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IssueStocksWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
