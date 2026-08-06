from ai_engine.ranking.candidate_ranker import CandidateRanker


candidates = [
    {
        "candidate_id": 1,
        "candidate_name": "Candidate A",
        "semantic_score": 65.71,
        "skill_score": 37.5,
        "experience_score": 45,
        "quality_score": 80,
        "section_score": 70
    },
    {
        "candidate_id": 2,
        "candidate_name": "Candidate B",
        "semantic_score": 85,
        "skill_score": 75,
        "experience_score": 70,
        "quality_score": 90,
        "section_score": 80
    },
    {
        "candidate_id": 3,
        "candidate_name": "Candidate C",
        "semantic_score": 55,
        "skill_score": 25,
        "experience_score": 30,
        "quality_score": 60,
        "section_score": 50
    }
]


results = CandidateRanker.rank(
    candidates
)


print("\n" + "=" * 60)
print("CANDIDATE RANKING")
print("=" * 60)


for candidate in results:

    print()

    print(
        "Rank:",
        candidate["rank"]
    )

    print(
        "Candidate:",
        candidate["candidate_name"]
    )

    print(
        "Ranking Score:",
        candidate["ranking_score"]
    )

    print(
        "Recommendation:",
        candidate["recommendation"]
    )