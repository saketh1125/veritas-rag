import numpy as np
from sentence_transformers import SentenceTransformer


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve(query, chunks, chunk_embeddings, top_k=3):
    """
    Retrieves top-k relevant chunks.
    Returns tuples: (score, index, chunk_dict)
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query])[0]

    scores = []
    for i, emb in enumerate(chunk_embeddings):
        score = cosine_similarity(query_embedding, emb)
        scores.append((score, i, chunks[i]))

    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]
