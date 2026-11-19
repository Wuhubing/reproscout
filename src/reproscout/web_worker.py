"""One isolated controller process per browser-launched task."""

import os
import sys
from pathlib import Path

from .cli import execute
from .review import read
from .web import atomic


def main():
    root, key = Path(sys.argv[1]), sys.argv[2]
    folder = root / ".reproscout/jobs" / key

    def update(**values):
        job = read(folder, "job.json")
        job.update(values)
        atomic(folder / "job.json", job)

    def created(run):
        update(run_id=run.name, status="running")
        if (folder / "cancel.requested").exists():
            (run / "cancel.requested").touch()

    try:
        update(worker_pid=os.getpid())
        if (folder / "cancel.requested").exists():
            update(status="cancelled")
            return
        job = read(folder, "job.json")
        run = execute(
            root,
            "run",
            None,
            folder / "manifest.json",
            config_path=folder / "config.json",
            lesson_ids=job["lesson_ids"],
            on_run_created=created,
        )
        summary = read(run, "summary.json", {})
        status = (
            "cancelled"
            if (folder / "cancel.requested").exists()
            else "failed"
            if summary.get("infrastructure_failure")
            else "finished"
        )
        update(status=status, run_id=run.name)
    except Exception as exc:
        update(
            status="failed",
            error=f"{type(exc).__name__}: controller could not finish; see retained local worker log",
        )
        raise


if __name__ == "__main__":
    main()
