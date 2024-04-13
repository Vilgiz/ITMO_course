import asyncio
import threading
from datetime import datetime
from database import RTS, PartyManager


class Robot:
    """Класс для работы с сервером робота."""

    def __init__(self, host, port):
        """Инициализация объекта Robot.

        Args:
            host (str): Адрес сервера.
            port (int): Порт сервера.
        """
        self.host = host
        self.port = port
        self.writer = None
        self.manager = PartyManager()

    async def handle_client(self, reader, writer):
        """Обработчик клиентских подключений.

        Args:
            reader: Объект для чтения данных от клиента.
            writer: Объект для записи данных клиенту.
        """
        self.writer = writer  # Сохраняем объект writer для отправки сообщений
        while True:
            try:
                data = await asyncio.wait_for(reader.read(1024), timeout=0.5)
            except asyncio.exceptions.TimeoutError:
                print("Таймаут ожидания данных")
                continue
            if not data:
                print("Клиент отключился")
                break
            message = data.decode()
            print(f"Получено сообщение от клиента: {message}")
            if message == "quit":
                break
            # Обработка сообщения и добавление данных в базу
            data_dict = self.parse_message(message)
            if data_dict:
                self.manager.add_party(**data_dict)
            # response = self.process_message(message)
            # writer.write(response.encode())
            # await writer.drain()
        print("Закрытие соединения")
        writer.close()

    def parse_message(self, message):
        """Парсинг сообщения и преобразование в словарь данных.

        Args:
            message (str): Сообщение от клиента.

        Returns:
            dict: Словарь данных из сообщения.
        """
        pairs = message.strip().split(', ')
        data_dict = {}  # Создаем словарь для хранения данных текущей записи
        for pair in pairs:
            key, value = pair.split(': ')
            if key == 'start_time':
                # Преобразуем строку в объект datetime
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif key == 'stop_time':
                # Преобразуем строку в объект time
                value = datetime.strptime(value, "%H:%M:%S").time()
            else:
                # Преобразуем строку в целое число
                value = int(value)
            data_dict[key] = value
        return data_dict

    def process_message(self, message):
        """Обработка сообщения.

        Args:
            message (str): Сообщение от клиента.

        Returns:
            str: Ответ сервера.
        """
        return "Сообщение получено"

    def send_message(self, message):
        """Отправка сообщения клиенту.

        Args:
            message (str): Сообщение для отправки.
        """
        if self.writer is None:
            print("Ошибка: нет активного соединения")
            return
        try:
            self.writer.write(message.encode())
            self.writer.drain()
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")

    async def start_server(self):
        """Запуск асинхронного сервера."""
        while True:
            try:
                server = await asyncio.start_server(self.handle_client, self.host, self.port)

                print(f"Сервер слушает на {self.host}:{self.port}")

                async with server:
                    await server.serve_forever()
            except Exception as e:
                print(f"Ошибка сервера: {e}")
                print("Повторная попытка запуска сервера через 5 секунд...")
                await asyncio.sleep(5)


def run_server():
    """Запуск сервера в отдельном потоке."""
    asyncio.run(Robot('127.0.0.1', 48569).start_server())


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()
