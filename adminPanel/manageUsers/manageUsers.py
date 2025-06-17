from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QMainWindow, QVBoxLayout, QHBoxLayout, QComboBox, QDialog
)
from PyQt6.QtCore import Qt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class ManageUsersWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Management")
        # self.setContentsMargins(200, 100, 200, 100)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_widget = QWidget()
        inner_widget.setFixedSize(450, 400)  # Increased size to accommodate larger input

        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        # --------------------------------Username-----------------------------------------
        self.username_label = QLabel("Username:")
        self.username_label.setStyleSheet("font-size: 20px")
        self.username_input = QLineEdit()
        self.username_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.username_input.setFixedSize(300, 40)  # <-- updated size

        username_row = QHBoxLayout()
        username_row.setSpacing(10)
        username_row.addWidget(self.username_label)
        username_row.addWidget(self.username_input)
        form_layout.addLayout(username_row)

        # ----------------------------Email--------------------------------
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("font-size: 20px")
        self.email_input = QLineEdit()
        self.email_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.email_input.setPlaceholderText("Enter Email")
        self.email_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.email_input.setFixedSize(300, 40)

        email_row = QHBoxLayout()
        email_row.setSpacing(10)
        email_row.addWidget(self.email_label)
        email_row.addWidget(self.email_input)
        form_layout.addLayout(email_row)


        # ---------------------------------------------Password-------------------------------------------------
        self.password_label = QLabel("Password:")
        self.password_label.setStyleSheet("font-size: 20px")
        self.password_input = QLineEdit()
        self.password_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        self.password_input.setFixedSize(300, 40)  # <-- updated size

        password_row = QHBoxLayout()
        password_row.setSpacing(10)
        password_row.addWidget(self.password_label)
        password_row.addWidget(self.password_input)
        form_layout.addLayout(password_row)

        # --------------------------------------Role------------------------------------------------------------
        self.role_label = QLabel("Role:")
        self.role_label.setStyleSheet("font-size: 20px")
        self.role_type = QComboBox()
        self.role_type.setCursor(Qt.CursorShape.PointingHandCursor)
        self.role_type.setStyleSheet("background-color: white;")
        self.role_type.addItems(["Admin", "Manager", "Store Operator", "Viewer"])
        self.role_type.setFixedSize(300, 40)
        self.role_type.setStyleSheet(
            "QComboBox { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )

        role_row = QHBoxLayout()
        role_row.setSpacing(10)
        role_row.addWidget(self.role_label)
        role_row.addWidget(self.role_type)
        form_layout.addLayout(role_row)

        # Align label widths
        self.role_label.setFixedWidth(100)
        self.email_label.setFixedWidth(100)
        self.username_label.setFixedWidth(100)
        self.password_label.setFixedWidth(100)

        # Buttons
        self.register_button = QPushButton("Register")
        self.register_button.setFixedSize(100, 40)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
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
        self.register_button.clicked.connect(self.handle_register)
        button_row = QHBoxLayout()
        button_row.addWidget(self.register_button)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addLayout(button_row)

        inner_widget.setLayout(form_layout)
        outer_layout.addWidget(inner_widget)

        self.setLayout(outer_layout)

    def handle_register(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManageUsersWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
