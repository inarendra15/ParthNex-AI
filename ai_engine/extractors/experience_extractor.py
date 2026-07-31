import re


class ExperienceExtractor:

    @staticmethod
    def extract(text: str):

        experiences = []

        patterns = [
            r"(.*?)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*?(Present|\d{4})"
        ]

        lines = text.split("\n")

        for line in lines:

            line = line.strip()

            if len(line) < 5:
                continue

            for pattern in patterns:

                if re.search(pattern, line, re.IGNORECASE):

                    experiences.append(line)

        return experiences