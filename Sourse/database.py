from sqlalchemy import create_engine, Column, Integer, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time

# Создание подключения к базе данных
engine = create_engine('mysql://root:cf79db54Q@127.0.0.1/RTS')
Session = sessionmaker(bind=engine)

# Базовый класс для моделей
Base = declarative_base()


class RTS(Base):
    """Модель данных для таблицы rtc в базе данных.

    Определяет структуру и типы данных столбцов таблицы.
    """

    __tablename__ = 'rtc'

    part_number = Column(Integer, primary_key=True)
    detail_type = Column(Integer)
    detail_count = Column(Integer)
    sorting_start_time = Column(DateTime, default=datetime.now)
    sorting_end_time = Column(Time)
    defective_count = Column(Integer)
    error_count = Column(Integer)

    def __init__(self, part_number, detail_type, detail_count, sorting_end_time, defective_count, error_count):
        """Инициализация новой записи.

        Args:
            part_number (int): Номер детали.
            detail_type (int): Тип детали.
            detail_count (int): Количество деталей.
            sorting_end_time (datetime.time): Время окончания сортировки.
            defective_count (int): Количество бракованных деталей.
            error_count (int): Количество ошибок.
        """
        self.part_number = part_number
        self.detail_type = detail_type
        self.detail_count = detail_count
        self.sorting_end_time = sorting_end_time
        self.defective_count = defective_count
        self.error_count = error_count


class PartyManager:
    """Менеджер для работы с данными о партиях."""

    def __init__(self):
        """Инициализация менеджера."""
        self.session = Session()

    def add_party(self, part_number, detail_type, detail_count, sorting_end_time, defective_count, error_count):
        """Добавление новой партии в базу данных.

        Args:
            part_number (int): Номер детали.
            detail_type (int): Тип детали.
            detail_count (int): Количество деталей.
            sorting_end_time (datetime.time): Время окончания сортировки.
            defective_count (int): Количество бракованных деталей.
            error_count (int): Количество ошибок.
        """
        new_party = RTS(part_number, detail_type, detail_count,
                        sorting_end_time, defective_count, error_count)
        self.session.add(new_party)
        self.session.commit()

    def get_party_by_id(self, party_id):
        """Получение данных о партии по её номеру.

        Args:
            party_id (int): Номер партии.

        Returns:
            RTS: Объект партии, если найден, иначе None.
        """
        party = self.session.query(RTS).filter_by(part_number=party_id).first()
        return party


if __name__ == "__main__":
    manager = PartyManager()

    # Добавление новой партии
    manager.add_party(part_number=3, detail_type=2, detail_count=100,
                      sorting_end_time=time(12, 30), defective_count=5, error_count=2)

    # Получение данных по номеру партии
    party_id = 2
    party = manager.get_party_by_id(party_id)
    if party:
        print("Данные по партии с номером", party_id)
        print("Номер партии:", party.part_number)
        print("Тип детали:", party.detail_type)
        print("Количество деталей:", party.detail_count)
        print("Время начала сортировки:", party.sorting_start_time)
        print("Время окончания сортировки:", party.sorting_end_time)
        print("Количество бракованных деталей:", party.defective_count)
        print("Количество ошибок:", party.error_count)
    else:
        print("Партия с номером", party_id, "не найдена")
