from ai_engine.parsers.parser import ResumeParser
from ai_engine.preprocess.cleaner import TextCleaner
from ai_engine.embeddings.encoder import ResumeEncoder

text = ResumeParser.parse(
    "uploads/resumes/SIGNALCHIP.pdf"
)

text = TextCleaner.clean(text)

embedding = ResumeEncoder.encode(text)

print(type(embedding))
print()

print(embedding.shape)
print()

print(embedding[:20])