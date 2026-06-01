"""
Shared, dependency-free text embedding + cosine similarity.

Identical hashed bag-of-words scheme used when the DB was built, so the
vectors stored in case_notes.embedding are comparable to a freshly embedded
live query. Production would swap this for Vertex AI / Gemini embeddings — the
clustering and KNN logic above it does not change.
"""
import hashlib, math

EMBED_DIM = 64

def embed(text: str):
    vec = [0.0] * EMBED_DIM
    for tok in "".join(c.lower() if c.isalpha() else " " for c in text).split():
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16) % EMBED_DIM
        vec[h] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]

def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))  # both are L2-normalised
