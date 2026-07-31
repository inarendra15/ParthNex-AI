import re


class TextCleaner:

    @staticmethod
    def clean(text: str):

        text = re.sub(r"\n+", "\n", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()