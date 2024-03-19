import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider
import cv2
import json
from image import Image
from robot import Robot
import threading
import asyncio


class VideoPlayer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.camera = cv2.VideoCapture(
            "Basler_acA2000-165um__22729612__20240313_134953200.mp4")

        self.robot = Robot('127.0.0.1', 48569)

        self.width_frame = None
        self.height_frame = None

        self.brigh_fac_value = 0
        self.sat_fac_value = 0
        self.threshold_3_value = 0
        self.threshold_2_value = 0
        self.blur_value = 0
        self.dilate_value = 0
        self.num_of_frame = 0

        self.start_flag = True
        self.start_robot_flag = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        self.__init_main_window()
        self.__init_layouts()
        self.__init_widgets()
        self.__init_style()
        self.__init_sizes()
        self.__addition_widgets()
        self.__setting_layers()
        self.__settings()

    def __init_main_window(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Video")
        self.resize(600, 600)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 150);")

    def __init_widgets(self):
        self.video_label = QLabel()

        self.brigh_fac_slider = QSlider(Qt.Orientation.Horizontal)
        self.sat_fac_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_2_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_3_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.dilate_slider = QSlider(Qt.Orientation.Horizontal)

        self.brigh_fac_label = QLabel("Настройка яркости")
        self.sat_fac_label = QLabel("Настройка насыщения")
        self.threshold_2_label = QLabel(
            "Настройка чувствительность обнаружения № 2")
        self.threshold_3_label = QLabel(
            "Настройка чувствительность обнаружения № 3")
        self.blur_label = QLabel("Настройка размытия")
        self.dilate_label = QLabel("Настройка заполнения")

        self.detect_detail_label = QLabel("Обнаружено деталей:")

    def __init_layouts(self):
        self.main_layout = QHBoxLayout(self.central_widget)
        self.video_and_info_layout = QHBoxLayout()
        self.video_layout = QVBoxLayout()
        self.info_layout = QVBoxLayout()
        self.vid_info_and_dop_layout = QVBoxLayout()
        self.dop_layout = QHBoxLayout()
        self.calibration_layout = QVBoxLayout()

    def __addition_widgets(self):
        self.video_layout.addWidget(self.video_label)

        self.calibration_layout.addWidget(self.brigh_fac_label)
        self.calibration_layout.addWidget(self.brigh_fac_slider)
        self.calibration_layout.addWidget(self.sat_fac_label)
        self.calibration_layout.addWidget(self.sat_fac_slider)
        self.calibration_layout.addWidget(self.threshold_2_label)
        self.calibration_layout.addWidget(self.threshold_2_slider)
        self.calibration_layout.addWidget(self.threshold_3_label)
        self.calibration_layout.addWidget(self.threshold_3_slider)
        self.calibration_layout.addWidget(self.blur_label)
        self.calibration_layout.addWidget(self.blur_slider)
        self.calibration_layout.addWidget(self.dilate_label)
        self.calibration_layout.addWidget(self.dilate_slider)

        self.info_layout.addWidget(self.detect_detail_label)

    def __setting_layers(self):
        self.video_and_info_layout.addLayout(self.video_layout)
        self.video_and_info_layout.addLayout(self.info_layout)
        self.vid_info_and_dop_layout.addLayout(self.video_and_info_layout)
        self.vid_info_and_dop_layout.addLayout(self.dop_layout)
        self.main_layout.addLayout(self.vid_info_and_dop_layout)
        self.main_layout.addLayout(self.calibration_layout)

    def __settings(self):
        self.slider_label_mapping = {
            self.brigh_fac_slider: self.brigh_fac_label,
            self.sat_fac_slider: self.sat_fac_label,
            self.threshold_2_slider: self.threshold_2_label,
            self.threshold_3_slider: self.threshold_3_label,
            self.blur_slider: self.blur_label,
            self.dilate_slider: self.dilate_label
        }

        for slider, label in self.slider_label_mapping.items():
            slider.setMinimum(0)
            slider.setMaximum(255)
            slider.valueChanged.connect(self.on_slider_value_changed)

        if self.start_flag:
            with open('video_parametrs.json', 'r') as json_file:
                try:
                    data = json.load(json_file)
                except json.JSONDecodeError:
                    raise ValueError("Ошибка при чтении файла с данными.")

            self.brigh_fac_value = data.get('brigh', [])
            self.sat_fac_value = data.get('sat', [])
            self.threshold_3_value = data.get('threshold_3', [])
            self.threshold_2_value = data.get('threshold_2', [])
            self.blur_value = data.get('blur', [])
            self.dilate_value = data.get('dilate', [])

            self.brigh_fac_slider.setValue(int(self.brigh_fac_value*255/3))
            self.sat_fac_slider.setValue(self.sat_fac_value)
            self.threshold_3_slider.setValue(self.threshold_3_value)
            self.threshold_2_slider.setValue(self.threshold_2_value)
            self.blur_slider.setValue(self.blur_value)
            self.dilate_slider.setValue(self.dilate_value)
            self.start_flag = False

    def __init_style(self):
        pass

    def __init_sizes(self):
        ret, frame = self.camera.read()
        image = Image(frame)
        frame = image.transform_zone(frame)
        frame = image.transform_chees(frame)
        frame = image.image_correction(frame)
        self.height_frame, self.width_frame, _ = frame.shape
        self.video_label.setMinimumSize(
            int(self.width_frame*2), int(self.height_frame*2))

    def update_frame(self):
        ret, frame = self.camera.read()
        self.image = Image(frame)

        self.image.brightness_factor = self.brigh_fac_value
        self.image.threshold_3 = self.threshold_3_value
        self.image.threshold_2 = self.threshold_2_value
        self.image.dilate = self.dilate_value
        self.image.blur = self.blur_value

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

        self.video_label.setPixmap(QPixmap.fromImage(q_image))
        self.detect_detail_label.setText(
            f"Обнаружено деталей: {len(self.coordinates)}")
        self.num_of_frame = self.num_of_frame + 1

        if len(self.coordinates) != 0 and self.num_of_frame == 20:
            self.num_of_frame = 0
            self.robot_communication()

    def robot_communication(self):
        message = ";".join(("move", str(
            self.coordinates[0][1] + 7), str(self.coordinates[0][0] + 5), str(self.orientation[0])))
        self.robot.send_message(message)

    async def start_server(self):
        await self.robot.start_server()  # Предположим, что это асинхронная функция

    def closeEvent(self, event):
        self.robot.close_socket()
        event.accept()

    def on_slider_value_changed(self, value):
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


def run_server():
    asyncio.run(player.start_server())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    sys.exit(app.exec())
