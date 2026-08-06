from ai_engine.ranking.candidate_ranker import CandidateRanker
from ai_engine.ranking.shortlist_engine import ShortlistEngine


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


# Rank candidates first
ranked_candidates = CandidateRanker.rank(
    candidates
)


# Shortlist candidates
result = ShortlistEngine.shortlist(
    ranked_candidates,
    threshold=65
)


print("\n" + "=" * 60)
print("CANDIDATE SHORTLISTING")
print("=" * 60)

print(
    "\nThreshold:",
    result["threshold"]
)

print(
    "Total Candidates:",
    result["total_candidates"]
)

print(
    "Shortlisted:",
    result["shortlisted_count"]
)

print(
    "Not Shortlisted:",
    result["not_shortlisted_count"]
)


print("\nSHORTLISTED CANDIDATES")

for candidate in result["shortlisted"]:

    print(
        f'Rank {candidate["rank"]} | '
        f'{candidate["candidate_name"]} | '
        f'{candidate["ranking_score"]} | '
        f'{candidate["recommendation"]}'
    )


print("\nNOT SHORTLISTED")

for candidate in result["not_shortlisted"]:

    print(
        f'Rank {candidate["rank"]} | '
        f'{candidate["candidate_name"]} | '
        f'{candidate["ranking_score"]} | '
        f'{candidate["recommendation"]}'
    )