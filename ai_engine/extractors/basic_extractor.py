import re


class BasicExtractor:

    @staticmethod
    def extract_name(text: str):

        lines = text.split("\n")

        for line in lines[:5]:
            line = line.strip()

            if len(line.split()) >= 2 and len(line) < 50:
                return line

        return ""

    @staticmethod
    def extract_email(text: str):

        match = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text
        )

        return match.group() if match else ""

    @staticmethod
    def extract_phone(text: str):

        match = re.search(
            r"(\+91[- ]?)?[6-9]\d{9}",
            text
        )

        return match.group() if match else ""