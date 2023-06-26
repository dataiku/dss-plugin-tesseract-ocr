from dataiku.customrecipe import get_recipe_config
from PIL import Image
from io import BytesIO
import logging
from ocr_utils import get_input_output
from ocr_utils import convert_image_to_greyscale_bytes
from ocr_utils import image_conversion_parameters
from ocr_utils import pdf_to_pil_images_iterator
from ocr_constants import Constants

logger = logging.getLogger(__name__)

input_folder, output_folder = get_input_output('folder', 'folder')

params = image_conversion_parameters(get_recipe_config())

input_filenames = input_folder.list_paths_in_partition()
total_images = len(input_filenames)

# check if pdf and split pdf into multiple images
for i, sample_file in enumerate(input_filenames):
    prefix = sample_file.split('.')[0]
    suffix = sample_file.split('.')[-1]

    if suffix in Constants.TYPES:
        with input_folder.get_download_stream(sample_file) as stream:
            img_bytes = stream.read()

        if suffix == "pdf":
            for j, img in enumerate(pdf_to_pil_images_iterator(img_bytes)):
                img_bytes = convert_image_to_greyscale_bytes(img, quality=params[Constants.QUALITY])
                output_folder.upload_data("{0}/{0}{1}{2:05d}.jpg".format(prefix, Constants.PDF_MULTI_SUFFIX, j+1), img_bytes)

        else:
            img = Image.open(BytesIO(img_bytes))
            img_bytes = convert_image_to_greyscale_bytes(img, quality=params[Constants.QUALITY])
            output_folder.upload_data("{}.jpg".format(prefix), img_bytes)

        logger.info("OCR - Converted {}/{} images".format(i+1, total_images))

    else:
        logger.info("OCR - Rejecting {} because it is not a {} file.".format(sample_file, '/'.join(Constants.TYPES)))
        logger.info("OCR - Rejected {}/{} images".format(i+1, total_images))
