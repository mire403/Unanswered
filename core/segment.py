from __future__ import annotations

import re
from typing import List

from unanswered.schemas.question import Utterance


SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def split_into_sentences(text: str) -> List[str]:
    """
    Simple rule-based sentence splitter.
    For production, swap this for spaCy or a more robust segmenter.
    """
    text = text.strip()
    if not text:
        return []
    parts = SENTENCE_END_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def segment_utterances(utterances: List[Utterance]) -> List[Utterance]:
    """
    For now we keep utterances as-is and rely on the LLM
    to handle intra-utterance sentence-level classification.

    This function is a placeholder if you later want to explode each
    utterance into multiple sentence-level segments.
    """
    return utterances

