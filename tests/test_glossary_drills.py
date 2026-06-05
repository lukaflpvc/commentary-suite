from commentary_suite.drills import generate_drills
from commentary_suite.glossary import build_glossary
from commentary_suite.models import StyleReport, TranscriptDocument, TranscriptSegment


def test_build_glossary_groups_terms() -> None:
    report = StyleReport(
        video_id="v1",
        commentator="A",
        total_words=100,
        unique_words=50,
        avg_words_per_segment=10.0,
        avg_sentence_length=11.0,
        filler_density=0.01,
        less_is_more_score=82.0,
        top_words=[("drives", 4)],
        top_phrases=[("drives forward", 3), ("clinical finish", 2)],
        top_verbs=[("drives", 4)],
        top_adjectives=[("clinical", 2)],
    )
    terms = build_glossary([report])
    assert terms
    assert terms[0].count >= 2


def test_generate_drills() -> None:
    document = TranscriptDocument(
        video_id="v2",
        title="Test",
        source_type="file",
        source_reference="x",
        segments=[
            TranscriptSegment(text="He drives into the final third and squares for the striker."),
            TranscriptSegment(text="The finish is precise and calm under pressure."),
        ],
    )
    report = StyleReport(
        video_id="v2",
        commentator="B",
        total_words=20,
        unique_words=18,
        avg_words_per_segment=10.0,
        avg_sentence_length=10.0,
        filler_density=0.0,
        less_is_more_score=90.0,
        top_words=[("drives", 1)],
        top_phrases=[("drives into", 2)],
        top_verbs=[("drives", 1)],
        top_adjectives=[("calm", 1)],
    )
    drills = generate_drills(document, report, limit=8)
    assert drills
    assert all(drill.source_video_id == "v2" for drill in drills)
