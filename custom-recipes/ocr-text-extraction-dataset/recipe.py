from dataiku.customrecipe import get_recipe_config
import logging
from utils import get_input_output, text_extraction_parameters
from tesseractocr.extract_text import text_extraction
import pandas as pd
from constants import Constants

logger = logging.getLogger(__name__)

input_folder, output_dataset = get_input_output('folder', 'dataset')

params = text_extraction_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()
total_images = len(input_filenames)

df = pd.DataFrame(columns=['file', 'text'])

for i, sample_file in enumerate(input_filenames):
    if sample_file.split('.')[-1] != "jpg":
        logger.info("OCR - Rejecting {} because it is not a JPG file.".format(sample_file))
        logger.info("OCR - Rejected {}/{} images".format(i+1, total_images))
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        img_bytes = stream.read()

    img_text = text_extraction(img_bytes, params)
    logger.info("OCR - Extracted text from {}/{} images".format(i+1, total_images))

    df = df.append({'file': sample_file.split('/')[-1].split('.')[0], 'text': img_text}, ignore_index=True)

if params['recombine_pdf']:
    df['page_nb'] = df.apply(lambda row: int(row['file'].split(Constants.PDF_MULTI_SUFFIX)[1]) if Constants.PDF_MULTI_SUFFIX in row['file'] else 1, axis=1)
    df['file'] = df.apply(lambda row: row['file'].split(Constants.PDF_MULTI_SUFFIX)[0] if Constants.PDF_MULTI_SUFFIX in row['file'] else row['file'], axis=1)

    df = df.sort_values(['file', 'page_nb'], ascending=True)

    df = df.groupby('file').agg({'text': lambda x: '\n\n'.join(map(str, list(x)))}).reset_index()

    df = df[['file', 'text']]

output_dataset.write_with_schema(df)
