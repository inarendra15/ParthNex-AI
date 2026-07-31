from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.extractors.skill_extractor import SkillExtractor

text = ResumeParser.parse(
    "uploads/resumes/SIGNALCHIP.pdf"
)

text = TextCleaner.clean(text)

skills = SkillExtractor.extract(text)

print("\nDetected Skills:\n")

for skill in skills:
    print("-", skill)