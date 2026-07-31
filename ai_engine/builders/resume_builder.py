from ai_engine.schemas.resume_schema import (
    ResumeData,
    ResumeProfile
)

from ai_engine.extractors.basic_extractor import BasicExtractor
from ai_engine.extractors.skill_extractor import SkillExtractor
from ai_engine.extractors.education_extractor import EducationExtractor
from ai_engine.extractors.experience_extractor import ExperienceExtractor
from ai_engine.extractors.project_extractor import ProjectExtractor


class ResumeBuilder:

    @staticmethod
    def build(text: str):

        profile = BasicExtractor.extract(text)

        return ResumeData(
            profile=ResumeProfile(
                name=profile.get("name", ""),
                email=profile.get("email", ""),
                phone=profile.get("phone", ""),
                linkedin=profile.get("linkedin", ""),
                github=profile.get("github", "")
            ),
            skills=SkillExtractor.extract(text),
            education=EducationExtractor.extract(text),
            experience=ExperienceExtractor.extract(text),
            projects=ProjectExtractor.extract(text)
        )