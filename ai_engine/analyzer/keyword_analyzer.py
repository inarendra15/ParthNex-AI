from ai_engine.skill_extractor import SkillExtractor
from ai_engine.matcher.skill_matcher import SkillMatcher


class KeywordAnalyzer:

    @staticmethod
    def analyze(
        resume_text: str,
        job_description: str
    ):

        # Extract skills
        resume_skills = SkillExtractor.extract(
            resume_text
        )

        job_skills = SkillExtractor.extract(
            job_description
        )

        # Match job requirements against resume skills
        match_result = SkillMatcher.match(
            job_skills,
            resume_skills
        )

        matched = match_result["matched_skills"]
        missing = match_result["missing_skills"]
        score = match_result["skill_score"]

        # Skills present in resume but not required by job
        extra = sorted(
            list(
                set(resume_skills) -
                set(job_skills)
            )
        )

        coverage = 0.0

        if len(job_skills) > 0:
            coverage = round(
                len(matched) /
                len(job_skills) *
                100,
                2
            )

        return {
            "resume_skills": sorted(resume_skills),
            "job_skills": sorted(job_skills),
            "matched_skills": matched,
            "missing_skills": missing,
            "extra_skills": extra,
            "coverage": coverage,
            "skill_score": score
        }