import pypdf  # Changed from PyPDF2
from docx import Document
import io
from typing import Union

class FileHandler:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = pypdf.PdfReader(pdf_file)  # Updated from PyPDF2
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")

    def extract_text(self, file_content: bytes, filename: str) -> str:
        if filename.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_content)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")