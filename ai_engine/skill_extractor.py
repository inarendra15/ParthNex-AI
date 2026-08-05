import re


class SkillExtractor:
    """
    Extract technical skills from a job description.
    """

    SKILLS = {
        "python",
        "java",
        "c++",
        "c",
        "javascript",
        "typescript",
        "react",
        "angular",
        "vue",
        "nodejs",
        "express",
        "fastapi",
        "django",
        "flask",
        "spring",
        "spring boot",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "postgresql",
        "mysql",
        "mongodb",
        "redis",
        "sqlite",
        "rest api",
        "graphql",
        "git",
        "github",
        "linux",
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "opencv",
        "pandas",
        "numpy",
        "scikit-learn",
        "nlp",
        "langchain",
        "llm",
        "rag",
        "faiss",
        "sql",
        "html",
        "css"
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