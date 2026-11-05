---
title: 'From expressive piano audio to editable notation'
description: 'An audio-to-MIDI-to-score pipeline that makes timing preservation and notation loss explicit.'
year: '2026'
number: 3
category: 'PUBLIC PROJECT / AUDIO ML'
ownership: 'Independently developed'
status: 'Public repository; prototype pipeline with documented limitations'
format: 'Engineering case study'
public: true
---
## The problem

A piano performance is a sequence of notes, durations, dynamics and expressive timing. A readable score is a different representation. Turning a recording into notation therefore involves more than recognizing pitches: it forces a choice between **preserving the performance** and **regularizing it into a readable grid**.

I built a pipeline for recordings the user owns or is authorized to process. It takes local audio/video or an authorized URL, extracts a WAV file, runs a transcription model, preserves the resulting performance MIDI, and produces editable MusicXML and optionally PDF scores.

[Explore the public source and usage notes ↗](https://github.com/simplysoup/yt-piano-transcription)

## Processing stages

1. **Input:** accept a local recording or a permitted video URL; use `yt-dlp` for URLs only.
2. **Normalize audio:** `ffmpeg` converts the source to 44.1 kHz mono WAV.
3. **Transcribe:** Transkun produces performance MIDI. The original is kept intact as the reference output.
4. **Score conversion:** create full MusicXML and a simplified alternative, using MuseScore when PDF rendering is requested.
5. **Optional grid mode:** snap notes to a fixed tempo grid only on explicit request; timing-preserving conversion is the default.

## Default: preserve performance timing

The implementation favors **timing fidelity** over pretending it can automatically infer a composer's intended notation. Grid quantization can move onsets and note lengths. Conversely, preserving expressive performance timing can generate intricate written rhythms.

The project supports a simplified score by identifying possible ornament notes, while preserving their original timestamps in a separate record. That simplification is heuristic: flagged notes may be legitimate musical material, and should be reviewed against the recording.

## A preprocessing step I removed

An attempted source-separation/denoising stage was removed after it suppressed real notes in test material. For solo piano, that cost outweighed its apparent preprocessing benefit. This is a useful example of why a plausible model-pipeline stage should be justified through observed behavior, rather than inserted because it is fashionable.

## What remains uncertain

| Area | Current limitation |
| --- | --- |
| Hand assignment | Grand staff uses a pitch split, not learned left/right-hand identification |
| Meter | Defaults to 4/4 unless explicitly specified |
| Key signature | Inferred heuristically; may fail on chromatic or modal music |
| Tempo | Grid mode's estimate can choose half or double time |
| Ornament detection | Conservative heuristic; possible false positives |
| Engraving | Editable prototype, not guaranteed professional notation |

The repository is an **experimental tool**, not a claim of perfect transcription or automated music engraving. The stated license in the README should be checked against the repository's license file before any reuse of its code; this portfolio only links to the source.

**Source:** [Solo piano transcription repository](https://github.com/simplysoup/yt-piano-transcription).
