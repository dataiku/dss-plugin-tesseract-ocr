from PIL import Image
from io import BytesIO
import numpy as np
import pytesseract
import logging
import re
from text_extraction_ocr_utils import Constants

logger = logging.getLogger(__name__)


def extract_text_ocr(img_bytes, params):
    """
    extract text from bytes images using the selected OCR engine (with specified language)
    """
    img = Image.open(BytesIO(img_bytes))

    # convert to greyscale if not already
    if img.mode != 'L':
        logger.info("OCR - converting image to greyscale.")
        img = img.convert('L')

    if params[Constants.OCR_ENGINE] == Constants.TESSERACT:
        try:
            img = np.array(img)
            img_text = pytesseract.image_to_string(img, lang=params[Constants.LANGUAGE_TESSERACT])
        except Exception as e:
            raise Exception("OCR - Error calling pytesseract: {}".format(e))
    elif params[Constants.OCR_ENGINE] == Constants.EASYOCR:
        try:
            img = np.array(img)
            reader = params[Constants.EASYOCR_READER]
            img_text = " ".join(reader.readtext(img_bytes, detail=0))
        except Exception as e:
            raise Exception("OCR - Error calling easyocr: {}".format(e))
    else:
        raise NotImplementedError("OCR engine {} not implemented".format(params[Constants.OCR_ENGINE]))

    return img_text


def get_multi_page_pdf_page_nb(file_name):
    matched = re.fullmatch(r".*_pdf_page_(\d{5})\.jpg", file_name)
    if matched is not None:
        return int(matched.group(1))
    return 1


def get_multi_page_pdf_base_name(file_name):
    matched = re.fullmatch(r"(.*)_pdf_page_\d{5}\.jpg", file_name)
    if matched is not None:
        return "{}.pdf".format(matched.group(1))
    return file_name
