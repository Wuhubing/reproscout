import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Box,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Clock3,
  Download,
  FileSearch,
  FileText,
  FlaskConical,
  FolderOpen,
  History,
  LayoutDashboard,
  ListChecks,
  LoaderCircle,
  MoreHorizontal,
  Play,
  Plus,
  Search,
  ShieldCheck,
  Square,
  Terminal,
  TriangleAlert,
  X,
} from "lucide-react";
import "./style.css";

type Data = Record<string, any>;
let csrf = "";
async function api(path: string, data?: any) {
  const response = await fetch(
    "/api" + path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-ReproScout-CSRF": csrf,
          },
          body: JSON.stringify(data),
        },
  );
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || "Request failed");
  return value;
}
const label = (s: string) => (s || "pending").replaceAll("_", " ");
const money = (v: number) => "$" + (v || 0).toFixed(4);
const active = (s: string) => ["starting", "running", "cancelling"].includes(s);
function Badge({ value }: { value: string }) {
  return (
    <span className={"badge " + value}>
      <span />
      {label(value)}
    </span>
  );
}
function IconButton({
  children,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className="icon-button" {...props}>
      {children}
    </button>
  );
}
function Empty({
  title,
  children,
}: {
  title: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="empty">
      <FileSearch size={30} />
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
function Metric({
  title,
  value,
  caption,
  icon,
}: {
  title: string;
  value: React.ReactNode;
  caption: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="metric">
      <div className="metric-label">
        {title}
        {icon}
      </div>
      <strong>{value}</strong>
      <small>{caption}</small>
    </div>
  );
}

function useModalFocus(enabled: boolean) {
  useEffect(() => {
    if (!enabled) return;
    const previous = document.activeElement as HTMLElement | null;
    const dialog = document.querySelector<HTMLElement>('[role="dialog"]');
    const handle = (event: KeyboardEvent) => {
      if (event.key !== "Tab" || !dialog) return;
      const items = [
        ...dialog.querySelectorAll<HTMLElement>(
          "button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href]",
        ),
      ];
      const first = items[0],
        last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      }
      if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    };
    document.addEventListener("keydown", handle);
    return () => {
      document.removeEventListener("keydown", handle);
      previous?.focus();
    };
  }, [enabled]);
}

function App() {
  const [boot, setBoot] = useState<Data | null>(null),
    [page, setPage] = useState("overview"),
    [selected, setSelected] = useState<string | null>(null),
    [detail, setDetail] = useState<Data | null>(null),
    [newRun, setNewRun] = useState(false),
    [project, setProject] = useState(""),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [search, setSearch] = useState("");
  async function refresh() {
    const b = await api("/bootstrap");
    csrf = b.csrf;
    setBoot(b);
  }
  async function selectRun(id: string) {
    setSelected(id);
    setPage("run");
    setDetail(null);
    try {
      setDetail(await api("/runs/" + id));
    } catch (e) {
      setError((e as Error).message);
    }
  }
  useEffect(() => {
    refresh().catch((e) => setError(e.message));
  }, []);
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const b = await api("/runs");
        setBoot((old) => (old ? { ...old, ...b } : old));
        if (selected) {
          setDetail(await api("/runs/" + selected));
        }
      } catch {}
    }, 2500);
    return () => clearInterval(timer);
  }, [selected]);
  function navigate(next: string) {
    setSelected(null);
    setPage(next);
    setSearch("");
  }
  function openNew(id = "") {
    setProject(id);
    setNewRun(true);
  }
  const runs: Data[] = boot?.runs || [],
    projects: Data[] = boot?.projects || [],
    lessons: Data[] = boot?.lessons || [];
  const pending = runs.filter(
    (r) =>
      r.outcome !== "completed" &&
      r.outcome !== "cancelled" &&
      r.status !== "cancelled" &&
      !active(r.status),
  );
  const filtered = runs.filter((r) =>
    (r.title + " " + r.task_id).toLowerCase().includes(search.toLowerCase()),
  );
  const jobActive = boot?.jobs.some((j: Data) => active(j.status));
  const sidebar = [
    ["overview", "Overview", LayoutDashboard],
    ["projects", "Projects", FolderOpen],
    ["runs", "Runs & reviews", ListChecks],
    ["lessons", "Lessons", BookOpen],
  ] as const;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("overview");
          }}
        >
          <span className="brand-icon">
            <FlaskConical size={21} />
          </span>
          ReproScout<span className="version">0.8</span>
        </a>
        <div className="workspace-switch">
          <span className="workspace-avatar">R</span>
          <div>
            <b>Research workspace</b>
            <small>Local environment</small>
          </div>
          <MoreHorizontal size={17} />
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {sidebar.map(([id, title, Icon]) => (
            <button
              key={id}
              className={
                page === id || (id === "runs" && page === "run")
                  ? "nav-item selected"
                  : "nav-item"
              }
              onClick={() => navigate(id)}
            >
              <Icon size={18} />
              {title}
              {id === "runs" && (
                <span className="nav-count">{runs.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="nav-label second">REFERENCE</div>
        <a
          className="nav-item"
          href="/archive/experiments-v6.html"
          target="_blank"
          rel="noreferrer"
        >
          <History size={18} />
          Experiment archive
          <ArrowUpRight size={14} />
        </a>
        <div className="sidebar-bottom">
          <div className="environment">
            <span className="status-light" />
            <div>
              <b>Running locally</b>
              <small>Author sandbox stays offline</small>
            </div>
          </div>
          <button className="help-link" onClick={() => navigate("help")}>
            <CircleHelp size={17} />
            Workspace guide
          </button>
          <div className="profile">
            <span>RS</span>
            <div>
              <b>Local researcher</b>
              <small>No cloud account required</small>
            </div>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumbs">
            Workspace
            <ChevronRight size={14} />
            <b>
              {page === "run"
                ? "Run details"
                : page === "help"
                  ? "Guide"
                  : sidebar.find((x) => x[0] === page)?.[1]}
            </b>
          </div>
          <div className="top-meta">
            <span className="local-pill">
              <ShieldCheck size={14} />
              Original-code execution
            </span>
            <span className="avatar">RS</span>
          </div>
        </header>
        <main>
          {error && (
            <div className="toast error" role="alert">
              <TriangleAlert size={18} />
              <span>{error}</span>
              <IconButton
                aria-label="Dismiss error"
                onClick={() => setError("")}
              >
                <X size={16} />
              </IconButton>
            </div>
          )}
          {notice && (
            <div className="toast success" role="status">
              <CheckCircle2 size={18} />
              <span>{notice}</span>
              <IconButton
                aria-label="Dismiss notification"
                onClick={() => setNotice("")}
              >
                <X size={16} />
              </IconButton>
            </div>
          )}
          {!boot ? (
            <Empty title="Opening your workspace">
              {error || "Loading retained projects and evidence…"}
            </Empty>
          ) : (
            <>
              {(page === "overview" || page === "runs") && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">
                        {page === "overview"
                          ? "YOUR RESEARCH, WITH A RECORD"
                          : "EXECUTION & REVIEW"}
                      </div>
                      <h1>
                        {page === "overview"
                          ? "Reproduction workspace"
                          : "Runs & reviews"}
                      </h1>
                      <p>
                        {page === "overview"
                          ? "Run original code. Inspect the evidence. Make a supported decision."
                          : "Every attempt stays visible — including partial results and blockers."}
                      </p>
                    </div>
                    <button
                      className="button primary"
                      onClick={() => openNew()}
                    >
                      <Plus size={17} />
                      New reproduction
                    </button>
                  </div>
                  <div className="metrics">
                    <Metric
                      title="Prepared projects"
                      value={projects.length}
                      caption={`${projects.filter((p) => p.prepared).length} available on this machine`}
                      icon={<Box size={18} />}
                    />
                    <Metric
                      title="Completed runs"
                      value={
                        runs.filter((r) => r.outcome === "completed").length
                      }
                      caption="Execution completed · review is separate"
                      icon={<CheckCircle2 size={18} />}
                    />
                    <Metric
                      title="Needs attention"
                      value={pending.length}
                      caption="Partial, blocked, or failed attempts"
                      icon={<TriangleAlert size={18} />}
                    />
                    <Metric
                      title="Reviewed questions"
                      value={runs.reduce((n, r) => n + r.reviewed, 0)}
                      caption="Attributed decisions, not certification"
                      icon={<FileSearch size={18} />}
                    />
                  </div>
                  {page === "overview" && (
                    <div className="workflow-banner">
                      <span className="banner-symbol">
                        <FlaskConical size={27} />
                      </span>
                      <div>
                        <b>Keep the computation. Question the evidence.</b>
                        <p>
                          A successful execution is a starting point. Check the
                          metric, dataset, and units before accepting a result.
                        </p>
                      </div>
                      <button onClick={() => navigate("help")}>
                        How review works
                        <ChevronRight size={15} />
                      </button>
                    </div>
                  )}
                  <div className="dashboard-grid">
                    <section className="panel runs-panel">
                      <div className="panel-heading">
                        <h2>
                          {page === "overview"
                            ? "Recent activity"
                            : "All workspace runs"}
                          <span className="count-chip">{runs.length}</span>
                        </h2>
                        <div className="search-box">
                          <Search size={16} />
                          <input
                            aria-label="Search runs"
                            placeholder="Search runs…"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                          />
                        </div>
                      </div>
                      {boot.jobs
                        .filter((j: Data) => !j.run_id)
                        .map((j: Data) => (
                          <div className="job-notice" key={j.id}>
                            <Badge value={j.status} />
                            <span>{j.title}</span>
                            <small>
                              {j.error || "Preparing the author environment…"}
                            </small>
                            {active(j.status) && (
                              <button
                                className="button"
                                onClick={async () => {
                                  try {
                                    await api("/jobs/" + j.id + "/cancel", {});
                                    await refresh();
                                  } catch (e) {
                                    setError((e as Error).message);
                                  }
                                }}
                              >
                                Cancel
                              </button>
                            )}
                          </div>
                        ))}
                      <div className="table-scroll">
                        <table className="run-table">
                          <thead>
                            <tr>
                              <th>Project / run</th>
                              <th>Execution</th>
                              <th>Review</th>
                              <th>Usage</th>
                              <th />
                            </tr>
                          </thead>
                          <tbody>
                            {filtered.map((r) => (
                              <tr key={r.id} onClick={() => selectRun(r.id)}>
                                <td>
                                  <div className="project-cell">
                                    <span
                                      className={
                                        "project-icon " +
                                        (r.language === "R"
                                          ? "lavender"
                                          : "blue")
                                      }
                                    >
                                      <FileText size={19} />
                                    </span>
                                    <div>
                                      <button
                                        className="row-link"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          selectRun(r.id);
                                        }}
                                      >
                                        {r.title}
                                      </button>
                                      <small>
                                        {r.task_id} ·{" "}
                                        {r.historical
                                          ? "Saved development run"
                                          : "Workspace run"}
                                      </small>
                                    </div>
                                  </div>
                                </td>
                                <td>
                                  <Badge
                                    value={
                                      active(r.status) ||
                                      r.status === "cancelled"
                                        ? r.status
                                        : r.outcome
                                    }
                                  />
                                  <small>{r.scoring}</small>
                                </td>
                                <td>
                                  <span className="review-count">
                                    {r.reviewed}
                                    <span> / {r.questions}</span>
                                  </span>
                                  <small>questions reviewed</small>
                                </td>
                                <td>
                                  <span>{r.model_calls} calls</span>
                                  <small>
                                    {Math.round(r.seconds)}s · {money(r.cost)}
                                  </small>
                                </td>
                                <td>
                                  <ChevronRight size={17} />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {!filtered.length && (
                        <Empty title="No matching runs">
                          Start a reproduction or adjust your search.
                        </Empty>
                      )}
                      <div className="panel-footer">
                        <span>
                          <ShieldCheck size={14} />
                          All attempts retained
                        </span>
                        <span>{runs.length} workspace runs</span>
                      </div>
                    </section>
                    <aside className="insights">
                      <section className="panel attention-panel">
                        <div className="panel-heading">
                          <h2>
                            <TriangleAlert size={17} />
                            Needs attention
                          </h2>
                        </div>
                        {pending.slice(0, 2).map((r) => (
                          <button
                            key={r.id}
                            className="attention-item"
                            onClick={() => selectRun(r.id)}
                          >
                            <Badge value={r.outcome} />
                            <h3>{r.title}</h3>
                            <p>
                              Inspect the first failing step and retained
                              evidence before retrying.
                            </p>
                            <span>
                              Review attempt
                              <ChevronRight size={15} />
                            </span>
                          </button>
                        ))}
                        {!pending.length && (
                          <p className="muted padded">
                            No unresolved execution attempts.
                          </p>
                        )}
                      </section>
                      <section className="panel checklist">
                        <h2>What counts as evidence?</h2>
                        {[
                          "Produced by this execution",
                          "Matches the requested metric",
                          "Uses the intended dataset and units",
                        ].map((t) => (
                          <div key={t}>
                            <Check size={16} />
                            <span>{t}</span>
                          </div>
                        ))}
                        <p>
                          Reference-answer matching is optional and never
                          replaces semantic review.
                        </p>
                      </section>
                    </aside>
                  </div>
                </>
              )}
              {page === "projects" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">
                        PREPARED AUTHOR ENVIRONMENTS
                      </div>
                      <h1>Projects</h1>
                      <p>
                        Start from verified inputs and a pinned environment.
                      </p>
                    </div>
                    <ImportProject
                      onSave={async () => {
                        await refresh();
                        setNotice("Prepared project registered.");
                      }}
                      onError={setError}
                    />
                  </div>
                  <div className="project-grid">
                    {projects.map((p) => (
                      <section className="panel project-card" key={p.id}>
                        <div className="project-card-top">
                          <span className="project-icon lavender">
                            <Box size={22} />
                          </span>
                          <Badge value={p.prepared ? "ready" : "unavailable"} />
                        </div>
                        <h2>{p.title}</h2>
                        <p>{p.description}</p>
                        <div className="project-tags">
                          <span>{p.language}</span>
                          <span>
                            {Object.keys(p.questions).length} questions
                          </span>
                          <span>{label(p.split)}</span>
                        </div>
                        <div className="project-card-footer">
                          <small>{p.task_id}</small>
                          <button
                            className="button"
                            disabled={!p.prepared}
                            onClick={() => openNew(p.id)}
                          >
                            <Play size={14} />
                            New run
                          </button>
                        </div>
                      </section>
                    ))}
                  </div>
                </>
              )}
              {page === "run" &&
                (detail ? (
                  <RunDetail
                    data={detail}
                    onChange={async () => {
                      await refresh();
                      setDetail(await api("/runs/" + selected));
                    }}
                    onError={setError}
                    onNotice={setNotice}
                  />
                ) : (
                  <Empty title="Loading run">
                    Opening the retained evidence…
                  </Empty>
                ))}
              {page === "lessons" && (
                <Lessons
                  lessons={lessons}
                  runs={runs}
                  onChange={refresh}
                  onError={setError}
                  onNotice={setNotice}
                />
              )}
              {page === "help" && (
                <>
                  <div className="page-heading">
                    <div className="eyebrow">WORKSPACE GUIDE</div>
                    <h1>From execution to a reviewed result</h1>
                    <p>
                      ReproScout is a local scientific reproduction review tool.
                    </p>
                  </div>
                  <div className="guide-grid">
                    {[
                      [
                        "Prepare a project",
                        "Select a prepared Python or R capsule with original author code, data, questions, and a pinned container. Import an existing manifest to add your own prepared project. Arbitrary repository adaptation is not automatic.",
                      ],
                      [
                        "Run original code",
                        "Choose questions, answer types, budgets, and optional approved lessons. The author sandbox is offline. Monitor execution and request cancellation; an in-flight bounded operation is allowed to finish safely.",
                      ],
                      [
                        "Inspect the evidence",
                        "Execution success, output provenance, semantic support, file changes, and optional correctness are separate. Read the evidence at its exact lines. Keep partial output visible without promoting it to a successful computation.",
                      ],
                      [
                        "Record a decision",
                        "For each question, record supported, unsupported, or uncertain, with your identity, rationale, and evidence. New reviews are saved as versions; historical reports remain unchanged. Download the portable report to share it.",
                      ],
                    ].map(([title, text]) => (
                      <section className="panel guide-card" key={title}>
                        <h2>{title}</h2>
                        <p>{text}</p>
                      </section>
                    ))}
                  </div>
                  <div className="callout">
                    <ShieldCheck />
                    <div>
                      <b>
                        {boot.credential_ready
                          ? "API credential configured on the host."
                          : "Browsing is available. Execution needs a host API credential."}
                      </b>
                      <p>
                        Credentials never appear in the browser or author
                        container. Only one workspace run executes at a time.
                        Known offline dependency failures stop further execution
                        and allow two finalization calls.
                      </p>
                    </div>
                  </div>
                </>
              )}
            </>
          )}
        </main>
        <footer className="app-footer">
          <span>ReproScout · Scientific reproduction review</span>
          <span>Local-first. Evidence preserved.</span>
        </footer>
      </div>
      {newRun && boot && (
        <NewRun
          projects={projects}
          lessons={lessons}
          initial={project}
          blocked={jobActive || !boot.credential_ready}
          onClose={() => setNewRun(false)}
          onStart={async (job) => {
            setNewRun(false);
            await refresh();
            navigate("runs");
            setNotice(
              "Run started. The workspace will update as evidence arrives.",
            );
            if (job.run_id) selectRun(job.run_id);
          }}
          onError={setError}
        />
      )}
    </div>
  );
}

function ImportProject({
  onSave,
  onError,
}: {
  onSave: () => void;
  onError: (s: string) => void;
}) {
  return (
    <label className="button">
      <FolderOpen size={16} />
      Import prepared manifest
      <input
        className="sr-only"
        type="file"
        accept=".json"
        aria-label="Import prepared manifest"
        onChange={async (e) => {
          try {
            const file = e.target.files?.[0];
            if (!file) return;
            await api("/projects", JSON.parse(await file.text()));
            onSave();
          } catch (err) {
            onError((err as Error).message);
          }
          e.target.value = "";
        }}
      />
    </label>
  );
}

function NewRun({
  projects,
  lessons,
  initial,
  blocked,
  onClose,
  onStart,
  onError,
}: {
  projects: Data[];
  lessons: Data[];
  initial: string;
  blocked: boolean;
  onClose: () => void;
  onStart: (d: Data) => void;
  onError: (s: string) => void;
}) {
  const [id, setId] = useState(initial || projects[0]?.id || ""),
    [questions, setQuestions] = useState<Record<string, string>>({}),
    [types, setTypes] = useState<Record<string, string>>({}),
    [calls, setCalls] = useState(20),
    [seconds, setSeconds] = useState(1800),
    [cost, setCost] = useState(1),
    [chosen, setChosen] = useState<string[]>([]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  useModalFocus(true);
  useEffect(() => {
    const p = projects.find((p) => p.id === id);
    setQuestions({ ...p?.questions });
    setTypes({ ...p?.answer_types });
  }, [id]);
  useEffect(() => {
    const fn = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !busy) onClose();
    };
    window.addEventListener("keydown", fn);
    return () => window.removeEventListener("keydown", fn);
  }, [busy]);
  return (
    <div
      className="modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget && !busy) onClose();
      }}
    >
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="new-title"
      >
        <div className="modal-heading">
          <div>
            <div className="eyebrow">ORIGINAL CODE · NEW ATTEMPT</div>
            <h2 id="new-title">New reproduction</h2>
          </div>
          <IconButton
            aria-label="Close new run"
            onClick={onClose}
            disabled={busy}
          >
            <X size={20} />
          </IconButton>
        </div>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy(true);
            setError("");
            try {
              const job = await api("/runs", {
                project_id: id,
                questions,
                answer_types: types,
                max_model_calls: calls,
                wall_time_seconds: seconds,
                model_budget_usd: cost,
                lesson_ids: chosen,
              });
              onStart(job);
            } catch (err) {
              setError((err as Error).message);
              onError((err as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <div className="modal-body">
            <label className="field">
              Prepared project
              <select
                aria-label="Prepared project"
                value={id}
                onChange={(e) => setId(e.target.value)}
                autoFocus
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id} disabled={!p.prepared}>
                    {p.title}
                    {!p.prepared ? " — unavailable" : ""}
                  </option>
                ))}
              </select>
            </label>
            <div className="form-section">
              <h3>Research questions</h3>
              <p>
                Keep each question tied to an output of the original author
                computation.
              </p>
              {Object.entries(questions).map(([qid, q]) => (
                <div className="question-input" key={qid}>
                  <label className="field">
                    <span>{qid.toUpperCase()}</span>
                    <textarea
                      required
                      maxLength={4000}
                      value={q}
                      onChange={(e) =>
                        setQuestions({ ...questions, [qid]: e.target.value })
                      }
                    />
                  </label>
                  <label className="field">
                    Answer type
                    <select
                      value={types[qid] || "number"}
                      onChange={(e) =>
                        setTypes({ ...types, [qid]: e.target.value })
                      }
                    >
                      <option value="number">Number</option>
                      <option value="string">Text</option>
                      <option value="number_list">Number list</option>
                    </select>
                  </label>
                </div>
              ))}
            </div>
            <div className="form-section">
              <h3>Run budget</h3>
              <div className="budget-fields">
                <label className="field">
                  Model calls
                  <input
                    type="number"
                    min={3}
                    max={20}
                    value={calls}
                    onChange={(e) => setCalls(+e.target.value)}
                    required
                  />
                </label>
                <label className="field">
                  Time limit (seconds)
                  <input
                    type="number"
                    min={60}
                    max={1800}
                    value={seconds}
                    onChange={(e) => setSeconds(+e.target.value)}
                    required
                  />
                </label>
                <label className="field">
                  Model cost cap ($)
                  <input
                    type="number"
                    min={0.01}
                    max={1}
                    step={0.01}
                    value={cost}
                    onChange={(e) => setCost(+e.target.value)}
                    required
                  />
                </label>
              </div>
            </div>
            <div className="form-section">
              <h3>
                Approved lessons <span className="muted">Optional</span>
              </h3>
              {lessons
                .filter((l) => l.effective_status === "approved")
                .map((l) => (
                  <label className="check-field" key={l.id}>
                    <input
                      type="checkbox"
                      checked={chosen.includes(l.id)}
                      onChange={(e) =>
                        setChosen(
                          e.target.checked
                            ? [...chosen, l.id]
                            : chosen.filter((x) => x !== l.id),
                        )
                      }
                    />
                    <span>
                      {l.id}
                      <small>Approved by {l.reviewer}</small>
                    </span>
                  </label>
                ))}
              {!lessons.some((l) => l.effective_status === "approved") && (
                <p>
                  No approved lessons. This run will use the original-author
                  workflow without additional rules.
                </p>
              )}
            </div>
            <div className="callout compact">
              <ShieldCheck size={19} />
              <p>
                Original-author execution only. Reference scoring is off. Every
                attempt, including a failed one, is retained.
              </p>
            </div>
            {blocked && (
              <p className="form-error">
                Execution is unavailable while another run is active or the host
                credential is missing.
              </p>
            )}
            {error && (
              <p role="alert" className="form-error">
                {error}
              </p>
            )}
          </div>
          <div className="modal-actions">
            <button
              type="button"
              className="button"
              onClick={onClose}
              disabled={busy}
            >
              Cancel
            </button>
            <button
              className="button primary"
              disabled={busy || blocked || !id}
            >
              {busy ? (
                <LoaderCircle className="spin" size={16} />
              ) : (
                <Play size={16} />
              )}
              Start reproduction
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

function RunDetail({
  data,
  onChange,
  onError,
  onNotice,
}: {
  data: Data;
  onChange: () => Promise<void>;
  onError: (s: string) => void;
  onNotice: (s: string) => void;
}) {
  const [tab, setTab] = useState("results"),
    [qid, setQid] = useState(""),
    [evidence, setEvidence] = useState<Data | null>(null),
    [preview, setPreview] = useState<Data | null>(null),
    [reviewer, setReviewer] = useState(""),
    [kind, setKind] = useState("human"),
    [support, setSupport] = useState("uncertain"),
    [rationale, setRationale] = useState(""),
    [saving, setSaving] = useState(false),
    [trace, setTrace] = useState<Data | null>(null);
  const r = data.run,
    a = data.assessment,
    questions = data.manifest.questions || {},
    questionIds = Object.keys(questions);
  const current = qid || questionIds[0],
    question = a.questions?.[current],
    candidate = question?.candidate;
  const reviewedBy = [...(data.reviews || [])]
    .reverse()
    .find((record: Data) => record.questions?.[current]);
  const decision = reviewedBy?.questions?.[current];
  const isActive = active(r.status);
  useEffect(() => {
    setEvidence(candidate?.evidence?.[0] || null);
    setRationale("");
    setSupport("uncertain");
  }, [r.id, current, candidate?.evidence?.[0]?.artifact]);
  useEffect(() => {
    if (!evidence) {
      setPreview(null);
      return;
    }
    const url =
      "/runs/" +
      r.id +
      "/evidence?artifact=" +
      encodeURIComponent(evidence.artifact);
    if (data.artifacts[evidence.artifact]?.kind === "image") {
      setPreview({ image: "/api" + url });
      return;
    }
    api(url)
      .then(setPreview)
      .catch((e) => onError(e.message));
  }, [evidence?.artifact, r.id]);
  async function saveReview() {
    setSaving(true);
    try {
      const record = {
        reviewer: reviewer.trim(),
        reviewer_kind: kind,
        questions: { [current]: { support, rationale, evidence: [evidence] } },
      }; // Existing decisions retain their provenance in prior review versions; new record is this reviewer's assertion.
      await api("/runs/" + r.id + "/review", record);
      await onChange();
      onNotice(
        "Review saved as a new version. Original records are unchanged.",
      );
      setRationale("");
    } catch (e) {
      onError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">
            {data.manifest.task_id} · {data.manifest.language} ·{" "}
            {r.historical ? "SAVED DEVELOPMENT RUN" : "WORKSPACE RUN"}
          </div>
          <h1>{r.title}</h1>
          <p className="run-id">{r.id}</p>
        </div>
        <div className="heading-actions">
          {isActive ? (
            <button
              className="button danger"
              onClick={async () => {
                try {
                  await api("/jobs/" + r.job_id + "/cancel", {});
                  await onChange();
                  onNotice(
                    "Cancellation requested. The current bounded operation will finish, then evidence is finalized.",
                  );
                } catch (e) {
                  onError((e as Error).message);
                }
              }}
              disabled={r.status === "cancelling"}
            >
              <Square size={14} />
              {r.status === "cancelling"
                ? "Cancellation requested"
                : "Cancel run"}
            </button>
          ) : (
            <a className="button" href={"/api/runs/" + r.id + "/export"}>
              <Download size={16} />
              Export report
            </a>
          )}
        </div>
      </div>
      <div className="run-summary">
        <Badge
          value={isActive || r.status === "cancelled" ? r.status : r.outcome}
        />
        <span>
          <Clock3 size={15} />
          {Math.round(r.seconds)} seconds
        </span>
        <span>
          <Activity size={15} />
          {r.model_calls} model calls
        </span>
        <span>{money(r.cost)} estimated</span>
        <span className="score-label">{r.scoring}</span>
      </div>
      {isActive && (
        <div className="running-banner">
          <LoaderCircle className="spin" size={20} />
          <div>
            <b>
              {r.status === "cancelling"
                ? "Finishing the current operation before cancellation"
                : "Running original author code"}
            </b>
            <p>
              New steps and evidence appear automatically. Budgets remain
              enforced.
            </p>
          </div>
        </div>
      )}
      {data.blocker && (
        <div className="callout warning">
          <TriangleAlert />
          <div>
            <b>Known offline dependency blocker</b>
            <p>
              {data.blocker.reason} {data.blocker.next_action}
            </p>
          </div>
        </div>
      )}
      <div className="tabs" role="tablist">
        {[
          ["results", "Results & review"],
          ["execution", "Execution"],
          ["source", "Source integrity"],
          ["lessons", "Loaded lessons"],
          ["trace", "Full trace"],
        ].map(([id, title]) => (
          <button
            role="tab"
            aria-selected={tab === id}
            className={tab === id ? "active" : ""}
            key={id}
            onClick={async () => {
              setTab(id);
              if (id === "trace") {
                try {
                  setTrace(await api("/runs/" + r.id + "/trace"));
                } catch (e) {
                  onError((e as Error).message);
                }
              }
            }}
          >
            {title}
            {id === "results" && <span>{questionIds.length}</span>}
          </button>
        ))}
      </div>
      {tab === "results" && (
        <div className="review-layout">
          <section>
            <div className="question-list">
              {questionIds.map((id) => (
                <button
                  key={id}
                  className={
                    (current === id ? "selected " : "") + "question-tab"
                  }
                  onClick={() => setQid(id)}
                >
                  <span>{id.toUpperCase()}</span>
                  <b>{questions[id]}</b>
                  <ChevronRight size={16} />
                </button>
              ))}
            </div>
            <section className="panel candidate-card">
              <div className="panel-heading">
                <h2>Candidate answer</h2>
                <Badge
                  value={
                    decision
                      ? decision.support
                      : candidate?.value != null
                        ? "needs_review"
                        : "unresolved"
                  }
                />
              </div>
              <div className="candidate-value">
                {candidate?.value == null
                  ? "No answer submitted"
                  : Array.isArray(candidate.value)
                    ? candidate.value.join(", ")
                    : String(candidate.value)}
              </div>
              <div className="candidate-checks">
                <span>
                  <ShieldCheck size={16} />
                  Successful-execution provenance{" "}
                  <b>
                    {question?.successful_execution_provenance
                      ? "Verified"
                      : "Not established"}
                  </b>
                </span>
                <span>
                  <FileText size={16} />
                  Citation validity{" "}
                  <b>
                    {question?.citation_valid ? "Valid" : "Not established"}
                  </b>
                </span>
              </div>
              <p className="fine-print">
                A valid citation does not establish semantic support. Match the
                metric, object, and units.
              </p>
              {candidate?.explanation && (
                <p className="padded">{candidate.explanation}</p>
              )}
            </section>
            <section className="panel review-form">
              <div className="panel-heading">
                <h2>Your review</h2>
                <FileSearch size={18} />
              </div>
              {decision && (
                <div className="previous-review">
                  <Badge value={decision.support} />
                  <p>{decision.rationale}</p>
                  <small>
                    {reviewedBy.reviewer_kind} review by {reviewedBy.reviewer}
                  </small>
                </div>
              )}
              <label className="field">
                Decision
                <select
                  value={support}
                  onChange={(e) => setSupport(e.target.value)}
                >
                  <option value="uncertain">
                    Uncertain — more evidence needed
                  </option>
                  <option value="supported">
                    Supported by the cited evidence
                  </option>
                  <option value="unsupported">
                    Not supported by the cited evidence
                  </option>
                </select>
              </label>
              <label className="field">
                Reasoning
                <textarea
                  placeholder="Explain how the metric, dataset, and units match — or why they do not."
                  value={rationale}
                  onChange={(e) => setRationale(e.target.value)}
                  rows={4}
                />
              </label>
              <div className="review-identity">
                <label className="field">
                  Reviewer name
                  <input
                    placeholder="Your name or identifier"
                    value={reviewer}
                    onChange={(e) => setReviewer(e.target.value)}
                  />
                </label>
                <label className="field">
                  Reviewer type
                  <select
                    value={kind}
                    onChange={(e) => setKind(e.target.value)}
                  >
                    <option value="human">Human</option>
                    <option value="assistant">AI assistant</option>
                  </select>
                </label>
              </div>
              <p className="fine-print">
                The selected evidence and line range will be saved with this
                decision.
              </p>
              <button
                className="button primary"
                disabled={
                  isActive ||
                  saving ||
                  !evidence ||
                  !reviewer.trim() ||
                  !rationale.trim()
                }
                onClick={saveReview}
              >
                {saving ? (
                  <LoaderCircle className="spin" size={16} />
                ) : (
                  <Check size={16} />
                )}
                Save review
              </button>
            </section>
          </section>
          <section className="panel evidence-panel">
            <div className="panel-heading">
              <h2>
                <FileText size={18} />
                Evidence inspector
              </h2>
              <span className="count-chip">
                {Object.keys(data.artifacts).length} artifacts
              </span>
            </div>
            <div className="evidence-controls">
              <label className="field">
                Retained artifact
                <select
                  value={evidence?.artifact || ""}
                  onChange={(e) =>
                    setEvidence({
                      artifact: e.target.value,
                      ...(data.artifacts[e.target.value]?.kind === "image"
                        ? {}
                        : { line_start: 1, line_end: 1 }),
                    })
                  }
                >
                  <option value="" disabled>
                    Select an artifact
                  </option>
                  {Object.keys(data.artifacts).map((name) => (
                    <option key={name} value={name}>
                      {name.replace("artifacts/", "")}
                    </option>
                  ))}
                </select>
              </label>
              {evidence &&
                data.artifacts[evidence.artifact]?.kind !== "image" && (
                  <div className="line-range">
                    <label>
                      From line
                      <input
                        aria-label="Evidence start line"
                        type="number"
                        min={1}
                        value={evidence.line_start || 1}
                        onChange={(e) =>
                          setEvidence({
                            ...evidence,
                            line_start: +e.target.value,
                          })
                        }
                      />
                    </label>
                    <label>
                      To line
                      <input
                        aria-label="Evidence end line"
                        type="number"
                        min={evidence.line_start || 1}
                        value={evidence.line_end || 1}
                        onChange={(e) =>
                          setEvidence({
                            ...evidence,
                            line_end: +e.target.value,
                          })
                        }
                      />
                    </label>
                  </div>
                )}
            </div>
            {preview?.image ? (
              <img
                className="evidence-image"
                src={preview.image}
                alt="Retained generated output"
              />
            ) : preview?.text !== undefined ? (
              <div className="code-view" tabIndex={0}>
                {preview.text.split("\n").map((text: string, i: number) => (
                  <div
                    className={
                      i + 1 >= (evidence?.line_start || 0) &&
                      i + 1 <= (evidence?.line_end || 0)
                        ? "highlight"
                        : ""
                    }
                    key={i}
                  >
                    <button
                      title="Select this evidence line"
                      onClick={() =>
                        setEvidence({
                          ...evidence,
                          line_start: i + 1,
                          line_end: i + 1,
                        })
                      }
                    >
                      {i + 1}
                    </button>
                    <code>{text.replace(/\x1b\[[0-9;]*m/g, "") || " "}</code>
                  </div>
                ))}
              </div>
            ) : (
              <Empty title="Choose evidence to inspect">
                Select a retained artifact, including partial output or a
                failure log.
              </Empty>
            )}
            <div className="evidence-note">
              <ShieldCheck size={15} />
              <span>
                Original retained snapshot. Line selection does not modify
                evidence.
              </span>
            </div>
          </section>
        </div>
      )}
      {tab === "execution" && (
        <div className="execution-grid">
          <section className="panel padded">
            <h2>Execution timeline</h2>
            <p className="muted">
              Started, succeeded, and failed events are retained separately.
            </p>
            <div className="timeline">
              {data.ledger.map((event: Data, i: number) => (
                <div className="timeline-event" key={i}>
                  <span className={"timeline-marker " + event.status}>
                    {event.status === "succeeded" ? (
                      <Check size={13} />
                    ) : event.status === "failed" ? (
                      <X size={13} />
                    ) : (
                      <Terminal size={13} />
                    )}
                  </span>
                  <div>
                    <div>
                      <b>{event.path || label(event.operation)}</b>
                      <Badge value={event.status} />
                    </div>
                    <small>
                      {event.mode && `${event.mode} · `}
                      {event.execution_id && `Execution ${event.execution_id}`}
                      {event.input_hashes_verified &&
                        ` · ${event.input_hashes_verified} inputs verified`}
                    </small>
                    {event.reason && <p>{event.reason}</p>}
                  </div>
                </div>
              ))}
            </div>
            {!data.ledger.length && (
              <Empty title="No execution steps yet">
                The controller is preparing, or this attempt stopped before
                execution.
              </Empty>
            )}
          </section>
          <section className="panel padded">
            <h2>Diagnosis</h2>
            <p>{data.diagnosis.primary_cause || "Waiting for finalization."}</p>
            {data.diagnosis.contributors?.map((c: Data, i: number) => (
              <div className="diagnosis-item" key={i}>
                <Badge value={c.label} />
                <p>Stage: {label(c.stage)}</p>
                {c.evidence
                  .filter((e: any) => typeof e === "object")
                  .slice(0, 3)
                  .map((ev: Data, j: number) => (
                    <button
                      className="text-link"
                      key={j}
                      onClick={() => {
                        setEvidence(ev);
                        setTab("results");
                      }}
                    >
                      {ev.artifact} · line {ev.line_start}
                    </button>
                  ))}
              </div>
            ))}
            <h3>Next actions</h3>
            <ul>
              {data.diagnosis.next_actions?.map((t: string) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
            <p className="fine-print">
              Diagnosis is provisional. Error signatures are clues, not proof of
              root cause.
            </p>
            {data.summary.sample_error && (
              <pre className="error-pre">{data.summary.sample_error}</pre>
            )}
          </section>
        </div>
      )}
      {tab === "source" && (
        <section className="panel padded">
          <h2>Source & input integrity</h2>
          <div className="callout">
            <ShieldCheck />
            <div>
              <b>
                {data.source_audit.unchanged === true
                  ? "Original inputs unchanged"
                  : data.source_audit.unchanged === false
                    ? "Input changes need review"
                    : "Integrity audit not available yet"}
              </b>
              <p>
                {data.source_audit.checked_files || 0} files checked. Changes
                alone do not establish tampering; original preprocessing can
                rewrite data.
              </p>
            </div>
          </div>
          {data.source_audit.changed_or_missing?.length > 0 && (
            <ul>
              {data.source_audit.changed_or_missing.map((p: string) => (
                <li key={p}>
                  <code>{p}</code>
                </li>
              ))}
            </ul>
          )}
          <details>
            <summary>Source audit record</summary>
            <pre>{JSON.stringify(data.source_audit, null, 2)}</pre>
          </details>
        </section>
      )}
      {tab === "lessons" && (
        <section className="panel padded">
          <h2>Loaded lesson snapshots</h2>
          <p className="muted">
            These are the exact rules loaded for this attempt. Loading is not
            proof of benefit.
          </p>
          {data.lessons.map((l: Data) => (
            <div className="lesson-snapshot" key={l.id}>
              <h3>{l.id}</h3>
              <p>
                Source: {l.source_run} · Approved by {l.reviewer}
              </p>
              <pre>{l.content}</pre>
              <small className="hash">SHA-256: {l.approved_sha256}</small>
            </div>
          ))}
          {!data.lessons.length && (
            <Empty title="No lessons loaded">
              This run used the original-author workflow without selected
              lessons.
            </Empty>
          )}
        </section>
      )}
      {tab === "trace" && (
        <section className="panel padded">
          <h2>Visible execution trace</h2>
          <p className="muted">
            Messages and tool interactions. Encrypted provider reasoning is
            excluded.
          </p>
          {trace?.messages?.map((m: Data, i: number) => (
            <details className="trace-message" key={i}>
              <summary>
                <span className={"badge " + m.role}>{m.role}</span>
                <span>
                  {typeof m.content === "string"
                    ? m.content.slice(0, 110)
                    : m.tool_calls?.map((t: Data) => t.function).join(", ") ||
                      "Message content"}
                </span>
              </summary>
              <pre>{JSON.stringify(m, null, 2)}</pre>
            </details>
          ))}
          {!trace?.messages?.length && (
            <Empty title="Trace not available yet">
              The full visible trace is exported when the run finishes.
            </Empty>
          )}
        </section>
      )}
    </>
  );
}

function Lessons({
  lessons,
  runs,
  onChange,
  onError,
  onNotice,
}: {
  lessons: Data[];
  runs: Data[];
  onChange: () => Promise<void>;
  onError: (s: string) => void;
  onNotice: (s: string) => void;
}) {
  const [selected, setSelected] = useState(""),
    [content, setContent] = useState(""),
    [reviewer, setReviewer] = useState(""),
    [proposing, setProposing] = useState(false),
    [source, setSource] = useState(""),
    [artifacts, setArtifacts] = useState<string[]>([]),
    [ev, setEv] = useState(""),
    [id, setId] = useState(""),
    [action, setAction] = useState(""),
    [applies, setApplies] = useState(""),
    [busy, setBusy] = useState(false);
  const [proposalError, setProposalError] = useState("");
  useModalFocus(proposing);
  useEffect(() => {
    if (!proposing) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) setProposing(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [proposing, busy]);
  const lesson = lessons.find((l) => l.id === selected);
  useEffect(() => {
    setContent(lesson?.content || "");
  }, [selected, lesson?.content]);
  useEffect(() => {
    if (source)
      api("/runs/" + source)
        .then((d) => {
          const keys = Object.keys(d.artifacts);
          setArtifacts(keys);
          setEv(keys[0] || "");
        })
        .catch((e) => onError(e.message));
  }, [source]);
  async function mutate(operation: string) {
    setBusy(true);
    try {
      await api(
        "/lessons/" + selected + "/" + operation,
        operation === "edit" ? { content } : { reviewer: reviewer.trim() },
      );
      await onChange();
      onNotice(
        operation === "edit"
          ? "Lesson saved. Changed content requires approval again."
          : operation === "approve"
            ? "Lesson approved. Select it explicitly for a new run."
            : "Lesson disabled. Existing run snapshots remain unchanged.",
      );
    } catch (e) {
      onError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">EXPLICIT, AUDITABLE GUIDANCE</div>
          <h1>Lessons</h1>
          <p>
            Development experience, reviewed before reuse. Never learned from
            evaluation runs.
          </p>
        </div>
        <button
          className="button primary"
          onClick={() => {
            setProposing(true);
            setSource(runs[0]?.id || "");
          }}
        >
          <Plus size={16} />
          Propose lesson
        </button>
      </div>
      <div className="callout compact">
        <BookOpen size={19} />
        <p>
          Proposed rules stay inactive. Editing an approved rule invalidates
          approval. Disabled rules cannot be loaded.
        </p>
      </div>
      <div className="lesson-layout">
        <section className="panel lesson-list">
          {lessons.map((l) => (
            <button
              className={l.id === selected ? "selected" : ""}
              key={l.id}
              onClick={() => setSelected(l.id)}
            >
              <div>
                <BookOpen size={19} />
                <b>{l.id}</b>
              </div>
              <Badge value={l.effective_status} />
              <small>Source: {l.source_run}</small>
            </button>
          ))}
          {!lessons.length && (
            <Empty title="No lessons yet">
              Propose a rule from retained development evidence.
            </Empty>
          )}
        </section>
        <section className="panel padded">
          {lesson ? (
            <>
              <div className="panel-heading no-padding">
                <h2>{lesson.id}</h2>
                <Badge value={lesson.effective_status} />
              </div>
              <p className="muted">Source: {lesson.source_run}</p>
              <p className="fine-print">Evidence: {lesson.evidence}</p>
              <label className="field">
                Editable Markdown
                <textarea
                  className="lesson-editor"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={12}
                />
              </label>
              <button
                className="button"
                disabled={busy || content === lesson.content}
                onClick={() => mutate("edit")}
              >
                Save changes
              </button>
              <hr />
              <label className="field">
                Approver / reviewer identity
                <input
                  placeholder="Your name or assistant identifier"
                  value={reviewer}
                  onChange={(e) => setReviewer(e.target.value)}
                />
              </label>
              <div className="inline-actions">
                <button
                  className="button primary"
                  disabled={
                    busy || !reviewer.trim() || content !== lesson.content
                  }
                  onClick={() => mutate("approve")}
                >
                  <Check size={16} />
                  Approve current version
                </button>
                <button
                  className="button"
                  disabled={busy || !reviewer.trim()}
                  onClick={() => mutate("disable")}
                >
                  Disable lesson
                </button>
              </div>
              <small className="hash">
                Approved SHA-256: {lesson.approved_sha256 || "Not approved"}
              </small>
              <details className="trace-message">
                <summary>
                  Approval & edit history ({lesson.history?.length || 0})
                </summary>
                {lesson.history?.length ? (
                  lesson.history.map((event: Data, index: number) => (
                    <div className="diagnosis-item" key={index}>
                      <Badge value={event.action} />
                      <p>
                        {new Date(
                          event.recorded_at_unix_ns / 1e6,
                        ).toLocaleString("en-US")}
                      </p>
                      <small>
                        {event.action === "edit"
                          ? "Content edited; approval must be checked again."
                          : "Reviewer: " +
                            (event.record?.reviewer ||
                              "Proposal — not approved")}
                      </small>
                      <details>
                        <summary>Audit record</summary>
                        <pre>{JSON.stringify(event, null, 2)}</pre>
                      </details>
                    </div>
                  ))
                ) : (
                  <p className="fine-print">
                    No transition history recorded for this older lesson.
                    Existing run snapshots remain available.
                  </p>
                )}
              </details>
            </>
          ) : (
            <Empty title="Select a lesson">
              Inspect its source, edit the rule, and manage approval.
            </Empty>
          )}
        </section>
      </div>
      {proposing && (
        <div className="modal-backdrop">
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="lesson-title"
          >
            <div className="modal-heading">
              <h2 id="lesson-title">Propose a development lesson</h2>
              <IconButton
                aria-label="Close lesson proposal"
                onClick={() => setProposing(false)}
              >
                <X size={20} />
              </IconButton>
            </div>
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                setBusy(true);
                try {
                  await api("/lessons", {
                    id,
                    source_run: source,
                    evidence: ev,
                    action,
                    applicability: applies,
                  });
                  await onChange();
                  setProposing(false);
                  setSelected(id);
                  onNotice(
                    "Lesson proposed. It remains inactive until approved.",
                  );
                } catch (err) {
                  setProposalError((err as Error).message);
                  onError((err as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
            >
              <div className="modal-body">
                {proposalError && (
                  <p role="alert" className="form-error">
                    {proposalError}
                  </p>
                )}
                <label className="field">
                  Lesson ID
                  <input
                    required
                    pattern="[a-z0-9][a-z0-9_-]*"
                    maxLength={80}
                    placeholder="inspect-generated-metrics"
                    value={id}
                    onChange={(e) => setId(e.target.value)}
                  />
                </label>
                <label className="field">
                  Source run
                  <select
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                  >
                    {runs
                      .filter((r) => !active(r.status))
                      .map((r) => (
                        <option key={r.id} value={r.id}>
                          {r.title} · {r.id}
                        </option>
                      ))}
                  </select>
                </label>
                <label className="field">
                  Retained evidence
                  <select value={ev} onChange={(e) => setEv(e.target.value)}>
                    {artifacts.map((a) => (
                      <option key={a}>{a}</option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  When does this apply?
                  <textarea
                    required
                    value={applies}
                    onChange={(e) => setApplies(e.target.value)}
                    placeholder="Describe the relevant project or failure conditions."
                  />
                </label>
                <label className="field">
                  Recommended action
                  <textarea
                    required
                    rows={4}
                    value={action}
                    onChange={(e) => setAction(e.target.value)}
                    placeholder="A concrete workflow instruction, without replacing the scientific computation."
                  />
                </label>
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="button"
                  onClick={() => setProposing(false)}
                >
                  Cancel
                </button>
                <button className="button primary" disabled={busy || !ev}>
                  Save proposal
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
