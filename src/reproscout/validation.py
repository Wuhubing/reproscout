"""Offline checks executed by a deterministic Inspect solver, never an LLM."""

from pathlib import Path

from inspect_ai.solver import solver
from inspect_ai.util import sandbox

from .tasks import write_json


@solver
def environment_checks(output: Path, manual: bool = False):
    async def solve(state, generate):
        checks = {}
        commands = {
            "runtime": "python --version; python -c 'import sklearn,networkx,numpy; print(sklearn.__version__,networkx.__version__,numpy.__version__)'",
            "no_old_results": 'test -z "$(ls -A /results)"',
            "no_socket": "test ! -e /var/run/docker.sock",
            "no_credentials": 'test -z "${OPENAI_API_KEY:-}"',
            "no_private_answers": "test ! -e /private/pilot_answers.json && test ! -e /capsule/core_train.json",
            "network_blocked": "python -c \"import socket; s=socket.socket(); s.settimeout(2); r=s.connect_ex(('1.1.1.1',443)); print(r); assert r != 0\"",
        }
        commands.update(
            {
                "no_host_home": "test ! -d /Users && test ! -d /host_mnt",
                "no_host_private_mount": "test ! -e /private && test ! -e /host",
                "capabilities_dropped": "grep -q 'CapEff:[[:space:]]*0000000000000000' /proc/1/status",
                "alternate_egress_blocked": "python -c \"import socket; s=socket.socket(); s.settimeout(2); assert s.connect_ex(('8.8.8.8',53)) != 0\"",
            }
        )
        for name, command in commands.items():
            result = await sandbox().exec(["bash", "-c", command], timeout=30)
            checks[name] = {
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        try:
            await sandbox().exec(
                ["bash", "-c", "sleep 5; touch /tmp/timeout-escaped"],
                timeout=1,
                timeout_retry=False,
            )
            checks["timeout_raised"] = {"passed": False}
        except TimeoutError:
            checks["timeout_raised"] = {"passed": True}
        await sandbox().exec(["sleep", "6"], timeout=10)
        # Use the shell builtin: the old image's standalone /usr/bin/test can
        # crash under amd64 emulation (139), which is not evidence of a live child.
        remaining = await sandbox().exec(
            ["bash", "-c", "test ! -e /tmp/timeout-escaped"], timeout=10
        )
        checks["timed_out_process_terminated"] = {
            "passed": remaining.returncode == 0,
            "exit_code": remaining.returncode,
            "stdout": remaining.stdout,
            "stderr": remaining.stderr,
            "probe": "bash builtin test after delayed marker command",
        }
        if manual:
            result = await sandbox().exec(
                ["bash", "run.sh"], cwd="/code", timeout=180, timeout_retry=False
            )
            (output / "manual.stdout.txt").write_text(result.stdout, encoding="utf-8")
            (output / "manual.stderr.txt").write_text(result.stderr, encoding="utf-8")
            checks["manual_author_run"] = {
                "passed": result.returncode == 0,
                "exit_code": result.returncode,
            }
        write_json(output / "environment-checks.json", checks)
        state.completed = True
        return state

    return solve


def source_audit(output: Path, manifest: dict):
    """Hash original inputs before sandbox cleanup, without exporting reference answers."""

    async def cleanup(state):
        expected = {"/" + item["path"]: item["sha256"] for item in manifest["input_inventory"]}
        result = await sandbox().exec(["sha256sum", *expected], timeout=30)
        actual = {}
        for line in result.stdout.splitlines():
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                actual[parts[1]] = parts[0]
        changed = [path for path, sha in expected.items() if actual.get(path) != sha]
        write_json(
            output / "source-audit.json",
            {
                "checked_files": len(expected),
                "unchanged": not changed and result.returncode == 0,
                "changed_or_missing": changed,
                "stderr": result.stderr,
            },
        )

    return cleanup
