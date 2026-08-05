from ai_engine.scorer.ats_scorer import ATSScorer


score = ATSScorer.calculate(
    semantic_score=82,
    skill_score=75,
    section_score=90,
    experience_score=70,
    quality_score=80,
)

print("ATS Score:", score)