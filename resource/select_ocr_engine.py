from text_extraction_ocr_utils import get_default_ocr_engine
from text_extraction_ocr_utils import Constants


OCR_ENGINES = {
    Constants.TESSERACT: "Tesseract",
    Constants.EASYOCR: "EasyOCR"
}


def do(payload, config, plugin_config, inputs):
    """
    Retrieve a list of OCR engines including a default engine that points to an available engine.  
    """
    choices = []
    if payload.get("parameterName") == Constants.OCR_ENGINE:
        default_ocr_engine = get_default_ocr_engine()
        choices.append({
            "label": "Default ({})".format(OCR_ENGINES[default_ocr_engine]),
            "value": "default"
        })

        if default_ocr_engine != Constants.TESSERACT:
            OCR_ENGINES[Constants.TESSERACT] += " (not installed)"

        for engine_value, engine_label in OCR_ENGINES.items():
            choices.append({
                "label": engine_label,
                "value": engine_value
            })

    return {"choices": choices}
