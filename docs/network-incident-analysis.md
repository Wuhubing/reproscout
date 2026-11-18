# Historical DNS incident and recovery evidence

This is a post-hoc investigation of prepared-v3. It does not replace any failed
result, change the prepared-v4 freeze, or establish a new causal experiment.

## Direct observations

The original fifty-nine failures have DNS-resolution errors in their retained
Inspect exception chains, before an API HTTP response. Fifty-five attempts made
no model generation. They are not observed HTTP 429 responses, quota errors, or
scientific-code failures. See the [original failure evidence](../reports/transport-failures-v3.json).

A read-only inspection of the host's power-management log found this timeline:

| Event | UTC on November 17, 2026 | America/New_York |
|---|---|---|
| First v3 Inspect start | 22:42:45 | 17:42:45 |
| Recorded clamshell sleep transition | 22:52:14 | 17:52:14 |
| First DNS-failed attempt completion | 23:19:33 | 18:19:33 |
| Last DNS-failed attempt completion | 23:39:47 | 18:39:47 |

All fifty-nine failure completions occurred after the clamshell transition, during
a sequence of sleep and short background wakes. The latest recorded transition
at completion was **DarkWake for 56** and **Sleep for 3**. The three Sleep cases
completed only one or two seconds after the transition was logged; this is not a
claim that ordinary execution occurred while the machine was fully asleep.
Completion timestamps are a proxy for error timing, not the precise instant of
the DNS lookup.

The one answer-solved v3 attempt, capsule-1175539 B1, also completed during a
DarkWake interval at 23:20:55 UTC. This counterexample is retained: power state
alone does not deterministically explain every request outcome.

The [sanitized correlation ledger](../reports/power-correlation-v3.json) contains
all fifty-nine completion/transition pairs, the successful control, and a hash of
locally retained source evidence. Public data omit process names, device details,
wake requests, and battery information. Original power-transition lines remain
in ignored private storage, alongside the original local Inspect evidence.

## Interpretation and limits

Host sleep/wake-related network availability is a plausible explanation supported
by the observed timing and DNS error class. The exact resolver, gateway, or network
mechanism remains unproven. These logs are not a packet capture, a controlled
sleep/wake intervention, or proof of an OpenAI service outage.

The old controller compounded the incident: it disabled count-request retries,
continued dispatching tasks without a network health gate, and considered any run
summary sufficient to fill a planned cell. This turned infrastructure failures
into a misleadingly complete attempt matrix. The v3 scientific comparison remains
invalid even though every attempt record is preserved.

A later counting probe and the v4 pre-repair connectivity baseline succeeded.
Therefore the observed recovery cannot be attributed solely to the new retry
wrapper. The improvements that can be verified separately are bounded retry
behavior, live development operation, infrastructure-aware completion rules,
shared retry budgets, and preserved audit evidence.

## Operational controls in v4

The frozen protocol adds live preflights, audited retries, and explicit completion
semantics. Scientific failures remain final; infrastructure failures do not fill
scientific cells. All attempts consume the original shared cell allowances.
The run is launched with `caffeinate -i`, as declared before freezing, to prevent
idle sleep while the runner is active. The installed macOS `caffeinate(8)` manual
defines this option as an idle-sleep assertion; it is not a promise of uninterrupted
connectivity or protection from every sleep trigger.

For a laptop replay, keep the display open and the machine awake during execution.
Apple identifies closing a Mac laptop's display as a way to put it to sleep in its
[sleep/wake guide](https://support.apple.com/en-bh/guide/mac-help/mh10330/mac).
On macOS, the published runner can be invoked as:

```bash
caffeinate -i uv run python scripts/run_experiment.py experiments/prepared-v4 \
  --key-file /absolute/path/to/your-key-file
```

The health gate must still succeed. Exhausted connectivity retries leave the study
incomplete; a keep-awake command is not a substitute for that gate. See the
[frozen recovery protocol](network-recovery-protocol.md) and
[measured version comparison](controller-comparison.md).
