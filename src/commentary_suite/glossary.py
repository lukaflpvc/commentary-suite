from __future__ import annotations

from collections import defaultdict

from .models import GlossaryTerm, StyleReport

CATEGORY_MAP: dict[str, set[str]] = {
    "goal_finishing": {"scores", "finish", "clinical", "strikes", "buries", "rifles"},
    "chance_creation": {"threads", "through", "slides", "crosses", "finds", "opens"},
    "defending": {"blocks", "clearance", "presses", "wins", "intercepts"},
    "transition": {"counter", "break", "drives", "turns", "surges"},
    "control_tempo": {"holds", "slows", "calms", "patient", "composed"},
}


def _categorize_phrase(phrase: str) -> str:
    words = set(phrase.split())
    for category, vocabulary in CATEGORY_MAP.items():
        if words & vocabulary:
            return category
    return "general_commentary"


def build_glossary(reports: list[StyleReport]) -> list[GlossaryTerm]:
    bucket: dict[tuple[str, str], GlossaryTerm] = {}
    for report in reports:
        for phrase, count in report.top_phrases:
            category = _categorize_phrase(phrase)
            key = (phrase, category)
            if key not in bucket:
                bucket[key] = GlossaryTerm(
                    phrase=phrase,
                    category=category,
                    count=count,
                    example_video_ids=[report.video_id],
                )
            else:
                bucket[key].count += count
                if report.video_id not in bucket[key].example_video_ids:
                    bucket[key].example_video_ids.append(report.video_id)

    return sorted(bucket.values(), key=lambda item: item.count, reverse=True)


def category_summary(terms: list[GlossaryTerm]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for term in terms:
        counts[term.category] += 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
