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

- The v3 and v4 cohorts have fifteen unique capsules, all previously evaluated. In v2,
  two had previous v0.1.0 exposure and thirteen were newly evaluated. Repeated runs do
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

## Historical prepared-v1 presentation maintenance

After all eight formal cells completed, the exporter received two presentation
fixes: reading the diagnosis field named `label` and marking the first development
attempt's absent source audit explicitly as not recorded. The original execution
freeze is preserved as `experiments/prepared-v1/freeze-execution.json` and in commit
`3e4e5db`. The delivery freeze records the old/new exporter hashes and reason.
No agent, runner, scoring, task input, configuration, lesson, or experimental result
changed. New visual-tool unit tests were added without modifying execution code.

## Expanded-study metadata

The displayed vision flag is the preparation heuristic used consistently in both
studies: a question contains the substring `fig`. It is not an independently
validated taxonomy or proof that the agent inspected an image. The results report
also counts actual image-tool artifacts separately. The expanded study retains
five development tasks and frozen lessons; it does not claim ten development tasks
merely because the original held-out target of fifteen was recovered.

## Historical v1/v2 request bound versus model context capacity

`Pilot context limit reached` is raised by ReproScout's own request-reservation
controller, not by the OpenAI service. It stops when the serialized request byte
bound plus an 8,192 framing allowance exceeds 60,000. Image payloads are replaced
with conservative 8,192-character placeholders for this calculation. Other
serialized message fields, including opaque provider reasoning payloads, remain
in that bound. This conservative policy can stop an attempt well before the
model's actual context window or the $1 monetary cap is exhausted. It is unchanged
between A and B and between the original and expanded study. Interpret failures
as performance of this bounded application, not a measurement of the model's
maximum context capacity. The public export omits opaque fields for readability
and credential-scanner reliability; the execution policy and original private
logs remain unchanged.

## Expanded presentation-only amendments

All sixty formal records completed before public-export changes. The original
execution freeze is retained as `experiments/prepared-v2/freeze-execution.json`,
with execution source commit `068f30b`. The delivery freeze records old and new
hashes for two presentation scripts: the exporter omits opaque encrypted provider
reasoning and uses an accurate missing-audit explanation; the demo renderer updates
the software-test count after two privacy regression tests. Visible model messages,
tool calls, outputs, and returned usage are retained. Original raw logs stay local.
No agent, scorer, task input, configuration, lesson, or experimental result changed.

Encrypted provider payloads may contain random strings that resemble credentials.
The public exporter removes those opaque fields while retaining the conservative
credential check for visible content. Tests verify that visible evidence survives,
original in-memory data is not mutated, and a visible key still blocks export.

## Native-count controller and v3 transport failures

V3 counts the full native request, including tools, images and encrypted reasoning,
and adds a 2,048-token margin under a 60,000-token input cap. Maximum output,
monetary reservation, model-call count, command timeout and wall-time policies
remain separately enforced. No context is deleted for counting. The conversion
adapter is isolated and pinned to Inspect 0.3.290; count failures refuse generation.

All sixty formal attempts completed without changing the freeze. Fifty-nine
failed during host-side DNS resolution before a count-request HTTP response, and
55 made no model call. The sole successful attempt cannot establish a lesson effect.
All 39 generated requests had exact native/returned input-count agreement; eight
crossed the historical byte threshold. These accounting observations do not
establish end-to-end reliability. Lower time/cost and unchanged-input rates are
strongly affected by early refusal. Read controller-comparison.md for all five
comparison dimensions and the transport failure records.

Development validation covered both conditions on five training tasks. One B
notebook attempt changed its data loader despite correct answers; it remains
flagged and is not described as faithful reproduction. Correctness and unchanged
input hashes do not, even together, establish semantic evidence support.

Two initial timeout checks failed because the standalone test executable itself
exited with 139 under emulation. The revised deterministic probe uses bash's builtin
and records the exit code. It passed all thirteen checks; prior failures remain
in development-v3-validation.json. This did not change the agent's command timeout.

## Frozen execution and rendered-report interpretation

No frozen source, script, configuration, lesson, input or protocol was amended
for v3, including after completion. The rendered HTML homepage was annotated with
the DNS-failure finding and its zero-call label was made cause-neutral. Markdown
reports distinguish primary answer scoring, input integrity, runtime and transport
failure. These are presentation artifacts, not replacement experimental records.
Regenerating the generic exporter alone does not recreate all editorial annotations.

## v4 network recovery and completion semantics

The new network and scheduler tests cover transient recovery, persistent failures,
non-retryable authentication/quota responses, refusal to retry ambiguous generation,
and preservation of infrastructure failures outside scientific completion counts.
The development gate includes thirty real calls through the same Inspect adapter,
two injected DNS failures followed by live recovery, and ten training A/B outcomes.
These bounded observations do not guarantee future network stability or identify
the historical resolver root cause.

Only non-infrastructure scientific outcomes fill the sixty-cell matrix. All attempts
remain exported, and failed attempts consume the original shared cell cost, call,
and time allowances. Scientific budget failures and incorrect submissions are final.
Preflight exhaustion or exhausted infrastructure retry budgets leave the experiment
incomplete rather than manufacturing a completed matrix. See the frozen network
protocol and complete comparison for exact results. No frozen file changed during
or after v4 evaluation; report narratives are separate delivery artifacts.

The request JSONL ledger records application-level operations. The pinned underlying HTTP transport may retry a connection internally; the ledger is not a packet-level or individual TCP-attempt trace. The historical sleep/DarkWake correlation and successful control are documented separately in [the incident analysis](network-incident-analysis.md).

## v0.5.0 completed lesson-revision study

The revised lesson candidate passed the amended development
gate after a rejected first candidate; twenty training outcomes are retained. All sixty formal scientific outcomes completed under an unchanged freeze:
A 20/30, B 26/30, with 0 separately retained infrastructure
attempts. This is test-informed method revision on an exposed cohort. Original-file
hashes do not audit scientific changes to new copies; supplemental trajectory review
and the original scorer remain separate. The v0.4.0 release and all failures persist.

See [the four-pair diagnosis](lesson-pair-analysis-v4.md),
[revision protocol](lesson-revision-protocol.md), and [comparison](controller-comparison.md).
