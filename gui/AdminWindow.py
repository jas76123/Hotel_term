from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from .ReservationWindow import ReservationForm
from .RoomForm import RoomForm
from .GuestForm import GuestForm

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель администратора")
        self.setGeometry(100, 100, 300, 200)

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

    def show_reservation_form(self):
        self.reservation_form = ReservationForm()
        self.reservation_form.show()

    def show_room_form(self):
        self.room_form = RoomForm()
        self.room_form.show()

    def show_guest_form(self):
        self.guest_form = GuestForm()
        self.guest_form.show() 