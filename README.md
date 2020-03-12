# dss-plugin-tesseract-ocr
Plugin for optical character recognition (OCR) in python using the tesseract engine

The plugin has two recipes:
- Image processing: convert images (jpg, png and jpeg) into jpg images and split multi-page PDF documents into multiple jpg images.
- OCR - text extraction from images: extract text from images and output either a folder of text files or a dataset with a filename column and a text column.

It is the first version, no image preprocessing and no specific language available.

## Requirements

Tesseract must be installed on DSS instance server:

For macOS using brew: `brew install tesseract`.

Otherwise, go to: <https://github.com/tesseract-ocr/tesseract/wiki>

To be able to use the python package pdf2image:

For macOS using brew: `brew install poppler`.

Otherwise, go to: <https://github.com/Belval/pdf2image>

## Advanced parameters

In the text extraction recipe, advanced parameters can be set to make better OCR.

`deskew` uses the python package found at <https://pypi.org/project/deskew/>. It can really improve results but takes a long time (a few seconds per image).

`language` specifies which language to use in tesseract. Language must be installed by user on system, they can be found at <https://tesseract-ocr.github.io/tessdoc/Data-Files>

