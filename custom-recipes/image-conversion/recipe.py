import dataiku
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import logging
from utils import get_input_output

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='OCR Plugin %(levelname)s - %(message)s')

input_folder, output_folder = get_input_output('folder', 'folder')

input_filenames = input_folder.list_paths_in_partition()

# check if pdf and split pdf into multiple images
for sample_file in input_filenames:
    prefix = sample_file.split('.')[0]
    suffix = sample_file.split('.')[-1]

    if suffix == "pdf":
        with input_folder.get_download_stream(sample_file) as stream:
            data = stream.readlines()
        img_bytes = b"".join(data)

        pdf_images = convert_from_bytes(img_bytes, fmt='jpg')

        for i, img in enumerate(pdf_images):
            img = img.convert('L')
            buf = BytesIO()
            img.save(buf, format='JPEG')
            img_bytes = buf.getvalue()

            output_folder.upload_data("{}_pdf_page_{:05d}.jpg".format(prefix, i+1), img_bytes)

    elif suffix in ["jpg", "png", "jpeg", "tiff"]:

        with input_folder.get_download_stream(sample_file) as stream:
            data = stream.readlines()
        img_bytes = b"".join(data)

        img = Image.open(BytesIO(img_bytes)).convert('L')
        buf = BytesIO()
        img.save(buf, format='JPEG')
        img_bytes = buf.getvalue()

        output_folder.upload_data(prefix + ".jpg", img_bytes)
