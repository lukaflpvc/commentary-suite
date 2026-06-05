from commentary_suite.analysis import analyze_document
from commentary_suite.models import TranscriptDocument, TranscriptSegment


def test_analyze_document_basic_metrics() -> None:
    document = TranscriptDocument(
        video_id="v1",
        title="Test",
        source_type="file",
        source_reference="test",
        commentator="Commentator",
        segments=[
            TranscriptSegment(text="He drives forward and scores."),
            TranscriptSegment(text="Clinical finish and brilliant movement."),
        ],
    )

    report = analyze_document(document)

    assert report.total_words > 0
    assert report.unique_words > 0
    assert 0 <= report.less_is_more_score <= 100
    assert isinstance(report.top_words, list)
