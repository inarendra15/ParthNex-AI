from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.extractors.experience_extractor import ExperienceExtractor

text = ResumeParser.parse(
    "uploads/resumes/SIGNALCHIP.pdf"
)

text = TextCleaner.clean(text)

experience = ExperienceExtractor.extract(text)

print("\nDetected Experience:\n")

for exp in experience:
    print("-", exp)