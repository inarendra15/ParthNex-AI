import re


class SkillExtractor:

    SKILLS = {

        # Programming
        "python",
        "java",
        "c",
        "c++",
        "c#",
        "javascript",
        "typescript",
        "go",
        "rust",
        "php",
        "kotlin",
        "swift",
        "r",

        # Web
        "html",
        "css",
        "bootstrap",
        "react",
        "reactjs",
        "nextjs",
        "angular",
        "vue",
        "nodejs",
        "express",
        "fastapi",
        "django",
        "flask",

        # Database
        "mysql",
        "postgresql",
        "mongodb",
        "sqlite",
        "redis",

        # AI/ML
        "machine learning",
        "deep learning",
        "tensorflow",
        "keras",
        "pytorch",
        "opencv",
        "scikit-learn",
        "numpy",
        "pandas",

        # Cloud
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",

        # Tools
        "git",
        "github",
        "linux",
        "windows",
        "vscode",
        "postman",
        "jira",

        # CS Subjects
        "operating system",
        "computer networks",
        "dbms",
        "sql",
        "oops",
        "data structures",
        "algorithms"
    }

    @staticmethod
    def extract(text: str):

        text = text.lower()

        found = set()

        for skill in SkillExtractor.SKILLS:

            pattern = r"\b" + re.escape(skill) + r"\b"

            if re.search(pattern, text):
                found.add(skill)

        return sorted(found)