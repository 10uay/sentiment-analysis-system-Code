import hashlib
import json
import math
from pathlib import Path
import numpy as np
from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.model = None
        self._try_load_sentence_transformer()

    def _try_load_sentence_transformer(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            self.dim = self.model.get_sentence_embedding_dimension()
        except Exception:
            self.model = None

    # Convert text to a numeric vector
    def embed(self, text: str) -> list[float]:
        # Convert text to a numeric vector. Use the real model if available,
        # otherwise fallback to hash-based embedding.
        if self.model:
            # [text] for batch input; normalize for simpler cosine similarity.
            emb = self.model.encode([text], normalize_embeddings=True)[0]
            return emb.astype(float).tolist()
        return self._hash_embedding(text)

    def _hash_embedding(self, text: str) -> list[float]:
        # Builds a deterministic vector from token hashes (no semantic meaning).
        vec = np.zeros(self.dim, dtype=float)
        for token in text.lower().split():
            # Hash each token (word) with SHA256 to get a deterministic position and sign.
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            # Map the hash to a valid index in the vector.
            idx = int.from_bytes(digest[:4], "little") % self.dim
            # Use a byte from the hash to decide +1 or -1.
            sign = 1 if digest[4] % 2 == 0 else -1
            vec[idx] += sign
        # Normalize to unit length so cosine similarity still works.
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec.tolist()
        return (vec / norm).tolist()

    # Compute cosine similarity between two embedding vectors.
    # Measures the angle between vectors: 1.0 = identical, 0.0 = unrelated, -1.0 = opposite.
    @staticmethod
    def cosine(a: list[float], b: list[float]) -> float:
        # dot = dot product (sum of element-wise products)
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        # Guard against division by zero if either vector has zero magnitude.
        return float(dot / (na * nb)) if na and nb else 0.0

    # create/update the vector_index. 
    def save_index(self, items: list[dict], path: str | None = None):
        path = path or settings.vector_index_path
        Path(path).write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    # load the vector_index file (it is List), otherwise return empty List
    def load_index(self, path: str | None = None) -> list[dict]:
        path = path or settings.vector_index_path
        p = Path(path)
        if not p.exists():
            return []
        return json.loads(p.read_text(encoding="utf-8"))
