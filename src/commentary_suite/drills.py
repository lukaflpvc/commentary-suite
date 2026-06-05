from __future__ import annotations

from .models import Drill, StyleReport, TranscriptDocument


def generate_drills(document: TranscriptDocument, report: StyleReport, limit: int = 10) -> list[Drill]:
    drills: list[Drill] = []
    key_lines = [segment.text for segment in document.segments if len(segment.text.split()) >= 6][:4]

    for line in key_lines:
        drills.append(
            Drill(
                title="Less Is More Rewrite",
                prompt=f"Rewrite this line in 12 words or fewer without losing intensity:\n{line}",
                source_video_id=document.video_id,
                category="brevity",
            )
        )
        drills.append(
            Drill(
                title="Verb Upgrade",
                prompt=f"Replace any generic verb in this line with a sharper commentary verb:\n{line}",
                source_video_id=document.video_id,
                category="word_choice",
            )
        )

    for phrase, _ in report.top_phrases[:3]:
        drills.append(
            Drill(
                title="Synonym Expansion",
                prompt=f"Create 3 alternative commentary phrases for: '{phrase}'. Keep same meaning, vary rhythm.",
                source_video_id=document.video_id,
                category="synonyms",
            )
        )

    drills.append(
        Drill(
            title="Silence Awareness",
            prompt=(
                "Pick a 20-second section from this clip and mark where silence would be stronger than speech. "
                "Explain why each pause improves the moment."
            ),
            source_video_id=document.video_id,
            category="restraint",
        )
    )

    drills.append(
        Drill(
            title="Style Contrast",
            prompt=(
                "Write one call in a dramatic tone and one in a tactical tone for the same moment. "
                "Then note which words changed and why."
            ),
            source_video_id=document.video_id,
            category="style_range",
        )
    )

    return drills[:limit]
