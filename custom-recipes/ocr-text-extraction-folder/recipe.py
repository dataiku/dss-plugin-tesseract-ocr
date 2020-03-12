import dataiku
from dataiku.customrecipe import *
import logging
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
from PIL import Image
from io import BytesIO
import pytesseract
import re
from utils import get_input_output_folder, text_extraction_parameters
from tesseractocr import text_extraction

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='OCR Plugin %(levelname)s - %(message)s')

input_folder, output_folder = get_input_output_folder()

params = text_extraction_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()

for sample_file in input_filenames:
    if sample_file.split('.')[-1] != "jpg":
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        data = stream.readlines()
    img_bytes = b"".join(data)

    img_text_clean = text_extraction(img_bytes, params)

    output_folder.upload_data(sample_file.split('.')[0] + ".txt", img_text_clean.encode())
