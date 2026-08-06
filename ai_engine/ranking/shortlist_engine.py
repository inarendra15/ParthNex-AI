class ShortlistEngine:

    # Minimum score required for automatic shortlisting
    DEFAULT_THRESHOLD = 65.0

    @classmethod
    def shortlist(
        cls,
        ranked_candidates: list,
        threshold: float = DEFAULT_THRESHOLD
    ) -> dict:

        # Keep threshold within valid score range
        threshold = max(
            0.0,
            min(100.0, float(threshold))
        )

        shortlisted = []
        not_shortlisted = []

        for candidate in ranked_candidates:

            ranking_score = float(
                candidate.get(
                    "ranking_score",
                    0
                )
            )

            candidate_result = candidate.copy()

            if ranking_score >= threshold:

                candidate_result["shortlisted"] = True

                shortlisted.append(
                    candidate_result
                )

            else:

                candidate_result["shortlisted"] = False

                not_shortlisted.append(
                    candidate_result
                )

        return {
            "threshold": threshold,

            "total_candidates": len(
                ranked_candidates
            ),

            "shortlisted_count": len(
                shortlisted
            ),

            "not_shortlisted_count": len(
                not_shortlisted
            ),

            "shortlisted": shortlisted,

            "not_shortlisted": not_shortlisted
        }