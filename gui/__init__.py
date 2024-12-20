from PySide6.QtWidgets import QApplication
import sys
from .LoginWindow import LoginForm


def show_login_window(service):
    app = QApplication(sys.argv)
    window = LoginForm(service)
    window.show()
    sys.exit(app.exec())