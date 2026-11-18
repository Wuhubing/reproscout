# ReproScout

ReproScout runs authors' scientific code in isolated containers, submits answers
with execution evidence, and tests whether frozen development lessons help on
held-out tasks. This is an independently authored MIT 1.125 project by Weibing Wang.

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

## v0.4.0: completed scientific matrix after network recovery

**All sixty scientific A/B cells completed under one unchanged freeze.**
The scheduler distinguishes scientific outcomes from infrastructure attempts.
It retains every failed attempt, checks connectivity before each cell, and applies
bounded audited retries with shared cell budgets. Scientific failures are final;
they are never rerun to improve scores.

A solved 12/15 and 13/15; B solved
10/15 and 11/15. Total answer success was
46/60; 46 attempts combined
correct answers with unchanged prepared inputs. Average B-minus-A solved count:
-2.0. This is a descriptive result on fifteen previously evaluated tasks,
not a significance claim or unseen generalization.

All-attempt estimated model cost was $1.84094.
Retained infrastructure attempts: 1; terminal native-count
failures: 0; measured-token stops: 0.
All 721 generations are auditable; native counts matched returned
input usage on 721. Source integrity, answer scoring,
and semantic evidence support remain separate properties.

[Download v0.4.0](https://github.com/Wuhubing/reproscout/releases/tag/v0.4.0) ·
[Portable results app](reports/index.html) · [Three-version comparison](docs/controller-comparison.md) ·
[Per-run results](docs/results.md) · [Lessons analysis](docs/lessons-analysis.md) ·
[English demo](deliverables/reproscout-demo.mp4)

The delivery preserves 217 agent records and all earlier experiments. Before
freezing, thirty real counting probes passed, two injected DNS failures recovered,
and ten A/B training outcomes produced 82 generations with exact native counting
and no network failures. One container startup failure was retained and retried.
Thirteen deterministic environment checks and 31 software tests passed.

The [historical power-state investigation](docs/network-incident-analysis.md) records a sleep/wake association without claiming a proven resolver cause.

The previous v3 matrix was **infrastructure-invalid**, with 59 DNS failures and
55 zero-generation attempts. Its 1/60 success and low cost/time do not establish a
lesson effect or efficiency. V2 had 20/60 successes and 39 byte-bound controller
stops. Original v0.1.0, v0.2.0, and v0.3.0 releases remain available.

See the [frozen network protocol](docs/network-recovery-protocol.md),
[development evidence](reports/development-v4-validation.json),
[project overview](docs/project-overview.md), and [reproduction guide](docs/delivery-guide.md).
No API key is needed to inspect saved evidence.

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
