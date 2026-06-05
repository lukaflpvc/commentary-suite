from pathlib import Path

from commentary_suite.transcripts import extract_youtube_video_id, import_from_file


def test_extract_youtube_video_id() -> None:
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_youtube_video_id(url) == "dQw4w9WgXcQ"


def test_import_local_txt(tmp_path: Path) -> None:
    transcript_file = tmp_path / "clip.txt"
    transcript_file.write_text("First line\nSecond line\n", encoding="utf-8")

    document = import_from_file(str(transcript_file), commentator="Tester")

    assert document.source_type == "file"
    assert document.commentator == "Tester"
    assert len(document.segments) == 2
