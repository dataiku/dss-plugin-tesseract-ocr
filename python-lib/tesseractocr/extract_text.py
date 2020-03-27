import numpy as np
from PIL import Image
from io import BytesIO
import pytesseract
import re
import cv2
from deskew import determine_skew
import math



def rotate(image: np.ndarray, angle: float) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))))


def image_processing(img_bytes, params):
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

from dataiku.customrecipe import get_plugin_config

def simple(x):
    print("hello")
    return 99

def text_extraction(img_bytes, params):
    img = Image.open(BytesIO(img_bytes))
    img = np.array(img)

    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    language = params['language']

    img_text = pytesseract.image_to_string(img, lang=language)

    if params['remove_special_characters']:
        img_text = re.sub('[^A-Za-z0-9 \n]+', '', img_text)

    return img_text
