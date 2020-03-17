# dss-plugin-tesseract-ocr
Plugin for optical character recognition (OCR) in python using the tesseract engine

The plugin has three components (two recipes and a notebook template):
- image-conversion recipe: convert all types of images into jpg images and split multi-page PDF documents into multiple jpg images. It also convert images to grayscale.
- ocr-text-extraction-dataset recipe:: extract text from images using tesseract and output a dataset with a filename column and a text column. This recipe has parameters to recombine formely split multi-page PDF into a single text, to specify the language used in tesseract, and to remove special charaters from the extracted text. It takes as input a folder of JPG images (the output of the image-conversion recipe or of the notebook).
- image processing notebook: notebook to explore different types of image processing to improve (or not) text extraction from tesseract. Then, the notebook acts as a recipe to process images and output a folder of processed images that can be used by the ocr-text-extraction-dataset recipe.

## Instructions to use the notebook template
 
In order to use notebook template as code recipe after exploring different image processing, you need to create a code env with the same requirements as the plugin code env (because notebooks converted into recipe can't use plugin code envs).

Go to notebook (G+N) and create a new python notebook. Select the template `Image processing for text extraction` and select as code env the one you created manually.

Then you can use the notebook to explore different type of image processing (use the existing functions or write your owns). You need to enter the input folder id or name manually in the notebook.

Then, you convert the notebook into a recipe, and you must go to the advanced tab to select your code env.

You must paste the output folder id found at the bottom of the code recipe into the output_folder_id variable.


## Requirements

Tesseract must be installed on DSS instance server:

For macOS using brew: `brew install tesseract`.

Otherwise, go to: <https://github.com/tesseract-ocr/tesseract/wiki>

To be able to use the python package pdf2image:

For macOS using brew: `brew install poppler`.

Otherwise, go to: <https://github.com/Belval/pdf2image>

## Advanced requirements

If you want to use the `deskew` package in the image processing step, you can find instructions to install it here <https://pypi.org/project/deskew/>. It can really improve results but takes a long time (a few seconds per image).

If you want to specify languages in tesseract, you must install them on your DSS instance, you can find instructions to install them here <https://tesseract-ocr.github.io/tessdoc/Data-Files>

