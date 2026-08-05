from ai_engine.parsers.parser import ResumeParser

from ai_engine.analyzer.keyword_analyzer import KeywordAnalyzer


resume = ResumeParser.parse(
    "server/uploads/resumes/d74eabd0-e3d0-4337-8c70-4c1133357c1a.pdf"
)

job = """

Python

FastAPI

Docker

REST API

Machine Learning

PostgreSQL

Git

AWS

"""


result = KeywordAnalyzer.analyze(
    resume,
    job
)

print()

print("=" * 50)

print("KEYWORD ANALYSIS")

print("=" * 50)

for k, v in result.items():

    print(f"{k} :")

    print(v)

    print()