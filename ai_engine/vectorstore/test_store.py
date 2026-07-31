from ai_engine.embeddings.encoder import ResumeEncoder
from ai_engine.vectorstore.faiss_store import ResumeVectorStore


store = ResumeVectorStore()

encoder = ResumeEncoder()

resume1 = """
Python
FastAPI
SQL
Docker
"""

resume2 = """
React
JavaScript
NodeJS
MongoDB
"""

resume3 = """
Machine Learning
PyTorch
TensorFlow
Deep Learning
"""

store.add(
    1,
    encoder.encode(resume1)
)

store.add(
    2,
    encoder.encode(resume2)
)

store.add(
    3,
    encoder.encode(resume3)
)
store.save()
store = ResumeVectorStore.load()

job = """
Python
FastAPI
REST API
Docker
"""

results = store.search(
    encoder.encode(job),
    top_k=3
)

print(results)