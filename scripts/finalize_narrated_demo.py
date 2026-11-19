"""Render a solo-project delivery master from acoustically aligned narration.

All recordings, ASR results, screenshots and media remain in ignored private
storage. Scene cuts are keyed to recognized spoken phrases, not text length.
"""

import json
import math
import re
import textwrap
import wave
from pathlib import Path

from PIL import Image, ImageDraw
from render_narrated_demo import background, card, duration, lines, run, stamp

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "private/video-final"
OUT = WORK / "delivery"
SHOTS = WORK / "shots"
RUN = "20261119T052436478104Z-sklearn-diabetes-ols-102-run-A1"


def paste(im, name, box, crop=None):
    image = Image.open(SHOTS / f"{name}.png").convert("RGB")
    if crop:
        image = image.crop(crop)
    x, y, w, h = box
    image.thumbnail((w, h), Image.Resampling.LANCZOS)
    # Enlarge genuine UI crops for readable evidence, never redraw their content.
    scale = min(w / image.width, h / image.height)
    image = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    im.paste(image, (x + (w - image.width) // 2, y + (h - image.height) // 2))


def frame(scene, kind):
    im = background(scene)
    d = ImageDraw.Draw(im)
    if kind in ["title", "workflow", "ci", "public", "pilot", "closing"]:
        im = card(
            {
                **scene,
                "scene": {
                    "title": "01",
                    "workflow": "02",
                    "ci": "09",
                    "public": "09",
                    "pilot": "09",
                    "closing": "10",
                }[kind],
            }
        )
        d = ImageDraw.Draw(im)
        # Overlay authorship explicitly; no collective/team attribution.
        if kind == "title":
            d.rectangle((150, 815, 1800, 890), fill="#101321")
            lines(d, "An independent project by Weibing Wang  /  MIT 1.125", (166, 830), 28)
        if kind == "closing":
            d.rectangle((140, 655, 1800, 850), fill="#101321")
            lines(
                d,
                "ReproScout  /  Weibing Wang  /  Independent project",
                (160, 660),
                30,
                fill="#BDA4FF",
                bold=True,
            )
            lines(d, "wuhubing.github.io/reproscout", (160, 725), 32, fill="white")
            lines(d, "github.com/Wuhubing/reproscout", (160, 780), 28)
        if kind in ["public", "pilot"]:
            x = 160 if kind == "public" else 990
            d.rounded_rectangle((x, 530, x + 770, 790), 24, outline="#BDA4FF", width=5)
        if kind == "ci":
            d.rounded_rectangle((160, 285, 1760, 480), 24, outline="#ADF0CA", width=4)
        return im
    if kind.startswith("workflow-"):
        im = card({**scene, "scene": "02"})
        d = ImageDraw.Draw(im)
        x = 160 + 550 * int(kind[-1])
        d.rounded_rectangle((x, 350, x + 500, 800), 24, outline="#BDA4FF", width=5)
        return im
    if kind in [
        "overview",
        "projects",
        "import-complete",
        "run-summary",
        "q2-context",
        "export-button",
        "offline-report",
        "offline-citation",
    ]:
        paste(im, kind, (100, 110, 1720, 810))
        return im
    if kind in ["import-empty", "import-selected", "run-settings", "run-budget"]:
        paste(im, kind, (120, 120, 940, 800))
        heading = (
            "Prepared project" if kind.startswith("import") else "Bounded original-code execution"
        )
        lines(d, heading, (1120, 260), 35, width=29, bold=True, fill="white")
        items = (
            [
                "Original code and inputs",
                "SHA-256 input inventory",
                "Explicit questions",
                "Approved pinned runtime",
            ]
            if kind.startswith("import")
            else [
                "Choose research questions",
                "Set time and model-call limits",
                "Set the model-cost cap",
                "Scientific container stays offline",
            ]
        )
        for i, t in enumerate(items):
            lines(d, t, (1120, 390 + i * 82), 27, width=37)
        return im
    if kind.startswith("q") and len(kind) == 2:
        i = kind[-1]
        lines(
            d,
            {"1": "Regression coefficient", "2": "Test mean squared error", "3": "Test R-squared"}[
                i
            ],
            (130, 140),
            40,
            bold=True,
            fill="white",
        )
        paste(im, f"candidate-{i}", (120, 280, 670, 430))
        paste(im, f"evidence-{i}", (840, 240, 960, 670))
        lines(
            d,
            "Inspect the metric, value, and context in the retained output.",
            (130, 905),
            26,
            width=105,
        )
        return im
    if kind == "evidence-focus":
        lines(d, "Mean squared error: 2548.07", (160, 150), 48, fill="white", bold=True)
        paste(im, "evidence-2", (220, 260, 1480, 630))
        return im
    if kind == "source":
        lines(
            d, "Original inputs: inventory and hash check", (160, 170), 42, fill="white", bold=True
        )
        paste(im, "source-audit", (160, 300, 1600, 550))
        lines(
            d,
            "Four prepared input files checked. Hashes do not establish scientific correctness.",
            (160, 880),
            26,
            width=110,
        )
        return im
    if kind == "execution":
        lines(d, "Retained original-code execution", (160, 165), 44, fill="white", bold=True)
        paste(im, "execution", (160, 300, 1600, 520))
        lines(
            d,
            "Recorded acceptance run; this edit does not launch a new scientific attempt.",
            (160, 875),
            25,
            width=110,
        )
        return im
    if kind in ["review", "attribution"]:
        paste(im, "review-form", (140, 140, 650, 780))
        lines(d, "A decision with provenance", (900, 210), 42, width=35, fill="white", bold=True)
        paste(im, "saved-review", (880, 330, 900, 365))
        lines(d, "Reviewer: researcher", (920, 740), 30, fill="white")
        lines(d, "Reviewer type: AI assistant", (920, 795), 30, fill="#BDA4FF", bold=True)
        lines(d, "Not independent human validation", (920, 855), 25, width=45)
        return im
    if kind == "history":
        records = json.loads(
            (ROOT / "reports/online-runs" / RUN / "review-history.json").read_text()
        ) + [json.loads((ROOT / "reports/online-runs" / RUN / "manual-review.json").read_text())]
        lines(d, "Retained review records", (160, 160), 46, fill="white", bold=True)
        for i, r in enumerate(records):
            y = 290 + i * 185
            d.rounded_rectangle((160, y, 1760, y + 150), 20, fill="#23233C")
            q = next(iter(r["questions"]))
            entry = r["questions"][q]
            lines(
                d,
                f"{q.upper()}   {entry['support'].upper()}   /   {r['reviewer_kind']} review by {r['reviewer']}",
                (200, y + 25),
                30,
                fill="#D4C4FF",
                bold=True,
            )
            lines(
                d,
                "Version " + str(r.get("review_version", "current")),
                (200, y + 85),
                23,
                width=115,
            )
        lines(
            d,
            "Editorial view of the real saved JSON records; earlier versions are preserved.",
            (160, 900),
            25,
            width=110,
        )
        return im
    if kind == "offline-output":
        lines(
            d,
            "Portable report: citation opens the original output",
            (160, 160),
            40,
            fill="white",
            bold=True,
        )
        paste(im, "offline-output-zoom", (160, 300, 1600, 560), crop=(0, 0, 1600, 450))
        lines(
            d,
            "Opened outside the application. The highlighted line is retained evidence.",
            (160, 900),
            26,
            width=110,
        )
        return im
    raise ValueError(kind)


def normal(t):
    return re.sub("[^a-z0-9]", "", t.lower())


def cue(scene, phrase):
    words = scene["words"]
    p = [normal(t) for t in phrase.split()]
    seq = [normal(w["text"]) for w in words]
    for i in range(len(seq) - len(p) + 1):
        if seq[i : i + len(p)] == p:
            return max(0, words[i]["start"] - 0.08)
    raise ValueError(f"Missing speech cue {scene['scene']}: {phrase}")


def plan(s):
    n = s["scene"]

    def c(phrase):
        return cue(s, phrase)

    return {
        "01": lambda: [(0, "title"), (c("When a research"), "overview")],
        "02": lambda: [
            (0, "workflow"),
            (c("The input"), "workflow-0"),
            (c("The output"), "workflow-2"),
        ],
        "03": lambda: [
            (0, "projects"),
            (c("After signing"), "import-empty"),
            (c("I upload"), "import-selected"),
            (c("before registering"), "import-complete"),
            (c("The server"), "import-selected"),
        ],
        "04": lambda: [
            (0, "run-settings"),
            (c("execution limits"), "run-budget"),
            (c("The controller"), "execution"),
            (c("The interface"), "run-summary"),
        ],
        "05": lambda: [
            (0, "run-summary"),
            (c("regression coefficient"), "q1"),
            (c("test mean squared"), "q2"),
            (c("R-squared value"), "q3"),
        ],
        "06": lambda: [
            (0, "q2-context"),
            (c("The highlighted line"), "evidence-focus"),
            (c("I can check"), "q2"),
            (c("The source integrity"), "source"),
        ],
        "07": lambda: [
            (0, "review"),
            (c("Reviews also preserve"), "attribution"),
            (c("Earlier review"), "history"),
        ],
        "08": lambda: [
            (0, "export-button"),
            (c("open it outside"), "offline-report"),
            (c("Following a citation"), "offline-citation"),
            (c("relevant output lines"), "offline-output"),
        ],
        "09": lambda: [
            (0, "ci"),
            (c("The public website"), "public"),
            (c("The authenticated app"), "pilot"),
        ],
        "10": lambda: [(0, "closing")],
    }[n]()


def make_captions(s):
    sentences = []
    sentence = []
    for word in s["words"]:
        sentence.append(word)
        if re.search(r"[.!?]$", word["text"]):
            sentences.append(sentence)
            sentence = []
    if sentence:
        sentences.append(sentence)
    groups = []
    for sentence in sentences:
        parts = []
        group = []
        for word in sentence:
            proposed = " ".join(x["text"] for x in group + [word])
            if group and (len(proposed) > 76 or word["end"] - group[0]["start"] > 5.7):
                parts.append(group)
                group = []
            group.append(word)
        if group:
            parts.append(group)
        # Avoid orphaned sentence endings and splitting the GitHub Actions name.
        if len(parts) > 1:
            while (
                len(" ".join(w["text"] for w in parts[-1])) < 22
                or parts[-1][0]["text"] == "Actions,"
            ) and len(parts[-2]) > 3:
                parts[-1].insert(0, parts[-2].pop())
        groups.extend(parts)
    out = []
    for i, g in enumerate(groups):
        start = max(0, g[0]["start"] - 0.06)
        end = g[-1]["end"] + 0.18
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0]["start"] - 0.10)
        end = max(start + 0.4, end)
        text = " ".join(w["text"] for w in g)
        out.append(
            {
                "start": round(start, 3),
                "end": round(end, 3),
                "text": text,
                "lines": textwrap.wrap(text, 42, break_long_words=False, break_on_hyphens=False),
            }
        )
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((WORK / "alignment.json").read_text())
    allcaps = []
    segments = []
    timeline = []
    offset = 0
    for s in data["scenes"]:
        n = s["scene"]
        raw = WORK / "audio" / s["audio"]
        trim = s["leading_trim_seconds"]
        d = duration(raw) - trim
        frames = math.ceil((d + 0.65 + (3 if n == "10" else 0)) * 30)
        length = frames / 30
        cuts = plan(s)
        rows = make_captions(s)
        normalized = OUT / f"scene-{n}.wav"
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(raw),
                "-af",
                f"atrim=start={trim},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5:LRA=11,apad",
                "-t",
                str(length),
                "-ar",
                "24000",
                "-c:a",
                "pcm_s16le",
                str(normalized),
            ]
        )
        # Force sample-exact scene lengths; resampler timestamps can otherwise
        # shorten a WAV by a packet and accumulate audio/video drift.
        with wave.open(str(normalized), "rb") as source:
            params = source.getparams()
            pcm = source.readframes(source.getnframes())
        target_bytes = frames * 800 * params.sampwidth * params.nchannels
        assert abs(len(pcm) - target_bytes) < 24000, "Unexpected audio duration error"
        with wave.open(str(normalized), "wb") as fixed:
            fixed.setparams(params)
            fixed.writeframes((pcm + bytes(max(0, target_bytes - len(pcm))))[:target_bytes])
        image_list = []
        shot_records = []
        for i, (start, kind) in enumerate(cuts):
            start = round(start * 30) / 30
            end = round(cuts[i + 1][0] * 30) / 30 if i + 1 < len(cuts) else length
            assert end > start, (n, kind, start, end)
            png = WORK / f"frame-{n}-{i}.png"
            frame(s, kind).save(png)
            image_list.extend([f"file '{png}'", f"duration {end - start:.6f}"])
            shot_records.append(
                {"start_seconds": start, "end_seconds": end, "visual": kind, "frame": png.name}
            )
        image_list.append(f"file '{png}'")
        listing = WORK / f"frames-{n}.txt"
        listing.write_text("\n".join(image_list) + "\n")
        srt = WORK / f"captions-{n}.srt"
        srt.write_text(
            "\n\n".join(
                f"{i + 1}\n{stamp(r['start'])} --> {stamp(r['end'])}\n" + "\n".join(r["lines"])
                for i, r in enumerate(rows)
            )
            + "\n"
        )
        filt = f"fps=30,subtitles={srt}:force_style='FontName=Arial,FontSize=9,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101321,Outline=0.6,Shadow=0,Alignment=2,MarginV=8'"
        dest = WORK / f"final-{n}.mp4"
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(listing),
                "-i",
                str(normalized),
                "-vf",
                filt,
                "-an",
                "-frames:v",
                str(frames),
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-threads",
                "4",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                "-video_track_timescale",
                "30000",
                "-movflags",
                "+faststart",
                str(dest),
            ]
        )
        segments.append(dest)
        allcaps.extend({**r, "start": offset + r["start"], "end": offset + r["end"]} for r in rows)
        timeline.append(
            {
                "scene": n,
                "title": s["title"],
                "start_seconds": offset,
                "end_seconds": offset + length,
                "narration": s["text"],
                "captions": rows,
                "shots": shot_records,
                "leading_trim_seconds": trim,
                "regenerated": s["regenerated"],
            }
        )
        offset += length
        print("Rendered final scene", n, round(length, 2), "seconds", flush=True)
    listing = WORK / "final-segments.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in segments))
    # Assemble video only; use a continuous PCM-derived audio stream to avoid AAC priming gaps at scene joins.
    video = WORK / "picture-master.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-map",
            "0:v:0",
            "-c:v",
            "copy",
            "-an",
            str(video),
        ]
    )
    audio_list = WORK / "final-audio.txt"
    audio_list.write_text(
        "".join("file '" + str(OUT / f"scene-{s['scene']}.wav") + "'\n" for s in timeline)
    )
    wav = OUT / "full-narration.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(audio_list),
            "-c:a",
            "pcm_s16le",
            str(wav),
        ]
    )
    (OUT / "captions.srt").write_text(
        "\n\n".join(
            f"{i + 1}\n{stamp(r['start'])} --> {stamp(r['end'])}\n" + "\n".join(r["lines"])
            for i, r in enumerate(allcaps)
        )
        + "\n"
    )
    (OUT / "captions.vtt").write_text(
        "WEBVTT\n\n"
        + "\n\n".join(
            f"{stamp(r['start'], '.')} --> {stamp(r['end'], '.')}\n" + "\n".join(r["lines"])
            for r in allcaps
        )
        + "\n"
    )
    final = OUT / "reproscout-final.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(video),
            "-i",
            str(wav),
            "-i",
            str(OUT / "captions.srt"),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=eng",
            "-metadata",
            "title=ReproScout — Independent project by Weibing Wang",
            "-t",
            str(offset),
            "-movflags",
            "+faststart",
            str(final),
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(wav),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "160k",
            str(OUT / "full-narration.mp3"),
        ]
    )
    frame(data["scenes"][0], "title").save(OUT / "thumbnail.png")
    (OUT / "timeline.json").write_text(
        json.dumps(
            {
                "status": "Final delivery master",
                "author": "Weibing Wang",
                "project_type": "Independent individual project",
                "model": "qwen-audio-3.1-tts-plus",
                "alignment": data["method"],
                "duration_seconds": offset,
                "scenes": timeline,
            },
            indent=2,
        )
        + "\n"
    )
    (OUT / "narration.txt").write_text("\n\n".join(s["text"] for s in data["scenes"]) + "\n")
    print("FINAL", final, round(offset, 3), flush=True)


if __name__ == "__main__":
    main()
