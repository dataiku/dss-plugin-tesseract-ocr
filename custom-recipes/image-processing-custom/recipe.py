from dataiku.customrecipe import get_recipe_config
from PIL import Image
from io import BytesIO
import numpy as np
import logging
from utils import get_input_output, image_processing_parameters


logger = logging.getLogger(__name__)

input_folder, output_folder = get_input_output('folder', 'folder')

input_filenames = input_folder.list_paths_in_partition()
total_images = len(input_filenames)

params = image_processing_parameters(get_recipe_config())

logger.info("params: {}".format(params))

try:
    if params['functions_definition']:
        logger.info("about to execute: {}".format(params['functions_definition']))
        exec(params['functions_definition'])

    if params['pipeline_definition']:
        logger.info("about to execute: {}".format(params['pipeline_definition']))
        exec(params['pipeline_definition'])

    complete_processing  # check that this function exists
except Exception as e:
    raise Exception("OCR - Problem executing python code defined by user: {}".format(e))

for i, sample_file in enumerate(input_filenames):
    if sample_file.split('.')[-1] != "jpg":
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        raw_img_bytes = stream.read()
    raw_image = np.array(Image.open(BytesIO(raw_img_bytes)))

    processed_image = complete_processing(raw_image)
    logger.info("OCR - Processed {}/{} images".format(i+1, total_images))

    buf = BytesIO()
    Image.fromarray(processed_image).save(buf, format='JPEG')
    processed_img_bytes = buf.getvalue()

    output_folder.upload_data(sample_file, processed_img_bytes)
