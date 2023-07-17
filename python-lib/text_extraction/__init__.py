import docx
from io import BytesIO
import logging
import os
import pypandoc
import pypdfium2 as pdfium
import tempfile


logger = logging.getLogger(__name__)


def try_download_pandoc():
    """ download pandoc prebuilt binaries into the temporary job folder """
    try:
        import pypandoc
        pandoc_tmp_directory = os.getcwd()
        pypandoc.download_pandoc(targetfolder=pandoc_tmp_directory, download_folder=pandoc_tmp_directory)
        return True
    except Exception as e:
        logger.warning("Failed to download pandoc binaries: {}".format(e))
        return False


def extract_text_content(file_bytes, extension, with_pandoc):
    """
    First extract with pdfium or docx PDFs and docx files.
    Then try to extract text using pandoc into plain text.
    Finally, just decode the bytes if pandoc failed or is not downloaded.
    """
    if extension == "pdf":
        pdf_pages = pdfium.PdfDocument(file_bytes)
        return "\n".join([page.get_textpage().get_text_range() for page in pdf_pages])
    elif extension == "docx":
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        text = ""
        if with_pandoc:
            try:
                temporary_job_folder = os.getcwd()
                with tempfile.NamedTemporaryFile(dir=temporary_job_folder, suffix=".{}".format(extension)) as tmp:
                    tmp.write(file_bytes)
                    text = pypandoc.convert_file(tmp.name, to="plain", format=extension)

            except Exception as e:
                logger.warning("Failed to extract text with pandoc: {}".format(e))

        if not text.strip():
            return file_bytes.decode()
        
        return text
            