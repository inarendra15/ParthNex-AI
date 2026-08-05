import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.matcher.skill_matcher import SkillMatcher

job_skills = [
    "Python",
    "FastAPI",
    "Docker",
    "AWS",
    "REST API"
]

resume_skills = [
    "Python",
    "Docker",
    "FastAPI",
    "PostgreSQL",
    "Git"
]

result = SkillMatcher.match(
    job_skills,
    resume_skills
)

print(result)