import logging
import os
import pandas as pd
from time import perf_counter

from dataiku.customrecipe import get_recipe_config
from text_extraction_ocr_utils.recipes_io_utils import get_input_output
from text_extraction_ocr_utils import text_extraction_parameters
from text_extraction_ocr_utils import Constants
from text_extraction import extract_text_content
from text_extraction import extract_text_chunks
from text_extraction import download_pandoc_binaries


# call this method to download pandoc binaries
with_pandoc = download_pandoc_binaries()

logger = logging.getLogger(__name__)

input_folder, output_dataset = get_input_output('folder', 'dataset')

params = text_extraction_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()
total_files = len(input_filenames)

rows = []

for i, sample_file in enumerate(input_filenames):
    prefix, suffix = os.path.splitext(sample_file)
    suffix = suffix[1:].lower()  # removing the dot from the extension and accepting capital letters

    start = perf_counter()

    logger.info("Extracting text from file {} ...".format(sample_file))

    with input_folder.get_download_stream(sample_file) as stream:
        file_bytes = stream.read()
    
    if params[Constants.EXTRACT_CHUNKS]:
        try:
            extracted_chunks = extract_text_chunks(sample_file, file_bytes, suffix, with_pandoc, params[Constants.METADATA_AS_PLAIN_TEXT], params[Constants.USE_PDF_BOOKMARKS])

            if len(extracted_chunks) == 0:
                raise ValueError("Extracted chunks are empty")

            rows.extend(extracted_chunks)
            logger.info("Extracted text chunks from {}/{} files (in {:.2f} seconds)".format(i+1, total_files, perf_counter() - start))
        except Exception as e:
            rows.append({'file': sample_file, 'text': "", 'chunk_id': "", 'metadata': "", 'error_message': e})
            logger.info("Failed extracting text from file {} because: {}".format(sample_file, e))
    else:
        try:
            extracted_text = extract_text_content(file_bytes, suffix, with_pandoc)

            if not extracted_text.strip():
                logger.warning("Extracted text is empty")

            rows.append({'file': sample_file, 'text': extracted_text, 'error_message': ""})
            logger.info("Extracted text from {}/{} files (in {:.2f} seconds)".format(i+1, total_files, perf_counter() - start))
        except Exception as e:
            rows.append({'file': sample_file, 'text': "", 'error_message': e})
            logger.info("Failed extracting text from file {} because: {}".format(sample_file, e))

df = pd.DataFrame(rows)

output_dataset.write_with_schema(df)
