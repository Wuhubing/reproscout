# Measured results: prepared-v1

Experiment date: November 17, 2026. Model: `gpt-5.4-mini-2026-03-17`, low reasoning.
This is a prepared-author-environment experiment on a small selected subset,
not an unchanged CORE-Bench Medium score.

## Frozen paired comparison

| Condition / repeat | Solved capsules | Estimated model cost | Total seconds |
|---|---:|---:|---:|
| A1 | 1/2 | $0.02299 | 529.8 |
| B1 | 1/2 | $0.02214 | 355.2 |
| A2 | 1/2 | $0.02294 | 268.6 |
| B2 | 1/2 | $0.02385 | 423.1 |

Average B-minus-A solved count: **+0.0**.
All eight planned formal records are present. Both conditions solved the R task
and failed the Python task in both repetitions. The time difference reversed
between repeats: B was faster in repeat 1 and slower in repeat 2. This does not
support a stable time-benefit claim. Total formal estimated model cost:
**$0.09192**. A is baseline; B includes the frozen development lessons.
Costs exclude image preparation, host compute, and development assistance.

| Capsule | Cell | Correct questions | Solved | Model cost | Seconds | Sample status |
|---|---|---:|---|---:|---:|---|
| capsule-4180912 | A1 | 0/2 | False | $0.01482 | 510.8 | error |
| capsule-4180912 | B1 | 0/2 | False | $0.01220 | 323.6 | error |
| capsule-1175539 | A1 | 1/1 | True | $0.00817 | 19.0 | success |
| capsule-1175539 | B1 | 1/1 | True | $0.00994 | 31.6 | success |
| capsule-4180912 | B2 | 0/2 | False | $0.01202 | 394.6 | error |
| capsule-4180912 | A2 | 0/2 | False | $0.01630 | 245.4 | error |
| capsule-1175539 | B2 | 1/1 | True | $0.01183 | 28.5 | success |
| capsule-1175539 | A2 | 1/1 | True | $0.00664 | 23.3 | success |

The denominator is two unique held-out capsules, each repeated twice per condition.
A sample without a submission counts as unsolved. Framework log completion is
not used as a proxy for sample success. Repetition is not an independent task.
These observations do not establish statistical significance or generalization.
The original target of two additional solved tasks is not claimed on this evidence.

## Selection and environment

The fixed size-ranked preparation target was five development and ten held-out
tasks, including Python and R. Seven author images were available. Eight of the
ten selected held-out images failed preparation with HTTP 429, including three
bounded retry attempts per unavailable image. The smaller available cohort was
frozen before evaluation; no held-out model scores determined replacements.
Selection decisions for all 90 official records and image preparation failures
are published in `manifests/selection.json` and the provisioning ledgers.

The resulting cohort contains five official training tasks and two official test
tasks: Python text capsule-4180912 and R vision-labelled capsule-1175539. Runtime
networking is disabled, author images are pre-provisioned, and amd64 execution is
emulated on an ARM64 host. Each command has a 180-second timeout, each task a
30-minute wall bound and a $1 model budget, plus call and context bounds.

## Development evidence

Six development agent attempts cover five distinct tasks. The final attempts solve
three of the five tasks: CULP (6/6 questions), capsule-2916503 (3/3), and
capsule-9168639 (2/2). Both CULP attempts are preserved. The other development tasks
expose missing offline data and context-bound failures during notebook inspection.
These are development observations, not an additional held-out estimate.

Three developer-curated lessons address missing external data, efficient notebook
output inspection, and documentation discovery. Source cases are listed in the
frozen lessons file. No held-out trace contributed new lessons during evaluation.

## Integrity and verification

- Original prepared inputs unchanged in **8/8 formal runs**.
- Every exported formal evidence artifact was checked against its recorded SHA-256.
- Formal image-tool artifacts recorded: **0**. Task modality and actual tool
  use are separate properties.
- Fourteen software tests and thirteen deterministic environment checks passed.
- GitHub Actions software checks passed for the frozen implementation commit.
- Independent human diagnosis agreement: **not measured**.
- Ten adversarial model-prompt trials: **not conducted**. Deterministic isolation
  checks must not be described as that experiment.

The portable report includes original submitted values, evidence links, usage,
source audits, provisional diagnoses, and exported model/tool trajectories.
The automatic evidence validator checks references, not semantic faithfulness.
See `validation-and-limitations.md` for interpretation limits and development fixes.
