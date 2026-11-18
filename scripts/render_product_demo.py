"""Record an English walkthrough of the real offline product reports (macOS)."""

import json
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    work = Path("/tmp/reproscout-product-demo")
    work.mkdir(exist_ok=True)
    rows = json.loads((ROOT / "reports/product-index.json").read_text())
    good = ROOT / "reports" / rows[0]["report"]
    blocked = ROOT / "reports" / rows[2]["report"]
    assessment = json.loads((good.parent / "review-assessment.json").read_text())
    first = next(iter(assessment["questions"].values()))["candidate"]["evidence"][0]
    evidence = good.parent / (first["artifact"] + ".html")
    scenes = [
        (
            ROOT / "reports/index.html",
            None,
            "ReproScout is a local scientific reproduction review tool. Supply original author code, data, a prepared environment, and explicit questions. This dashboard shows three real development runs. The older experiments remain available separately.",
        ),
        (
            good,
            None,
            "This is the actual CULP report. The author code ran in the isolated environment. There is no answer key in this product run, so correctness is not scored. Execution provenance and semantic support are separate. A completed run still needs review.",
        ),
        (
            evidence,
            f"#L{first['line_start']}",
            "Each candidate links to retained evidence at an exact line. Review the dataset, statistic, and units before accepting a value. Merely finding the same number, or matching a reference answer, does not establish that the evidence answers the question.",
        ),
        (
            blocked,
            None,
            "This is the actual Iris notebook run. The report preserves failed author execution and partial output. An offline dependency or unavailable dataset is a blocker. ReproScout does not silently replace the dataset or rewrite the scientific computation to obtain an answer.",
        ),
        (
            good,
            "text=Loaded lessons",
            "Lessons have an explicit lifecycle. A development run supplies provenance. A proposed rule stays inactive until approved. The selected rule and its content hash are saved with the run. Edited or disabled rules cannot be loaded. Approval here is attributed to an assistant, not an independent human.",
        ),
        (
            good,
            "text=Audit records",
            "The report retains source changes, provisional diagnosis, budget, and the visible execution trace. A reviewer can import a structured decision with identity, rationale, and evidence. These three runs validate a product workflow. They do not establish that lessons improve success or generalize to unseen tasks.",
        ),
    ]
    segments = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            headless=True,
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        for index, (path, target, narration) in enumerate(scenes):
            page.goto(path.as_uri() + (target if target and target.startswith("#") else ""))
            if target and not target.startswith("#"):
                page.locator(target).first.scroll_into_view_if_needed()
            page.screenshot(path=str(work / f"{index}.png"))
            text = work / f"{index}.txt"
            text.write_text(narration)
            audio = work / f"{index}.aiff"
            subprocess.run(
                ["say", "-v", "Samantha", "-r", "150", "-f", str(text), "-o", str(audio)],
                check=True,
            )
            segment = work / f"{index}.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-loglevel",
                    "error",
                    "-loop",
                    "1",
                    "-i",
                    str(work / f"{index}.png"),
                    "-i",
                    str(audio),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-tune",
                    "stillimage",
                    "-pix_fmt",
                    "yuv420p",
                    "-r",
                    "24",
                    "-c:a",
                    "aac",
                    "-shortest",
                    str(segment),
                ],
                check=True,
            )
            segments.append(segment)
        browser.close()
    listing = work / "concat.txt"
    listing.write_text("".join(f"file '{p}'\n" for p in segments))
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
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
            str(ROOT / "deliverables/reproscout-product-v7.mp4"),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
