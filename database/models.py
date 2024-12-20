from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy import String, Boolean, DateTime, Integer, Column, ForeignKey

class User(Base):
    __tablename__ = 'Пользователь'
    id = Column('Код_пользователя', Integer, primary_key=True)
    is_block = Column('Заблокирован', Boolean)
    last_login = Column('Последний_вход', DateTime)
    login = Column('Логин', String(255), nullable=False)
    password = Column('Пароль', String(64), nullable=False)
    role_id = Column('Роль', ForeignKey('Роль.Код_роли'))
    cout_fail_try = Column('КоличествоНеверныхПопыток', Integer, default=0)
    
    role = relationship('Role', back_populates='users')
    cleanings = relationship('Cleaning', back_populates='maid')

class Role(Base):
    __tablename__ = 'Роль'
    id = Column('Код_роли', Integer, primary_key=True)
    name = Column('Название', String(100), nullable=False)
    users = relationship("User", back_populates='role')

class Cleaning(Base):
    __tablename__ = 'Уборка_номера'
    id = Column('Код_уборки', Integer, primary_key=True)
    date = Column('Дата_уборки', DateTime)
    maid_id = Column('Горничная', ForeignKey('Пользователь.Код_пользователя'))
    maid = relationship("User", back_populates='cleanings')
    floor_id = Column('Этаж', ForeignKey('Этаж.Код_этажа'))
    floor = relationship("Floor", back_populates='cleanings')

class Floor(Base):
    __tablename__ = 'Этаж'
    id = Column('Код_этажа', Integer, primary_key=True)
    number = Column('Номер_этажа', Integer)
    cleanings = relationship("Cleaning", back_populates='floor')
    rooms = relationship("Room", back_populates='floor')

class Room(Base):
    __tablename__ = 'Номер'
    id = Column('Код_номера', Integer, primary_key=True)
    number = Column('Номер', Integer)
    room_status = Column('Статус_номера', String)
    cleaning_status = Column('Статус_уборки', String)
    floor_id = Column('Этаж', ForeignKey('Этаж.Код_этажа'))
    floor = relationship("Floor", back_populates='rooms')
    category_id = Column('Категория', ForeignKey('Категория.Код_категории'))
    category = relationship("Category", back_populates='rooms')
    reservations = relationship("Reservation", back_populates='room')

class Category(Base):
    __tablename__ = 'Категория'
    id = Column('Код_категории', Integer, primary_key=True)
    name = Column('Название', String)
    price = Column('Цена', Integer) 
    description = Column('Описание', String)
    rooms = relationship("Room", back_populates='category')

class Reservation(Base):
    __tablename__ = 'Бронь'
    id = Column('Код_брони', Integer, primary_key=True)
    guest_id = Column('Гость', Integer, ForeignKey('Гость.Код_гостя'))
    room_id = Column('Номер', Integer, ForeignKey('Номер.Код_номера'))
    reservation_date = Column('Дата_заселения', DateTime)
    check_in = Column('Дата_заселение', DateTime)
    check_out = Column('Дата_выселения', DateTime)
    roommate_id = Column('Сожитель', String)
    payment_id = Column('Оплата', Integer, ForeignKey('Оплата.Код_оплаты'))
    room = relationship("Room", back_populates='reservations')
    guest = relationship("Guest", back_populates='reservations')
    payment = relationship("Payment", back_populates='reservations')
    reservations_services = relationship("Reservation_service", back_populates='reservation')

class Roommate(Base):
    __tablename__ = 'Сожитель'
    id = Column('Код_сожителя', Integer, primary_key=True)
    surname = Column('Фамилия', String)
    name = Column('Имя', String)
    father_name = Column('Отчество', String)
    dinner = Column('Ужин', Boolean)
    breakfast = Column('Завтрак', Boolean)
    birthday = Column('Дата_рождения', DateTime)
    place = Column('Дополнительное_место', Boolean)
    guest_id = Column('Код_гостя', Integer, ForeignKey('Гость.Код_гостя'))
    guest = relationship("Guest", back_populates="roommates")

class Payment(Base):
    __tablename__ = 'Оплата'
    id = Column('Код_оплаты', Integer, primary_key=True)
    final_sum = Column('Сумма', Integer)
    date = Column('Дата_оплаты', DateTime)
    reservations = relationship("Reservation", back_populates='payment')

class Reservation_service(Base):
    __tablename__ = 'Бронь_услуги'
    id = Column('Код_Брони_услуги', Integer, primary_key=True)
    reservation_id = Column('Бронь', ForeignKey('Бронь.Код_брони'))
    service_id = Column('Услуги', ForeignKey('Услуги.Код_услуги'))
    reservation = relationship("Reservation", back_populates='reservations_services') 
    services = relationship("Service", back_populates='reservations_services')

class Service(Base):
    __tablename__ = 'Услуги'
    id = Column('Код_услуги', Integer, primary_key=True)
    name = Column('Название', String)
    description = Column('Описание', String)
    price = Column('Цена', Integer) 
    reservations_services = relationship("Reservation_service", back_populates='services')

class Guest(Base):
    __tablename__ = 'Гость'
    id = Column('Код_гостя', Integer, primary_key=True)
    surname = Column('Фамилия', String)
    name = Column('Имя', String)
    father_name = Column('Отчество', String)
    number = Column('Номер', String)
    birthday = Column('Дата_рождения', DateTime)
    birth_place = Column('Место_рождения', String)
    seria_passport = Column('Серия_паспорта', Integer)
    number_passport = Column('Номер_паспорта', Integer)
    who_issued_passport = Column('Кем_выдан_паспорт', String)
    residential_address = Column('Адрес_проживания', String)
    roommates = relationship("Roommate", back_populates="guest")
    reservations = relationship("Reservation", back_populates='guest')
