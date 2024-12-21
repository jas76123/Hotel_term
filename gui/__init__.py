from PySide6.QtWidgets import QApplication
import sys
from .LoginWindow import LoginForm


def show_login_window(service):
    window = LoginForm(service)
    window.show()