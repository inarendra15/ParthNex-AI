import re


class EducationExtractor:

    @staticmethod
    def extract(text: str):

        education = []

        patterns = [
            r"(M\.?Tech.*?)(?=B\.?Tech|XII|10th|Projects|Skills|Experience|$)",
            r"(B\.?Tech.*?)(?=M\.?Tech|XII|10th|Projects|Skills|Experience|$)",
            r"(Bachelor.*?)(?=Master|Projects|Skills|Experience|$)",
            r"(Master.*?)(?=Projects|Skills|Experience|$)",
        ]

        for pattern in patterns:
            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE | re.DOTALL
            )

            for match in matches:
                education.append(match.strip())

        return list(dict.fromkeys(education))