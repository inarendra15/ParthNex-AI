from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner

text = ResumeParser.parse(
    "uploads/resumes/SIGNALCHIP.pdf"
)

text = TextCleaner.clean(text)

print(text)