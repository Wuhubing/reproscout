# Delivery artifacts

v0.6.0 includes 368 portable reports, sixty new scientific outcomes, all previous
studies and failed attempts, source, protocols and an English saved-results video.
Open `../reports/index.html`. Read `../docs/controller-comparison.md` and the
separate fidelity/semantic assessment before interpreting answer scores.

The video uses disclosed synthetic macOS narration. Its text is in
`../docs/demo-script.md`. Credentials, private reference files, author archives and
raw binary Inspect logs are excluded. Earlier releases remain available.

## v0.7.0 product delivery

Open `../reports/index.html` for the product dashboard. The historical dashboard is
preserved as `../reports/experiments-v6.html`; old run artifacts are unchanged.
`reproscout-product-v7.mp4` walks through the actual development reports, evidence
anchors, partial notebook outcome, and lesson/review provenance. It uses synthetic
macOS Samantha narration. See `../scripts/render_product_demo.py` for narration
and regeneration (`uv run --with playwright python scripts/render_product_demo.py`).
See `../docs/product-guide.md` for commands and `../docs/product-release-v7.md` for
observed results, limitations, and acceptance evidence.

## v0.8.0 local workspace

Run `uv run reproscout serve` from the repository root, then open
`http://127.0.0.1:8765`. The repository includes prebuilt frontend assets.
`workspace-*-v8.png` shows actual desktop, review, lessons, new-run, and mobile
screens. `../reports/workspace-v8.html` indexes the four retained browser-launched
acceptance attempts. The earlier videos and reports are preserved.

Read `../docs/workspace-guide-v8.md` for setup and `../docs/workspace-release-v8.md`
for acceptance results and limitations. An independent-user usability session
remains pending; the browser checks were automated and reviews are attributed
to an assistant.
