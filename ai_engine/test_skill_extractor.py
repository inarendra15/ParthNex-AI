from skill_extractor import SkillExtractor


job = """
Python Backend Developer

Python
FastAPI
REST API
Docker
PostgreSQL
Machine Learning
Git
AWS
"""

skills = SkillExtractor.extract(job)

print(skills)