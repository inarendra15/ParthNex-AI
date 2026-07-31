from app.services.job_matching_service import JobMatchingService

job = """
Backend Python Developer

Python
FastAPI
REST API
Docker
PostgreSQL
Machine Learning
"""

results = JobMatchingService.search(
    job,
    top_k=5
)

print(results)