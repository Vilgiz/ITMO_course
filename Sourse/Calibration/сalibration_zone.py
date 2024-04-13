import cv2
import numpy as np
from pypylon import pylon
import json


class Marker:
    def __init__(self, id, center, corners):
        self.id = id
        self.center = center
        [self.topLeft, self.topRight, self.bottomRight, self.bottomLeft] = corners


class ImageProcessor():
    def detectArucoMarkers(self, image):
        markers = {}

        arucoDictionary = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_4X4_50)

        arucoParameters = cv2.aruco.DetectorParameters()

        (corners, ids, rejected) = cv2.aruco.detectMarkers(
            image, arucoDictionary, parameters=arucoParameters)

        ids = ids.flatten()

        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
            topRight = [int(topRight[0]), int(topRight[1])]
            bottomRight = [int(bottomRight[0]), int(bottomRight[1])]
            bottomLeft = [int(bottomLeft[0]), int(bottomLeft[1])]
            topLeft = [int(topLeft[0]), int(topLeft[1])]
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            print("[INFO] ArUco marker ID: {}".format(markerID))
            markers[markerID] = Marker(
                markerID, [cX, cY], [topLeft, topRight, bottomRight, bottomLeft])

        return markers

    def cropImage(self, image, points):
        rect = np.array(points, dtype="float32")
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        maxWidth = 279
        maxHeight = 197
        # dst = np.array([
        #     [0, 0],
        #     [maxWidth - 1, 0],
        #     [maxWidth - 1, maxHeight - 1],
        #     [0, maxHeight - 1]], dtype="float32")
        dst = np.array([
            [0, 0],
            [279, 0],
            [279, 197],
            [0, 197]], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)

        # Запись M, maxWidth и maxHeight в JSON
        data = {
            'M': M.tolist(),
            'maxWidth': maxWidth,
            'maxHeight': maxHeight
        }

        with open('transformation_data.json', 'w') as json_file:
            json.dump(data, json_file)

        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped


camera = pylon.InstantCamera(
    pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

if __name__ == "__main__":
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    while camera.IsGrabbing():

        grabResult = camera.RetrieveResult(
            5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():

            frame = grabResult.Array
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            ip = ImageProcessor()

            markers = ip.detectArucoMarkers(image)

            cropped_image = ip.cropImage(image, [
                markers[0].topLeft,
                markers[1].topRight,
                markers[2].bottomRight,
                markers[3].bottomLeft])

            cv2.imshow("Original Image", cv2.cvtColor(
                cropped_image, cv2.COLOR_RGB2BGR))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

camera.StopGrabbing()
cv2.destroyAllWindows()
