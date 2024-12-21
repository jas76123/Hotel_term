from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QPushButton,
                              QTableWidgetItem, QHeaderView, QHBoxLayout)
from database import Session, Reservation
from datetime import datetime
from .PaymentWindow import PaymentWindow

class SelectReservationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.session = Session()
        self.setup_ui()
        self.load_reservations()

    def setup_ui(self):
        self.setWindowTitle("Выбор брони для оплаты")
        self.setGeometry(100, 100, 1000, 600)
        layout = QVBoxLayout()

        # Таблица броней
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Гость", "Номер", "Дата заезда", 
            "Дата выезда", "Статус оплаты", "Сумма"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        select_button = QPushButton("Перейти к оплате")
        select_button.clicked.connect(self.open_payment)
        buttons_layout.addWidget(select_button)
        
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_reservations)
        buttons_layout.addWidget(refresh_button)
        
        cancel_button = QPushButton("Закрыть")
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_reservations(self):
        # Получаем все брони
        reservations = self.session.query(Reservation)\
            .order_by(Reservation.check_in.desc())\
            .all()

        self.table.setRowCount(0)
        for reservation in reservations:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID брони
            self.table.setItem(row, 0, QTableWidgetItem(str(reservation.id)))
            
            # Гость
            guest_name = f"{reservation.guest.surname} {reservation.guest.name}"
            self.table.setItem(row, 1, QTableWidgetItem(guest_name))
            
            # Номер
            self.table.setItem(row, 2, QTableWidgetItem(str(reservation.room.number)))
            
            # Даты
            check_in = reservation.check_in.strftime("%d.%m.%Y")
            check_out = reservation.check_out.strftime("%d.%m.%Y")
            self.table.setItem(row, 3, QTableWidgetItem(check_in))
            self.table.setItem(row, 4, QTableWidgetItem(check_out))
            
            # Статус оплаты
            payment_status = "Оплачено" if reservation.payment_id else "Не оплачено"
            self.table.setItem(row, 5, QTableWidgetItem(payment_status))
            
            # Сумма (если есть оплата)
            amount = str(reservation.payment.final_sum) if reservation.payment else "-"
            self.table.setItem(row, 6, QTableWidgetItem(amount))

    def open_payment(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            reservation_id = int(self.table.item(current_row, 0).text())
            # Проверяем, не оплачена ли уже бронь
            reservation = self.session.query(Reservation).get(reservation_id)
            if reservation.payment_id:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Внимание", "Эта бронь уже оплачена!")
                return
                
            self.payment_window = PaymentWindow(reservation_id)
            self.payment_window.show()
            self.close() 