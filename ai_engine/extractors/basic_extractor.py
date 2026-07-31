import re


class BasicExtractor:

    @staticmethod
    def extract(text: str):

        profile = {
            "name": "",
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": ""
        }

        # Email
        email = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text
        )

        if email:
            profile["email"] = email.group()

        # Phone
        phone = re.search(
            r"(\+91[-\s]?)?[6-9]\d{9}",
            text
        )

        if phone:
            profile["phone"] = phone.group()

        # LinkedIn
        linkedin = re.search(
            r"(https?://)?(www\.)?linkedin\.com/[^\s]+",
            text,
            re.IGNORECASE
        )

        if linkedin:
            profile["linkedin"] = linkedin.group()

        # GitHub
        github = re.search(
            r"(https?://)?(www\.)?github\.com/[^\s]+",
            text,
            re.IGNORECASE
        )

        if github:
            profile["github"] = github.group()

        # Name (assume first non-empty line)
        for line in text.split("\n"):
            line = line.strip()

            if (
                len(line) > 3
                and "@" not in line
                and not re.search(r"\d", line)
            ):
                profile["name"] = line
                break

        return profile