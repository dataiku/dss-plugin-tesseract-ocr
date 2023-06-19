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

    if params[Constants.OCR_ENGINE] == Constants.TESSERACT:
        try:
            img = np.array(img)
            img_text = pytesseract.image_to_string(img, lang=params[Constants.LANGUAGE])
        except Exception as e:
            raise Exception("OCR - Error calling pytesseract: {}".format(e))
    elif params[Constants.OCR_ENGINE] == Constants.EASYOCR:
        try:
            img = np.array(img)
            reader = params[Constants.EASYOCR_READER]
            img_text = " ".join(reader.readtext(img_bytes, detail=0))
        except Exception as e:
            raise Exception("OCR - Error calling easyocr: {}".format(e))

    return img_text
