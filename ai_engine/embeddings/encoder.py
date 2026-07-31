from sentence_transformers import SentenceTransformer


class ResumeEncoder:

    # Load model only once
    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    @staticmethod
    def encode(text: str):

        return ResumeEncoder.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )