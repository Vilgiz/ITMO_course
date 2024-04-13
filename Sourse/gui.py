import sys
import threading
import asyncio
import json
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QPushButton
import cv2
from image import Image
from robot import Robot
from database_show import DatabaseWindow


class VideoPlayer(QMainWindow):
    """Класс для создания приложения видеоплеера."""

    def __init__(self):
        """Инициализация видеоплеера."""
        super().__init__()
        self.camera = cv2.VideoCapture("Video_2.mp4")

        # Создание объекта робота для взаимодействия
        self.robot = Robot('127.0.0.1', 48569)

        # Инициализация параметров
        self.width_frame = None
        self.height_frame = None
        self.brigh_fac_value = 0
        self.threshold_3_value = 0
        self.threshold_2_value = 0
        self.blur_value = 0
        self.dilate_value = 0
        self.num_of_frame = 0
        self.start_flag = True

        # Создание графического интерфейса
        self.__init_main_window()
        self.__init_layouts()
        self.__init_widgets()
        self.__init_style()
        self.__init_sizes()
        self.__addition_widgets()
        self.__setting_layers()
        self.__settings()

    def __init_main_window(self):
        """Инициализация основного окна приложения."""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Video")
        self.resize(600, 600)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 150);")

    def __init_widgets(self):
        """Инициализация виджетов."""
        self.video_label = QLabel()

        # Создание слайдеров для настройки параметров обработки изображения
        self.brigh_fac_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_2_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_3_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.dilate_slider = QSlider(Qt.Orientation.Horizontal)

        # Создание кнопок управления
        self.start_button = QPushButton("Старт")
        self.stop_button = QPushButton("Стоп")
        self.continue_button = QPushButton("Продолжить")
        self.statisticks_button = QPushButton(f"Статистика\nкомплекса")
        self.auto_correction_button = QPushButton("Автокоррекция\nкамеры")

        self.detect_detail_label = QLabel("Обнаружено деталей:")

    def __init_layouts(self):
        """Инициализация компоновок виджетов."""
        self.main_layout = QHBoxLayout(self.central_widget)
        self.video_and_info_layout = QHBoxLayout()
        self.video_layout = QVBoxLayout()
        self.info_layout = QVBoxLayout()
        self.vid_info_and_dop_layout = QVBoxLayout()
        self.dop_layout = QHBoxLayout()
        self.calibration_layout = QVBoxLayout()

    def __addition_widgets(self):
        """Добавление виджетов на компоновки."""
        self.video_layout.addWidget(self.video_label)

        # Добавление виджетов настройки параметров
        self.calibration_layout.addWidget(self.brigh_fac_label)
        self.calibration_layout.addWidget(self.brigh_fac_slider)
        self.calibration_layout.addWidget(self.threshold_2_label)
        self.calibration_layout.addWidget(self.threshold_2_slider)
        self.calibration_layout.addWidget(self.threshold_3_label)
        self.calibration_layout.addWidget(self.threshold_3_slider)
        self.calibration_layout.addWidget(self.blur_label)
        self.calibration_layout.addWidget(self.blur_slider)
        self.calibration_layout.addWidget(self.dilate_label)
        self.calibration_layout.addWidget(self.dilate_slider)

        # Добавление кнопок управления
        self.dop_layout.addWidget(self.start_button)
        self.dop_layout.addWidget(self.stop_button)
        self.dop_layout.addWidget(self.continue_button)
        self.dop_layout.addWidget(self.statisticks_button)
        self.dop_layout.addWidget(self.auto_correction_button)

    def __setting_layers(self):
        """Настройка компоновок виджетов."""
        self.video_and_info_layout.addLayout(self.video_layout)
        self.video_and_info_layout.addLayout(self.info_layout)
        self.vid_info_and_dop_layout.addLayout(self.video_and_info_layout)
        self.vid_info_and_dop_layout.addLayout(self.dop_layout)
        self.main_layout.addLayout(self.vid_info_and_dop_layout)
        self.main_layout.addLayout(self.calibration_layout)

    def __settings(self):
        """Настройка начальных значений и обработчиков событий."""
        self.stop_button.clicked.connect(self.send_em_stop)
        self.continue_button.clicked.connect(self.send_continue)
        self.start_button.clicked.connect(self.send_start)
        self.statisticks_button.clicked.connect(self.show_database_window)

        # Маппинг слайдеров и их меток
        self.slider_label_mapping = {
            self.brigh_fac_slider: self.brigh_fac_label,
            self.threshold_3_slider: self.threshold_3_label,
            self.threshold_2_slider: self.threshold_2_label,
            self.blur_slider: self.blur_label,
            self.dilate_slider: self.dilate_label
        }

        for slider, label in self.slider_label_mapping.items():
            slider.setMinimum(0)
            slider.setMaximum(255)
            slider.valueChanged.connect(self.on_slider_value_changed)

        if self.start_flag:
            # Загрузка начальных значений из файла конфигурации
            with open('video_parametrs.json', 'r') as json_file:
                try:
                    data = json.load(json_file)
                except json.JSONDecodeError:
                    raise ValueError("Ошибка при чтении файла с данными.")

            # Установка начальных значений слайдеров
            self.brigh_fac_value = data.get('brigh', [])
            self.threshold_3_value = data.get('threshold_3', [])
            self.threshold_2_value = data.get('threshold_2', [])
            self.blur_value = data.get('blur', [])
            self.dilate_value = data.get('dilate', [])

            self.brigh_fac_slider.setValue(int(self.brigh_fac_value*255/3))
            self.threshold_3_slider.setValue(self.threshold_3_value)
            self.threshold_2_slider.setValue(self.threshold_2_value)
            self.blur_slider.setValue(self.blur_value)
            self.dilate_slider.setValue(self.dilate_value)
            self.start_flag = False

    def __init_style(self):
        """Настройка стилей виджетов."""
        font = QFont("Ubuntu", 14)
        font_min = QFont("Ubuntu", 10)
        self.start_button.setStyleSheet(
            "background-color: green; color: white;")
        self.stop_button.setStyleSheet("background-color: red; color: white;")
        self.continue_button.setStyleSheet(
            "background-color: yellow; color: black;")
        self.statisticks_button.setStyleSheet("color: black;")
        self.auto_correction_button.setStyleSheet("color: black;")

        self.start_button.setFont(font)
        self.stop_button.setFont(font)
        self.continue_button.setFont(font)
        self.statisticks_button.setFont(font)
        self.auto_correction_button.setFont(font)

        self.brigh_fac_label.setFont(font_min)
        self.threshold_2_label.setFont(font_min)
        self.threshold_3_label.setFont(font_min)
        self.blur_label.setFont(font_min)
        self.dilate_label.setFont(font_min)

        self.detect_detail_label.setFont(font)

    def __init_sizes(self):
        """Настройка размеров виджетов."""
        ret, frame = self.camera.read()
        image = Image(frame)
        frame = image.transform_zone(frame)
        frame = image.transform_chees(frame)
        frame = image.image_correction(frame)
        self.height_frame, self.width_frame, _ = frame.shape
        self.video_label.setMinimumSize(
            int(self.width_frame*2), int(self.height_frame*2))
        self.start_button.setMinimumSize(100, 100)
        self.stop_button.setMinimumSize(100, 100)
        self.continue_button.setMinimumSize(100, 100)
        self.stop_button.setMinimumSize(100, 100)
        self.continue_button.setMinimumSize(100, 100)
        self.statisticks_button.setMinimumSize(100, 100)
        self.auto_correction_button.setMinimumSize(100, 100)

    def update_frame(self):
        """Обновление кадра видео."""
        ret, frame = self.camera.read()
        self.image = Image(frame)

        # Установка параметров обработки изображения
        self.image.brightness_factor = self.brigh_fac_value
        self.image.threshold_3 = self.threshold_3_value
        self.image.threshold_2 = self.threshold_2_value
        self.image.dilate = self.dilate_value
        self.image.blur = self.blur_value

        # Преобразование и обработка кадра
        frame = self.image.transform_zone(frame)
        frame = self.image.transform_chees(frame)
        frame = self.image.image_correction(frame)
        frame, self.coordinates, self.orientation = self.image.detect_contours(
            frame)
        frame = self.image.draw_contours(frame)
        frame = cv2.resize(frame, None, fx=2, fy=2,
                           interpolation=cv2.INTER_AREA)
        self.height_frame, self.width_frame, _ = frame.shape
        bytes_per_line = 3 * self.width_frame
        q_image = QImage(frame.data, self.width_frame, self.height_frame,
                         bytes_per_line, QImage.Format.Format_BGR888)

        # Отображение кадра в QLabel
        self.video_label.setPixmap(QPixmap.fromImage(q_image))
        self.detect_detail_label.setText(f"Обнаружено деталей: {len(self.coordinates)}\n"
                                         f"\nТип деталей: type 1\n\nСтатус соединения:"
                                         f"not active\n\nCостояние робота: -")
        self.num_of_frame = self.num_of_frame + 1

        if len(self.coordinates) != 0 and self.num_of_frame == 10:
            # Отправка команды роботу каждые 10 кадров
            self.num_of_frame = 0
            self.robot_communication()

    def robot_communication(self):
        """Взаимодействие с роботом."""
        message = ";".join(("move", str(
            self.coordinates[0][1] + 7), str(self.coordinates[0][0] + 5), str(self.orientation[0])))
        print(message)
        self.robot.send_message(message)

    async def start_server(self):
        """Запуск сервера робота."""
        await self.robot.start_server()

    def closeEvent(self, event):
        """Обработка события закрытия приложения."""
        self.robot.close_socket()
        event.accept()

    def on_slider_value_changed(self, value):
        """Обработчик изменения значений слайдеров."""
        if self.start_flag == True:
            return 0
        sender_slider = self.sender()

        corresponding_label = self.slider_label_mapping.get(sender_slider)

        if sender_slider == self.brigh_fac_slider:
            self.brigh_fac_value = value/255*3
            description = "Яркость"
        elif sender_slider == self.threshold_3_slider:
            self.threshold_3_value = value
            description = "Настройка чувствительность обнаружения № 3"
        elif sender_slider == self.threshold_2_slider:
            self.threshold_2_value = value+1
            description = "Настройка чувствительность обнаружения № 2"
        elif sender_slider == self.blur_slider:
            self.blur_value = value
            description = "Настройка размытия"
        elif sender_slider == self.dilate_slider:
            self.dilate_value = value
            description = "Настройка заполнения"

        if corresponding_label is not None:
            corresponding_label.setText(f"{description}: {value}")

        data = {
            'brigh': self.brigh_fac_value,
            'sat': self.sat_fac_value,
            'threshold_3': self.threshold_3_value,
            'threshold_2': self.threshold_2_value,
            'blur': self.blur_value,
            'dilate': self.dilate_value
        }
        with open('video_parametrs.json', 'w') as json_file:
            json.dump(data, json_file)

        self.image.brightness_factor = self.brigh_fac_value
        self.image.threshold_3 = self.threshold_3_value
        self.image.threshold_2 = self.threshold_2_value
        self.image.blur = self.threshold_3_value
        self.image.dilate = self.threshold_2_value

    def send_start(self):
        """Отправка команды старта."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)
        message = ("start;")
        print(message)
        self.robot.send_message(message)

    def send_em_stop(self):
        """Отправка команды стоп."""
        message = ("stop;")
        print(message)
        self.robot.send_message(message)

    def send_continue(self):
        """Отправка команды продолжить."""
        message = ("continue;")
        print(message)
        self.robot.send_message(message)

    def show_database_window(self):
        """Отображение окна статистики."""
        self.database_window = DatabaseWindow()
        self.database_window.exec()


def run_server():
    """Запуск сервера в отдельном потоке."""
    asyncio.run(player.start_server())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()

    # Запуск сервера в отдельном потоке
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    sys.exit(app.exec())