import re


class QualityAnalyzer:

    @staticmethod
    def analyze(text: str):

        if not text or not text.strip():
            return {
                "word_count": 0,
                "bullet_count": 0,
                "quantified_achievements": 0,
                "action_verbs_found": [],
                "quality_score": 0.0
            }

        text_lower = text.lower()

        # -----------------------------
        # Word Count
        # -----------------------------

        words = re.findall(
            r"\b\w+\b",
            text
        )

        word_count = len(words)

        # -----------------------------
        # Bullet Points
        # -----------------------------

        bullet_count = len(
            re.findall(
                r"(?m)^\s*[•●▪◦\-]\s+",
                text
            )
        )

        # -----------------------------
        # Quantified Achievements
        # -----------------------------

        quantified_achievements = len(
            re.findall(
                r"\b\d+(?:\.\d+)?\s*%",
                text
            )
        )

        # -----------------------------
        # Action Verbs
        # -----------------------------

        action_verbs = [
            "developed",
            "implemented",
            "designed",
            "built",
            "created",
            "optimized",
            "improved",
            "managed",
            "led",
            "automated",
            "deployed",
            "integrated",
            "trained",
            "analyzed",
            "achieved"
        ]

        action_verbs_found = sorted(
            {
                verb
                for verb in action_verbs
                if re.search(
                    r"\b" + re.escape(verb) + r"\b",
                    text_lower
                )
            }
        )

        # -----------------------------
        # Quality Scoring
        # -----------------------------

        score = 0.0

        # Appropriate resume length
        if 300 <= word_count <= 1000:
            score += 30

        elif 200 <= word_count < 300:
            score += 20

        elif word_count > 1000:
            score += 15

        # Bullet usage
        if bullet_count >= 10:
            score += 25

        elif bullet_count >= 5:
            score += 15

        elif bullet_count > 0:
            score += 10

        # Quantified achievements
        if quantified_achievements >= 3:
            score += 20

        elif quantified_achievements >= 1:
            score += 10

        # Strong action verbs
        action_count = len(action_verbs_found)

        if action_count >= 6:
            score += 25

        elif action_count >= 3:
            score += 15

        elif action_count >= 1:
            score += 10

        return {
            "word_count": word_count,
            "bullet_count": bullet_count,
            "quantified_achievements": quantified_achievements,
            "action_verbs_found": action_verbs_found,
            "quality_score": round(
                min(score, 100.0),
                2
            )
        }