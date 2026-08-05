from ai_engine.parsers.parser import ResumeParser

from ai_engine.analyzer.experience_analyzer import ExperienceAnalyzer


resume = ResumeParser.parse(
    "server/uploads/resumes/d74eabd0-e3d0-4337-8c70-4c1133357c1a.pdf"
)

result = ExperienceAnalyzer.analyze(
    resume
)

print()

print("=" * 50)

print("EXPERIENCE ANALYSIS")

print("=" * 50)

for key, value in result.items():
    print(f"{key:25} {value}")