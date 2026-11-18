# What A and B mean, and why v6 B scores lower

A is the unrestricted baseline without the B lesson intervention. B originally added lessons to the same agent. In v6, B also has a different execution tool boundary and strict submission validation. V6 is therefore a **combined lessons-and-capabilities intervention**, not a clean estimate of the effect of lesson text.

| Property | A | B in v6 |
|---|---|---|
| Model, tasks, resources and request budget | Same | Same |
| Scientific commands | Unrestricted shell; can write calculations | Controller dispatch of hash-verified original author files |
| Non-null evidence | Existing general artifact validation | Must trace to a successful original execution |
| Numeric types | Measured after submission | Enforced before acceptance |
| Missing or blocked output | May infer or recalculate | May abstain with null; source-only answers rejected |
| Answer solved | 24/30 | 20/30 |

A's model-facing prompt and four tool schemas are exactly unchanged from v5. No B lessons were supplied to A. There are fifteen exposed tasks, two repeats per condition, for sixty scientific outcomes. The historical term held-out describes the original split; it is not a claim of fresh unseen evaluation after repeated revisions.

## The observed four-run gap

Among thirty matched task/repeat pairs, five are A-only successes and one is B-only, producing a net difference of four. B's ten unsuccessful runs comprise **eight reports containing nulls, one call-cap failure without a report, and one incorrect non-null report**. A has four incorrect reports and two call-cap failures without reports. These categories preserve all failures; infrastructure failures are zero.

B abstentions combine genuine author-pipeline obstacles with weaknesses of the constrained workflow. Original executions can time out, require unavailable external inputs, or depend on rendering context. The all-chunk R fallback fails on `render_appendix()` outside knitting; refusing its partial output lowers the score. In other trajectories B fails to choose an allowed standalone script or the available chunk fallback. These are limitations to improve, not evidence that abstention is inherently superior.

A can obtain a score by supplying new numerical calculations, looking up input data or inferring labels from source. The manual review observes additional/reimplemented scientific calculations in fourteen A runs, with other concerns such as a replacement HTML page containing asserted answers. That does not make every A success invalid, and it is not a measured overall fidelity failure rate. It explains why answer scoring alone cannot adjudicate the research objective.

B also retains interpretation errors. One run selects Original 0.77 rather than Recalculated 1.31 from the correct generated table. Two score-successful runs cite adjusted regression coefficients or means to answer median questions; the separate artifact review marks these citations unsupported. Capability restrictions solve neither statistic selection nor evidence interpretation automatically.

## What the fix establishes

All thirty B executed command sequences match the original-file dispatcher; no model-authored scientific code was executed through its tools. All accepted B reports comply with the numeric contracts. This is not an all-success claim: B has 29 reports, one missing report, eight reports with nulls, and automatic execution statuses of 22 verified, seven unverified and one violated. The violated run regenerates six processed RDS inputs through original preprocessing. The status is retained, even though no model-authored calculation was dispatched.

The mechanical score-plus-verified-execution intersection is 20/30, but semantic evidence review is separate. A's automatic unverified status must not be read as zero faithful reproductions. The observed score gap cannot isolate a causal effect of lessons because B changed tools as well as instructions and the runs remain stochastic.

[Full version comparison](controller-comparison.md) · [Separate artifact review](../reports/semantic-review-v6.json) · [A decline from v4 to v5](baseline-decline-v5.md) · [A transitions from v5 to v6](baseline-transition-v6.md)
