from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QPushButton, QComboBox, QDateEdit, QLabel, QMessageBox,
                              QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import QDateTime
from database import Session, Room, Guest, Reservation, Roommate
from database.models import update_room_status
from datetime import datetime


class ReservationForm(QWidget):
    def __init__(self):
        super().__init__()
        self.session = Session()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Создание брони")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Выбор гостя
        guest_layout = QHBoxLayout()
        self.guest_combo = QComboBox()
        self.refresh_guests()
        guest_layout.addWidget(QLabel("Гость:"))
        guest_layout.addWidget(self.guest_combo)
        layout.addLayout(guest_layout)

        # Таблица сожителей
        roommates_label = QLabel("Сожители:")
        layout.addWidget(roommates_label)
        
        self.roommates_table = QTableWidget()
        self.roommates_table.setColumnCount(5)
        self.roommates_table.setHorizontalHeaderLabels([
            "ФИО", "Дата рождения", "Завтрак", "Ужин", "Доп. место"
        ])
        self.roommates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.roommates_table)

        # Выбор номера
        room_layout = QHBoxLayout()
        self.room_combo = QComboBox()
        self.refresh_rooms()
        room_layout.addWidget(QLabel("Номер:"))
        room_layout.addWidget(self.room_combo)
        layout.addLayout(room_layout)

        # Дата заселения
        check_in_layout = QHBoxLayout()
        self.check_in_date = QDateEdit()
        self.check_in_date.setDateTime(QDateTime.currentDateTime())
        check_in_layout.addWidget(QLabel("Дата заселения:"))
        check_in_layout.addWidget(self.check_in_date)
        layout.addLayout(check_in_layout)

        # Дата выселения
        check_out_layout = QHBoxLayout()
        self.check_out_date = QDateEdit()
        self.check_out_date.setDateTime(QDateTime.currentDateTime().addDays(1))
        check_out_layout.addWidget(QLabel("Дата выселения:"))
        check_out_layout.addWidget(self.check_out_date)
        layout.addLayout(check_out_layout)

        # Кнопка создания брони
        self.create_button = QPushButton("Создать бронь")
        self.create_button.clicked.connect(self.create_reservation)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

        # Подключаем обновление таблицы сожителей при выборе гостя
        self.guest_combo.currentIndexChanged.connect(self.update_roommates_table)

    def refresh_guests(self):
        self.guest_combo.clear()
        guests = self.session.query(Guest).all()
        for guest in guests:
            self.guest_combo.addItem(f"{guest.surname} {guest.name}", guest.id)

    def refresh_rooms(self):
        self.room_combo.clear()
        rooms = self.session.query(Room).all()
        for room in rooms:
            self.room_combo.addItem(f"Номер {room.number}", room.id)

    def update_roommates_table(self):
        guest_id = self.guest_combo.currentData()
        if not guest_id:
            return

        # Получаем сожителей для выбранного гостя
        roommates = self.session.query(Roommate).filter(
            Roommate.guest_id == guest_id
        ).all()

        self.roommates_table.setRowCount(len(roommates))
        
        for row, roommate in enumerate(roommates):
            # ФИО
            fio = f"{roommate.surname} {roommate.name} {roommate.father_name}"
            self.roommates_table.setItem(row, 0, QTableWidgetItem(fio))
            
            # Дата рождения
            birth_date = roommate.birthday.strftime("%d.%m.%Y") if roommate.birthday else "-"
            self.roommates_table.setItem(row, 1, QTableWidgetItem(birth_date))
            
            # Завтрак
            breakfast = "Да" if roommate.breakfast else "Нет"
            self.roommates_table.setItem(row, 2, QTableWidgetItem(breakfast))
            
            # Ужин
            dinner = "Да" if roommate.dinner else "Нет"
            self.roommates_table.setItem(row, 3, QTableWidgetItem(dinner))
            
            # Дополнительное место
            extra_place = "Да" if roommate.place else "Нет"
            self.roommates_table.setItem(row, 4, QTableWidgetItem(extra_place))

    def create_reservation(self):
        try:
            guest_id = self.guest_combo.currentData()
            room_id = self.room_combo.currentData()
            check_in = self.check_in_date.dateTime().toPython()
            check_out = self.check_out_date.dateTime().toPython()
            current_date = datetime.now().date()

            # Проверяем статус уборки номера
            room = self.session.query(Room).get(room_id)
            
            # Проверяем, является ли дата заезда сегодняшней
            is_today = check_in.date() == current_date
            
            # Если заезд сегодня и номер требует уборки - запрещаем бронирование
            if is_today and room.cleaning_status == "Требует уборки":
                QMessageBox.warning(self, "Ошибка", 
                    "Этот номер требует уборки и не может быть забронирован!")
                return

            # Проверяем, не пересекается ли новая бронь с существующими
            existing_reservation = self.session.query(Reservation).filter(
                Reservation.room_id == room_id,
                Reservation.check_out >= check_in,
                Reservation.check_in <= check_out
            ).first()

            if existing_reservation:
                QMessageBox.warning(self, "Ошибка", 
                    "На эти даты номер уже забронирован!")
                return

            # Получаем ID сожителей для выбранного гостя
            roommates = self.session.query(Roommate).filter(
                Roommate.guest_id == guest_id
            ).all()
            roommate_ids = ','.join([str(r.id) for r in roommates]) if roommates else None

            new_reservation = Reservation(
                guest_id=guest_id,
                room_id=room_id,
                reservation_date=QDateTime.currentDateTime().toPython(),
                check_in=check_in,
                check_out=check_out,
                roommate_id=roommate_ids
            )

            self.session.add(new_reservation)
            self.session.commit()
            
            # Обновляем статусы номеров сразу после создания брони
            update_room_status()
            
            QMessageBox.information(self, "Успех", "Бронь успешно создана")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании брони: {str(e)}")
            self.session.rollback() 