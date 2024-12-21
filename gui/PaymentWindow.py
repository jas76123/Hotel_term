from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QMessageBox, QTableWidget, 
                              QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from database import Session, Reservation, Service, Payment, Roommate
from datetime import datetime

class PaymentWindow(QWidget):
    def __init__(self, reservation_id):
        super().__init__()
        self.session = Session()
        self.reservation_id = reservation_id
        self.reservation = self.session.query(Reservation).get(reservation_id)
        self.setup_ui()
        self.calculate_total()

    def setup_ui(self):
        self.setWindowTitle("Оплата")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        # Информация о брони
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Гость: {self.reservation.guest.surname} {self.reservation.guest.name}"))
        info_layout.addWidget(QLabel(f"Номер: {self.reservation.room.number}"))
        info_layout.addWidget(QLabel(f"Период: {self.reservation.check_in.strftime('%d.%m.%Y')} - {self.reservation.check_out.strftime('%d.%m.%Y')}"))
        layout.addLayout(info_layout)

        # Таблица услуг и расчетов
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Услуга", "Количество дней", "Цена за день", "Количество человек", "Итого"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Итоговая сумма
        self.total_label = QLabel("Итого к оплате: 0 руб.")
        layout.addWidget(self.total_label)

        # Кнопки
        buttons_layout = QHBoxLayout()
        pay_button = QPushButton("Оплатить")
        pay_button.clicked.connect(self.process_payment)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(pay_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def calculate_total(self):
        total = 0
        days = (self.reservation.check_out - self.reservation.check_in).days
        roommates_count = len(self.get_roommates()) + 1  # +1 для основного гостя

        self.table.setRowCount(0)  # Очищаем таблицу

        # Стоимость номера
        room_price = self.reservation.room.category.price
        self.add_table_row("Проживание", days, room_price, 1, room_price * days)
        total += room_price * days

        # Услуги из брони
        for reservation_service in self.reservation.reservations_services:
            service = reservation_service.services
            service_total = service.price * days * roommates_count
            self.add_table_row(service.name, days, service.price, roommates_count, service_total)
            total += service_total

        # Услуги сожителей
        roommates = self.get_roommates()
        for roommate in roommates:
            if roommate.breakfast:
                breakfast_service = self.get_service_by_name("Завтрак")
                if breakfast_service:
                    service_total = breakfast_service.price * days
                    self.add_table_row(f"Завтрак ({roommate.surname})", days, 
                                     breakfast_service.price, 1, service_total)
                    total += service_total
            
            if roommate.dinner:
                dinner_service = self.get_service_by_name("Ужин")
                if dinner_service:
                    service_total = dinner_service.price * days
                    self.add_table_row(f"Ужин ({roommate.surname})", days, 
                                     dinner_service.price, 1, service_total)
                    total += service_total
            
            if roommate.place:
                extra_place = self.get_service_by_name("Дополнительное место")
                if extra_place:
                    service_total = extra_place.price * days
                    self.add_table_row(f"Доп. место ({roommate.surname})", days, 
                                     extra_place.price, 1, service_total)
                    total += service_total

        self.total_amount = total
        self.total_label.setText(f"Итого к оплате: {total} руб.")

    def add_table_row(self, service_name, days, price, people, total):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(service_name)))
        self.table.setItem(row, 1, QTableWidgetItem(str(days)))
        self.table.setItem(row, 2, QTableWidgetItem(str(price)))
        self.table.setItem(row, 3, QTableWidgetItem(str(people)))
        self.table.setItem(row, 4, QTableWidgetItem(str(total)))

    def get_roommates(self):
        if not self.reservation.roommate_id:
            return []
        roommate_ids = [int(id_) for id_ in self.reservation.roommate_id.split(',')]
        return self.session.query(Roommate).filter(Roommate.id.in_(roommate_ids)).all()

    def get_service_by_name(self, name):
        return self.session.query(Service).filter(Service.name == name).first()

    def process_payment(self):
        try:
            # Создаем запись об оплате
            payment = Payment(
                final_sum=self.total_amount,
                date=datetime.now()
            )
            self.session.add(payment)
            self.session.flush()  # Получаем ID платежа

            # Привязываем платеж к брони
            self.reservation.payment_id = payment.id
            
            self.session.commit()
            QMessageBox.information(self, "Успех", "Оплата проведена успешно")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проведении оплаты: {str(e)}")
            self.session.rollback() 