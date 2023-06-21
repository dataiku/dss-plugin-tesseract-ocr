import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role
from io import BytesIO
from ocr_constants import Constants
from shutil import which


def get_input_output(input_type='dataset', output_type='dataset'):
    if input_type == 'folder':
        input_names = get_input_names_for_role('input_folder')[0]
        input_obj = dataiku.Folder(input_names)
    else:
        input_names = get_input_names_for_role('input_dataset')[0]
        input_obj = dataiku.Dataset(input_names)

    if output_type == 'folder':
        output_names = get_output_names_for_role('output_folder')[0]
        output_obj = dataiku.Folder(output_names)
    else:
        output_names = get_output_names_for_role('output_dataset')[0]
        output_obj = dataiku.Dataset(output_names)

    return input_obj, output_obj


def convert_image_to_greyscale_bytes(img, quality=75):
    """ convert a PIL image to greyscale with a specified dpi and output image as bytes """
    img = img.convert('L')
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality)
    return buf.getvalue()


def image_conversion_parameters(recipe_config):
    """ retrieve image conversion recipe parameters """
    params = {}
    dpi = recipe_config.get(Constants.DPI, 200)
    assert dpi > 0 and dpi <= 4000
    params[Constants.DPI] = dpi

    quality = recipe_config.get(Constants.QUALITY, 75)
    assert quality > 0 and quality <= 95
    params[Constants.QUALITY] = quality

    return params


def image_processing_parameters(recipe_config):
    """ retrieve image processing recipe parameters """
    params = {}
    params[Constants.FUNCTIONS_DEF] = recipe_config.get(Constants.FUNCTIONS_DEF, None)
    params[Constants.PIPELINE_DEF] = recipe_config.get(Constants.PIPELINE_DEF, None)
    return params


def text_extraction_parameters(recipe_config):
    """ retrieve text extraction recipe parameters """
    params = {}
    params[Constants.RECOMBINE_PDF] = recipe_config.get(Constants.RECOMBINE_PDF, False)
    params[Constants.OCR_ENGINE] = _get_ocr_engine(recipe_config)
    advanced = recipe_config.get('advanced_parameters', False)
    if params[Constants.OCR_ENGINE] == Constants.TESSERACT:
        params[Constants.LANGUAGE_TESSERACT] = recipe_config.get(Constants.LANGUAGE_TESSERACT, "eng") if advanced else "eng"
    elif params[Constants.OCR_ENGINE] == Constants.EASYOCR:
        import easyocr
        language = recipe_config.get(Constants.LANGUAGE_EASYOCR, "en") if advanced else "en"
        params[Constants.EASYOCR_READER] = easyocr.Reader([language])

    return params


def _get_ocr_engine(recipe_config):
    selected_ocr_engine = recipe_config.get(Constants.OCR_ENGINE, Constants.DEFAULT_ENGINE)
    if selected_ocr_engine == Constants.DEFAULT_ENGINE:
        return get_default_ocr_engine()
    else:
        return selected_ocr_engine


def get_default_ocr_engine():
    if which("tesseract") is not None:  # check if tesseract is in the path
        return Constants.TESSERACT
    return Constants.EASYOCR
