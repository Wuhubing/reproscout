"""Capture actual authenticated UI interactions; keep sessions and footage private.

Requires the development server and two existing private account-code files.
The dedicated video account must be empty for the first import recording.
Existing completed captures are reused. No new reproduction run is launched.
"""

import json
import time
import zipfile
from pathlib import Path

from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parents[1]
W = R / "private/video-plus"
BASE = "http://127.0.0.1:8780"
RUN = "20261119T052436478104Z-sklearn-diabetes-ols-102-run-A1"
shots = json.loads((W / "captures.json").read_text()) if (W / "captures.json").exists() else {}
errors = []


def pause(p, s=1):
    p.wait_for_timeout(s * 1000)


def runpage(p):
    p.goto(BASE)
    p.get_by_role("button", name="Diabetes regression — scikit-learn", exact=True).click()
    p.get_by_role("heading", name="Candidate answer").wait_for()
    pause(p)


def capture(n, state, fn):
    if (W / f"scene-{n}.webm").exists():
        return
    c = b.new_context(
        storage_state=state,
        viewport={"width": 1600, "height": 850},
        record_video_dir=str(W / "captures"),
        record_video_size={"width": 1600, "height": 850},
        accept_downloads=True,
    )
    p = c.new_page()
    p.on("pageerror", lambda e: errors.append(str(e)))
    # Begin the edit after the first page has loaded; authentication is never filmed.
    p.goto(BASE)
    p.get_by_role("heading", name="Reproduction workspace", exact=True).wait_for()
    pause(p, 0.5)
    start = time.monotonic()
    fn(p)
    pause(p, 1)
    p.screenshot(path=str(W / f"scene-{n}.png"))
    v = p.video
    c.close()
    v.save_as(str(W / f"scene-{n}.webm"))
    shots[n] = {"file": f"scene-{n}.webm", "elapsed_actions_seconds": time.monotonic() - start}
    (W / "captures.json").write_text(json.dumps(shots, indent=2))
    print("Captured scene", n, flush=True)


with sync_playwright() as pw:
    b = pw.chromium.launch(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        headless=True,
    )
    states = {}
    for name, file in [("researcher", "online-access.txt"), ("presenter", "video-access.txt")]:
        c = b.new_context()
        p = c.new_page()
        p.goto(BASE)
        p.get_by_label("Workspace access code").fill((R / "private" / file).read_text().strip())
        p.get_by_role("button", name="Sign in", exact=True).click()
        p.get_by_role("heading", name="Reproduction workspace", exact=True).wait_for()
        states[name] = c.storage_state()
        c.close()
    capture("01", states["researcher"], lambda p: pause(p, 5))

    def imp(p):
        p.get_by_role("button", name="Projects", exact=True).click()
        pause(p, 1)
        if p.locator(".project-card").count():
            p.screenshot(path=str(W / "import-already-exists.png"))
            raise RuntimeError(
                "Import capture account already contains a project; preserve prior capture"
            )
        p.get_by_role("button", name="Import project", exact=True).click()
        pause(p, 1)
        p.get_by_label("Project import file").set_input_files(
            str(R / "deliverables/sklearn-diabetes-ols-102.zip")
        )
        pause(p, 2)
        with p.expect_response(lambda r: r.url.endswith("/projects/import")) as res:
            p.get_by_role("button", name="Verify & import", exact=True).click()
        assert res.value.status == 201
        pause(p, 3)

    capture("03", states["presenter"], imp)

    def config(p):
        p.get_by_role("button", name="Projects", exact=True).click()
        p.locator(".project-card").get_by_role("button", name="New run", exact=True).click()
        pause(p, 3)
        p.get_by_label("Model cost cap ($)", exact=True).scroll_into_view_if_needed()
        pause(p, 3)
        p.get_by_role("button", name="Cancel", exact=True).click()
        runpage(p)
        p.get_by_role("tab", name="Execution", exact=True).click()
        pause(p, 4)

    capture("04", states["researcher"], config)

    def result(p):
        runpage(p)
        pause(p, 3)
        for i in [1, 2]:
            p.locator(".question-tab").nth(i).click()
            pause(p, 2)

    capture("05", states["researcher"], result)

    def evidence(p):
        runpage(p)
        p.locator(".question-tab").nth(1).click()
        p.locator(".code-view").scroll_into_view_if_needed()
        pause(p, 5)
        p.get_by_role("tab", name="Source integrity", exact=True).click()
        p.get_by_text("Source audit record", exact=True).click()
        pause(p, 4)

    capture("06", states["researcher"], evidence)

    def review(p):
        runpage(p)
        p.locator(".question-tab").nth(1).click()
        p.locator(".previous-review").scroll_into_view_if_needed()
        pause(p, 3)
        p.locator(".review-identity select").select_option("assistant")
        pause(p, 3)
        # Inspect saved provenance in the exported report; do not add a redundant decision.
        p.goto((R / "reports/online-runs" / RUN / "report.html").as_uri())
        p.get_by_text("Audit records", exact=True).scroll_into_view_if_needed()
        pause(p, 2)
        p.goto((R / "reports/online-runs" / RUN / "review-history.json").as_uri())
        pause(p, 3)

    capture("07", states["researcher"], review)

    def export(p):
        runpage(p)
        pause(p, 1)
        with p.expect_download() as dl:
            p.get_by_role("link", name="Export report", exact=True).click()
        zpath = W / "reviewed-report.zip"
        dl.value.save_as(str(zpath))
        with zipfile.ZipFile(zpath) as z:
            z.extractall(W / "export")
        p.goto((W / "export" / RUN / "report.html").as_uri())
        pause(p, 3)
        link = p.locator('a[href*="step-003.stdout.txt.html#L3"]').first
        link.scroll_into_view_if_needed()
        pause(p, 1)
        link.click()
        pause(p, 4)
        assert "2548.07" in p.locator("body").inner_text()

    capture("08", states["researcher"], export)
    b.close()
(W / "browser-errors.json").write_text(json.dumps(errors))
assert not errors, errors
