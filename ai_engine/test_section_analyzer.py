from ai_engine.parsers.parser import ResumeParser

from ai_engine.analyzer.section_analyzer import SectionAnalyzer


text = ResumeParser.parse(
    "server/uploads/resumes/d74eabd0-e3d0-4337-8c70-4c1133357c1a.pdf"
)

result = SectionAnalyzer.analyze(text)

print()

print("========== SECTION ANALYSIS ==========\n")

for key, value in result.items():
    print(f"{key:20} {value}")