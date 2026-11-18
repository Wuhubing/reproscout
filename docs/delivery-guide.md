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
freeze, check out that tag; current package code belongs to the repaired-controller study. The prepared-v2
freeze records that its agent source, model configuration, and lessons were
byte-identical to v0.1.0. Prepared-v3 intentionally changes request accounting
while retaining the same model, lessons, inputs, and primary execution budgets.

See [registry recovery](registry-recovery.md) for the observed HTTP behavior,
implemented retry policy, and cache verification evidence.

## Review v0.3.0 accurately

Read `docs/controller-comparison.md` before interpreting the new solved count.
The 60-cell matrix completed, but 59 count requests failed on host-side DNS
resolution. All failures remain included. This is not evidence that lessons
improved or that the application became faster or cheaper at completing science.
The same fifteen test capsules had prior exposure.

The v3 source and freeze remain unchanged at execution commit a74abe6 and freeze
commit ebb0b76. Historical v2 verification belongs at tag v0.2.0; historical v1
verification belongs at tag v0.1.0. Use a fresh experiment ID for any future rerun.
Do not replace failed cells in the published matrix.

For a completed locally generated comparison, the generic evidence commands are:

```bash
uv run python scripts/export_delivery.py --experiment experiments/YOUR_ID
uv run python scripts/summarize_experiment.py experiments/YOUR_ID
uv run python scripts/summarize_controller.py experiments/YOUR_ID --previous experiments/prepared-v2
```

The published narrative and homepage also include editorial interpretation of the
observed DNS failures. Preserve that interpretation when regenerating the package.
The native-counter dependency must be checked separately from Docker networking:
the scientific container stays offline while the host connects to the model API.
The post-run connectivity check is diagnostic only and does not replace any result.
