import re


class SectionAnalyzer:

    SECTIONS = {
        "summary": [
            "summary",
            "professional summary",
            "profile",
            "objective",
            "career objective"
        ],

        "skills": [
            "skills",
            "technical skills",
            "core skills",
            "competencies"
        ],

        "education": [
            "education",
            "academic background",
            "qualification"
        ],

        "experience": [
            "experience",
            "work experience",
            "employment",
            "professional experience"
        ],

        "projects": [
            "projects",
            "academic projects",
            "personal projects"
        ],

        "certifications": [
            "certifications",
            "certificates",
            "licenses"
        ],

        "achievements": [
            "achievements",
            "awards",
            "honors"
        ],

        "languages": [
            "languages"
        ]
    }

    @classmethod
    def analyze(cls, text: str):

        text = text.lower()

        result = {}

        found = 0

        total = len(cls.SECTIONS) + 2

        for section, keywords in cls.SECTIONS.items():

            present = any(
                re.search(r"\b" + re.escape(word) + r"\b", text)
                for word in keywords
            )

            result[section] = present

            if present:
                found += 1

        github = (
            "github.com" in text
        )

        linkedin = (
            "linkedin.com" in text
        )

        result["github"] = github
        result["linkedin"] = linkedin

        if github:
            found += 1

        if linkedin:
            found += 1

        result["section_score"] = round(
            (found / total) * 100,
            2
        )

        return result