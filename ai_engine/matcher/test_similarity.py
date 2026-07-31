from ai_engine.matcher.similarity import SemanticMatcher

resume = """
Python
FastAPI
PostgreSQL
Docker
Machine Learning
"""

job = """
Backend Engineer

Python

REST API

Docker

SQL
"""

score = SemanticMatcher.similarity(
    resume,
    job
)

print()

print("Similarity:", score)