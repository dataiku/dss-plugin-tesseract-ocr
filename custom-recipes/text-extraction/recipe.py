import logging
import os
import pandas as pd
from time import perf_counter

from ocr_recipes_io_utils import get_input_output
from ocr_utils import extract_text
from ocr_utils import try_download_pandoc


# call this method to download pandoc binaries
with_pandoc = try_download_pandoc()

logger = logging.getLogger(__name__)

input_folder, output_dataset = get_input_output('folder', 'dataset')

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

    try:
        extracted_text = extract_text(file_bytes, suffix, with_pandoc)
        rows.append({'file': sample_file, 'text': extracted_text, 'error': ""})
        logger.info("Extracted text from {}/{} files (in {:.2f} seconds)".format(i+1, total_files, perf_counter() - start))
    except Exception as e:
        rows.append({'file': sample_file, 'text': "", "error": e})
        logger.info("Failed extracting text from file {} because: {}".format(sample_file, e))

df = pd.DataFrame(rows)

output_dataset.write_with_schema(df)
