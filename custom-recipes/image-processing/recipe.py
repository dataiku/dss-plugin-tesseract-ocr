import dataiku
from dataiku.customrecipe import *
from dataiku import pandasutils as pdu
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import logging
from utils import get_input_output_folder

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='OCR Plugin %(levelname)s - %(message)s')

input_folder, output_folder = get_input_output_folder()

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
            buf = BytesIO()
            img.save(buf, format='JPEG')
            byte_img = buf.getvalue()

            output_folder.upload_data(prefix + "_page_" + str(i+1) + ".jpg", byte_img)

    elif suffix in ["jpg","png","jpeg"]:

        with input_folder.get_download_stream(sample_file) as stream:
            data = stream.readlines()
        img_bytes = b"".join(data)

        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        buf = BytesIO()
        img.save(buf, format='JPEG')
        byte_img = buf.getvalue()

        output_folder.upload_data(prefix + ".jpg", byte_img)