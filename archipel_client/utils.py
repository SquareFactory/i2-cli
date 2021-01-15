import base64

import cv2
import numpy as np


def binary_to_img(binary_img):
    """Binary image to image."""
    binary_img = base64.b64decode(binary_img)
    img = np.frombuffer(binary_img, np.uint8)
    return cv2.imdecode(img, cv2.IMREAD_COLOR)


def img_to_binary(img: np.ndarray) -> bytes:
    """Images to binary images."""
    _, binary_img = cv2.imencode(".jpg", img)
    return base64.b64encode(binary_img.tobytes())
