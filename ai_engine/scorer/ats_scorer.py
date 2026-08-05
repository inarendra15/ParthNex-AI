class ATSScorer:

    SEMANTIC_WEIGHT = 0.40
    SKILL_WEIGHT = 0.30
    SECTION_WEIGHT = 0.15
    EXPERIENCE_WEIGHT = 0.10
    QUALITY_WEIGHT = 0.05

    @classmethod
    def calculate(
        cls,
        semantic_score: float,
        skill_score: float,
        section_score: float,
        experience_score: float,
        quality_score: float,
    ) -> float:

        score = (
            semantic_score * cls.SEMANTIC_WEIGHT
            + skill_score * cls.SKILL_WEIGHT
            + section_score * cls.SECTION_WEIGHT
            + experience_score * cls.EXPERIENCE_WEIGHT
            + quality_score * cls.QUALITY_WEIGHT
        )

        return round(score, 2)