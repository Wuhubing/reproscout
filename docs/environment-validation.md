# Environment validation

Validation performed on November 17, 2026.

- Host: ARM64 macOS; Python 3.12.2.
- Docker Engine: 29.5.2 in Colima; Docker Compose: 2.30.3-desktop.1.
- Inspect AI: 0.3.290; dependency resolution pinned in uv.lock.
- Colima was initially stopped. It was started with 4 CPUs and 8 GiB memory.
- The active Docker context changed from an unavailable OrbStack context to Colima.
- A broken Compose plugin symlink was redirected to the installed Docker Desktop binary.
- The CULP author image runs linux/amd64 via emulation. Its runtime reports Python
  3.6.3, scikit-learn 0.19.2, networkx 2.1, and numpy 1.13.3.

The deterministic `validate` run checked network failure, absent credentials,
absent host Docker socket, absent supplied results, runtime versions, timeout
raising, and termination of a timed-out process. The author entry script completed.
See the exported environment-checks.json for machine-readable observations.

## Integration findings

- A mock model has no default pricing metadata; deterministic validation must not
  configure a monetary limit on that mock model.
- The pinned real model also needed explicit pricing registration in Inspect.
- Inspect's input_tokens excludes cache-read tokens. An initial accounting formula
  double-subtracted cached tokens; it was corrected using the untouched raw usage
  and covered by a regression test before formal evaluation.
- Inspect can finish a task log successfully while a sample has an error. Run
  status therefore checks the sample error independently.
- Some author code requires runtime external data. Such tasks fail under the
  offline policy; this is retained as a meaningful environment constraint.
- The registry rate-limited bulk image pulls with HTTP 429. Preparation attempts
  and final cohort membership are retained separately from evaluation outcomes.
