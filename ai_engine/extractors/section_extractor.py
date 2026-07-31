import re


class SectionExtractor:

    HEADINGS = [
        "profile",
        "summary",
        "education",
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "projects",
        "technical skills",
        "skills",
        "certifications",
        "achievements",
        "languages",
    ]

    @staticmethod
    def extract(text: str):

        sections = {}

        matches = []

        for heading in SectionExtractor.HEADINGS:

            pattern = re.compile(
                rf"(?im)^\s*{re.escape(heading)}\s*$"
            )

            for match in pattern.finditer(text):
                matches.append(
                    (
                        match.start(),
                        heading
                    )
                )

        matches.sort()

        for i, (start, heading) in enumerate(matches):

            if i + 1 < len(matches):
                end = matches[i + 1][0]
            else:
                end = len(text)

            sections[heading] = text[start:end].strip()

        return sections