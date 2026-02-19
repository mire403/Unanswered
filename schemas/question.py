from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class QuestionType(str, Enum):
    CLARIFICATION = "clarification"
    DECISION = "decision"
    TECHNICAL = "technical"
    OPEN_ENDED = "open_ended"
    RHETORICAL = "rhetorical"


class ResolutionStatus(str, Enum):
    ANSWERED = "answered"
    PARTIALLY_ANSWERED = "partially_answered"
    UNANSWERED = "unanswered"
    UNCERTAIN = "uncertain"


@dataclass
class Utterance:
    """Single message/line in the discussion."""

    id: int
    speaker: Optional[str]
    timestamp: Optional[str]
    text: str


@dataclass
class QuestionEvidence:
    """Evidence for why we consider a question answered or not."""

    supporting_utterance_ids: List[int] = field(default_factory=list)
    missing_utterance_ids: List[int] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class QuestionCandidate:
    """Raw question detected at sentence/utterance level before clustering."""

    id: int
    utterance_id: int
    text: str
    asker: Optional[str]
    timestamp: Optional[str]
    question_type: Optional[QuestionType] = None
    is_rhetorical: bool = False


@dataclass
class QuestionCluster:
    """Cluster of similar/duplicate questions."""

    id: int
    canonical_text: str
    member_ids: List[int]


@dataclass
class QuestionResolution:
    """Final structured result for a question or cluster of questions."""

    cluster_id: int
    canonical_text: str
    askers: List[Optional[str]]
    timestamps: List[Optional[str]]
    question_type: Optional[QuestionType]
    status: ResolutionStatus
    answered_by_utterance_ids: List[int] = field(default_factory=list)
    evidence: Optional[QuestionEvidence] = None

