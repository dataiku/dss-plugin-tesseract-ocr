import docx
from io import BytesIO
import logging
import os
import pypandoc
import pypdfium2 as pdfium
import tempfile


logger = logging.getLogger(__name__)


def download_pandoc_binaries():
    """ download pandoc prebuilt binaries into the temporary job folder """
    try:
        import pypandoc
        pandoc_tmp_directory = os.getcwd()
        pypandoc.ensure_pandoc_installed(targetfolder=pandoc_tmp_directory)
        return True
    except Exception as e:
        logger.warning("Failed to download pandoc binaries: {}".format(e))
        return False


def extract_text_content(file_bytes, extension, with_pandoc):
    """
    Extract text content from file bytes:
    - First try to extract from PDF or docx file
    - Then try using pandoc to extract other files into plain text.
    - Finally, just decode the bytes if pandoc failed or is not downloaded.
    """
    if extension == "pdf":
        pdf_pages = pdfium.PdfDocument(file_bytes)
        return "\n".join([page.get_textpage().get_text_range() for page in pdf_pages])
    elif extension == "docx":
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    elif extension == "doc":
        raise ValueError("'doc' files are not supported, try to convert them to docx.")
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

        # pandoc outputs empty string with new line for some formats that work with .decode() (for instance csv/tsv)
        if not text.strip():
            return file_bytes.decode()
        
        return text


def extract_text_chunks(filename, file_bytes, extension, with_pandoc):
    if extension == "pdf":
        pdf_pages = pdfium.PdfDocument(file_bytes)
        return [
            {
                'file': filename,
                'text': page.get_textpage().get_text_range(),
                'id': page_id + 1,
                'metadata': {"page": page_id + 1},
                'error_message': ""
            }
            for page_id, page in enumerate(pdf_pages)
        ]
    elif extension == "doc":
        raise ValueError("'doc' files are not supported, try to convert them to docx.")
    elif extension == "txt":
        return [{
            'file': filename,
            'text': file_bytes.decode(),
            'id': 1,
            'metadata': "",
            'error_message': ""
        }]
    elif extension == "md":
        return extract_markdown_chunks(file_bytes.decode(), filename)
    else:
        if not with_pandoc:
            raise ValueError("pandoc is required to extract chunks from files (except for PDFs and markdown).")

        try:
            temporary_job_folder = os.getcwd()
            with tempfile.NamedTemporaryFile(dir=temporary_job_folder, suffix=".{}".format(extension)) as tmp:
                tmp.write(file_bytes)
                markdown = pypandoc.convert_file(tmp.name, to="gfm", format=extension)
        except Exception as e:
            raise ValueError("Cannot convert file into markdown using pandoc because: {}".format(e))
    
        return extract_markdown_chunks(markdown, filename)


def extract_markdown_chunks(markdown, filename):
    """
    Extracts chunks from a markdown document. 
    
    The document is chunked according to its headers. Headers with levels 4+ are considered
    as part of the text.

    Returns a list of dictionaries, where each dictionary contains a chunk data and 
    corresponding metadata.

    This code is largely inspired by `langchain.text_splitter.MarkdownHeaderTextSplitter.split_text`
    https://github.com/langchain-ai/langchain/blob/v0.0.333/libs/langchain/langchain/text_splitter.py#L376
    """

    lines = markdown.split("\n")
    # Final output
    lines_with_metadata = []
    # text and metadata of the chunk currently being processed
    current_text = []
    current_metadata = {}
    # Keep track of the nested header structure
    # header_stack: List[Dict[str, Union[int, str]]] = []
    header_stack = []
    initial_metadata = {}

    in_code_block = False

    for line in lines:
        stripped_line = line
        if not stripped_line.startswith(("    ", "\t")):
            # Header lines can only start with 0 to 3 spaces
            stripped_line = line.lstrip()

        if stripped_line.startswith(("```", "~~~")):
            # code block in one row (only for ```) 
            if stripped_line.count("```") >= 2:
                in_code_block = False
            else:
                in_code_block = not in_code_block

        if in_code_block:
            current_text.append(line)
            continue

        # Check each line against each of the header types (e.g., #, ##), header_level is the number of '#'
        for header_level in range(1, 4):
            # Check if line starts with a header that we intend to split on
            if stripped_line.startswith("#" * header_level) and (
                # Header with no text OR header is followed by space are valid conditions that sep is being used a header
                len(stripped_line) == header_level or stripped_line[header_level] == " "
            ):

                # Pop out headers of lower or same level from the stack
                while header_stack and header_stack[-1]["level"] >= header_level:
                    # We have encountered a new header at the same or higher level
                    popped_header = header_stack.pop()
                    # Clear the metadata for the popped header in initial_metadata
                    if popped_header["level"] in initial_metadata:
                        initial_metadata.pop(popped_header["level"])

                # Push the current header to the stack
                header = {
                    "level": header_level,
                    "data": stripped_line[header_level :].strip(),
                }
                header_stack.append(header)
                # Update initial_metadata with the current header
                initial_metadata[header_level] = header["data"]

                # Add the previous line to the lines_with_metadata only if current_text is not empty
                if current_text:
                    if any(current_text):  # Add only chunks that contain at least one non-empty element
                        lines_with_metadata.append(
                            {
                                "text": "\n".join(current_text),
                                "metadata": current_metadata.copy(),
                            }
                        )
                    current_text.clear()

                break
        else:
            # Add line to current_text when no header was found
            current_text.append(line)

        current_metadata = initial_metadata.copy()

    if current_text:
        lines_with_metadata.append(
            {"text": "\n".join(current_text), "metadata": current_metadata}
        )

    chunks = []
    for line_id, line in enumerate(lines_with_metadata):
        # Header metadata is encoded as {"headers": ["header 1", "header 2", "header 3"]}
        headers = list(line["metadata"].values())
        header_metadata = {"headers": headers} if len(headers) > 0 else ""
        chunks.append({"file": filename, "text": line["text"], "id": line_id + 1, "metadata": header_metadata, "error_message": ""})

    return chunks
