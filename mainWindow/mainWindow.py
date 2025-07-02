from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QMainWindow, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor
import functools

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adminPanel import AdminPanelWindow
from managerPanel import ManagerPanelWindow
from storeOperatorPanel import StoreOperatorPanelWindow
from viewerPanel import ViewerPanelWindow

SERVER_URL = "http://13.200.108.197:5000"
executor = ThreadPoolExecutor()

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Management")
        self.setContentsMargins(200, 100, 200, 100)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_widget = QWidget()
        inner_widget.setFixedSize(450, 400)  # Increased size to accommodate larger input

        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        self.message = QLabel("Welcome!")
        self.message.setStyleSheet("color: green; font-weight: bold; font-size: 36px")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.message)

        # Username
        self.username_label = QLabel("Username:")
        self.username_label.setStyleSheet("font-size: 20px")
        self.username_input = QLineEdit()
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

        # Password
        self.password_label = QLabel("Password:")
        self.password_label.setStyleSheet("font-size: 20px")
        self.password_input = QLineEdit()
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

        # Align label widths
        self.username_label.setFixedWidth(100)
        self.password_label.setFixedWidth(100)

        # Buttons
        self.login_button = QPushButton("Login")
        # self.signup_button = QPushButton("Sign-Up")
        self.login_button.setFixedSize(100, 40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
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
        
        self.login_button.clicked.connect(self.handle_login)
        # self.signup_button.clicked.connect(self.handle_signup)
        button_row = QHBoxLayout()
        button_row.addWidget(self.login_button)
        # button_row.addWidget(self.signup_button)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addLayout(button_row)

        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: red; font-size: 12px")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(self.message_label)

        inner_widget.setLayout(form_layout)
        outer_layout.addWidget(inner_widget)

        central_widget = QWidget()
        central_widget.setLayout(outer_layout)
        self.setCentralWidget(central_widget)

    def handle_login(self):
        if not self.username_input.text():
            msg_box = HandPointerMessageBox()
            msg_box.setWindowTitle("Warning")
            msg_box.setText("Please enter username!")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
            return

        if not self.password_input.text():
            msg_box = HandPointerMessageBox()
            msg_box.setWindowTitle("Warning")
            msg_box.setText("Please enter password!")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
            return

        try:
            response = requests.post(
                f"{SERVER_URL}/login",
                json={"user": self.username_input.text(), "pass": self.password_input.text()}
            )
            data = response.json()
            print("Login response:", data)  # 👈 Debugging

            role = data.get("role")
            if role == "Admin":
                self.switch_window(role=role)
            elif role == "Manager":
                self.switch_window(role=role)
            elif role == "Store Operator":
                self.switch_window(role=role)
            elif role == "Viewer":
                self.switch_window(role=role)
            else:
                self.message_label.setText(data.get("error"))

        except Exception as e:
            self.message_label.setText(f"Error: {str(e)}")

    def switch_window(self, role = None):
        if role == "Admin":
            window = AdminPanelWindow()
        elif(role == "Manager"):
            window = ManagerPanelWindow()
        elif(role == "Store Operator"):
            window = StoreOperatorPanelWindow()
        else:
            window = ViewerPanelWindow()
        window.setStyleSheet("background-color: #add8e6;")
        window.showMaximized()
        self.close()


class HandPointerMessageBox(QMessageBox):
    def showEvent(self, event):
        super().showEvent(event)
        for button in self.buttons():
            if isinstance(button, QPushButton):
                button.setCursor(Qt.CursorShape.PointingHandCursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
