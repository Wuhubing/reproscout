# Research references and implementation boundaries

## Direct dependencies

- [Inspect AI](https://inspect.aisi.org.uk/): general model interface, ReAct loop,
  Docker sandbox lifecycle, structured execution logs, and Inspect View.
- Docker/Compose: isolated author environments and resource constraints.
- SciPy: Student's t quantile for the original numerical prediction interval.

Exact installed versions are in `uv.lock`. There is no `inspect-evals` dependency.

## Consulted implementations

- [CORE-Bench](https://github.com/siegelz/core-bench), commit
  `e32a2980e72fe6eb04ee04eb749458f570625663`: task definitions and original scoring
  behavior. Our scorer independently implements the stated 95% prediction
  interval, exact question mapping, percentage-string conversion, and case-insensitive
  string comparison. It does not use the Inspect Evals punctuation normalization.
- [Inspect Evals CORE-Bench](https://github.com/UKGovernmentBEIS/inspect_evals/tree/a9f1b2c154b32fa8b3eda6286bcae01499815779/src/inspect_evals/core_bench):
  reference for task composition and pitfalls, not imported, forked, or executed.
- [ExpeL](https://arxiv.org/abs/2308.10144): experience collection, insight extraction,
  then evaluation. Our frozen rule intervention does not reproduce all ExpeL features.
- [Reflexion](https://arxiv.org/abs/2303.11366): textual reflection from feedback.
  No held-out reflection is added to the frozen rules.
- [HAL](https://github.com/princeton-pli/hal-harness): cost-aware experimental
  organization. Its archived harness is not a runtime dependency.

## Project-owned code

Task preparation, private answer separation, conservative request reservations,
controller-owned evidence snapshots, submission validation, external scoring,
experiment freezing, and project reports are authored in this repository.
We use reference designs without copying a benchmark tree or invoking its task.

## Data and licensing

Capsule downloads remain outside Git. Author code and data retain their own licenses.
The initial capsule is [CULP: Classification Using Link Prediction](https://doi.org/10.24433/CO.0609cc4f-8b95-4d94-8fd0-9456d262b3a5)
by Seyed Amin Fadaee and Maryam Amir Haeri. Download hashes and input inventory
are recorded in the manifest. The project license does not relicense capsules.

## Known differences

- Trusted preparation supplies the archived image; the agent does not build it.
- Runtime networking is disabled, stricter than a package-index allowlist.
- Supplied results and metadata are excluded before the agent starts.
- Reference answers are loaded by the controller only after the agent finishes,
  never included in Inspect Sample metadata or model messages.
- Evidence is mandatory in addition to the benchmark answer mapping.
- Scoring rejects nonfinite numbers and fails clearly on invalid reference data.
  It does not reproduce broad exception swallowing in the original script.
