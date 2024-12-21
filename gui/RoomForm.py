from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QPushButton, QSpinBox, QLabel, QMessageBox)
from database import Session, Room, Category, Floor

class RoomForm(QWidget):
    def __init__(self):
        super().__init__()
        self.session = Session()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Добавление номера")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        # Номер комнаты
        room_layout = QHBoxLayout()
        self.room_number = QSpinBox()
        self.room_number.setMinimum(1)
        self.room_number.setMaximum(999)
        room_layout.addWidget(QLabel("Номер:"))
        room_layout.addWidget(self.room_number)
        layout.addLayout(room_layout)

        # Этаж
        floor_layout = QHBoxLayout()
        self.floor_number = QSpinBox()
        self.floor_number.setMinimum(1)
        self.floor_number.setMaximum(99)
        floor_layout.addWidget(QLabel("Этаж:"))
        floor_layout.addWidget(self.floor_number)
        layout.addLayout(floor_layout)

        # Категория
        category_layout = QHBoxLayout()
        self.category_name = QLineEdit()
        category_layout.addWidget(QLabel("Категория:"))
        category_layout.addWidget(self.category_name)
        layout.addLayout(category_layout)

        # Цена
        price_layout = QHBoxLayout()
        self.price = QSpinBox()
        self.price.setMinimum(0)
        self.price.setMaximum(1000000)
        price_layout.addWidget(QLabel("Цена:"))
        price_layout.addWidget(self.price)
        layout.addLayout(price_layout)

        # Описание
        description_layout = QHBoxLayout()
        self.description = QLineEdit()
        description_layout.addWidget(QLabel("Описание:"))
        description_layout.addWidget(self.description)
        layout.addLayout(description_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_room)
        buttons_layout.addWidget(save_button)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(cancel_button)
        
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def save_room(self):
        try:
            # Получаем или создаем этаж
            floor = self.session.query(Floor).filter_by(
                number=self.floor_number.value()
            ).first()
            
            if not floor:
                floor = Floor(number=self.floor_number.value())
                self.session.add(floor)
                self.session.flush()

            # Получаем или создаем категорию
            category = self.session.query(Category).filter_by(
                name=self.category_name.text()
            ).first()
            
            if not category:
                category = Category(
                    name=self.category_name.text(),
                    price=self.price.value(),
                    description=self.description.text()
                )
                self.session.add(category)
                self.session.flush()

            # Создаем или обновляем номер
            room = self.session.query(Room).filter_by(
                number=self.room_number.value()
            ).first()
            
            if room:
                room.floor_id = floor.id
                room.category_id = category.id
            else:
                room = Room(
                    number=self.room_number.value(),
                    floor_id=floor.id,
                    category_id=category.id,
                    room_status='Свободен',  # Устанавливаем начальный статус
                    cleaning_status='Убран'   # Начальный статус уборки
                )
                self.session.add(room)

            self.session.commit()
            
            # Обновляем статусы номеров после сохранения
            from database.models import update_room_status
            update_room_status()
            
            QMessageBox.information(self, "Успех", "Номер успешно сохранен")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении номера: {str(e)}")
            self.session.rollback() 