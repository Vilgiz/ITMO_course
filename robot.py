import socket


class Robot:

    def __init__(self):
        self.host = '192.168.0.21'
        self.port = 48569
        self.received_message = ""
        self.is_moving = False
        self.coord_add = False

    def open_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        print(f"Сервер слушает на {self.host}:{self.port}")
        self.server_socket.listen(1)
        self.client_socket, client_address = self.server_socket.accept()
        print(f"Подключен клиент {client_address}")

    def send_message(self, message):
        self.client_socket.sendall(message.encode())

    def receive_message(self):
        data = self.client_socket.recv(1024)
        return data.decode()

    def cast_message(self, command, cX, cY, angle):
        self.message = ""
        self.message = f"{command};{cX};{cY};{angle};"

    def close_socket(self):
        self.client_socket.close()
        self.server_socket.close()


if __name__ == "__main__":
    robot = Robot()
    try:
        robot.open_socket()
        robot.cast_message("answer;", "100", "150", "angle")
        robot.send_message(robot.message)
        received_message = robot.receive_message()
        print(f"Получено сообщение от клиента: {received_message}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        robot.close_socket()
