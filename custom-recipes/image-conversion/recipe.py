from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import logging
from utils import get_input_output

logger = logging.getLogger(__name__)

input_folder, output_folder = get_input_output('folder', 'folder')

input_filenames = input_folder.list_paths_in_partition()
total_images = len(input_filenames)

# check if pdf and split pdf into multiple images
for i, sample_file in enumerate(input_filenames):
    prefix = sample_file.split('.')[0]
    suffix = sample_file.split('.')[-1]

    if suffix == "pdf":
        with input_folder.get_download_stream(sample_file) as stream:
            img_bytes = stream.read()
        pdf_images = convert_from_bytes(img_bytes, fmt='jpg')

        for i, img in enumerate(pdf_images):
            img = img.convert('L')
            buf = BytesIO()
            img.save(buf, format='JPEG')
            img_bytes = buf.getvalue()
            output_folder.upload_data("{}_pdf_page_{:05d}.jpg".format(prefix, i+1), img_bytes)

    elif suffix in ["jpg", "png", "jpeg", "tiff"]:
        with input_folder.get_download_stream(sample_file) as stream:
            img_bytes = stream.read()

        img = Image.open(BytesIO(img_bytes)).convert('L')
        buf = BytesIO()
        img.save(buf, format='JPEG')
        img_bytes = buf.getvalue()

        output_folder.upload_data(prefix + ".jpg", img_bytes)

    logger.info("OCR - Converted {}/{} images".format(i+1, total_images))
