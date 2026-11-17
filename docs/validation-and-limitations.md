# Validation and limitations

## What the checks establish

The software checks cover archive path/link rejection, supplied-result exclusion,
clearing stored notebook outputs, fixed question mapping and numeric scoring,
evidence reference boundaries, conservative request reservations, cached-token
accounting, and rejection of changed frozen inputs or test-split lesson sources.

The deterministic integration run checks thirteen properties: expected runtime,
empty supplied results, no Docker socket, no API credential, no private reference
answers, blocked network access, no host home, no private host mount, dropped Linux
capabilities, alternate blocked egress, raised command timeout, termination of the
timed-out process, and successful execution of the original pilot entry script.
These observations apply to the tested configuration, not every possible image.

GitHub Actions runs software checks without an API credential. Scientific replay
and Docker integration remain explicit local steps and are not disguised as unit
tests. External API charges are estimated from returned usage, not a provider
billing receipt. Failed or interrupted calls can retain reserved unknown cost.

## Limits of interpretation

- The available held-out cohort has only two unique capsules. Repeated runs do
  not increase the number of independent tasks. Neither significance nor broad
  language/modality performance should be inferred from these counts.
- Prepared author environments remove the environment-construction burden of
  original Medium tasks. Offline execution can fail on authors' external data
  dependencies. These are deliberate protocol choices, not unchanged benchmark settings.
- The author images run through amd64 emulation on an ARM64 host. A per-command
  timeout can censor a legitimate long scientific computation. Such failures are
  retained in the denominator under the frozen resource policy.
- Evidence references establish that an artifact exists, with a recorded hash and
  line range. They do not prove that the cited computation is the intended one.
  Answer scoring, execution evidence, and semantic interpretation are separate.
- Source audits compare prepared original inputs. New analysis files are allowed.
  A successful score alone is not proof of faithful reproduction.
- Automatic diagnosis uses trace signatures. Environment, code, output, and budget
  categories can overlap; unclear instructions require review rather than a
  confident automatic attribution. No independent annotation agreement is measured.
- Deterministic isolation checks are not ten adversarial model prompts and are
  not a formal security proof. Archived third-party images are trusted inputs to
  this local research setup. The model has no web-search tool or runtime egress.
- Development lessons were curated with Codex assistance. They are not an
  autonomous, fully reproduced ExpeL learning procedure.
- Capsule archives, reference keys, original binary logs, and container images are
  not bundled in the public source release. The report exports actual trajectories
  and evidence; replay depends on the upstream artifact services remaining available.

## Development provenance

Two early startup attempts failed before a run summary: missing mock-model pricing
configuration and missing explicit pricing for the chosen real model. They are
implementation setup failures, not omitted scientific evaluation cells. All six
completed development agent records, including two runs of the initial pilot, are
retained in the report. The first pilot cost was recalculated from its original
usage after a cached-token accounting bug was fixed. The later pilot includes a
source hash audit. Notebook stored-output stripping was added after development
inspection and before the formal experiment; original notebook code-cell source
was preserved. Held-out evaluation uses the frozen prepared inputs.

Project-authored text is English. Unmodified third-party scientific filenames,
code excerpts, task titles, or tool output may retain the authors' original language.

## Post-evaluation presentation maintenance

After all eight formal cells completed, the exporter received two presentation
fixes: reading the diagnosis field named `label` and marking the first development
attempt's absent source audit explicitly as not recorded. The original execution
freeze is preserved as `experiments/prepared-v1/freeze-execution.json` and in commit
`3e4e5db`. The delivery freeze records the old/new exporter hashes and reason.
No agent, runner, scoring, task input, configuration, lesson, or experimental result
changed. New visual-tool unit tests were added without modifying execution code.
