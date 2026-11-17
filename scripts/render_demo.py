"""Render the English saved-results walkthrough on macOS (say, ffmpeg, Chrome)."""

import argparse
import html
import json
import re
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument("experiment", type=Path)
args = parser.parse_args()
work = Path("/tmp/reproscout-video")
work.mkdir(exist_ok=True)
results = json.loads((args.experiment / "results.json").read_text())
freeze = json.loads((args.experiment / "freeze.json").read_text())
assert not results["missing"]
heldout = len(freeze["cohort"]["heldout"])
sections = re.split(r"^## \d+\. .+\n", (root / "docs/demo-script.md").read_text(), flags=re.M)[1:]
titles = [
    "Why reproduction needs evidence",
    "An independent research instrument",
    "A real run, with inspectable evidence",
    "Frozen lessons, paired comparison",
    "Measured outcomes",
    "What is delivered, and what is limited",
]
notes = [
    [
        "MIT 1.125 • Weibing Wang",
        "Question: do failure-derived lessons help?",
        "Audience: researchers, reviewers, students",
        "Input: author code + data + questions",
        "Output: answers + evidence + failure record",
    ],
    [
        "Inspect AI: orchestration, Docker, traces",
        "ReproScout: preparation, tools, scoring, budgets",
        "Fresh offline author container for each attempt",
        "Host-private reference answers and credentials",
        "shell → read_file → view_image → submit_report",
    ],
    [
        "CULP development pilot: 6 / 6 questions correct",
        "Original author code executed in the container",
        "Submitted values link to captured output lines",
        "Repeated pilot has an unchanged-source audit",
        "Failed development attempts are also retained",
    ],
    [
        "5 official training tasks → 3 workflow lessons",
        f"{heldout} held-out tasks × A/B × 2 repeats",
        "A: no lessons • B: frozen lessons",
        "Code, configuration, inputs and rules hashed",
        "No lessons derived from held-out traces",
    ],
    [],
    [
        "Runnable repo + pinned dependencies + reports",
        "16 software tests • 13 environment checks",
        "Small cohort; no significance claim",
        "Prepared environments, not unchanged Medium",
        "Codex-assisted implementation; synthetic narration",
    ],
]

for label, v in results["totals"].items():
    notes[4].append(
        f"{label}: {v['solved']} / {v['planned']} solved · ${v['cost_estimated_usd']:.4f} · {v['seconds']:.0f}s"
    )
notes[4].append(f"Average B − A: {results['average_solved_difference_B_minus_A']:+.1f} solved")
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        headless=True,
    )
    page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
    for i, (title, body, bullets) in enumerate(zip(titles, sections, notes)):
        text = " ".join(body.strip().split())
        (work / f"{i}.txt").write_text(text)
        subprocess.run(
            [
                "say",
                "-v",
                "Samantha",
                "-r",
                "160",
                "-f",
                str(work / f"{i}.txt"),
                "-o",
                str(work / f"{i}.aiff"),
            ],
            check=True,
        )
        duration = float(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(work / f"{i}.aiff"),
                ]
            )
        )
        markup = """<html><style>*{box-sizing:border-box}body{margin:0;background:#102b3b;color:#edf5f9;font-family:Arial,sans-serif}.wrap{padding:58px 70px}header{font-size:21px;color:#8bd6ce;letter-spacing:3px}h1{font-size:43px;line-height:1.15;max-width:1080px;margin:30px 0 35px}li{font-size:25px;line-height:1.45;margin:21px 0}footer{position:absolute;bottom:36px;font-size:17px;color:#abc1cd}.number{position:absolute;right:70px;bottom:36px;color:#8bd6ce}</style><div class=wrap><header>REPROSCOUT / EVIDENCE BEFORE CLAIMS</header>"""
        markup += (
            f"<h1>{html.escape(title)}</h1><ul>"
            + "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
            + "</ul><footer>Saved real experiments • Prepared author environments • github.com/Wuhubing/reproscout</footer>"
            + f"<span class=number>{i + 1} / 6</span></div></html>"
        )
        page.set_content(markup)
        if i == 2:
            page.goto(
                (
                    root / "reports/runs/20261117T201102589008Z-capsule-6460826-run-A1/report.html"
                ).as_uri()
            )
        elif i == 4:
            page.goto((root / "reports/index.html").as_uri())
        page.screenshot(path=str(work / f"{i}.png"))
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-loop",
                "1",
                "-framerate",
                "10",
                "-i",
                str(work / f"{i}.png"),
                "-i",
                str(work / f"{i}.aiff"),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-tune",
                "stillimage",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-t",
                str(duration + 0.4),
                "-af",
                "apad=pad_dur=0.4",
                str(work / f"{i}.mp4"),
            ],
            check=True,
        )
        print(f"Slide {i + 1}: {duration:.1f}s", flush=True)
    browser.close()
(work / "concat.txt").write_text("".join(f"file '{work}/{i}.mp4'\n" for i in range(6)))
out = root / "deliverables/reproscout-demo.mp4"
subprocess.run(
    [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(work / "concat.txt"),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(out),
    ],
    check=True,
)
duration = float(
    subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(out),
        ]
    )
)
if abs(duration - 210) > 3:
    speed = duration / 210
    adjusted = work / "timed.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(out),
            "-filter_complex",
            f"[0:v]setpts=PTS/{speed}[v];[0:a]atempo={speed}[a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(adjusted),
        ],
        check=True,
    )
    adjusted.replace(out)
print(out)
