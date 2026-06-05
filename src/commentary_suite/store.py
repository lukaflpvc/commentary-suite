from __future__ import annotations

import json
import re
from pathlib import Path

from .models import GlossaryTerm, StyleReport, TranscriptDocument


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def data_dir(base_dir: str | None = None) -> Path:
    if base_dir:
        root = Path(base_dir)
    else:
        root = Path.cwd() / "data"
    root.mkdir(parents=True, exist_ok=True)
    return root


def transcript_path(video_id: str, base_dir: str | None = None) -> Path:
    path = data_dir(base_dir) / "transcripts"
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{slugify(video_id)}.json"


def style_report_path(video_id: str, base_dir: str | None = None) -> Path:
    path = data_dir(base_dir) / "analysis"
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{slugify(video_id)}.json"


def glossary_path(base_dir: str | None = None) -> Path:
    return data_dir(base_dir) / "glossary.json"


def save_transcript(document: TranscriptDocument, base_dir: str | None = None) -> Path:
    path = transcript_path(document.video_id, base_dir)
    path.write_text(json.dumps(document.to_dict(), indent=2), encoding="utf-8")
    return path


def load_transcript(video_id: str, base_dir: str | None = None) -> TranscriptDocument:
    path = transcript_path(video_id, base_dir)
    return TranscriptDocument.from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_transcripts(base_dir: str | None = None) -> list[TranscriptDocument]:
    path = data_dir(base_dir) / "transcripts"
    if not path.exists():
        return []
    documents: list[TranscriptDocument] = []
    for file in sorted(path.glob("*.json")):
        documents.append(TranscriptDocument.from_dict(json.loads(file.read_text(encoding="utf-8"))))
    return documents


def save_style_report(report: StyleReport, base_dir: str | None = None) -> Path:
    path = style_report_path(report.video_id, base_dir)
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return path


def load_style_report(video_id: str, base_dir: str | None = None) -> StyleReport:
    path = style_report_path(video_id, base_dir)
    return StyleReport.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_glossary(terms: list[GlossaryTerm], base_dir: str | None = None) -> Path:
    path = glossary_path(base_dir)
    payload = [term.to_dict() for term in terms]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_glossary(base_dir: str | None = None) -> list[GlossaryTerm]:
    path = glossary_path(base_dir)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [GlossaryTerm.from_dict(item) for item in payload]
