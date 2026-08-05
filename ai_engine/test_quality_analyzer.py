from ai_engine.parsers.parser import ResumeParser
from ai_engine.analyzer.quality_analyzer import QualityAnalyzer


resume_text = ResumeParser.parse(
    "server/uploads/resumes/d74eabd0-e3d0-4337-8c70-4c1133357c1a.pdf"
)

result = QualityAnalyzer.analyze(
    resume_text
)

print("\n========== QUALITY ANALYSIS ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")