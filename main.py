from database import create_db, Session, User
from gui import show_login_window
from datetime import datetime


class LoginService:
    def __init__(self):
        self.session = Session()
        self.current_user = None

    def login(self, login, password):
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

    def get_current_user(self):
        return self.current_user


create_db()
show_login_window(
    LoginService()
)