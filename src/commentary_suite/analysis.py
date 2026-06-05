from __future__ import annotations

import re
from collections import Counter

from .models import StyleReport, TranscriptDocument

WORD_RE = re.compile(r"[a-zA-Z']+")
SENTENCE_RE = re.compile(r"[.!?]+")
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "for",
    "with",
    "on",
    "at",
    "by",
    "is",
    "it",
    "that",
    "this",
    "as",
    "be",
    "are",
    "was",
    "were",
    "he",
    "she",
    "they",
    "you",
    "i",
    "we",
}
FILLER_WORDS = {"really", "very", "just", "maybe", "kind", "sort", "quite", "well"}
COMMON_VERBS = {
    "drives",
    "passes",
    "slides",
    "presses",
    "wins",
    "scores",
    "shoots",
    "crosses",
    "finds",
    "holds",
    "spins",
    "delivers",
    "threads",
}
COMMON_ADJECTIVES = {
    "brilliant",
    "clinical",
    "sharp",
    "dangerous",
    "composed",
    "quick",
    "nervous",
    "excellent",
    "clean",
    "superb",
}


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]


def _extract_phrases(tokens: list[str], n: int = 2) -> Counter[str]:
    phrases = Counter()
    for idx in range(len(tokens) - n + 1):
        phrase = " ".join(tokens[idx : idx + n])
        if any(token in STOPWORDS for token in phrase.split()):
            continue
        phrases[phrase] += 1
    return phrases


def _sentence_lengths(text: str) -> list[int]:
    fragments = [part.strip() for part in SENTENCE_RE.split(text) if part.strip()]
    lengths = [len(_tokenize(fragment)) for fragment in fragments]
    return [length for length in lengths if length > 0]


def analyze_document(document: TranscriptDocument) -> StyleReport:
    full_text = "\n".join(segment.text for segment in document.segments)
    tokens = _tokenize(full_text)
    total_words = len(tokens)
    if total_words == 0:
        raise ValueError("Cannot analyze an empty transcript.")

    counts = Counter(tokens)
    cleaned_counts = Counter({token: count for token, count in counts.items() if token not in STOPWORDS})

    sentence_lengths = _sentence_lengths(full_text)
    avg_sentence_length = (sum(sentence_lengths) / len(sentence_lengths)) if sentence_lengths else 0.0
    avg_words_per_segment = total_words / max(len(document.segments), 1)

    filler_count = sum(counts.get(word, 0) for word in FILLER_WORDS)
    filler_density = filler_count / total_words

    bigrams = _extract_phrases(tokens, n=2)
    trigrams = _extract_phrases(tokens, n=3)
    phrases = bigrams + trigrams

    verbs = Counter({token: count for token, count in counts.items() if token in COMMON_VERBS or token.endswith("ing")})
    adjectives = Counter(
        {
            token: count
            for token, count in counts.items()
            if token in COMMON_ADJECTIVES or token.endswith("ive") or token.endswith("ful")
        }
    )

    repetition_penalty = min((sum(1 for _, count in cleaned_counts.items() if count >= 4) / 20), 1.0)
    length_penalty = min(max((avg_sentence_length - 14) / 18, 0), 1.0)
    filler_penalty = min(filler_density * 5, 1.0)
    less_is_more_score = max(0.0, min(100.0, 100.0 * (1 - (0.4 * length_penalty + 0.4 * filler_penalty + 0.2 * repetition_penalty))))

    return StyleReport(
        video_id=document.video_id,
        commentator=document.commentator,
        total_words=total_words,
        unique_words=len(set(tokens)),
        avg_words_per_segment=round(avg_words_per_segment, 2),
        avg_sentence_length=round(avg_sentence_length, 2),
        filler_density=round(filler_density, 4),
        less_is_more_score=round(less_is_more_score, 2),
        top_words=cleaned_counts.most_common(15),
        top_phrases=[item for item in phrases.most_common(15) if item[1] > 1],
        top_verbs=verbs.most_common(10),
        top_adjectives=adjectives.most_common(10),
    )
