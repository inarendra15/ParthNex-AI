import re


class ProjectExtractor:

    @staticmethod
    def extract(text: str):

        projects = []

        patterns = [
            r"Projects?(.*?)(Technical Skills|Experience|Education|Achievements|Languages|$)"
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE | re.DOTALL
            )

            for match in matches:

                if isinstance(match, tuple):
                    content = match[0]
                else:
                    content = match

                content = content.strip()

                if content:
                    projects.append(content)

        return projects