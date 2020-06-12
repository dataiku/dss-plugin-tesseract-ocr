import numpy as np
from PIL import Image
from io import BytesIO
import pytesseract
import cv2
from deskew import determine_skew
import math


def rotate(image: np.ndarray, angle: float) -> np.ndarray:
    """
    rotate a numpy array image of a specified angle
    """
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))))


def clean_image(img_bytes, params):
    """
    clean bytes image depending on some parameters
    (not actually use in the plugin, processing is done by users in the notebook)
    """
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img)

    if params['grayscaling']:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if params['deskew']:
        angle = determine_skew(img)
        if -10 <= angle <= 10:
            img = rotate(img, angle)

    if params['blurring']:
        img = cv2.medianBlur(img, 3)

    if params['thresholding']:
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    buf = BytesIO()
    Image.fromarray(img).save(buf, format='JPEG')
    img_bytes = buf.getvalue()

    return img_bytes


def text_extraction(img_bytes, params):
    """
    extract text from bytes images using pytesseract (with some parameters)
    """
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img)

    if len(img.shape) > 2:  # set image to black and white if it is not already
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img_text = pytesseract.image_to_string(img, lang=params['language'])

    return img_text
