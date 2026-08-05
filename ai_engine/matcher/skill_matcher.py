class SkillMatcher:

    @staticmethod
    def match(job_skills, resume_skills):

        # Normalize skills
        job = {skill.lower() for skill in job_skills}
        resume = {skill.lower() for skill in resume_skills}

        matched = sorted(job & resume)
        missing = sorted(job - resume)

        if len(job) == 0:
            score = 0.0
        else:
            score = round(len(matched) / len(job) * 100, 2)

        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_score": score
        }