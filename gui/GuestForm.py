from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QPushButton, QLabel, QMessageBox, QDateEdit, 
                              QCheckBox, QScrollArea, QFrame)
from PySide6.QtCore import QDateTime
from database import Session, Guest, Roommate

class RoommateWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(1)

        # ФИО сожителя
        self.surname = QLineEdit()
        self.surname.setPlaceholderText("Фамилия сожителя")
        layout.addWidget(self.surname)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Имя сожителя")
        layout.addWidget(self.name)

        self.father_name = QLineEdit()
        self.father_name.setPlaceholderText("Отчество сожителя")
        layout.addWidget(self.father_name)

        # Дата рождения сожителя
        birthday_layout = QHBoxLayout()
        self.birthday = QDateEdit()
        self.birthday.setDateTime(QDateTime.currentDateTime())
        birthday_layout.addWidget(QLabel("Дата рождения:"))
        birthday_layout.addWidget(self.birthday)
        layout.addLayout(birthday_layout)

        # Опции питания и размещения
        self.dinner = QCheckBox("Ужин")
        layout.addWidget(self.dinner)

        self.breakfast = QCheckBox("Завтрак")
        layout.addWidget(self.breakfast)

        self.extra_place = QCheckBox("Дополнительное место")
        layout.addWidget(self.extra_place)

        self.setLayout(layout)

    def get_data(self):
        return {
            'surname': self.surname.text(),
            'name': self.name.text(),
            'father_name': self.father_name.text(),
            'birthday': self.birthday.dateTime().toPython(),
            'dinner': self.dinner.isChecked(),
            'breakfast': self.breakfast.isChecked(),
            'place': self.extra_place.isChecked()
        }

class GuestForm(QWidget):
    def __init__(self):
        super().__init__()
        self.session = Session()
        self.roommates = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Добавление гостя")
        self.setGeometry(100, 100, 500, 800)

        main_layout = QVBoxLayout()

        # Создаем область прокрутки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

        # ФИО гостя
        guest_group = QVBoxLayout()
        guest_group.addWidget(QLabel("Данные гостя:"))

        self.surname = QLineEdit()
        self.surname.setPlaceholderText("Фамилия")
        guest_group.addWidget(self.surname)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Имя")
        guest_group.addWidget(self.name)

        self.father_name = QLineEdit()
        self.father_name.setPlaceholderText("Отчество")
        guest_group.addWidget(self.father_name)

        # Телефон
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("Номер телефона")
        guest_group.addWidget(self.phone)

        # Дата рождения
        birthday_layout = QHBoxLayout()
        self.birthday = QDateEdit()
        self.birthday.setDateTime(QDateTime.currentDateTime())
        birthday_layout.addWidget(QLabel("Дата рождения:"))
        birthday_layout.addWidget(self.birthday)
        guest_group.addLayout(birthday_layout)

        # Место рождения
        self.birth_place = QLineEdit()
        self.birth_place.setPlaceholderText("Место рождения")
        guest_group.addWidget(self.birth_place)

        # Паспортные данные
        self.seria_passport = QLineEdit()
        self.seria_passport.setPlaceholderText("Серия паспорта")
        guest_group.addWidget(self.seria_passport)

        self.number_passport = QLineEdit()
        self.number_passport.setPlaceholderText("Номер паспорта")
        guest_group.addWidget(self.number_passport)

        self.who_issued_passport = QLineEdit()
        self.who_issued_passport.setPlaceholderText("Кем выдан паспорт")
        guest_group.addWidget(self.who_issued_passport)

        # Адрес
        self.address = QLineEdit()
        self.address.setPlaceholderText("Адрес проживания")
        guest_group.addWidget(self.address)

        layout.addLayout(guest_group)

        # Контейнер для сожителей
        self.roommates_container = QVBoxLayout()
        layout.addWidget(QLabel("Сожители:"))
        layout.addLayout(self.roommates_container)

        # Кнопка добавления сожителя
        add_roommate_btn = QPushButton("Добавить сожителя")
        add_roommate_btn.clicked.connect(self.add_roommate)
        layout.addWidget(add_roommate_btn)

        # Кнопки сохранения/отмены
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_guest_and_roommates)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def add_roommate(self):
        roommate_widget = RoommateWidget()
        self.roommates.append(roommate_widget)
        self.roommates_container.addWidget(roommate_widget)

    def save_guest_and_roommates(self):
        try:
            # Создаем гостя
            new_guest = Guest(
                surname=self.surname.text(),
                name=self.name.text(),
                father_name=self.father_name.text(),
                number=self.phone.text(),
                birthday=self.birthday.dateTime().toPython(),
                birth_place=self.birth_place.text(),
                seria_passport=int(self.seria_passport.text()),
                number_passport=int(self.number_passport.text()),
                who_issued_passport=self.who_issued_passport.text(),
                residential_address=self.address.text()
            )
            self.session.add(new_guest)
            self.session.flush()  # Чтобы получить id гостя

            # Создаем сожителей и связываем их с гостем
            for roommate_widget in self.roommates:
                data = roommate_widget.get_data()
                if data['surname'] and data['name']:  # Проверяем, что основные поля заполнены
                    new_roommate = Roommate(
                        surname=data['surname'],
                        name=data['name'],
                        father_name=data['father_name'],
                        birthday=data['birthday'],
                        dinner=data['dinner'],
                        breakfast=data['breakfast'],
                        place=data['place'],
                        guest_id=new_guest.id  # Связываем сожителя с гостем
                    )
                    self.session.add(new_roommate)

            self.session.commit()
            QMessageBox.information(self, "Успех", "Гость и сожители успешно сохранены")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении данных: {str(e)}")
            self.session.rollback() 