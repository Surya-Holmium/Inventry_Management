from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QDialog, QMessageBox, QTableWidgetItem, QTableWidget
)
from PyQt6.QtCore import Qt
import sys
import os
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
SERVER_URL = "http://192.168.0.17:5000"

class ManageUsersWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inventory Management - Manage User")
        self.setMinimumSize(900, 600)

        # ------------------- Simulated Toolbar -------------------
        self.toolbar_layout = QHBoxLayout()
        self.toolbar_layout.setSpacing(20)

        self.add_user_button = QPushButton("Add User")
        self.add_user_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_user_button.clicked.connect(self.add_user_dialog)

        self.view_user_button = QPushButton("View Users")
        self.view_user_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_user_button.clicked.connect(self.view_user_as_table)

        for btn in [self.view_user_button, self.add_user_button]:
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

        self.toolbar_layout.addWidget(self.view_user_button)
        self.toolbar_layout.addWidget(self.add_user_button)
        self.toolbar_layout.addStretch()

        # ------------------- Main Layout -------------------
        self.outer_layout = QVBoxLayout()
        self.outer_layout.addLayout(self.toolbar_layout)
        self.outer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Placeholder for dynamic content (table, forms, etc.)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.outer_layout.addWidget(self.content_widget)

        self.setLayout(self.outer_layout)

    def setup_input_field(self, label, input_field, layout):
        label.setStyleSheet("font-size: 20px")
        label.setFixedWidth(100)
        input_field.setCursor(Qt.CursorShape.PointingHandCursor)
        input_field.setFixedSize(300, 40)
        input_field.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }"
        )
        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(label)
        row.addWidget(input_field)
        layout.addLayout(row)

    def add_user_dialog(self):
        add_user = AddUserWindow(self.view_user_as_table)
        add_user.setStyleSheet("background-color: #add8e6;")
        add_user.exec()

    def view_user_as_table(self):
        response = requests.get(f"{SERVER_URL}/view_user")
        data = response.json()

        display_headers = ["UserID", "UserName", "Email", "Role", "Status"]
        data_keys = ["user_id","uName", "uEmail", "uRole", "sts"]

        self.table = QTableWidget()
        self.table.setColumnCount(len(display_headers))
        self.table.setHorizontalHeaderLabels(display_headers)
        self.table.setStyleSheet('font-size: 14px; background-color: white')
        self.table.setRowCount(len(data))
        self.table.verticalHeader().setVisible(False)

        for row_index, row_data in enumerate(data):
            for col_index, key in enumerate(data_keys):
                value = row_data.get(key, "")
                display_value = "" if value is None else str(value)
                self.table.setItem(row_index, col_index, QTableWidgetItem(display_value))

        # Clear previous widgets from the content layout
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.table.cellClicked.connect(self.getCellValue)
        # Add the table below the toolbar
        self.content_layout.addWidget(self.table)

    def getCellValue(self):
        self.edit_user = QPushButton("Edit User", self)

        self.edit_user.clicked.connect(self.edit_user_dialog)
        self.edit_user.setCursor(Qt.CursorShape.PointingHandCursor)

        self.deleteuser = QPushButton("Delete User", self)
        self.deleteuser.clicked.connect(self.delete_user)
        self.deleteuser.setCursor(Qt.CursorShape.PointingHandCursor)

        for btn in [self.edit_user, self.deleteuser]:
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
        for i in reversed(range(self.toolbar_layout.count())):
            widget = self.toolbar_layout.itemAt(i).widget()
            if widget and widget.text() in ["Edit User", "Delete User"]:
                self.toolbar_layout.removeWidget(widget)
                # widget.setParent(None)  # Optional: removes it from the layout hierarchy


        # Add fresh actions
        self.toolbar_layout.addWidget(self.edit_user)
        self.toolbar_layout.addWidget(self.deleteuser)

    def delete_user(self):
        index = self.table.currentRow()
        user_id = self.table.item(index, 0).text()
        response = requests.delete(f"{SERVER_URL}/delete_user/{user_id}")
        if response.ok:
            self.view_user_as_table()

    def edit_user_dialog(self):
        index = self.table.currentRow()
        user_id = self.table.item(index, 0).text()
        uName = self.table.item(index, 1).text()
        uEmail = self.table.item(index, 2).text()
        uRole = self.table.item(index, 2).text()
        editStock = EditUserWindow(user_id, uName, uEmail, uRole, self.view_user_as_table)
        editStock.setStyleSheet("background-color: #add8e6;")
        editStock.exec()


class HandPointerMessageBox(QMessageBox):
    def showEvent(self, event):
        super().showEvent(event)
        for button in self.buttons():
            if isinstance(button, QPushButton):
                button.setCursor(Qt.CursorShape.PointingHandCursor)


class EditUserWindow(QDialog):
    def __init__(self, user_id, uName, uEmail, uRole,  on_update_user):
        super().__init__()
        self.user_id = user_id
        self.uName = uName
        self.uEmail = uEmail
        self.uRole = uRole
        self.on_update_user = on_update_user

        self.setWindowTitle("Inventory Management - Add User")
        self.setMinimumSize(600, 400)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_widget = QWidget()
        inner_widget.setFixedSize(450, 400)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        # ----------------- Username -----------------
        self.username_label = QLabel("Username:")
        self.username_label.setStyleSheet("font-size: 20px")
        self.username_input = QLineEdit()
        self.username_input.setText(self.uName)
        self.username_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        self.username_input.setFixedSize(300, 40)

        username_row = QHBoxLayout()
        username_row.setSpacing(10)
        username_row.addWidget(self.username_label)
        username_row.addWidget(self.username_input)
        form_layout.addLayout(username_row)

        # ----------------- Email -----------------
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("font-size: 20px")
        self.email_input = QLineEdit()
        self.email_input.setText(self.uEmail)
        self.email_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.email_input.setPlaceholderText("Enter Email")
        self.email_input.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        self.email_input.setFixedSize(300, 40)

        email_row = QHBoxLayout()
        email_row.setSpacing(10)
        email_row.addWidget(self.email_label)
        email_row.addWidget(self.email_input)
        form_layout.addLayout(email_row)

        # ----------------- Role -----------------
        self.role_label = QLabel("Role:")
        self.role_label.setStyleSheet("font-size: 20px")
        self.role_type = QComboBox()
        self.role_type.setCurrentText(self.uRole)
        self.role_type.setCursor(Qt.CursorShape.PointingHandCursor)
        self.role_type.addItems(["Admin", "Manager", "Store Operator", "Viewer"])
        self.role_type.setFixedSize(300, 40)
        self.role_type.setStyleSheet("QComboBox { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        role_row = QHBoxLayout()
        role_row.setSpacing(10)
        role_row.addWidget(self.role_label)
        role_row.addWidget(self.role_type)
        form_layout.addLayout(role_row)

        # Align label widths
        for label in [self.username_label, self.email_label, self.role_label]:
            label.setFixedWidth(100)

        # ----------------- Register Button -----------------
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
        self.update_button.clicked.connect(self.handle_register)

        button_row = QHBoxLayout()
        button_row.addWidget(self.update_button)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addLayout(button_row)

        inner_widget.setLayout(form_layout)
        outer_layout.addWidget(inner_widget)
        self.setLayout(outer_layout)

    def handle_register(self):
        if not self.username_input.text():
            self.show_warning("Please enter username!")
            return
        if not self.email_input.text():
            self.show_warning("Please enter email!")
            return
        if not self.role_type.currentText():
            self.show_warning("Please select role!")
            return

        response = requests.put(
            f"{SERVER_URL}/update_user/{self.user_id}",
            json={
                "uName": self.username_input.text(),
                "uEmail": self.email_input.text(),
                "uRole": self.role_type.currentText()
            }
        )
        print(response.json())
        if response.ok:
            if self.on_update_user:
                self.on_update_user()
            self.close()

    def show_warning(self, text):
        msg_box = HandPointerMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()


class AddUserWindow(QDialog):
    def __init__(self, on_add_user):
        super().__init__()
        self.on_add_user = on_add_user

        self.setWindowTitle("Inventory Management - Add User")
        self.setMinimumSize(600, 400)

        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inner_widget = QWidget()
        inner_widget.setFixedSize(450, 400)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        # ----------------- Username -----------------
        self.username_label = QLabel("Username:")
        self.username_label.setStyleSheet("font-size: 20px")
        self.username_input = QLineEdit()
        self.username_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        self.username_input.setFixedSize(300, 40)

        username_row = QHBoxLayout()
        username_row.setSpacing(10)
        username_row.addWidget(self.username_label)
        username_row.addWidget(self.username_input)
        form_layout.addLayout(username_row)

        # ----------------- Email -----------------
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("font-size: 20px")
        self.email_input = QLineEdit()
        self.email_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.email_input.setPlaceholderText("Enter Email")
        self.email_input.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        self.email_input.setFixedSize(300, 40)

        email_row = QHBoxLayout()
        email_row.setSpacing(10)
        email_row.addWidget(self.email_label)
        email_row.addWidget(self.email_input)
        form_layout.addLayout(email_row)

        # ----------------- Password -----------------
        self.password_label = QLabel("Password:")
        self.password_label.setStyleSheet("font-size: 20px")
        self.password_input = QLineEdit()
        self.password_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("QLineEdit { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")
        self.password_input.setFixedSize(300, 40)

        password_row = QHBoxLayout()
        password_row.setSpacing(10)
        password_row.addWidget(self.password_label)
        password_row.addWidget(self.password_input)
        form_layout.addLayout(password_row)

        # ----------------- Role -----------------
        self.role_label = QLabel("Role:")
        self.role_label.setStyleSheet("font-size: 20px")
        self.role_type = QComboBox()
        self.role_type.setCursor(Qt.CursorShape.PointingHandCursor)
        self.role_type.addItems(["Admin", "Manager", "Store Operator", "Viewer"])
        self.role_type.setFixedSize(300, 40)
        self.role_type.setStyleSheet("QComboBox { background-color: white; border: 2px solid gray; border-radius: 14px; padding: 0 8px; }")

        role_row = QHBoxLayout()
        role_row.setSpacing(10)
        role_row.addWidget(self.role_label)
        role_row.addWidget(self.role_type)
        form_layout.addLayout(role_row)

        # Align label widths
        for label in [self.username_label, self.email_label, self.password_label, self.role_label]:
            label.setFixedWidth(100)

        # ----------------- Register Button -----------------
        self.update_button = QPushButton("Register")
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
        self.update_button.clicked.connect(self.handle_register)

        button_row = QHBoxLayout()
        button_row.addWidget(self.update_button)
        button_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addLayout(button_row)

        inner_widget.setLayout(form_layout)
        outer_layout.addWidget(inner_widget)
        self.setLayout(outer_layout)

    def handle_register(self):
        if not self.username_input.text():
            self.show_warning("Please enter username!")
            return
        if not self.email_input.text():
            self.show_warning("Please enter email!")
            return
        if not self.password_input.text():
            self.show_warning("Please enter password!")
            return
        if not self.role_type.currentText():
            self.show_warning("Please select role!")
            return

        response = requests.post(
            f"{SERVER_URL}/add_user",
            json={
                "uName": self.username_input.text(),
                "uEmail": self.email_input.text(),
                "uPwd": self.password_input.text(),
                "uRole": self.role_type.currentText()
            }
        )
        if response.ok:
            if self.on_add_user:
                self.on_add_user()
            self.close()

    def show_warning(self, text):
        msg_box = HandPointerMessageBox()
        msg_box.setWindowTitle("Warning")
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ManageUsersWindow()
    window.setStyleSheet("background-color: #add8e6;")
    window.showMaximized()
    sys.exit(app.exec())
