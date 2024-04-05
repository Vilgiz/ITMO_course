import socket
import time
import asyncio
import threading

class RobotClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        while True:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
                print("Подключение к серверу установлено.")
                break
            except Exception as e:
                print(f"Ошибка подключения: {e}")
                print("Повторная попытка подключения через 5 секунд...")
                await asyncio.sleep(5)
                continue

    async def send_message(self, message):
        try:
            self.writer.write(message.encode())
            await self.writer.drain()
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")

    async def receive_message(self):
        while True:
            try:
                # Установка таймаута в 10 секунд
                data = await asyncio.wait_for(self.reader.read(1024), timeout=10.0)
                if not data:
                    print("Сервер закрыл соединение")
                    break
                print(f"Получено сообщение от сервера: {data.decode()}")
            except asyncio.exceptions.TimeoutError:
                print("Превышено время ожидания данных, продолжаем ожидание...")
                continue
            except Exception as e:
                print(f"Ошибка при получении сообщения: {e}")
                break
            await asyncio.sleep(1)


if __name__ == "__main__":
    async def start_client():
        robot_client = RobotClient('127.0.0.1', 48569)
        await robot_client.connect()
        asyncio.create_task(robot_client.receive_message())
        i = 0
        await robot_client.receive_message()
        while True:
            if i == 10:
                await robot_client.send_message("coord")
                i = 0
            i += 1
            await asyncio.sleep(1)

    asyncio.run(start_client())
