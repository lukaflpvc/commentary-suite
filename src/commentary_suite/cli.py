from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .analysis import analyze_document
from .drills import generate_drills
from .glossary import build_glossary, category_summary
from .store import (
    list_transcripts,
    load_style_report,
    load_transcript,
    save_glossary,
    save_style_report,
    save_transcript,
)
from .transcripts import import_from_file, import_from_youtube

app = typer.Typer(help="Commentary training CLI for transcript analysis and deliberate practice.")
import_app = typer.Typer(help="Import transcripts into the local corpus.")
analyze_app = typer.Typer(help="Analyze transcript style and export style reports.")
glossary_app = typer.Typer(help="Build and inspect commentary glossary terms.")
drills_app = typer.Typer(help="Generate deliberate practice drills.")

app.add_typer(import_app, name="import")
app.add_typer(analyze_app, name="analyze")
app.add_typer(glossary_app, name="glossary")
app.add_typer(drills_app, name="drills")

console = Console()


@import_app.command("youtube")
def import_youtube(
    url: str = typer.Option(..., "--url", help="YouTube URL."),
    commentator: str | None = typer.Option(None, "--commentator"),
    match_name: str | None = typer.Option(None, "--match"),
    competition: str | None = typer.Option(None, "--competition"),
    language: str = typer.Option("en", "--language"),
) -> None:
    document = import_from_youtube(
        url=url,
        commentator=commentator,
        match_name=match_name,
        competition=competition,
        language=language,
    )
    path = save_transcript(document)
    console.print(f"[green]Imported transcript:[/green] {document.video_id}")
    console.print(f"Saved to: {path}")


@import_app.command("file")
def import_file(
    file_path: str = typer.Option(..., "--file", help="Path to .txt or .srt transcript file."),
    commentator: str | None = typer.Option(None, "--commentator"),
    match_name: str | None = typer.Option(None, "--match"),
    competition: str | None = typer.Option(None, "--competition"),
    language: str = typer.Option("en", "--language"),
) -> None:
    document = import_from_file(
        file_path=file_path,
        commentator=commentator,
        match_name=match_name,
        competition=competition,
        language=language,
    )
    path = save_transcript(document)
    console.print(f"[green]Imported transcript:[/green] {document.video_id}")
    console.print(f"Saved to: {path}")


@app.command("list")
def list_corpus() -> None:
    documents = list_transcripts()
    if not documents:
        console.print("[yellow]No transcripts imported yet.[/yellow]")
        return
    table = Table(title="Imported Transcripts")
    table.add_column("Video ID")
    table.add_column("Title")
    table.add_column("Commentator")
    table.add_column("Segments", justify="right")
    for doc in documents:
        table.add_row(doc.video_id, doc.title, doc.commentator or "-", str(len(doc.segments)))
    console.print(table)


@analyze_app.command("video")
def analyze_video(video_id: str = typer.Option(..., "--video-id")) -> None:
    document = load_transcript(video_id)
    report = analyze_document(document)
    path = save_style_report(report)
    _print_style_report(report)
    console.print(f"Saved style report: {path}")


def _print_style_report(report) -> None:
    table = Table(title=f"Style Report: {report.video_id}")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Commentator", report.commentator or "-")
    table.add_row("Total words", str(report.total_words))
    table.add_row("Unique words", str(report.unique_words))
    table.add_row("Avg words/segment", f"{report.avg_words_per_segment:.2f}")
    table.add_row("Avg sentence length", f"{report.avg_sentence_length:.2f}")
    table.add_row("Filler density", f"{report.filler_density:.4f}")
    table.add_row("Less-is-more score", f"{report.less_is_more_score:.2f}")
    console.print(table)


@glossary_app.command("build")
def build_glossary_cmd() -> None:
    reports = []
    for document in list_transcripts():
        try:
            reports.append(load_style_report(document.video_id))
        except FileNotFoundError:
            reports.append(analyze_document(document))
    if not reports:
        console.print("[yellow]No transcripts available to build glossary.[/yellow]")
        return
    terms = build_glossary(reports)
    path = save_glossary(terms)
    summary = category_summary(terms)
    table = Table(title="Glossary Categories")
    table.add_column("Category")
    table.add_column("Terms", justify="right")
    for category, count in summary.items():
        table.add_row(category, str(count))
    console.print(table)
    console.print(f"Saved glossary: {path}")


@glossary_app.command("show")
def show_glossary(limit: int = typer.Option(20, "--limit")) -> None:
    path = Path.cwd() / "data" / "glossary.json"
    if not path.exists():
        console.print("[yellow]Glossary has not been built yet.[/yellow]")
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    table = Table(title="Top Glossary Terms")
    table.add_column("Phrase")
    table.add_column("Category")
    table.add_column("Count", justify="right")
    for item in payload[:limit]:
        table.add_row(item["phrase"], item["category"], str(item["count"]))
    console.print(table)


@drills_app.command("generate")
def drills_generate(
    video_id: str = typer.Option(..., "--video-id"),
    limit: int = typer.Option(10, "--limit"),
) -> None:
    document = load_transcript(video_id)
    try:
        report = load_style_report(video_id)
    except FileNotFoundError:
        report = analyze_document(document)
    drills = generate_drills(document, report, limit=limit)
    table = Table(title=f"Practice Drills: {video_id}")
    table.add_column("Title")
    table.add_column("Category")
    table.add_column("Prompt")
    for drill in drills:
        table.add_row(drill.title, drill.category, drill.prompt)
    console.print(table)


def main() -> None:
    app()
