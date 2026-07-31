from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.extractors.section_extractor import SectionExtractor

text = ResumeParser.parse(
    "uploads/resumes/SIGNALCHIP.pdf"
)

text = TextCleaner.clean(text)

sections = SectionExtractor.extract(text)

for name, content in sections.items():
    print("\n==========================")
    print(name.upper())
    print("==========================")
    print(content[:600])