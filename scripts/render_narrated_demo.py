"""Assemble the authorized Qwen Plus narration and genuine browser captures.

Inputs and outputs stay in ignored private storage. No provider credentials or
voice recordings are embedded in this script. Caption timing uses measured
pauses and text weights; it is an editorial draft, not forced alignment.
"""

import hashlib
import json
import re
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "private/video-plus"
AUDIO = ROOT / "private/voice-demo/full-plus"
OUT = WORK / "delivery"
FONT = Path("/System/Library/Fonts/Supplemental")


def run(args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def duration(path):
    return float(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(path),
            ]
        ).stdout
    )


def font(size, bold=False):
    return ImageFont.truetype(str(FONT / ("Arial Bold.ttf" if bold else "Arial.ttf")), size)


def lines(draw, text, xy, size=30, fill="#CBD0E5", width=85, bold=False, spacing=12):
    x, y = xy
    for line in textwrap.wrap(text, width=width):
        draw.text((x, y), line, font=font(size, bold), fill=fill)
        y += size + spacing
    return y


def background(scene):
    im = Image.new("RGB", (1920, 1080), "#101321")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1920, 5), fill="#A98AFF")
    d.text((160, 30), f"{scene['scene']}  /  {scene['title']}", font=font(28, True), fill="#F7F4FF")
    tags = {
        "01": "REPROSCOUT / MIT 1.125",
        "02": "RESEARCH WORKFLOW",
        "03": "ACTUAL IMPORT / DEVELOPMENT HOST",
        "04": "RUN SETTINGS + RETAINED EXECUTION",
        "05": "RETAINED BROWSER ACCEPTANCE RUN",
        "06": "RETAINED EVIDENCE / SOURCE AUDIT",
        "07": "SAVED ASSISTANT REVIEW / HISTORY",
        "08": "ACTUAL EXPORT / OFFLINE REPORT",
        "09": "VALIDATED STATUS / NOVEMBER 19, 2026",
        "10": "PRESERVE / INSPECT / REVIEW",
    }
    tag = tags[scene["scene"]]
    d.text((1760 - d.textlength(tag, font=font(17)), 40), tag, font=font(17), fill="#B6A7D9")
    return im


def card(scene):
    im = background(scene)
    d = ImageDraw.Draw(im)
    n = scene["scene"]
    if n == "01":
        d.text((160, 230), "ReproScout", font=font(110, True), fill="white")
        lines(d, "Scientific reproduction, open to review.", (166, 380), 44, width=60)
        d.rounded_rectangle((160, 500, 1760, 760), 24, fill="#23233C")
        lines(d, "Did the original computation run?", (210, 550), 42, width=60, bold=True)
        lines(
            d,
            "Does the evidence support the answer?",
            (210, 630),
            42,
            fill="#BDA4FF",
            width=60,
            bold=True,
        )
        lines(d, "Weibing Wang  /  MIT 1.125", (166, 830), 28)
    elif n == "02":
        lines(
            d,
            "From a prepared project to an inspectable result",
            (160, 180),
            48,
            width=58,
            bold=True,
        )
        for i, (title, body) in enumerate(
            [
                (
                    "01  PREPARE",
                    "Original code\nData or data sources\nResearch questions\nPinned environment",
                ),
                (
                    "02  EXECUTE",
                    "Original computation\nOffline Docker sandbox\nExplicit budgets\nRetained outputs",
                ),
                (
                    "03  REVIEW",
                    "Answers with citations\nSource integrity\nAttributed decisions\nPortable report",
                ),
            ]
        ):
            x = 160 + i * 550
            d.rounded_rectangle(
                (x, 350, x + 500, 800), 24, fill="#23233C", outline="#48405D", width=2
            )
            lines(d, title, (x + 36, 400), 30, fill="#BDA4FF", width=30, bold=True)
            for j, line in enumerate(body.split("\n")):
                lines(d, line, (x + 36, 490 + j * 62), 27, width=30)
        lines(
            d,
            "Project preparation is a prerequisite; dependencies are not inferred automatically.",
            (160, 860),
            25,
            width=110,
        )
    elif n == "09":
        rec = json.loads(
            (ROOT / "reports/actions-acceptance/44469346488/acceptance.json").read_text()
        )
        assert rec["status"] == "passed"
        lines(
            d,
            "Validated workflow. Clear deployment boundaries.",
            (160, 160),
            46,
            width=65,
            bold=True,
        )
        d.rounded_rectangle((160, 285, 1760, 480), 24, fill="#20352E")
        lines(
            d, "PASS  /  Docker reproduction acceptance", (200, 320), 36, fill="#ADF0CA", bold=True
        )
        lines(
            d,
            f"Retained GitHub Actions record: 44469346488  |  {rec['summary']['model_calls']} model calls  |  {rec['summary']['seconds']:.2f}s controller",
            (200, 390),
            26,
            width=110,
        )
        for x, title, body in [
            (160, "PUBLIC WEBSITE", "Read-only evidence archive\nwuhubing.github.io/reproscout"),
            (
                990,
                "AUTHENTICATED PILOT",
                "Upload, execute, review, export\nVerified on the development host",
            ),
        ]:
            d.rounded_rectangle((x, 530, x + 770, 790), 24, fill="#23233C")
            lines(d, title, (x + 36, 570), 30, fill="#BDA4FF", bold=True)
            for j, line in enumerate(body.split("\n")):
                lines(d, line, (x + 36, 640 + j * 52), 27, width=48)
        lines(
            d,
            "Public execution deployment remains pending. CI is an integration test.",
            (160, 850),
            29,
            width=100,
        )
    elif n == "10":
        lines(d, "Preserve the computation.", (160, 200), 62, fill="white", bold=True)
        lines(d, "Inspect the evidence.", (160, 310), 62, fill="#BDA4FF", bold=True)
        lines(d, "Record the judgment.", (160, 420), 62, fill="white", bold=True)
        lines(
            d,
            "Next: hosted execution and independent researcher evaluation.",
            (160, 570),
            30,
            width=100,
        )
        lines(d, "wuhubing.github.io/reproscout", (160, 700), 34, fill="white")
        lines(d, "github.com/Wuhubing/reproscout", (160, 760), 29)
        lines(
            d,
            "Narration generated with the presenter's authorized AI voice clone.",
            (160, 880),
            23,
            width=120,
        )
    return im


def stamp(seconds, sep=","):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def captions(scene, audio):
    # Snap sentence endpoints to measured pauses near their expected positions.
    result = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(audio),
            "-af",
            "silencedetect=noise=-35dB:d=0.18",
            "-f",
            "null",
            "-",
        ]
    )
    pauses = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", result.stderr)]
    sentences = re.split(r"(?<=[.!?])\s+", scene["text"])
    total = sum(len(s) for s in sentences)
    elapsed = 0.0
    consumed = 0
    end = scene["duration_seconds"]
    rows = []
    for index, sentence in enumerate(sentences):
        consumed += len(sentence)
        expected = end * consumed / total
        candidates = [p for p in pauses if p > elapsed + 1 and abs(p - expected) < 1.6]
        boundary = (
            min(candidates, key=lambda p: abs(p - expected))
            if candidates and index < len(sentences) - 1
            else expected
        )
        chunks = textwrap.wrap(sentence, width=92, break_long_words=False)
        chars = sum(len(c) for c in chunks)
        cursor = elapsed
        for chunk in chunks:
            stop = cursor + (boundary - elapsed) * len(chunk) / chars
            rows.append((cursor + 0.15, stop + 0.15, chunk))
            cursor = stop
        elapsed = boundary
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((AUDIO / "manifest.json").read_text())
    segments = []
    allcaptions = []
    timeline = []
    offset = 0
    for scene in data["scenes"]:
        n = scene["scene"]
        wav = AUDIO / scene["audio"]
        d = duration(wav)
        scene["duration_seconds"] = d
        length = d + 1.2 + (3 if n == "10" else 0)
        bg = WORK / f"background-{n}.png"
        background(scene).save(bg)
        graphic = WORK / f"card-{n}.png"
        if n in {"01", "02", "09", "10"}:
            card(scene).save(graphic)
        rows = captions(scene, wav)
        srt = WORK / f"scene-{n}.srt"
        srt.write_text(
            "\n\n".join(
                f"{i + 1}\n{stamp(a)} --> {stamp(b)}\n" + "\n".join(textwrap.wrap(t, 70))
                for i, (a, b, t) in enumerate(rows)
            )
            + "\n"
        )
        allcaptions.extend((offset + a, offset + b, t) for a, b, t in rows)
        normalized = OUT / f"scene-{n}.wav"
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(wav),
                "-af",
                "loudnorm=I=-16:TP=-1.5:LRA=11,adelay=150,apad",
                "-t",
                str(length),
                "-ar",
                "24000",
                "-c:a",
                "pcm_s16le",
                str(normalized),
            ]
        )
        args = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-loop",
            "1",
            "-framerate",
            "30",
            "-i",
            str(graphic if n in {"02", "09", "10"} else bg),
        ]
        if n in {"02", "09", "10"}:
            args += ["-i", str(normalized)]
            filt = "[0:v]null[v]"
            ai = "1:a"
        else:
            clip = WORK / f"scene-{n}.webm"
            trim = 1.2
            clipduration = duration(clip) - trim
            args += ["-i", str(clip), "-i", str(normalized)]
            filt = f"[1:v]trim=start={trim},setpts=(PTS-STARTPTS)*{length / clipduration},fps=30,tpad=stop_mode=clone:stop_duration=2[screen];[0:v][screen]overlay=160:100:shortest=1[v]"
            ai = "2:a"
            if n == "01":
                args += ["-loop", "1", "-i", str(graphic)]
                filt = filt.replace("[v]", "[base]") + ";[base][3:v]overlay=0:0:enable=lt(t\\,6)[v]"
        filt += f";[v]subtitles={srt}:force_style='FontName=Arial,FontSize=9,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101321,Outline=1,Shadow=0,Alignment=2,MarginV=8'[final]"
        dest = WORK / f"edited-{n}.mp4"
        args += [
            "-filter_complex",
            filt,
            "-map",
            "[final]",
            "-map",
            ai,
            "-t",
            str(length),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-threads",
            "4",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            "+faststart",
            str(dest),
        ]
        run(args)
        segments.append(dest)
        timeline.append(
            {
                "scene": n,
                "title": scene["title"],
                "start_seconds": round(offset, 3),
                "end_seconds": round(offset + length, 3),
                "narration": scene["text"],
                "audio_seconds": d,
                "audio_sha256": hashlib.sha256(wav.read_bytes()).hexdigest(),
            }
        )
        offset += length
        print(f"Rendered scene {n} ({length:.2f}s)", flush=True)
    listing = WORK / "segments.txt"
    listing.write_text("".join(f"file '{s}'\n" for s in segments))
    final = OUT / "reproscout-qwen-plus-demo.mp4"
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
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(final),
        ]
    )
    (OUT / "captions.srt").write_text(
        "\n\n".join(
            f"{i + 1}\n{stamp(a)} --> {stamp(b)}\n" + "\n".join(textwrap.wrap(t, 70))
            for i, (a, b, t) in enumerate(allcaptions)
        )
        + "\n"
    )
    (OUT / "captions.vtt").write_text(
        "WEBVTT\n\n"
        + "\n\n".join(f"{stamp(a, '.')} --> {stamp(b, '.')}\n{t}" for a, b, t in allcaptions)
        + "\n"
    )
    wavlist = WORK / "audio-segments.txt"
    audio_paths = [OUT / ("scene-" + s["scene"] + ".wav") for s in timeline]
    wavlist.write_text("".join(f"file '{path}'\n" for path in audio_paths))
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
            str(wavlist),
            "-c:a",
            "pcm_s16le",
            str(OUT / "full-narration.wav"),
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(OUT / "full-narration.wav"),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "160k",
            str(OUT / "full-narration.mp3"),
        ]
    )
    card(data["scenes"][0]).save(OUT / "thumbnail.png")
    metadata = {
        "status": "First assembled cut; presenter listening and timing review pending",
        "model": data["model"],
        "duration_seconds": round(offset, 3),
        "caption_alignment": "Measured audio duration, sentence-length estimates snapped to detected pauses; not forced alignment",
        "footage": "Actual development-host browser interactions and clearly labeled retained acceptance run; editorial workflow/status cards",
        "new_model_execution": False,
        "scenes": timeline,
    }
    (OUT / "timeline.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(str(final), flush=True)


if __name__ == "__main__":
    main()
