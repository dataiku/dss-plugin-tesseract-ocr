import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role
from io import BytesIO
from ocr_constants import Constants
import pypdfium2 as pdfium
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


def pdf_to_pil_images_iterator(pdf_bytes, dpi=None):
    """ iterator over the multiple images of pdf bytes """
    pdf_pages = pdfium.PdfDocument(pdf_bytes)
    # scale is DPI / 72 according to pypdfium2 doc
    scale = dpi / 72 if dpi else 2
    for pdf_page in pdf_pages:
        yield pdf_page.render(scale=scale).to_pil()


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
    selected_ocr_engine = recipe_config.get(Constants.OCR_ENGINE, Constants.DEFAULT_ENGINE)
    advanced = recipe_config.get('advanced_parameters', False)

    if selected_ocr_engine == Constants.DEFAULT_ENGINE:
        advanced = False
        selected_ocr_engine = get_default_ocr_engine()

    params[Constants.OCR_ENGINE] = selected_ocr_engine

    if params[Constants.OCR_ENGINE] == Constants.TESSERACT:
        params[Constants.LANGUAGE_TESSERACT] = recipe_config.get(Constants.LANGUAGE_TESSERACT, "eng") if advanced else "eng"
    elif params[Constants.OCR_ENGINE] == Constants.EASYOCR:
        import easyocr
        language = recipe_config.get(Constants.LANGUAGE_EASYOCR, "en") if advanced else "en"
        # instantiate the easyocr.Reader only once here because it takes some time
        params[Constants.EASYOCR_READER] = easyocr.Reader([language])

    return params


def get_default_ocr_engine():
    if which("tesseract") is not None:  # check if tesseract is in the path
        return Constants.TESSERACT
    return Constants.EASYOCR
