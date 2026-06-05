from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class TranscriptSegment:
    text: str
    start: float | None = None
    duration: float | None = None


@dataclass(slots=True)
class TranscriptDocument:
    video_id: str
    title: str
    source_type: str
    source_reference: str
    commentator: str | None = None
    match: str | None = None
    competition: str | None = None
    language: str = "en"
    imported_at: str = field(default_factory=utc_now_iso)
    segments: list[TranscriptSegment] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TranscriptDocument":
        segments = [TranscriptSegment(**segment) for segment in data.get("segments", [])]
        return cls(
            video_id=data["video_id"],
            title=data.get("title", data["video_id"]),
            source_type=data["source_type"],
            source_reference=data["source_reference"],
            commentator=data.get("commentator"),
            match=data.get("match"),
            competition=data.get("competition"),
            language=data.get("language", "en"),
            imported_at=data.get("imported_at", utc_now_iso()),
            segments=segments,
            tags=data.get("tags", []),
        )


@dataclass(slots=True)
class StyleReport:
    video_id: str
    commentator: str | None
    total_words: int
    unique_words: int
    avg_words_per_segment: float
    avg_sentence_length: float
    filler_density: float
    less_is_more_score: float
    top_words: list[tuple[str, int]]
    top_phrases: list[tuple[str, int]]
    top_verbs: list[tuple[str, int]]
    top_adjectives: list[tuple[str, int]]
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StyleReport":
        return cls(**data)


@dataclass(slots=True)
class GlossaryTerm:
    phrase: str
    category: str
    count: int
    example_video_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GlossaryTerm":
        return cls(**data)


@dataclass(slots=True)
class Drill:
    title: str
    prompt: str
    source_video_id: str
    category: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
