from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import docx2txt
import io


def extract_text_from_pdf(pdf_file):
    # FIX: Check for the underlying file buffer (for Mock and Streamlit compatibility)
    if hasattr(pdf_file, 'file'):
        input_file = pdf_file.file  # Get the BytesIO object
    else:
        input_file = pdf_file  # Assume it is a standard file object or path

    # Ensure the stream is reset to the beginning before being read by pdfminer
    if hasattr(input_file, 'seek'):
        input_file.seek(0)

    laparams = LAParams()
    # Now input_file is guaranteed to be a BytesIO object (which pdfminer accepts)
    return extract_text(input_file, laparams=laparams)


def extract_text_from_docx(docx_file):
    # docx2txt generally works fine with the Streamlit UploadedFile object
    return docx2txt.process(docx_file)


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    else:
        return ""