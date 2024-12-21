from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Base(DeclarativeBase):
    pass

from .models import User, Role, Cleaning,\
      Floor, Room, Category, Reservation,\
          Roommate, Payment, Reservation_service,\
              Service, Guest

eng = create_engine('sqlite:///DataBase.db')
Session = sessionmaker(bind=eng)

def initialize_roles():
    session = Session()
    try:
        # Проверяем и создаем роли
        roles = [
            {'name': 'Администратор', 'id': 1},
            {'name': 'Горничная', 'id': 2}
        ]
        
        for role_data in roles:
            role = session.query(Role).filter_by(name=role_data['name']).first()
            if not role:
                role = Role(id=role_data['id'], name=role_data['name'])
                session.add(role)
        session.commit()
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
        session.rollback()
    finally:
        session.close()

def create_db():
    Base.metadata.create_all(bind=eng)
    initialize_roles()