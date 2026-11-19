"""Read-only release checks: historical bytes, portable links, and live UI smoke."""

import hashlib
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if fields.get("id"):
            self.ids.add(fields["id"])
        if tag == "a" and fields.get("href"):
            self.links.append(fields["href"])


def main():
    original = subprocess.check_output(
        ["git", "ls-tree", "-r", "v0.7.0", "--", "reports"], cwd=ROOT, text=True
    ).splitlines()
    for row in original:
        metadata, name = row.split("\t")
        data = (ROOT / name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert actual == metadata.split()[2], name
    count = 0
    pages = [
        ROOT / "reports/workspace-v8.html",
        *(ROOT / "reports/workspace-runs").glob("**/*.html"),
    ]
    for page in pages:
        parser = Links()
        parser.feed(page.read_text())
        for href in parser.links:
            link = urlsplit(href)
            if link.scheme or link.netloc:
                continue
            target = (page.parent / unquote(link.path)).resolve() if link.path else page
            assert target.is_file(), (page, href)
            if link.fragment and target.suffix == ".html":
                destination = Links()
                destination.feed(target.read_text())
                assert link.fragment in destination.ids, (page, href)
            count += 1
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            headless=True,
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto("http://127.0.0.1:8765/")
        page.get_by_role("heading", name="Reproduction workspace", exact=True).wait_for()
        assert page.get_by_role("button", name="New reproduction", exact=True).is_enabled()
        page.get_by_role("button", name="Projects", exact=True).click()
        assert page.locator(".project-card").count() >= 3
        page.get_by_role("button", name="Overview", exact=True).click()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        assert not errors, errors
        browser.close()
    result = {
        "historical_report_files_unchanged": len(original),
        "portable_links_checked": count,
        "browser_smoke": "passed",
        "page_errors": errors,
        "independent_user_trial": "pending",
    }
    (ROOT / "reports/workspace-delivery-validation-v8.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
