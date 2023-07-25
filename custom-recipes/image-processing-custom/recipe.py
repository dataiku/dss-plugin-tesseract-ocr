from dataiku.customrecipe import get_recipe_config
from PIL import Image
from io import BytesIO
import numpy as np
import logging
from text_extraction_ocr_utils.recipes_io_utils import get_input_output
from text_extraction_ocr_utils import image_processing_parameters
from text_extraction_ocr_utils import Constants

logger = logging.getLogger(__name__)

input_folder, output_folder = get_input_output('folder', 'folder')

input_filenames = input_folder.list_paths_in_partition()
total_images = len(input_filenames)

params = image_processing_parameters(get_recipe_config())

try:
    if params[Constants.FUNCTIONS_DEF]:
        logger.info("OCR - about to execute: {}".format(params[Constants.FUNCTIONS_DEF]))
        exec(params[Constants.FUNCTIONS_DEF])

    if params[Constants.PIPELINE_DEF]:
        logger.info("OCR - about to execute: {}".format(params[Constants.PIPELINE_DEF]))
        exec(params[Constants.PIPELINE_DEF])

    complete_processing  # check that this function exists
except Exception as e:
    raise Exception("OCR - Problem executing python code defined by user: {}".format(e))

for i, sample_file in enumerate(input_filenames):
    if sample_file.split('.')[-1] != "jpg":
        logger.info("OCR - Rejecting {} because it is not a JPG file.".format(sample_file))
        logger.info("OCR - Rejected {}/{} images".format(i+1, total_images))
        continue

    with input_folder.get_download_stream(sample_file) as stream:
        raw_img_bytes = stream.read()
    raw_image = np.array(Image.open(BytesIO(raw_img_bytes)))

    processed_image = complete_processing(raw_image)
    if not isinstance(processed_image, np.ndarray) or len(processed_image.shape) != 2:
        raise Exception("OCR - output of complete_processing must be a 2d numpy array.")
    logger.info("OCR - Processed {}/{} images".format(i+1, total_images))

    buf = BytesIO()
    Image.fromarray(processed_image).save(buf, format='JPEG')
    processed_img_bytes = buf.getvalue()

    output_folder.upload_data(sample_file, processed_img_bytes)
