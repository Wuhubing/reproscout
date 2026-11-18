# ReproScout

ReproScout runs authors' scientific code in isolated containers, submits answers
with execution evidence, and evaluates whether frozen lessons help subsequent attempts. This is an independently authored MIT 1.125 project by Weibing Wang.

It uses **Inspect AI as infrastructure**, not an existing benchmark task. It does
not fork or invoke `inspect_evals/core_bench` or the original CORE-Agent harness.
See [implementation references](docs/research-references.md).

## What works

- Independent loading and preparation of official CORE-Bench train/test capsules.
- Archived author images pinned by digest; audits of original author inputs.
- No runtime network, privileged mode, host directory mounts, or Docker socket.
- Inspect ReAct with project-owned shell, file, image/PDF, and evidence submission tools.
- External answer scoring, per-call usage accounting, and request cost reservations.
- Original logs, controller-owned evidence snapshots, source-integrity checks,
  a SQLite event index, and portable HTML reports.
- Experiment freeze verification and resumable A/B repetition orchestration.

**Important scope:** the controller pre-provisions the author environment. This is
not an unchanged CORE-Bench Medium result. Image downloads occur before the sample
clock and are recorded separately. A successful pilot is not a benchmark-wide score.

## v0.5.0: evaluated lesson revision

All sixty scientific A/B cells completed under one unchanged freeze. A solved
**20/30**, B solved **26/30**. B scored higher than A in this rerun. This is a descriptive result,
not evidence of statistical significance or unseen generalization.
V4 scored A 25/30 and B 21/30: B gains five while A loses five, leaving the
combined score unchanged at 46/60. Two of the four recovered B scores still involve
reimplemented computations; one also violates the numeric-type reminder.

The [four-pair analysis](docs/lesson-pair-analysis-v4.md) found two numeric-format
failures, one wrong-output-family selection, and one exhausted submission budget.
It also found an A run that altered a scientific copy while original-file hashes
remained unchanged. Hash integrity and answer scoring do not establish full fidelity.
Revision 2 adds conditional execution, evidence selection, submission-budget and
JSON-type reminders, with an explicit prohibition on changing scientific copies.
The scorer, base prompt, scientific tools, model and limits remain unchanged.

Before the formal freeze, a fifteen-outcome three-arm training comparison rejected
the first candidate for a scientific-copy edit. A second candidate was then run
on all five training tasks, for twenty development outcomes in total. New B solved 3/5; old B
4/5; A 3/5. The final candidate submissions, numeric
formats, input hashes and manual scientific-copy checks passed the amended gate.
The legacy fidelity-qualified count was 3/5.
Original raw-score floor passed: False. The comparator
was amended before confirmation after a legacy success modified original code;
[the amendment is retained](docs/lesson-confirmation-protocol.md).
This is a limited mechanism check, not proof of superiority.

**Exposure disclosure:** the revision was informed by prior test trajectories.
The same fifteen test tasks were rerun twice. This is test-informed method development
and an exposed-cohort regression study, not a fresh held-out test.

All 60 formal attempts are retained, including 0
infrastructure failures outside the sixty-cell scientific denominator. Total estimated
model cost: $1.50081; calendar interval:
134.55 minutes. Original-input audits across all attempts:
`{'unchanged': 60}`. All old releases and 297 portable run records are preserved.

[Download v0.5.0](https://github.com/Wuhubing/reproscout/releases/tag/v0.5.0) ·
[Results app](reports/index.html) · [Four-version comparison](docs/controller-comparison.md) · [Four-pair follow-up](docs/adverse-pair-followup-v5.md) ·
[Full results](docs/results.md) · [Lessons analysis](docs/lessons-analysis.md) · [Development results](docs/lesson-development-results.md) ·
[English video](deliverables/reproscout-demo.mp4) · [Reproduction guide](docs/delivery-guide.md)

33 software tests passed. Source and dependency integrity, browser navigation,
artifact hashes and release checks are recorded in reports/delivery-validation.json.
Reading the saved evidence requires no API key.

## Install

Requirements: Python 3.12, `uv`, Docker Engine, and Docker Compose v2. The pilot uses
an amd64 author image; Apple Silicon needs Docker's amd64 emulation. Bulk preparation
also needs GnuPG. Allow substantial disk space for archived images.

```bash
git clone https://github.com/Wuhubing/reproscout.git
cd reproscout
uv sync --locked --extra dev
uv run reproscout doctor
uv run reproscout prepare
```

The preparation command downloads only the official training metadata and the
small CULP capsule, verifies checksums, excludes supplied results, and keeps
reference answers in ignored `private/`. Pull the pinned author image:

```bash
docker pull --platform linux/amd64 \
  registry.codeocean.com/published/0609cc4f-8b95-4d94-8fd0-9456d262b3a5@sha256:8627797e74cc92c24dff1abec45d299f62b842f41630be4d0a87421df24c3a5e
```

## Validate and run

```bash
uv run reproscout validate
uv run reproscout run --key-file /absolute/path/to/your-key-file
```

Alternatively, set `OPENAI_API_KEY` in the host process. The key is read in memory,
never copied into the repository or passed to the task container. Do not commit it.
The key file may contain a raw key or a single key assignment. No key is bundled.

`validate` uses a deterministic solver, not an LLM. It checks the runtime, network,
credential/socket absence, empty results, command termination, and original author
execution. `run` starts a fresh container and calls the configured model.

Every run writes a distinct directory under `runs/`. Open its `report.html`, or use
Inspect's general log viewer:

```bash
uv run inspect view --log-dir runs
```

## Understand a run

| File | Meaning |
|---|---|
| `manifest.json` | Exact task, source revision, input hashes, and image digest |
| `config.json` | Model, budget, condition, and repetition |
| `summary.json` | Sample status, scoring, elapsed time, and model costs |
| `submission.json` | Actual agent answers and evidence references |
| `artifacts/` | Controller-recorded tool outputs and image snapshots |
| `artifact-index.json` | Artifact hashes and provenance |
| `source-audit.json` | Whether original source/data changed |
| `diagnosis.json` | Provisional failure category with evidence |
| `budget.json` | Request reservations and actual returned usage |
| `network-events.jsonl` | Each request attempt, failure class, backoff and recovery |
| `retry-context.json` | Earlier infrastructure attempts and remaining shared budgets |
| `logs/*.eval` | Inspect's original trajectory |
| `index.sqlite` | Rebuildable index of trajectory events |

Answer correctness, source integrity, evidence availability, and semantic support
are separate checks. The automatic evidence validator does not establish semantic
support on its own. Missing or failed runs are retained, not silently removed.

## Budget and pricing

The current configuration uses `gpt-5.4-mini-2026-03-17`, low reasoning, one model
request at a time, at most 20 calls and 30 minutes per sample. Each command has a
180-second timeout. Requests reserve a conservative cost before dispatch; retries
use a bounded audited policy: counting retries transient errors, while generation retries require a classified DNS failure without an HTTP response. Unknown failed-call costs retain their reservation. See the frozen network protocol.

Standard API prices checked on November 17, 2026: $0.75/M uncached input tokens,
$0.075/M cached input tokens, and $4.50/M output tokens. See the
[official model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini).
The controller counts complete native requests, with a 60,000-token input cap
and a 2,048-token margin. The policy and historical byte proxy are described in
[validation limits](docs/validation-and-limitations.md); this is separate from the
provider model context window.

Amounts are usage-based estimates, not billing receipts. Inspect reports uncached
input and cache-read tokens separately; both are included correctly in our ledger.

## Tests

```bash
uv run pytest -q
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
```

The release passes 31 software tests and 13 deterministic environment checks.
Tests cover unsafe archives, stale result exclusion, evidence boundaries, original
numeric scoring, cached-token accounting, pre-dispatch reservations, and freeze
integrity. Container checks are run separately through `validate`.

## Research and limitations

The planned intervention is a frozen, human-readable lessons file derived only
from development runs. A and B use the same model, tools, budget, and task inputs.
No held-out trace contributes new lessons during a comparison.

Failure labels are provisional operational diagnoses, not an independently
validated attribution study. The application is a local research tool, not a
multi-user service or a general promise to reproduce arbitrary papers.

- [Implementation plan](docs/implementation-plan.md)
- [Research references](docs/research-references.md)
- [AI assistance disclosure](docs/ai-disclosure.md)

Scientific capsules retain their own code/data licenses. Project code is MIT licensed.
