import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QTableWidget, QTableWidgetItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import RTS

class DatabaseWindow(QDialog):
    """Окно для просмотра записей базы данных.

    Это окно позволяет пользователю просматривать записи из базы данных RTS.
    """

    def __init__(self):
        """Инициализация окна DatabaseWindow."""
        super().__init__()
        self.setWindowTitle("Просмотр базы данных")
        self.setGeometry(100, 100, 600, 400)

        self.table = QTableWidget(self)
        self.table.setGeometry(50, 50, 500, 300)

        self.populate_table()

    def populate_table(self):
        """Заполнение таблицы данными из базы данных."""
        # Создание соединения с базой данных
        engine = create_engine('mysql://root:cf79db54Q@127.0.0.1/RTS')
        Session = sessionmaker(bind=engine)
        session = Session()

        # Получение данных из базы данных
        data = session.query(RTS).all()

        # Установка количества строк и столбцов в таблице
        self.table.setRowCount(len(data))
        self.table.setColumnCount(7)  # количество колонок

        # Установка заголовков столбцов таблицы
        column_headers = ["Номер детали", "Тип детали", "Количество деталей", "Время начала сортировки", "Время окончания сортировки", "Количество дефектных деталей", "Количество ошибок"]
        self.table.setHorizontalHeaderLabels(column_headers)

        # Заполнение таблицы данными из запроса
        for row, record in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(record.part_number)))
            self.table.setItem(row, 1, QTableWidgetItem(str(record.detail_type)))
            self.table.setItem(row, 2, QTableWidgetItem(str(record.detail_count)))
            self.table.setItem(row, 3, QTableWidgetItem(str(record.sorting_start_time)))
            self.table.setItem(row, 4, QTableWidgetItem(str(record.sorting_end_time)))
            self.table.setItem(row, 5, QTableWidgetItem(str(record.defective_count)))
            self.table.setItem(row, 6, QTableWidgetItem(str(record.error_count)))

        # Закрытие сессии
        session.close()

if __name__ == "__main__":
    pass
