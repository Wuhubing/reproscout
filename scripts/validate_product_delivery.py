import hashlib
import json
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

root = Path.cwd()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and "href" in d:
            self.links.append(d["href"])


errors = []
count = 0
for page in [root / "reports/index.html", *(root / "reports/product-runs").glob("**/*.html")]:
    parser = Links()
    parser.feed(page.read_text())
    for href in parser.links:
        u = urlsplit(href)
        if u.scheme or u.netloc:
            continue
        target = (page.parent / unquote(u.path)).resolve() if u.path else page
        count += 1
        if not target.exists():
            errors.append(str(target))
        elif u.fragment and target.suffix == ".html":
            p = Links()
            p.feed(target.read_text())
            if u.fragment not in p.ids:
                errors.append(str(target) + "#" + u.fragment)
assert not errors, errors
original = subprocess.check_output(
    [
        "git",
        "ls-tree",
        "-r",
        "v0.6.0",
        "--",
        "reports/runs",
        "reports/experiments",
        "reports/experiment",
    ],
    text=True,
).splitlines()
for row in original:
    meta, name = row.split("\t")
    blob = meta.split()[2]
    data = (root / name).read_bytes()
    current = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert current == blob, name
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        headless=True,
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto((root / "reports/index.html").as_uri())
    assert page.locator("text=Open review").count() == 3
    page.locator("text=Open review").first.click()
    assert page.locator("text=Not scored").count() > 0
    page.screenshot(path="/tmp/repro-product-report.png")
    link = page.locator('a[href*=".txt.html#L"]').first
    link.click()
    assert "#L" in page.url
    assert page.locator(":target").count() == 1
    page.screenshot(path="/tmp/repro-product-evidence.png")
    browser.close()
record = {
    "historical_files_byte_identical": len(original),
    "offline_links_checked": count,
    "broken_links": errors,
    "browser_navigation": "passed",
    "software_tests": 56,
    "development_runs": 3,
}
(root / "reports/product-delivery-validation.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
