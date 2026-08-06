class CandidateRanker:

    # ==================================================
    # RANKING WEIGHTS
    # ==================================================

    SEMANTIC_WEIGHT = 0.35
    SKILL_WEIGHT = 0.30
    EXPERIENCE_WEIGHT = 0.15
    QUALITY_WEIGHT = 0.10
    SECTION_WEIGHT = 0.10

    # ==================================================
    # CALCULATE RANKING SCORE
    # ==================================================

    @classmethod
    def calculate_score(
        cls,
        semantic_score: float,
        skill_score: float,
        experience_score: float,
        quality_score: float,
        section_score: float
    ) -> float:

        scores = [
            semantic_score,
            skill_score,
            experience_score,
            quality_score,
            section_score
        ]

        # Prevent invalid scores
        scores = [
            max(0.0, min(100.0, float(score)))
            for score in scores
        ]

        (
            semantic_score,
            skill_score,
            experience_score,
            quality_score,
            section_score
        ) = scores

        ranking_score = (
            semantic_score * cls.SEMANTIC_WEIGHT
            + skill_score * cls.SKILL_WEIGHT
            + experience_score * cls.EXPERIENCE_WEIGHT
            + quality_score * cls.QUALITY_WEIGHT
            + section_score * cls.SECTION_WEIGHT
        )

        return round(ranking_score, 2)

    # ==================================================
    # MATCH CLASSIFICATION
    # ==================================================

    @staticmethod
    def classify(score: float) -> str:

        if score >= 80:
            return "Strong Match"

        if score >= 65:
            return "Good Match"

        if score >= 50:
            return "Consider"

        return "Weak Match"

    # ==================================================
    # RANK CANDIDATES
    # ==================================================

    @classmethod
    def rank(cls, candidates: list) -> list:

        ranked_candidates = []

        for candidate in candidates:

            ranking_score = cls.calculate_score(
                semantic_score=candidate.get(
                    "semantic_score",
                    0
                ),
                skill_score=candidate.get(
                    "skill_score",
                    0
                ),
                experience_score=candidate.get(
                    "experience_score",
                    0
                ),
                quality_score=candidate.get(
                    "quality_score",
                    0
                ),
                section_score=candidate.get(
                    "section_score",
                    0
                )
            )

            ranked_candidate = candidate.copy()

            ranked_candidate["ranking_score"] = (
                ranking_score
            )

            ranked_candidate["recommendation"] = (
                cls.classify(ranking_score)
            )

            ranked_candidates.append(
                ranked_candidate
            )

        # Highest score first
        ranked_candidates.sort(
            key=lambda candidate: candidate[
                "ranking_score"
            ],
            reverse=True
        )

        # Assign rank
        for index, candidate in enumerate(
            ranked_candidates,
            start=1
        ):
            candidate["rank"] = index

        return ranked_candidates