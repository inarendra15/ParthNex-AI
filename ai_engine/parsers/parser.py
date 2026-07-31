import os

from ai_engine.parsers.pdf_parser import PDFParser
from ai_engine.parsers.docx_parser import DOCXParser


class ResumeParser:

    @staticmethod
    def parse(file_path: str):

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension == ".pdf":
            return PDFParser.extract_text(file_path)

        if extension in [".docx", ".doc"]:
            return DOCXParser.extract_text(file_path)

        raise Exception(
            "Unsupported resume format."
        )