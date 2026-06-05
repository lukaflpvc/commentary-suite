# commentary-suite

Tools to become a better football commentator.

This project implements a local **Commentary Training Lab** with four loops:

1. Collect transcript data from YouTube or local files.
2. Analyze commentator style.
3. Build a reusable glossary of commentary phrases.
4. Generate deliberate practice drills.

## Install

```bash
pip install -e .
```

## Quickstart

Use the included sample file:

```bash
commentary import file --file data/samples/sample_commentary.txt --commentator "Sample Commentator" --match "Sample Match"
commentary list
commentary analyze video --video-id <video-id-from-list>
commentary glossary build
commentary glossary show
commentary drills generate --video-id <video-id-from-list>
```

Import from YouTube captions:

```bash
commentary import youtube --url "https://www.youtube.com/watch?v=<id>" --commentator "Patrick Kendrick" --match "Roma vs Inter"
```

## Commands

- `commentary import youtube` - Import transcript from YouTube captions.
- `commentary import file` - Import transcript from `.txt` or `.srt` files.
- `commentary list` - Show imported transcript corpus.
- `commentary analyze video` - Build and save style report for a transcript.
- `commentary glossary build` - Build glossary from style reports.
- `commentary glossary show` - Display top glossary terms.
- `commentary drills generate` - Create deliberate practice drills.

## Data Layout

Generated files are stored under `data/`:

- `data/transcripts/*.json` - normalized transcript documents.
- `data/analysis/*.json` - style reports.
- `data/glossary.json` - aggregated glossary terms.

## Notes

- YouTube import requires captions to be available for the target video.
- The first version uses lightweight NLP heuristics for phrase extraction and style metrics.
