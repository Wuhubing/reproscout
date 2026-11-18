# Delivery artifacts

- `reproscout-demo.mp4`: approximately 3.5-minute English walkthrough of saved real
  results. The narration uses the macOS system voice; it is not a live run recording.
- `../reports/index.html`: portable results application and evidence links.
- `../docs/demo-script.md`: exact narration text and presentation structure.
- `../docs/results.md`: measured outcomes, scope, and limitations.

A GitHub release bundles the source and report files for review. Scientific input
archives, author container images, raw binary logs, reference answer keys, and API
credentials are intentionally not bundled. Follow README.md to rerun the pilot.

The v0.2.0 walkthrough and reports cover fifteen held-out tasks and sixty fresh
formal A/B records. The portable app retains 74 records including development and
historical results, with experiment labels to avoid combining them accidentally.
The original v0.1.0 release remains available as a separate historical artifact.

The v0.3.0 walkthrough covers all sixty new attempts and explicitly explains why
59 DNS failures make the scientific A/B comparison inconclusive. The app preserves
145 agent records, including all earlier experiments and development attempts.
Success rates, controller failures, source integrity, recorded time, calendar span,
and model cost are compared in docs/controller-comparison.md. Lower time/cost is
not presented as an efficiency improvement. No frozen file or failed outcome was
changed during or after execution.
