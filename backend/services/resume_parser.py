import os
import PyPDF2
import pdfplumber
from docx import Document

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_path):
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as fallback_error:
                raise Exception(f"Failed to parse PDF: {str(fallback_error)}")

        return text.strip()

    @staticmethod
    def extract_text_from_docx(file_path):
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to parse DOCX: {str(e)}")

    @staticmethod
    def parse_resume(file_path):
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return ResumeParser.extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            return ResumeParser.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
