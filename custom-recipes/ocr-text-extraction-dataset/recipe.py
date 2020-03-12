import dataiku
from dataiku.customrecipe import *
import logging
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from PIL import Image
from io import BytesIO
import pytesseract
import re
from utils import get_input_output_dataset, text_extraction_parameters
from tesseractocr import text_extraction

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='OCR Plugin %(levelname)s - %(message)s')

input_folder, output_dataset = get_input_output_dataset()

params = text_extraction_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()

output_dataset.write_schema([
    {"name": "file", "type": "string", },
    {"name": "text", "type": "string", }])

with output_dataset.get_writer() as writer:

    for sample_file in input_filenames:
        if sample_file.split('.')[-1] != "jpg":
            continue

        with input_folder.get_download_stream(sample_file) as stream:
            data = stream.readlines()
        img_bytes = b"".join(data)

        img_text_clean = text_extraction(img_bytes, params)

        writer.write_row_dict({"file": sample_file.split('.')[0], "text": img_text_clean})
