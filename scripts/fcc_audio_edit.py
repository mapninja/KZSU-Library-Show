#!/usr/bin/env python3
"""
fcc_audio_edit.py: find FCC words in a song and reverse them, like the
Audacity "Reverse" trick, then save an edited copy.

HOW IT WORKS (step by step)
  1. Whisper (speech-to-text) listens to the song and writes down every word
     with its start and end time.
  2. The script checks each word against the FCC list.
  3. ffmpeg reverses only those short spans of audio (with tiny fades so
     there are no clicks) and writes "<name> (FCC edit).<ext>".
  4. A report lists every edit (word, time) so you can check by ear.
     Lyrics are never printed in full; only the flagged word and its time.

SETUP ON YOUR MAC (one time)
  brew install ffmpeg
  pip3 install faster-whisper
  The first run downloads the Whisper model (about 150 MB for "base.en").

RUN
  python3 scripts/fcc_audio_edit.py "path/to/Mad Technology.mp3"
  python3 scripts/fcc_audio_edit.py song.mp3 --model small.en      # more accurate, slower
  python3 scripts/fcc_audio_edit.py song.mp3 --dry-run             # report only, no audio written
  python3 scripts/fcc_audio_edit.py song.mp3 --add 83.2-83.6       # add a span you found by ear
  python3 scripts/fcc_audio_edit.py song.mp3 --model-dir ~/whisper-models/base.en  # local model folder

Rap verses are hard for any transcriber, so ALWAYS listen to the edit before air.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

# FCC words (must edit) and caution words (flag only), from references/house_rules.md.
# Each pattern is a regular expression; \b means "word boundary" so "cocktail" is not flagged.
FCC = {
    "fuck": r"f+u+c+k\w*|motherf\w*",
    "shit": r"\w*shit\w*",
    "piss": r"piss\w*",
    "cunt": r"cunts?",
    "cocksucker": r"cocksuck\w*",
    "cock": r"cocks?",
    "tits": r"tits?|titties",
}
CAUTION = {"bitch": r"bitch\w*", "asshole": r"assholes?", "goddamn": r"god ?damn\w*"}

PAD = 0.06   # seconds added before and after each word, since Whisper's edges are approximate
FADE = 0.01  # tiny fade at each edge of a reversed span to prevent clicks


def match(word, table):
    """Return the FCC key if this transcribed word matches one of the patterns."""
    clean = re.sub(r"[^a-z' ]", "", word.lower()).strip()
    for key, pat in table.items():
        if re.fullmatch(pat, clean):
            return key
    return None


def transcribe(path, model_name, model_dir):
    """Run Whisper and return a list of (word, start, end) in seconds."""
    from faster_whisper import WhisperModel  # imported here so --help works without it
    model = WhisperModel(model_dir or model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(path), word_timestamps=True, vad_filter=False)
    return [(w.word, w.start, w.end) for seg in segments for w in seg.words]


def merge(spans):
    """Join overlapping spans so we never reverse the same audio twice."""
    out = []
    for s, e, label in sorted(spans):
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e), out[-1][2] + "+" + label)
        else:
            out.append((s, e, label))
    return out


def build_filter(spans):
    """Build an ffmpeg filter that splits the song at each span, reverses those
    pieces, and glues everything back together in order."""
    cuts, t = [], 0.0
    for s, e, _ in spans:
        cuts.append((t, s, False))  # normal audio before the word
        cuts.append((s, e, True))   # the word, reversed
        t = e
    cuts.append((t, None, False))   # the rest of the song
    parts, labels = [], []
    for i, (s, e, rev) in enumerate(cuts):
        end = f":end={e}" if e is not None else ""
        chain = f"[0:a]atrim=start={s}{end},asetpts=PTS-STARTPTS"
        if rev:
            d = e - s
            chain += f",areverse,afade=t=in:d={FADE},afade=t=out:st={max(d - FADE, 0)}:d={FADE}"
        parts.append(chain + f"[p{i}]")
        labels.append(f"[p{i}]")
    parts.append("".join(labels) + f"concat=n={len(labels)}:v=0:a=1[out]")
    return ";".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--model", default="base.en", help="Whisper size: tiny.en, base.en, small.en, medium.en")
    ap.add_argument("--model-dir", help="folder with a downloaded faster-whisper model")
    ap.add_argument("--add", action="append", default=[], help="extra span to reverse, seconds: START-END")
    ap.add_argument("--dry-run", action="store_true", help="report only; do not write audio")
    a = ap.parse_args()

    src = Path(a.audio).expanduser()
    words = transcribe(src, a.model, a.model_dir)
    spans, caution = [], []
    for w, s, e in words:
        if (k := match(w, FCC)):
            spans.append((max(s - PAD, 0), e + PAD, k))
        elif (k := match(w, CAUTION)):
            caution.append((k, round(s, 2)))
    for extra in a.add:  # spans Stace found by ear
        s, e = (float(x) for x in extra.split("-"))
        spans.append((s, e, "manual"))
    spans = merge(spans)

    report = {
        "file": src.name,
        "words_transcribed": len(words),
        "edits": [{"word": l, "start": round(s, 2), "end": round(e, 2),
                   "at": f"{int(s // 60)}:{s % 60:05.2f}"} for s, e, l in spans],
        "caution_not_edited": caution,
    }
    if spans and not a.dry_run:
        out = src.with_name(f"{src.stem} (FCC edit){src.suffix}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                        "-filter_complex", build_filter(spans), "-map", "[out]",
                        "-map_metadata", "0", str(out)], check=True)
        report["output"] = str(out)
    print(json.dumps(report, indent=1))
    if not words:
        print("No words found. Instrumental, or the model could not hear the vocals.")


if __name__ == "__main__":
    main()
