from typing import Optional, Any
from pypylon import pylon
import cv2


class Camera:
    """
    Класс для работы с камерой, получения изображений и их отображения.

    Attributes:
        camera (pylon.InstantCamera): Объект камеры для захвата изображений.
        start_grab_flag (bool): Флаг, указывающий на начало захвата изображений.
    """

    def __init__(self) -> None:
        """
        Инициализация объекта Camera.
        """
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.start_grab_flag = True

    def get_image(self) -> Optional[Any]:
        """
        Получает изображение с камеры.

        Returns:
            frame (Optional[Any]): Изображение в формате NumPy
            массива или None, если произошла ошибка.
        """
        if self.start_grab_flag:
            self.camera.Open()
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self.start_grab_flag = False  # Установим флаг в False после первого вызова
        grab_result = self.camera.RetrieveResult(
            5000, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            frame = grab_result.Array
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
        return None

    def show(self, frame: Any) -> None:
        """
        Отображает изображение.

        Args:
            frame (Any): Изображение в формате NumPy массива.

        Returns:
            None
        """
        cv2.imshow("Test Video", frame)

    def end(self) -> None:
        """
        Прекращает работу камеры и закрывает окно отображения изображений.

        Returns:
            None
        """
        self.camera.StopGrabbing()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    camera = Camera()

    while True:
        frame = camera.get_image()
        camera.show(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.end_show()
