class SuggestionGenerator:

    @staticmethod
    def generate(
        section_result: dict,
        keyword_result: dict,
        experience_result: dict
    ):

        suggestions = []

        strengths = []

        weaknesses = []

        # -----------------------------
        # Missing Resume Sections
        # -----------------------------

        important_sections = [
            "summary",
            "skills",
            "education",
            "experience",
            "projects"
        ]

        for section in important_sections:

            if not section_result.get(section, False):

                suggestions.append(
                    f"Add a {section.title()} section."
                )

                weaknesses.append(
                    f"Missing {section.title()} section"
                )

            else:

                strengths.append(
                    f"{section.title()} section present"
                )

        # -----------------------------
        # Missing Skills
        # -----------------------------

        missing = keyword_result["missing_skills"]

        if missing:

            suggestions.append(

                "Consider adding these skills if applicable: "

                + ", ".join(missing)

            )

            weaknesses.append(

                f"{len(missing)} required skills missing"

            )

        else:

            strengths.append(
                "Excellent skill coverage"
            )

        # -----------------------------
        # GitHub
        # -----------------------------

        if not section_result["github"]:

            suggestions.append(
                "Add your GitHub profile."
            )

            weaknesses.append(
                "GitHub profile missing"
            )

        else:

            strengths.append(
                "GitHub profile included"
            )

        # -----------------------------
        # LinkedIn
        # -----------------------------

        if not section_result["linkedin"]:

            suggestions.append(
                "Add your LinkedIn profile."
            )

            weaknesses.append(
                "LinkedIn profile missing"
            )

        else:

            strengths.append(
                "LinkedIn profile included"
            )

        # -----------------------------
        # Experience
        # -----------------------------

        if experience_result["internships"] == 0:

            suggestions.append(
                "Try gaining internship experience."
            )

            weaknesses.append(
                "No internship experience"
            )

        else:

            strengths.append(
                "Internship experience present"
            )

        if experience_result["research_experience"] > 0:

            strengths.append(
                "Research experience detected"
            )

        # -----------------------------
        # Overall
        # -----------------------------

        return {

            "strengths": strengths,

            "weaknesses": weaknesses,

            "suggestions": suggestions

        }