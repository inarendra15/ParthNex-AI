from docx import Document


class DOCXParser:

    @staticmethod
    def extract_text(file_path: str):

        document = Document(file_path)

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )