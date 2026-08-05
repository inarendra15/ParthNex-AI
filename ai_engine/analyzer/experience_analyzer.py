import re


class ExperienceAnalyzer:

    INTERNSHIP_KEYWORDS = [
        "intern",
        "internship",
        "summer intern",
        "research intern"
    ]

    FULLTIME_KEYWORDS = [
        "software engineer",
        "developer",
        "engineer",
        "analyst",
        "consultant",
        "full time"
    ]

    LEADERSHIP_KEYWORDS = [
        "team lead",
        "leader",
        "coordinator",
        "president",
        "vice president",
        "secretary"
    ]

    RESEARCH_KEYWORDS = [
        "research",
        "publication",
        "paper",
        "journal"
    ]

    @classmethod
    def count_occurrences(cls, text, keywords):

        count = 0

        for word in keywords:

            count += len(
                re.findall(
                    r"\b" + re.escape(word) + r"\b",
                    text
                )
            )

        return count

    @classmethod
    def analyze(cls, text: str):

        text = text.lower()

        internships = cls.count_occurrences(
            text,
            cls.INTERNSHIP_KEYWORDS
        )

        fulltime = cls.count_occurrences(
            text,
            cls.FULLTIME_KEYWORDS
        )

        leadership = cls.count_occurrences(
            text,
            cls.LEADERSHIP_KEYWORDS
        )

        research = cls.count_occurrences(
            text,
            cls.RESEARCH_KEYWORDS
        )

        score = min(
            100,
            internships * 15 +
            fulltime * 35 +
            leadership * 15 +
            research * 15
        )

        return {

            "internships": internships,

            "fulltime_roles": fulltime,

            "leadership_roles": leadership,

            "research_experience": research,

            "experience_score": score

        }