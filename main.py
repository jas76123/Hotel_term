from database import create_db, Session, User
from gui import show_login_window
from datetime import datetime
from PySide6.QtWidgets import QApplication
import sys
from database.models import update_room_status, update_cleaning_status
from database.init_data import add_hotel_services


class LoginService:
    def __init__(self):
        self.session = Session()
        self.current_user = None

    def login(self, login, password):
        try:
            user = self.session.query(User).filter(User.login == login).first()
            
            if not user: 
                return "Пользователь не найден"
            elif user.last_login and (datetime.now() - user.last_login).days >= 30:
                user.is_block = True
                self.session.commit()
                return "Пользователь заблокирован"
            elif user.is_block:
                return "Пользователь заблокирован"
            elif user.password != password:
                user.cout_fail_try += 1
                if user.cout_fail_try == 3:
                    user.is_block = True
                self.session.commit()
                return "Пароль не верный"
            else:
                user.cout_fail_try = 0 
                user.last_login = datetime.now()
                self.session.commit()
                self.current_user = user
                return "Всё гуд"
        except Exception as e:
            print(f"Ошибка при авторизации: {e}")
            return "Ошибка авторизации"

    def get_current_user(self):
        return self.current_user


def main():
    try:
        app = QApplication(sys.argv)
        create_db()
        add_hotel_services()  # Добавляем базовые услуги
        update_room_status()  # Обновляем статусы при запуске
        update_cleaning_status()  # Добавляем обновление статусов уборки
        
        # Создаем таймер для периодического обновления статусов уборки
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(update_cleaning_status)
        timer.start(3600000)  # Обновление каждый час
        
        login_service = LoginService()
        from gui.LoginWindow import LoginForm
        window = LoginForm(login_service)
        window.show()
        
        return app.exec()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())