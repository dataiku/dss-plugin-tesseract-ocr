from PIL import Image
from io import BytesIO
import numpy as np
import pytesseract
import logging
from constants import Constants

logger = logging.getLogger(__name__)


def text_extraction(img_bytes, params):
    """
    extract text from bytes images using pytesseract (with specified language)
    """
    img = Image.open(BytesIO(img_bytes))

    # convert to greyscale if not already
    if img.mode != 'L':
        logger.info("OCR - converting image to greyscale.")
        img = img.convert('L')

    try:
        img = np.array(img)
        print('CONFFFFFIIIIF', params['config'])
        img_text = pytesseract.image_to_string(img, lang=params[Constants.LANGUAGE], config=params[Constants.CONFIG])
    except Exception as e:
        raise Exception("OCR - Error calling pytesseract: {}".format(e))

    return img_text
