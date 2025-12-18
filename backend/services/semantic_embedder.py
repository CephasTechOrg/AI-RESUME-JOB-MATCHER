from functools import lru_cache
from typing import Iterable, List, Optional, Tuple

import numpy as np

try:
    from sentence_transformers import SentenceTransformer, util
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None
    util = None


class SemanticEmbedder:
    """
    Thin wrapper around sentence-transformers with caching and graceful fallback
    when the model isn't available (e.g., offline environments).
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        if SentenceTransformer:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

    @lru_cache(maxsize=256)
    def _encode(self, text: str) -> Optional[np.ndarray]:
        if not self.model or not text.strip():
            return None
        return self.model.encode(text, normalize_embeddings=True)

    def similarity(self, text: str, candidates: Iterable[str]) -> Tuple[float, Optional[str]]:
        """
        Returns the best similarity score and the candidate phrase that matched.
        """
        if not self.model or not util:
            return 0.0, None

        base_emb = self._encode(text)
        if base_emb is None:
            return 0.0, None

        best_score = 0.0
        best_phrase: Optional[str] = None

        for phrase in candidates:
            emb = self._encode(phrase)
            if emb is None:
                continue
            score = float(util.cos_sim(base_emb, emb))
            if score > best_score:
                best_score = score
                best_phrase = phrase

        return best_score, best_phrase

    def any_above_threshold(self, text: str, candidates: Iterable[str], threshold: float = 0.6) -> Tuple[bool, float, Optional[str]]:
        score, phrase = self.similarity(text, candidates)
        return score >= threshold, score, phrase
