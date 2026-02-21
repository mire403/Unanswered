from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from unanswered.schemas.question import Utterance


@dataclass
class RawLine:
    """Represents a raw line from an input source."""

    text: str
    metadata: Optional[dict] = None


def parse_lines(lines: Iterable[str]) -> List[Utterance]:
    """
    Very simple parser that treats each line as one utterance.

    Expected (but optional) soft-conventions:
      - "[HH:MM] user: message"
      - "user: message"
    For production, replace this with format-specific parsers (GitHub, Slack, etc.).
    """
    utterances: List[Utterance] = []
    for idx, raw in enumerate(lines):
        raw = raw.strip()
        if not raw:
            continue

        speaker: Optional[str] = None
        timestamp: Optional[str] = None
        text = raw

        # crude parsing for "speaker: message"
        if ":" in raw:
            possible_speaker, rest = raw.split(":", 1)
            if 1 <= len(possible_speaker.split()) <= 3:
                speaker = possible_speaker.strip()
                text = rest.strip()

        utterances.append(
            Utterance(
                id=idx,
                speaker=speaker,
                timestamp=timestamp,
                text=text,
            )
        )
    return utterances

