from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QDialog
)
from PyQt6.QtCore import Qt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class AddStocksWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Management")
        # self.setContentsMargins(200, 100, 200, 100)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_widget = QWidget()
        inner_widget.setFixedSize(650, 600)  # Increased size to accommodate larger input

        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        # --------------------------------Username-----------------------------------------
        self.itemname_label = QLabel("Item Name:")
        self.itemname_label.setStyleSheet("font-size: 20px")
        self.itemname_input = QLineEdit()
        self.itemname_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.itemname_input.setPlaceholderText("Enter Username")
        self.itemname_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.itemname_input.setFixedSize(300, 40)  # <-- updated size

        itemname_row = QHBoxLayout()
        itemname_row.setSpacing(10)
        itemname_row.addWidget(self.itemname_label)
        itemname_row.addWidget(self.itemname_input)
        form_layout.addLayout(itemname_row)

        # ----------------------------Email--------------------------------
        self.category_label = QLabel("Category:")
        self.category_label.setStyleSheet("font-size: 20px")
        self.category_input = QLineEdit()
        self.category_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.category_input.setPlaceholderText("Enter Email")
        self.category_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.category_input.setFixedSize(300, 40)

        category_row = QHBoxLayout()
        category_row.setSpacing(10)
        category_row.addWidget(self.category_label)
        category_row.addWidget(self.category_input)
        form_layout.addLayout(category_row)


        # ---------------------------------------------Password-------------------------------------------------
        self.description_label = QLabel("Description:")
        self.description_label.setStyleSheet("font-size: 20px")
        self.description_input = QLineEdit()
        self.description_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.description_input.setPlaceholderText("Enter Description")
        self.description_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.description_input.setFixedSize(300, 40)  # <-- updated size

        description_row = QHBoxLayout()
        description_row.setSpacing(10)
        description_row.addWidget(self.description_label)
        description_row.addWidget(self.description_input)
        form_layout.addLayout(description_row)

        self.Quantity_label = QLabel("Quantity:")
        self.Quantity_label.setStyleSheet("font-size: 20px")
        self.quantity_input = QLineEdit()
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

        self.location_label = QLabel("Location:")
        self.location_label.setStyleSheet("font-size: 20px")
        self.location_input = QLineEdit()
        self.location_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.location_input.setPlaceholderText("Enter Location")
        self.location_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.location_input.setFixedSize(300, 40)  # <-- updated size

        location_row = QHBoxLayout()
        location_row.setSpacing(10)
        location_row.addWidget(self.location_label)
        location_row.addWidget(self.location_input)
        form_layout.addLayout(location_row)

        self.minstock_label = QLabel("Min Stock:")
        self.minstock_label.setStyleSheet("font-size: 20px")
        self.minstock_input = QLineEdit()
        self.minstock_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minstock_input.setPlaceholderText("Enter Min Stock")
        self.minstock_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.minstock_input.setFixedSize(300, 40)  # <-- updated size

        minstock_row = QHBoxLayout()
        minstock_row.setSpacing(10)
        minstock_row.addWidget(self.minstock_label)
        minstock_row.addWidget(self.minstock_input)
        form_layout.addLayout(minstock_row)

        self.unit_label = QLabel("Unit:")
        self.unit_label.setStyleSheet("font-size: 20px")
        self.unit_input = QLineEdit()
        self.unit_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.unit_input.setPlaceholderText("Enter Unit")
        self.unit_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.unit_input.setFixedSize(300, 40)  # <-- updated size


        self.category_label.setFixedWidth(100)
        self.itemname_label.setFixedWidth(100)
        self.description_label.setFixedWidth(100)
        self.Quantity_label.setFixedWidth(100)
        self.unitprice_label.setFixedWidth(100)
        self.supplier_label.setFixedWidth(100)
        self.location_label.setFixedWidth(100)
        self.minstock_label.setFixedWidth(100)
        self.unit_label.setFixedWidth(100)

        # Buttons
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
        button_row = QHBoxLayout()
        button_row.addWidget(self.submit_button)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addLayout(button_row)

        inner_widget.setLayout(form_layout)
        outer_layout.addWidget(inner_widget)

        self.setLayout(outer_layout)

    def handle_submit(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddStocksWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
