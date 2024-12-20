from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QPushButton, QComboBox, QDateEdit, QLabel, QMessageBox)
from PySide6.QtCore import QDateTime
from database import Session, Room, Guest, Reservation, Roommate

class ReservationForm(QWidget):
    def __init__(self):
        super().__init__()
        self.session = Session()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Создание брони")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        # Выбор гостя
        guest_layout = QHBoxLayout()
        self.guest_combo = QComboBox()
        self.refresh_guests()
        guest_layout.addWidget(QLabel("Гость:"))
        guest_layout.addWidget(self.guest_combo)
        layout.addLayout(guest_layout)

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

    def create_reservation(self):
        try:
            guest_id = self.guest_combo.currentData()
            room_id = self.room_combo.currentData()
            check_in = self.check_in_date.dateTime().toPython()
            check_out = self.check_out_date.dateTime().toPython()

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
            QMessageBox.information(self, "Успех", "Бронь успешно создана")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании брони: {str(e)}")
            self.session.rollback() 