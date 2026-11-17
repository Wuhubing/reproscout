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
uv run python scripts/recover_cohort.py --target 15
```

Inspect `manifests/selection-v2.json`, `manifests/recovery-v2.json`, and
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
Opaque encrypted provider reasoning is omitted from the public export; visible
messages, tool calls, outputs, and returned usage are retained.

## Presentation

Use `docs/demo-script.md` and the accompanying release video for an English
walkthrough. The video describes saved real runs; it is not presented as a live
recording of model execution. AI-generated narration is disclosed. Review course
submission requirements separately; this repository does not submit anything to
the class signup sheet or send messages to instructors.

## Expanded image recovery

```bash
uv run python scripts/recover_cohort.py --target 15
```

This preserves the original selection ledger, records the expanded fixed selection,
resolves public author images through standard registry authentication, verifies
manifest digests, and pulls serially. Resuming skips locally verified ready images
without additional registry requests. Upstream rate limits may require a cooldown;
there is no assumed reset window or identity rotation. Archive downloads and
reference answer extraction require GnuPG when the local cache is absent.

The original release remains available at tag v0.1.0. To verify its historical
freeze, check out that tag; current manifests and package version belong to the
expanded study. The expanded freeze records that all agent source files, model
configuration, and lessons are byte-identical to the original release.

See [registry recovery](registry-recovery.md) for the observed HTTP behavior,
implemented retry policy, and cache verification evidence.
