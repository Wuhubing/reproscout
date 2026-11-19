"""Project-owned evidence tools using Inspect's general ReAct loop."""

from __future__ import annotations

import json
import time
from pathlib import Path

from inspect_ai.agent import AgentPrompt, AgentState, AgentSubmit, react
from inspect_ai.model import GenerateConfig, get_model
from inspect_ai.tool import ContentImage, ContentText, Tool, ToolError, tool
from inspect_ai.util import sandbox

from .budget import Budget
from .evidence import validate_submission
from .network import transport_retry
from .request_count import count_request
from .tasks import digest, write_json

INSTRUCTIONS = """You are ReproScout, a scientific reproduction agent.
Execute the supplied author's code to answer the task questions. Read /code/README.md
and /REPRODUCING.md first. The controller has already provisioned the author's image:
run commands directly inside this container, not through nested Docker. Work in /code;
data are in /data and /results starts empty. Network access is disabled. Do not alter
experimental code, hardcode answers, or use remembered/published results.
If blocked, submit null values for unanswered questions, with evidence of the blocker
and an optional explanation field. Do not invent values to complete the report. If a required
code change is necessary, explain the blocker instead of silently patching it.
Keep every response in English. Tool outputs include controller-owned artifact IDs and
1-based line numbers. Submit each question's value with evidence from THIS execution.
For plots, use view_image on generated raster files or PDF pages; cite the returned
image artifact without line numbers. Use the submit_report tool with a JSON object keyed by question IDs, for example:
{"q1":{"value":12.3,"evidence":[{"artifact":"artifacts/step-002.stdout.txt",
"line_start":2,"line_end":2}]}}. The example number is not an answer.
An existing file reference does not prove correctness; cite actual computed output.
"""


def build_agent(run: Path, manifest: dict, config: dict, budget: Budget, lessons: str = ""):
    artifacts: dict = {}
    step = 0
    max_calls = config["max_model_calls"]
    constrained = config.get("controlled_execution", False)
    controller = None

    def retain(name: str, content: str, metadata: dict) -> str:
        relative = "artifacts/" + name
        path = run / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        artifacts[relative] = {"sha256": digest(content.encode()), **metadata}
        write_json(run / "artifact-index.json", artifacts)
        return relative

    @tool
    def shell() -> Tool:
        async def execute(command: str) -> str:
            """Run a shell command inside the isolated task container.

            Args:
                command: Bash command to execute in /code.
            """
            nonlocal step
            step += 1
            name = f"step-{step:03d}"
            started = time.monotonic()
            try:
                result = await sandbox().exec(
                    ["bash", "-o", "pipefail", "-c", command],
                    cwd="/code",
                    timeout=config["command_timeout_seconds"],
                    timeout_retry=False,
                )
            except TimeoutError:
                write_json(
                    run / f"{name}.json",
                    {
                        "command": command,
                        "status": "timeout",
                        "seconds": time.monotonic() - started,
                    },
                )
                raise ToolError("Command exceeded its execution timeout") from None
            out = retain(
                name + ".stdout.txt", result.stdout, {"kind": "command_stdout", "step": step}
            )
            err = retain(
                name + ".stderr.txt", result.stderr, {"kind": "command_stderr", "step": step}
            )
            write_json(
                run / f"{name}.json",
                {
                    "command": command,
                    "exit_code": result.returncode,
                    "seconds": time.monotonic() - started,
                    "stdout": out,
                    "stderr": err,
                },
            )

            def numbered(text: str) -> str:
                return "\n".join(f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1))[
                    :20000
                ]

            return (
                f"Exit code: {result.returncode}\n{out}\n{numbered(result.stdout)}"
                f"\n{err}\n{numbered(result.stderr)}"
            )

        return execute

    @tool
    def read_file() -> Tool:
        async def execute(path: str) -> str:
            """Read a task file and retain a controller-owned snapshot.

            Args:
                path: Absolute path inside /code, /data, /results, or /REPRODUCING.md.
            """
            nonlocal step
            from pathlib import PurePosixPath

            candidate = PurePosixPath(path)
            if ".." in candidate.parts or not (
                path.startswith(("/code/", "/data/", "/results/")) or path == "/REPRODUCING.md"
            ):
                raise ToolError("Path is outside the task file allowlist")
            result = await sandbox().exec(["readlink", "-f", path], timeout=10)
            real = result.stdout.strip()
            if result.returncode or not (
                real.startswith(("/code/", "/data/", "/results/")) or real == "/REPRODUCING.md"
            ):
                raise ToolError("Resolved path is outside the task file allowlist")
            size = await sandbox().exec(["stat", "-c", "%s", real], timeout=10)
            if size.returncode or int(size.stdout) > 1000000:
                raise ToolError("File unavailable or too large")
            text = await sandbox().read_file(real)
            step += 1
            artifact = retain(
                f"step-{step:03d}.file.txt", text, {"kind": "file_snapshot", "source": real}
            )
            return (
                artifact
                + "\n"
                + "\n".join(f"{i}: {line}" for i, line in enumerate(text.splitlines(), 1))[:20000]
            )

        return execute

    @tool
    def view_image() -> Tool:
        async def execute(path: str, page: int = 1) -> list[ContentText | ContentImage]:
            """View a generated image or a PDF page and save image evidence.

            Args:
                path: Absolute image or PDF path under /results or /code.
                page: One-based PDF page number; ignored for raster images.
            """
            import base64
            import io
            from pathlib import PurePosixPath

            import pymupdf
            from PIL import Image

            nonlocal step
            if ".." in PurePosixPath(path).parts or not path.startswith(("/results/", "/code/")):
                raise ToolError("Image path outside task scope")
            resolved = await sandbox().exec(["readlink", "-f", path], timeout=10)
            real = resolved.stdout.strip()
            if resolved.returncode or not real.startswith(("/results/", "/code/")):
                raise ToolError("Image resolves outside task scope")
            size = await sandbox().exec(["stat", "-c", "%s", real], timeout=10)
            if size.returncode or int(size.stdout) > 20_000_000:
                raise ToolError("Image unavailable or above 20 MB")
            data = await sandbox().read_file(real, text=False)
            try:
                if data.startswith(b"%PDF"):
                    with pymupdf.open(stream=data, filetype="pdf") as document:
                        if not 1 <= page <= len(document):
                            raise ToolError("PDF page out of range")
                        pix = document[page - 1].get_pixmap(matrix=pymupdf.Matrix(1, 1))
                        image = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                else:
                    image = Image.open(io.BytesIO(data)).convert("RGB")
                image.thumbnail((1024, 1024))
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
            except ToolError:
                raise
            except Exception:
                raise ToolError("Unable to decode image or PDF") from None
            step += 1
            artifact = f"artifacts/step-{step:03d}.png"
            (run / "artifacts").mkdir(exist_ok=True)
            encoded = buffer.getvalue()
            (run / artifact).write_bytes(encoded)
            artifacts[artifact] = {
                "kind": "image",
                "sha256": digest(encoded),
                "source": real,
                "source_sha256": digest(data),
                "page": page,
                "dimensions": list(image.size),
            }
            if controller is not None:
                artifacts[artifact].update(controller.lineage(real, digest(data)))
            write_json(run / "artifact-index.json", artifacts)
            return [
                ContentText(
                    text=f"Evidence artifact: {artifact}. Cite its artifact field without line numbers."
                ),
                ContentImage(image="data:image/png;base64," + base64.b64encode(encoded).decode()),
            ]

        return execute

    @tool
    def submit_report() -> Tool:
        async def execute(answers_json: str) -> str:
            """Submit answers with evidence references to recorded tool artifacts.

            Args:
                answers_json: JSON object keyed by question IDs, containing value and evidence.
            """
            try:
                answers = validate_submission(answers_json, manifest["questions"], artifacts, run)
            except (ValueError, TypeError, KeyError) as exc:
                raise ToolError(str(exc)) from None
            if constrained:
                from .controlled import validate_provenance, validate_types

                try:
                    validate_types(answers, config["answer_types"])
                    validate_provenance(answers, artifacts)
                except ValueError as exc:
                    controller.record(
                        operation="submit_report",
                        status="refused",
                        reason=str(exc),
                        answers=answers,
                    )
                    raise ToolError(str(exc)) from None
                controller.record(operation="submit_report", status="accepted")
            write_json(run / "submission.json", answers)
            return json.dumps(answers)

        return execute

    async def bounded_generate(state: AgentState, tools: list[Tool]) -> AgentState:
        """Generate one bounded text response through Inspect's provider interface.

        Args:
            state: Current agent conversation.
            tools: Available tools.
        """
        if config.get("stop_on_offline_blocker") or config.get("web_job_id"):
            from .blockers import before_generation

            before_generation(run)
        if len(budget.calls) >= max_calls:
            raise ValueError("Maximum model calls reached")
        generation_config = GenerateConfig(
            max_tokens=budget.max_output,
            max_retries=0,
            parallel_tool_calls=False,
            reasoning_effort=config["reasoning_effort"],
        )
        try:
            counts = await count_request(
                get_model(), state.messages, tools, generation_config, run / "network-events.jsonl"
            )
        except Exception as exc:
            budget.request_checks.append(
                {"status": "count_failed", "error_type": type(exc).__name__}
            )
            write_json(run / "budget.json", budget.__dict__)
            raise ValueError("Native request token counting failed; generation refused") from exc
        try:
            budget.reserve(counts["native_input_tokens"], counts)
        finally:
            write_json(run / "budget.json", budget.__dict__)
        output = await transport_retry(
            lambda: get_model().generate(state.messages, tools=tools, config=generation_config),
            kind="generation",
            audit_path=run / "network-events.jsonl",
            request_sha256=counts["request_sha256"],
        )
        if output.usage is None:
            raise ValueError("Provider returned no usage; reserved cost retained and run stopped")
        budget.settle(output.usage.model_dump(), output.model)
        write_json(run / "budget.json", budget.__dict__)
        state.output = output
        state.messages.append(output.message)
        return state

    selected_tools = [shell(), read_file(), view_image()]
    if constrained:
        from .controlled import ControlledExecution

        controller = ControlledExecution(
            run, manifest, artifacts, shell(), config.get("stop_on_offline_blocker", False)
        )

        @tool
        def inspect_file() -> Tool:
            async def execute(path: str, start_line: int = 1, line_count: int = 150) -> str:
                """Read a bounded text snapshot without executing any supplied code.

                Args:
                    path: Task file under /code, /data, /results or /REPRODUCING.md.
                    start_line: One-based first line.
                    line_count: Number of lines, at most 300.
                """
                nonlocal step
                try:
                    real = await controller.resolve(path)
                    if start_line < 1 or not 1 <= line_count <= 300:
                        raise ValueError("Invalid line range")
                    size = await sandbox().exec(["stat", "-c", "%s", real], timeout=10)
                    if size.returncode or int(size.stdout) > 10_000_000:
                        raise ValueError("Text unavailable or above 10 MB")
                    content = await sandbox().read_file(real)
                except (ValueError, UnicodeError) as exc:
                    raise ToolError(str(exc)) from None
                selected = "\n".join(
                    content.splitlines()[start_line - 1 : start_line - 1 + line_count]
                )[:20000]
                if not selected:
                    selected = "[No text in requested range]"
                step += 1
                artifact = retain(
                    f"step-{step:03d}.file.txt",
                    selected,
                    {
                        "kind": "file_snapshot",
                        "source": real,
                        "source_line_start": start_line,
                        **controller.lineage(real, digest(content.encode())),
                    },
                )
                return (
                    artifact
                    + "\n"
                    + "\n".join(f"{i}: {line}" for i, line in enumerate(selected.splitlines(), 1))
                )

            return execute

        @tool
        def inspect_output() -> Tool:
            async def execute(artifact: str, start_line: int = 1, line_count: int = 150) -> str:
                """Read more lines of an already captured text output; cite its original line numbers.

                Args:
                    artifact: Exact artifact ID from a previous tool.
                    start_line: One-based first line.
                    line_count: Number of lines, at most 300.
                """
                if artifact not in artifacts or artifacts[artifact].get("kind") == "image":
                    raise ToolError("Unknown text artifact")
                if start_line < 1 or not 1 <= line_count <= 300:
                    raise ToolError("Invalid line range")
                lines = (run / artifact).read_text().splitlines()
                return (
                    artifact
                    + "\n"
                    + "\n".join(
                        f"{i}: {line}"
                        for i, line in enumerate(
                            lines[start_line - 1 : start_line - 1 + line_count], start_line
                        )
                    )[:20000]
                )

            return execute

        selected_tools = controller.tools() + [inspect_file(), inspect_output(), view_image()]
        lessons += (
            "\nPublic answer type contracts (null allowed with blocker evidence):\n"
            + json.dumps(config["answer_types"])
        )

    return react(
        name="reproscout",
        prompt=AgentPrompt(
            instructions=INSTRUCTIONS + lessons, handoff_prompt=None, assistant_prompt=None
        ),
        model=bounded_generate,
        tools=selected_tools,
        submit=AgentSubmit(tool=submit_report(), keep_in_messages=True),
        retry_refusals=0,
        attempts=1,
    )
