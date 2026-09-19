"""Sentiment lexicons used as fallback when HF models are disabled.

Each lexicon is a set of normalized tokens (no diacritics, lowercase for
English) so that simple whitespace tokenization matches reliably.
"""

from app.models.lexicons.arabic_negative import NEGATIVE_WORDS_AR
from app.models.lexicons.arabic_positive import POSITIVE_WORDS_AR
from app.models.lexicons.english_negative import NEGATIVE_WORDS_EN
from app.models.lexicons.english_positive import POSITIVE_WORDS_EN

__all__ = [
    "POSITIVE_WORDS_AR",
    "NEGATIVE_WORDS_AR",
    "POSITIVE_WORDS_EN",
    "NEGATIVE_WORDS_EN",
]
