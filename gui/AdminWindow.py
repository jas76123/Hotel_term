from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import QTimer
from .ReservationWindow import ReservationForm
from .RoomForm import RoomForm
from .GuestForm import GuestForm
from .PaymentWindow import PaymentWindow
from database.models import update_room_status
from database import Session, Reservation
from .SelectReservationWindow import SelectReservationWindow

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setGeometry(100, 100, 300, 200)
        self.session = Session()

        # Создаем таймер для периодического обновления статусов
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_statuses)
        self.update_timer.start(60000)  # Обновление каждую минуту
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Кнопка создания новой брони
        create_reservation_btn = QPushButton("Создать бронь")
        create_reservation_btn.clicked.connect(self.show_reservation_form)
        layout.addWidget(create_reservation_btn)

        # Кнопка добавления номера
        add_room_btn = QPushButton("Добавить номер")
        add_room_btn.clicked.connect(self.show_room_form)
        layout.addWidget(add_room_btn)

        # Кнопка добавления гостя
        add_guest_btn = QPushButton("Добавить гостя")
        add_guest_btn.clicked.connect(self.show_guest_form)
        layout.addWidget(add_guest_btn)

        # Кнопка оплаты
        payment_btn = QPushButton("Оплата")
        payment_btn.clicked.connect(self.show_payment_form)
        layout.addWidget(payment_btn)

    def show_reservation_form(self):
        self.reservation_form = ReservationForm()
        self.reservation_form.show()

    def show_room_form(self):
        self.room_form = RoomForm()
        self.room_form.show()

    def show_guest_form(self):
        self.guest_form = GuestForm()
        self.guest_form.show()

    def show_payment_form(self):
        self.select_reservation_window = SelectReservationWindow()
        self.select_reservation_window.show()

    def update_statuses(self):
        """Периодическое обновление статусов номеров"""
        update_room_status() 