# Frontend architecture and reference implementations

The v0.8 workspace is an original ReproScout frontend over the existing execution and review modules. No dashboard repository was forked, and no third-party benchmark harness or observability backend is called.

| Reference | What informed this implementation | Reuse boundary |
| --- | --- | --- |
| [shadcn/ui](https://github.com/shadcn-ui/ui) | Quiet sidebar navigation, restrained cards, form controls, status badges, and master/detail layouts | Design reference only; no shadcn source or dashboard template copied. The repository identifies its code as MIT licensed. |
| [Langfuse](https://github.com/langfuse/langfuse) | Separating a run list, execution trace, and inspection details | Interaction reference only; no source copied, SDK installed, or Langfuse service called. Its mixed licensing is not inherited by this project. |
| [Lucide](https://github.com/lucide-icons/lucide) | Consistent navigational, evidence, and status icons | Actual `lucide-react` dependency; complete package license retained under `frontend/licenses`. |
| [React](https://github.com/facebook/react) | Component state and rendering | Actual React/React DOM dependencies, with MIT notices retained. |
| [Vite](https://github.com/vitejs/vite) | Local development and production asset bundling | Build tool; production assets are bundled locally and served by the Python application. |

References were inspected on November 18, 2026. Installed package versions and transitive dependencies are recorded in `frontend/package-lock.json`. All browser assets are local; no CDN, remote font, analytics, or external AI service is called directly by the frontend.

## Product layout

- **Overview:** actual project and run counts, completion and review kept separate, recent attempts, and unresolved runs.
- **Projects:** prepared manifests and author environments; register another already-prepared manifest or start a run.
- **Runs & reviews:** launch with questions, public answer types, bounded budgets and explicitly selected approved lessons; monitor and cancel.
- **Run details:** candidate values beside an evidence inspector; exact line selection, reviewer identity and rationale; separate execution, source integrity, lessons, and trace tabs.
- **Lessons:** explicit development-source proposal, editable text, approval and disabling, with content-hash invalidation.
- **Archive:** previous experiments remain separately accessible and unchanged.

The visual direction uses a dark navigation rail, light work area, purple action accents, and green/amber/red statuses. Status is also written in text, not communicated by color alone. Responsive layouts preserve task controls on smaller screens. Research evidence remains the central interaction; there are no decorative charts with fabricated values.

## Runtime

A loopback-only Python HTTP service exposes a small API over project-owned modules. Each model-backed run uses a separate worker process, so the web server remains responsive. One active worker is allowed per workspace. The browser receives neither the API credential nor arbitrary host filesystem access. Writes require a same-origin request and a per-server request token. Historical reports are read-only inputs to versioned review copies.

The frontend does not rewrite the scientific executor. It reuses `execute`, `ControlledExecution`, `assess`, `import_review`, `report`, and the lesson lifecycle. The main new execution behavior is conservative stopping after a demonstrated offline network dependency failure, with two bounded model calls for finalization.
