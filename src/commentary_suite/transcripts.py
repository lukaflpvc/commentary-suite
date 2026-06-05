from __future__ import annotations

import hashlib
import re
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

from .models import TranscriptDocument, TranscriptSegment

YOUTUBE_ID_PATTERN = re.compile(
    r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[?&]|$)|youtu\.be/([0-9A-Za-z_-]{11})"
)


def extract_youtube_video_id(url: str) -> str:
    match = YOUTUBE_ID_PATTERN.search(url)
    if not match:
        raise ValueError("Could not extract YouTube video id from URL.")
    return next(group for group in match.groups() if group)


def import_from_youtube(
    url: str,
    commentator: str | None = None,
    match_name: str | None = None,
    competition: str | None = None,
    language: str = "en",
) -> TranscriptDocument:
    video_id = extract_youtube_video_id(url)
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id, languages=[language])
    transcript_items = list(fetched)
    segments = [
        TranscriptSegment(
            text=item.text.strip(),
            start=float(item.start),
            duration=float(item.duration),
        )
        for item in transcript_items
        if item.text.strip()
    ]
    if not segments:
        raise ValueError("YouTube transcript was found but contains no usable text segments.")
    return TranscriptDocument(
        video_id=video_id,
        title=match_name or f"YouTube-{video_id}",
        source_type="youtube",
        source_reference=url,
        commentator=commentator,
        match=match_name,
        competition=competition,
        language=language,
        segments=segments,
    )


def _file_video_id(path: Path) -> str:
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:12]
    return f"local-{digest}"


def _segments_from_txt(text: str) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    for line in text.splitlines():
        clean = line.strip()
        if clean:
            segments.append(TranscriptSegment(text=clean))
    return segments


def _segments_from_srt(text: str) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        timing = lines[1] if "-->" in lines[1] else ""
        content_lines = lines[2:] if timing else lines[1:]
        content = " ".join(content_lines).strip()
        if not content:
            continue
        start = None
        duration = None
        if timing:
            start, duration = _parse_srt_timing(timing)
        segments.append(TranscriptSegment(text=content, start=start, duration=duration))
    return segments


def _parse_srt_timing(timing: str) -> tuple[float | None, float | None]:
    def _to_seconds(raw: str) -> float:
        h, m, s = raw.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    try:
        start_raw, end_raw = [part.strip() for part in timing.split("-->")]
        start = _to_seconds(start_raw)
        end = _to_seconds(end_raw)
        return start, max(end - start, 0.0)
    except Exception:
        return None, None


def import_from_file(
    file_path: str,
    commentator: str | None = None,
    match_name: str | None = None,
    competition: str | None = None,
    language: str = "en",
) -> TranscriptDocument:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {file_path}")
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".srt":
        segments = _segments_from_srt(text)
    else:
        segments = _segments_from_txt(text)
    if not segments:
        raise ValueError("Transcript file contains no usable segments.")
    return TranscriptDocument(
        video_id=_file_video_id(path),
        title=match_name or path.stem,
        source_type="file",
        source_reference=str(path),
        commentator=commentator,
        match=match_name,
        competition=competition,
        language=language,
        segments=segments,
    )
