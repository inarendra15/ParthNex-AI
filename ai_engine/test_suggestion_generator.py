from ai_engine.parsers.parser import ResumeParser

from ai_engine.analyzer.section_analyzer import SectionAnalyzer

from ai_engine.analyzer.keyword_analyzer import KeywordAnalyzer

from ai_engine.analyzer.experience_analyzer import ExperienceAnalyzer

from ai_engine.recommendation.suggestion_generator import SuggestionGenerator


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

AWS

Git

"""

section = SectionAnalyzer.analyze(resume)

keyword = KeywordAnalyzer.analyze(
    resume,
    job
)

experience = ExperienceAnalyzer.analyze(
    resume
)

report = SuggestionGenerator.generate(
    section,
    keyword,
    experience
)

print("=" * 60)
print("AI RESUME REPORT")
print("=" * 60)

for k, v in report.items():

    print(f"\n{k.upper()}")

    for item in v:

        print("-", item)