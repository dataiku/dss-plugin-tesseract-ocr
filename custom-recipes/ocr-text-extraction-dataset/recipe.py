import logging
import os
import pandas as pd
import re
from time import perf_counter

from dataiku.customrecipe import get_recipe_config
from ocr_constants import Constants
from ocr_recipes_io_utils import get_input_output
from ocr_utils import convert_image_to_greyscale_bytes
from ocr_utils import pdf_to_pil_images_iterator
from ocr_utils import text_extraction_parameters
from tesseractocr.extract_text import text_extraction


logger = logging.getLogger(__name__)

input_folder, output_dataset = get_input_output('folder', 'dataset')

params = text_extraction_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()
total_files = len(input_filenames)

rows = []

for i, sample_file in enumerate(input_filenames):
    prefix, suffix = os.path.splitext(sample_file)
    suffix = suffix[1:]  # removing the dot from the extension

    if suffix not in Constants.TYPES:
        logger.info("OCR - Rejecting {} because it is not a {} file.".format(sample_file, '/'.join(Constants.TYPES)))
        logger.info("OCR - Rejected {}/{} files".format(i+1, total_files))
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        img_bytes = stream.read()

    start = perf_counter()

    if suffix == "pdf":
        for j, img in enumerate(pdf_to_pil_images_iterator(img_bytes)):
            img_bytes = convert_image_to_greyscale_bytes(img)
            img_text = text_extraction(img_bytes, params)

            pdf_image_name = "{}{}{:05d}".format(prefix, Constants.PDF_MULTI_SUFFIX, j+1)
            rows.append({'file': pdf_image_name, 'text': img_text})
    else:
        img_text = text_extraction(img_bytes, params)
        rows.append({'file': prefix, 'text': img_text})

    logger.info("OCR - Extracted text from {}/{} files (in {:.2f} seconds)".format(i+1, total_files, perf_counter() - start))

df = pd.DataFrame(rows)

if params['recombine_pdf']:
    pdf_multi_page_pattern = "^.*{}\d{{5}}$".format(Constants.PDF_MULTI_SUFFIX)
    df['page_nb'] = df.apply(lambda row: int(row['file'].split(Constants.PDF_MULTI_SUFFIX)[1]) if re.match(pdf_multi_page_pattern, row['file']) else 1, axis=1)
    df['file'] = df.apply(lambda row: row['file'].split(Constants.PDF_MULTI_SUFFIX)[0] if re.match(pdf_multi_page_pattern, row['file']) else row['file'], axis=1)

    df = df.sort_values(['file', 'page_nb'], ascending=True)

    df = df.groupby('file').agg({'text': lambda x: '\n\n'.join(map(str, list(x)))}).reset_index()

    df = df[['file', 'text']]

output_dataset.write_with_schema(df)
