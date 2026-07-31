from pprint import pprint

from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.builders.resume_builder import ResumeBuilder

text = ResumeParser.parse(
    "uploads/resumes/SIGNALCHIP.pdf"
)

text = TextCleaner.clean(text)

resume = ResumeBuilder.build(text)

pprint(resume)