# Architecture

```text
Official task metadata (host-private answers)
            |
Independent preparation: checksum, input sanitization, pinned image
            |
Inspect Task -> ReAct -> bounded model generation
                         | shell / read_file / view_image / submit_report
                         v
                  Offline author container
                         |
               Controller-owned evidence snapshots
                         |
Agent finishes -> external scorer -> provisional diagnosis
                         |
       HTML report + original Inspect log + SQLite index
```

The model runs on the host via Inspect's provider interface. Its tools execute
only in the task container. Reference answers are not stored in Sample metadata
or supplied to model messages. Scoring runs after the agent stops. Evidence
snapshots are written outside the sandbox and cannot be edited by the agent.

Docker lifecycle and tool transport use Inspect. ReproScout owns the task input
contract, preparation policy, evidence contract, budget reservations, scoring,
freeze checks, and report generation. No existing benchmark task is invoked.

The first author image runs amd64 code through Colima's emulation on an ARM64
Mac. This is slower than native execution and is documented as an environment
limitation. Container isolation is tested, not claimed to be a formal security proof.

All original source/data input hashes are checked before cleanup. Additional files
may be created for analysis and outputs. Source modifications are reported rather
than silently accepted as unchanged reproduction.
