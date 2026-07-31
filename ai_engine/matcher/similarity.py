from sentence_transformers import util

from ai_engine.embeddings.encoder import ResumeEncoder


class SemanticMatcher:

    @staticmethod
    def similarity(text1: str, text2: str):

        emb1 = ResumeEncoder.encode(text1)
        emb2 = ResumeEncoder.encode(text2)

        score = util.cos_sim(
            emb1,
            emb2
        )

        return float(score)