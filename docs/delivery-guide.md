# Delivery guide

## Review without rerunning

Open `reports/index.html` in a browser. It works as a local static report. Start
with the frozen comparison, then follow an evidence report and its artifact links.
Read `docs/results.md` for the result interpretation and `docs/project-overview.md`
for the complete input/output and product contract. No API key is needed to review
these artifacts.

## Reproduce the pilot

Follow the install, image-pull, validate, and run commands in README.md. Keep the
key outside the checkout. A new run is written to a unique ignored `runs/` directory.
API model access, external capsule hosting, and registry availability are required.
An archived report remains readable even when those external services are unavailable.

## Prepare and run a new comparison

```bash
uv run python scripts/provision_cohort.py
# If selected images are rate-limited, retry the same selection:
uv run python scripts/retry_provisioning.py
```

Inspect `manifests/selection.json`, `manifests/provisioning.json`, and
`manifests/cohort.json` before accepting the available cohort. Preparation does not
promise the same images will be accessible in the future. Do not silently treat a
changed available cohort as a reproduction of the published experiment.

Run development tasks with `--manifest manifests/<task-id>.json`, retain failed
runs, and write lessons derived only from those official training runs. Freeze
with a new ID before any formal runs:

```python
from pathlib import Path
from reproscout.experiment import freeze
root = Path.cwd()
experiment = freeze(root, root / "lessons/development-v1.md",
                    ["YOUR_DEVELOPMENT_RUN_ID"], "your-new-experiment-id")
```

Then run the full paired comparison and export:

```bash
uv run python scripts/run_experiment.py experiments/your-new-experiment-id \
  --key-file /absolute/path/to/your-key-file
uv run python scripts/export_delivery.py --experiment experiments/your-new-experiment-id
```

The runner resumes missing cells and rejects code/configuration drift and duplicate
formal cells. Do not reuse the published experiment ID for new results. Local raw
logs, archives, reference answers, and credentials are intentionally excluded from Git.
Published reports include a portable export of actual model/tool trajectories.

## Presentation

Use `docs/demo-script.md` and the accompanying release video for an English
walkthrough. The video describes saved real runs; it is not presented as a live
recording of model execution. AI-generated narration is disclosed. Review course
submission requirements separately; this repository does not submit anything to
the class signup sheet or send messages to instructors.
