# ReproScout product guide

ReproScout is a local review tool for scientific computations. Its users are researchers, reviewers, and students who have author code, data, a prepared environment, and explicit questions. It runs the supplied author code, retains evidence and failures, and produces an offline review report. It does not certify a paper or independently establish scientific validity.

## Inputs and outputs

The input manifest specifies the title, questions, `answer_types` (`number`, `string`, or `number_list`), prepared archive and SHA-256, original input inventory, pinned container image, and split. `answers_path` is optional. Omit it to review without scoring; an explicitly configured but unreadable reference path is a configuration error. Reference answers remain on the host and are not included in the agent prompt or container.

The output is a timestamped run directory containing a report, candidate answers when available, original execution ledger, captured text and images, source audit, budget and network records, diagnosis, and a versioned review assessment. Missing answers and failed executions remain visible. A completed run still needs semantic review: a valid citation and an exact reference match do not prove that the cited statistic answers the question.

## Run a prepared task

Install the project using the repository setup instructions, start Docker, and configure an API credential outside the repository. Example:

```sh
reproscout doctor
reproscout run --manifest manifests/product/capsule-6460826.json --config configs/product.json
```

Use `OPENAI_API_KEY` or `--key-file /path/to/private/key.txt`. Never commit credentials. The product defaults to `execution_policy: author_only`. This exposes original-file execution and inspection tools, not arbitrary replacement science. All original R Markdown chunks may be executed as a documented fallback, but this can differ from native document rendering. Existing explicit experiment IDs retain legacy experiment behavior; historical experiments must be reproduced from their frozen tags and configurations.

The default budgets remain 20 model calls, 1,800 wall seconds, 180 seconds per command, and a $1 model cap. Network transport retries and accounting reuse the existing controller. The author sandbox is offline; missing external data is a real blocker, not permission to substitute data.

## Read and review

Open `report.html` in the returned run directory. Review the candidate value, exact evidence lines or image, execution success, changed inputs, and diagnosis separately. Partial output from a failed execution is candidate evidence only. An original preprocessing script can change data; review its role and provenance before interpreting that change. Signature-based diagnoses are provisional and can have multiple contributors.

To record a review, create an English JSON file:

```json
{
  "run_id": "EXACT-RUN-DIRECTORY-NAME",
  "reviewer": "Your name or assistant identifier",
  "reviewer_kind": "human",
  "questions": {
    "q1": {
      "support": "supported",
      "rationale": "Explain how the metric, object, and units match the question.",
      "evidence": [
        {"artifact": "artifacts/step-003.stdout.txt", "line_start": 4, "line_end": 6}
      ]
    }
  }
}
```

```sh
reproscout review runs/RUN-ID --import-file /path/to/review.json
```

Allowed support values are `supported`, `unsupported`, and `uncertain`. Use `reviewer_kind: assistant` for model-assisted review; this must never be represented as independent human agreement. Imports require identity, matching run ID, rationale, and valid retained citations. Existing imports cannot silently be overwritten.

## Lessons lifecycle

Lessons are editable Markdown accompanied by provenance JSON in `lessons/registry`. Creation is explicit. Only training, development, or user-project runs are eligible; formal evaluation runs and private answer files are rejected as sources.

```sh
reproscout lessons propose --id inspect-output --source-run runs/DEVELOPMENT-RUN \
  --action-text 'Inspect the generated output and match its metric to the question.' \
  --applicability 'Original scripts with printed statistics' \
  --evidence artifacts/step-003.stdout.txt
reproscout lessons list
reproscout lessons approve --id inspect-output --reviewer 'assistant:development-review'
reproscout run --manifest manifests/product/capsule-6460826.json --lesson-id inspect-output
reproscout lessons disable --id inspect-output --reviewer 'assistant:development-review'
```

Proposed rules are inactive. Select approved IDs explicitly for each run. Editing the Markdown invalidates approval until it is approved again. Disabled rules cannot be selected. The run stores the complete approved text, content hash, source run, evidence hash, and approver. Compare loaded rules with observable steps; loading alone is not proof of adherence or benefit.

## Scope and references

This release supports prepared CPU Python/R capsules. It does not automatically adapt arbitrary repositories, reconstruct papers into code, offer hosted accounts, or run a new benchmark study. It retains Inspect AI orchestration, Docker isolation, evidence capture, and project-owned execution controls.

The design references [CODECHECK](https://codecheck.org.uk/) for auditable computational review, [ExpeL](https://github.com/LeapLabTHU/ExpeL) for explicit experience-derived guidance, and [ReproZip](https://www.reprozip.org/) for portable provenance. These are design references, not forked implementations or runtime dependencies. CORE-Bench provides existing task data; its benchmark harness is not invoked.
