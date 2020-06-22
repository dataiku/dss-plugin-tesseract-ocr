from PIL import Image
from io import BytesIO
import pytesseract
import logging
from constants import Constants

logger = logging.getLogger(__name__)


def text_extraction(img_bytes, params):
    """
    extract text from bytes images using pytesseract (with some parameters)
    """
    img = Image.open(BytesIO(img_bytes))

    # convert to greyscale if not already
    if img.mode != 'L':
        logger.info("OCR - converting image to greyscale.")
        img = img.convert('L')

    try:
        img_text = pytesseract.image_to_string(img, lang=params[Constants.LANGUAGE])
    except Exception as e:
        logger.info("OCR - Error calling pytesseract: {}".format(e))

    return img_text
