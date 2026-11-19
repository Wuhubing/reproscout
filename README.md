# ReproScout

**An independent MIT 1.125 project by Weibing Wang.** I developed ReproScout to help researchers run original scientific code, inspect evidence behind candidate answers, record attributed reviews, and export portable reports.

**[Watch the 4:26 product demonstration](https://youtu.be/FWAhCytPl-0)** · **[Explore the evidence website](https://wuhubing.github.io/reproscout/)** · **[First-delivery guide](docs/first-delivery.md)**

The video shows prepared-project import, bounded execution, evidence inspection, source integrity, assistant-attributed reviews, and offline report export. The website is a read-only evidence archive; the authenticated execution app has been verified on the development host.

**GitHub Actions investigation:** [Feasibility, official limits, and a successful real Docker acceptance run](docs/github-actions-feasibility.md). Suitable for repository CI; not wired as the public application compute backend.

**v0.10 authenticated execution pilot:** browser login, private ZIP uploads, real Docker runs, saved reviews, and report export. [Setup, validation, and deployment status](docs/online-pilot-v10.md). Public execution hosting is pending a server; the existing Pages site remains read-only.

**Public evidence website:** [Open ReproScout](https://wuhubing.github.io/reproscout/). Explore published runs, inspect evidence, and download reports. GitHub Pages is read-only; import, execution, and review editing run locally. [New project walkthrough](docs/new-project-walkthrough-v9.md) · [Website deployment](docs/github-pages.md).

**v0.8 local App:** run `uv run reproscout serve` and open `http://127.0.0.1:8765`. [Workspace guide](docs/workspace-guide-v8.md) · [Validation](docs/workspace-release-v8.md) · [Frontend references](docs/frontend-references-v8.md).

**v0.7 product workflow:** [User guide](docs/product-guide.md) · [Offline review dashboard](reports/index.html) · [Release validation](docs/product-release-v7.md). Historical experiments remain available from the dashboard.

The retained experiments also investigate whether frozen lessons help subsequent attempts. Their results and failure records remain available as supporting research; they do not establish a consistent lesson benefit.

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

## v0.6.0: controlled execution and separate fidelity assessment

All **60 scientific A/B cells** completed under one unchanged freeze: **A 24/30,
B 20/30**. The previous v5 run scored A 20/30 and B 26/30; v4 scored A 25/30
and B 21/30. These are repeated samples on fifteen exposed tasks, not a new
held-out generalization result or proof of a causal lesson effect.

V6 changes B capabilities: it can execute only hash-verified original author files,
read generated outputs and submit typed evidence. It cannot supply replacement
scientific code, formulas, loaders or interpreter arguments. Numeric strings,
booleans and nonfinite numbers are rejected. Non-null citations must trace to a
successful original execution. A retains the exact v5 prompt and four tool schemas;
model, scorer, resource limits, transport and sandbox are unchanged.

**Scoring and fidelity are distinct.** B has 29/30 typed
submissions, 0 accepted type violations,
1 missing submissions and 8 runs
with null answers. B execution statuses: `{'verified_original_execution': 22, 'unverified': 7, 'violated': 1}`.
The solved-and-verified-execution intersection is 20/30.
This verifies a capability boundary and output provenance, not full scientific
coverage or semantic interpretation. A is not automatically certified because it
lacks the controlled ledger; unverified does not mean zero faithful reproductions.
Read the separate semantic review rather than equating score or hashes with fidelity.

Development completed ten scientific cells plus one retained setup failure: A 4/5,
B 3/5. A's extra notebook success replaced a loader in memory; B preserved the
missing-input blocker. All B typed submissions and provenance checks passed, with
three verified original-execution successes. The predeclared gate was not lowered.
48 software tests and two final offline wrapper probes passed; the initial failed
plotting fixture is also retained. See [development evidence](docs/fidelity-development-v6.md).

The [A-decline analysis](docs/baseline-decline-v5.md) accounts for every v4-to-v5
transition: six regressions and one gain. Wrong output selection, a contradiction
of computed medians, reimplemented calculations and failure to submit explain the
observed trajectories. A did not receive B's lessons; causation is not established.

All 60 formal attempts, 0 infrastructure failures,
old results and failed development evidence remain available in 368 portable
reports. Estimated formal model cost: $1.64149; calendar
interval: 138.03 minutes. 506 frozen file hashes
remained unchanged. Costs exclude development, host and image costs.

[Download v0.6.0](https://github.com/Wuhubing/reproscout/releases/tag/v0.6.0) ·
[Results app](reports/index.html) · [Full comparison](docs/controller-comparison.md) ·
[Fidelity interpretation](docs/lessons-analysis.md) · [Focused B follow-up](docs/controlled-followup-v6.md) · [All outcomes](docs/results.md) ·
[Historical v0.6 video](deliverables/reproscout-demo.mp4) · [Delivery guide](docs/delivery-guide.md)

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

[What A and B mean, and why B scores lower](docs/ab-interpretation-v6.md)
