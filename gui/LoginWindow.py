import sys
from PySide6.QtWidgets import QApplication, QLineEdit, QWidget, QVBoxLayout, QPushButton, QMessageBox
from .AdminWindow import AdminWindow


class LoginForm(QWidget):
    def __init__(self, service):
        super().__init__()
        self.setWindowTitle("Окно Авторизации")
        self.setGeometry(100, 100, 300, 200)

        layout_login = QVBoxLayout()

        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText('Введите логин:')
        layout_login.addWidget(self.login_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Введите пароль:')
        self.password_input.setEchoMode(QLineEdit.Password)
        layout_login.addWidget(self.password_input)
         
        self.login_button = QPushButton('Войти', self)
        self.login_button.clicked.connect(self.login)
        layout_login.addWidget(self.login_button)

        self.Service = service

        self.setLayout(layout_login)

    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()
        result = self.Service.login(login, password)
        
        if result == "Всё гуд":
            # Проверяем, является ли пользователь администратором
            user = self.Service.get_current_user()
            if user and user.role.name == "Администратор":
                self.admin_window = AdminWindow()
                self.admin_window.show()
                self.close()
            else:
                QMessageBox.information(self, "", "Доступ запрещен")
        else:
            QMessageBox.information(self, "", result)
