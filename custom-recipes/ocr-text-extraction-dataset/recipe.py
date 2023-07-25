import logging
import os
import pandas as pd
import re
from time import perf_counter

from dataiku.customrecipe import get_recipe_config
from text_extraction_ocr_utils import Constants
from text_extraction_ocr_utils.recipes_io_utils import get_input_output
from text_extraction_ocr_utils import convert_image_to_greyscale_bytes
from text_extraction_ocr_utils import pdf_to_pil_images_iterator
from text_extraction_ocr_utils import ocr_parameters
from ocr import extract_text_ocr
from ocr import get_multi_page_pdf_base_name
from ocr import get_multi_page_pdf_page_nb


logger = logging.getLogger(__name__)

input_folder, output_dataset = get_input_output('folder', 'dataset')

params = ocr_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()
total_files = len(input_filenames)

rows = []

for i, sample_file in enumerate(input_filenames):
    prefix, suffix = os.path.splitext(sample_file)
    suffix = suffix[1:].lower()  # removing the dot from the extension and accepting capital letters

    if suffix not in Constants.OCR_TYPES:
        logger.info("OCR - Rejecting {} because it is not a {} file.".format(sample_file, '/'.join(Constants.OCR_TYPES)))
        logger.info("OCR - Rejected {}/{} files".format(i+1, total_files))
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        img_bytes = stream.read()

    start = perf_counter()

    if suffix == "pdf":
        for j, img in enumerate(pdf_to_pil_images_iterator(img_bytes)):
            img_bytes = convert_image_to_greyscale_bytes(img)
            img_text = extract_text_ocr(img_bytes, params)

            pdf_image_name = "{}{}{:05d}.jpg".format(prefix, Constants.PDF_MULTI_SUFFIX, j+1)
            rows.append({'file': pdf_image_name, 'text': img_text})
    else:
        img_text = extract_text_ocr(img_bytes, params)
        rows.append({'file': sample_file, 'text': img_text})

    logger.info("OCR - Extracted text from {}/{} files (in {:.2f} seconds)".format(i+1, total_files, perf_counter() - start))

df = pd.DataFrame(rows)

if params['recombine_pdf']:
    df['page_nb'] = df.apply(lambda row: get_multi_page_pdf_page_nb(row['file']), axis=1)
    df['file'] = df.apply(lambda row: get_multi_page_pdf_base_name(row['file']), axis=1)

    df = df.sort_values(['file', 'page_nb'], ascending=True)

    df = df.groupby('file').agg({'text': lambda x: '\n\n'.join(map(str, list(x)))}).reset_index()

    df = df[['file', 'text']]

output_dataset.write_with_schema(df)
