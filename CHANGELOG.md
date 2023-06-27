# Changelog

## [Version 2.0.0](https://github.com/dataiku/dss-plugin-tesseract-ocr/releases/tag/v2.0.0) - Feature release - 2023-06

- Add EasyOCR
- Add an option for a default OCR engine that fallbacks to EasyOCR if tesseract is not installed on the system 
- Support of PDFs in the text extraction recipe
- Remove "Tesseract" from the plugin name
- Use pypdfium2 instead of pdf2images to not depend on any system packages 

## [Version 1.0.3](https://github.com/dataiku/dss-plugin-tesseract-ocr/releases/tag/v1.0.3) - Update release - 2023-04

- Update code env description to support python versions 3.8, 3.9, 3.10 and 3.11

## [Version 1.0.2](https://github.com/dataiku/dss-plugin-tesseract-ocr/releases/tag/v1.0.2) - Initial release - 2021-11

- Fix an error in python 37 in the text extraction recipe

## [Version 1.0.1](https://github.com/dataiku/dss-plugin-tesseract-ocr/releases/tag/v1.0.1) - Initial release - 2021-03

- Custom code of the image processing recipe is successfully saved when exiting and coming back to the recipe
