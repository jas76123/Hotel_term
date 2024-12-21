from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QTableWidget, QTableWidgetItem, 
                              QHeaderView, QComboBox, QMessageBox, QLabel)
from PySide6.QtCore import Qt, QTimer
from database import Session, Room, Cleaning, User
from datetime import datetime, timedelta

class MaidWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.session = Session()
        self.user_id = user_id
        self.current_user = self.session.query(User).get(user_id)
        self.setup_ui()
        self.load_cleaning_schedule()
        
        # Обновление каждые 5 минут
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.load_cleaning_schedule)
        self.update_timer.start(300000)

    def setup_ui(self):
        self.setWindowTitle(f"График уборки - {self.current_user.login}")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Фильтры
        filter_layout = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все статусы", "Убран", "Требует уборки"])
        self.status_filter.currentTextChanged.connect(self.load_cleaning_schedule)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)

        # Таблица графика уборки
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Номер", "Этаж", "Статус уборки", 
            "Последняя уборка", "Горничная", "Действия"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_cleaning_schedule)
        buttons_layout.addWidget(refresh_btn)
        
        layout.addLayout(buttons_layout)

    def load_cleaning_schedule(self):
        try:
            # Получаем все номера
            query = self.session.query(Room)
            
            # Применяем фильтр по статусу
            status_filter = self.status_filter.currentText()
            if status_filter != "Все статусы":
                query = query.filter(Room.cleaning_status == status_filter)
            
            rooms = query.all()
            
            self.table.setRowCount(0)
            for room in rooms:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Последняя уборка
                last_cleaning = self.session.query(Cleaning)\
                    .filter(Cleaning.floor_id == room.floor_id)\
                    .order_by(Cleaning.date.desc())\
                    .first()
                
                # Заполняем данные
                self.table.setItem(row, 0, QTableWidgetItem(str(room.number)))
                self.table.setItem(row, 1, QTableWidgetItem(str(room.floor.number)))
                self.table.setItem(row, 2, QTableWidgetItem(room.cleaning_status))
                
                if last_cleaning:
                    self.table.setItem(row, 3, 
                        QTableWidgetItem(last_cleaning.date.strftime("%d.%m.%Y %H:%M")))
                    self.table.setItem(row, 4, 
                        QTableWidgetItem(last_cleaning.maid.login))
                else:
                    self.table.setItem(row, 3, QTableWidgetItem("Нет данных"))
                    self.table.setItem(row, 4, QTableWidgetItem("-"))
                
                # Кнопка действия
                action_btn = QPushButton("Убрать")
                action_btn.clicked.connect(lambda checked, r=room.id: self.mark_as_cleaned(r))
                self.table.setCellWidget(row, 5, action_btn)
                
                # Подсветка строк, требующих уборки
                if room.cleaning_status == "Требует уборки":
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(Qt.yellow)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке графика: {str(e)}")

    def mark_as_cleaned(self, room_id):
        try:
            room = self.session.query(Room).get(room_id)
            if room:
                # Создаем запись об уборке
                cleaning = Cleaning(
                    date=datetime.now(),
                    maid_id=self.user_id,
                    floor_id=room.floor_id
                )
                self.session.add(cleaning)
                
                # Обновляем статус номера
                room.cleaning_status = "Убран"
                
                self.session.commit()
                self.load_cleaning_schedule()
                QMessageBox.information(self, "Успех", "Уборка отмечена")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отметке уборки: {str(e)}")
            self.session.rollback() 