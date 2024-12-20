from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Base(DeclarativeBase): ...

from .models import User, Role, Cleaning,\
      Floor, Room, Category, Reservation,\
          Roommate, Payment, Reservation_service,\
              Service, Guest

eng = create_engine('sqlite:///DataBase.db')

Session = sessionmaker(eng)

def create_db():
    Base.metadata.create_all(bind=eng)