import dataiku
from dataiku.customrecipe import get_recipe_config
import logging
from utils import get_input_output, text_extraction_parameters
from tesseractocr import text_extraction
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='OCR Plugin %(levelname)s - %(message)s')

input_folder, output_dataset = get_input_output('folder', 'dataset')

params = text_extraction_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()

df = pd.DataFrame(columns=['file', 'text'])

for sample_file in input_filenames:
    if sample_file.split('.')[-1] != "jpg":
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        data = stream.readlines()
    img_bytes = b"".join(data)

    img_text = text_extraction(img_bytes, params)

    df = df.append({'file': sample_file.split('.')[0], 'text': img_text}, ignore_index=True)

if params['recombine_pdf']:
    df['page_nb'] = df.apply(lambda row: int(row['file'].split('_pdf_page_')[1]) if '_pdf_page_' in row['file'] else 1, axis=1)
    df['file'] = df.apply(lambda row: row['file'].split('_pdf_page_')[0] if '_pdf_page_' in row['file'] else row['file'], axis=1)

    df = df.groupby(["file"]).apply(lambda x: x.sort_values(['page_nb'], ascending=True)).reset_index(drop=True)

    df = df.groupby('file').agg({'text': lambda x: '\n\n'.join(map(str, list(x)))}).reset_index()

    df = df[['file', 'text']]

output_dataset.write_with_schema(df)
