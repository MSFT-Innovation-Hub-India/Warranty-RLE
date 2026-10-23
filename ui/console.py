"""CLI adapter and durable local records for the Frontier Tuning console."""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".local" / "frontier-console"
WARRANTY_ENV = "598fd1b0-36f1-402f-ba36-aa00c8a67cc4"
TERMINAL = {"completed", "succeeded", "failed", "cancelled", "canceled", "deleted"}
LIST_LIMIT = 10000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def field(obj: dict, *names: str, default=None):
    for name in names:
        if name in obj and obj[name] is not None:
            return obj[name]
    return default


def identifier(value: str) -> str:
    return str(UUID(value))


def records(payload: object) -> list[dict]:
    if isinstance(payload, list) and all(isinstance(row, dict) for row in payload):
        return payload
    if isinstance(payload, dict):
        if any(payload.get(key) for key in ("nextLink", "@odata.nextLink", "continuationToken")):
            raise ValueError("The CLI returned another page. Cannot establish a complete job list.")
        for key in ("value", "items", "jobs", "executions", "skills"):
            if key in payload:
                return records(payload[key])
        if field(payload, "id", "Id", "jobId", "executionId"):
            return [payload]
    raise ValueError("Unexpected CLI collection shape; refusing to treat it as an empty list.")


def decode_json(text: str) -> object:
    text = text.lstrip("\ufeff").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as original:
        # Some CLI commands print a progress message before their JSON document.
        for match in re.finditer(r"(?m)^\s*[\[{]", text):
            try:
                value, end = json.JSONDecoder().raw_decode(text[match.start():].lstrip())
            except json.JSONDecodeError:
                continue
            candidate = text[match.start():].lstrip()
            if not candidate[end:].strip():
                return value
            raise ValueError("CLI output contains multiple documents or trailing non-JSON data.") from original
        raise ValueError("CLI output was not a JSON document. Inspect stdout and stderr.") from original


@dataclass(frozen=True)
class Reply:
    command: list[str]
    stdout: str
    stderr: str
    payload: object


class CommandError(RuntimeError):
    def __init__(self, message: str, command: list[str], stdout: str = "", stderr: str = ""):
        super().__init__(message)
        self.command = command
        self.stdout = stdout
        self.stderr = stderr


def invoke(command: list[str], timeout: int = 120, *, parse: bool = True) -> Reply:
    try:
        done = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout, shell=False,
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"},
        )
    except subprocess.TimeoutExpired as exc:
        def text(value: str | bytes | None) -> str:
            return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""
        raise CommandError(
            "CLI timed out. Any submitted service action may still be running; do not resubmit.",
            command, text(exc.stdout), text(exc.stderr),
        ) from exc
    except OSError as exc:
        raise CommandError(f"Could not start command: {exc}", command) from exc
    if done.returncode:
        raise CommandError(
            f"Command exited with code {done.returncode}. No automatic retry was made.",
            command, done.stdout, done.stderr,
        )
    try:
        payload = decode_json(done.stdout) if parse else None
    except ValueError as exc:
        raise CommandError(str(exc), command, done.stdout, done.stderr) from exc
    return Reply(command, done.stdout, done.stderr, payload)


class CLI:
    def __init__(self, executable: str | None = None):
        self.executable = executable or shutil.which("frontier-tuning")
        if not self.executable:
            raise ValueError("frontier-tuning is not on PATH. Install/sign in using the operations runbook.")

    def command(self, args: list[str], env: str | None = None) -> list[str]:
        return [self.executable, *(["-e", identifier(env)] if env else []), *args, "-o", "json-legacy"]

    def read(self, args: list[str], env: str | None = None) -> Reply:
        return invoke(self.command(args, env))

    def context(self, env: str) -> dict:
        with ThreadPoolExecutor(max_workers=3) as pool:
            environment_read = pool.submit(self.read, ["environments", "get", env], env)
            skills_read = pool.submit(self.read, ["skills", "list"], env)
            models_read = pool.submit(self.read, ["models", "list"], env)
            environment = environment_read.result().payload
            skills = records(skills_read.result().payload)
            models = models_read.result().payload
        if not isinstance(models, dict) or not isinstance(models.get("trainingModels"), list):
            raise ValueError("Model catalog has an unexpected shape.")
        details = {}
        for skill in skills:
            sid = field(skill, "id", "Id")
            if sid and field(skill, "isEnabled", "IsEnabled", default=False):
                details[sid] = self.read(["skills", "get", sid, "--show-rubrics"], env).payload
        return {"environment": environment, "skills": skills, "details": details, "models": models, "readUtc": utc_now()}

    def assert_idle(self, env: str) -> list[dict]:
        evidence = []
        for kind in ("executions", "evaluate", "tune"):
            args = [kind, "list"]
            if kind != "executions":
                args += ["--limit", str(LIST_LIMIT)]
            reply = self.read(args, env)
            rows = records(reply.payload)
            if len(rows) >= LIST_LIMIT:
                raise ValueError(f"{kind} listing may be truncated; cannot confirm the environment is idle.")
            active = [
                row for row in rows
                if str(field(row, "status", "Status", default="unknown")).lower() not in TERMINAL
            ]
            if active:
                ids = [str(field(row, "id", "Id", "jobId", default="?")) for row in active]
                raise ValueError(f"{kind} has active/unknown-status entries: {', '.join(ids)}. Nothing submitted/reset.")
            evidence.append({"command": reply.command, "payload": reply.payload, "checkedUtc": utc_now()})
        return evidence


def run_args(query: str, strategy: str, model: str = "", best_of_n: int | None = None,
             early_stop: float | None = None) -> list[str]:
    if not query.strip():
        raise ValueError("Enter a query.")
    if strategy not in {"Simple", "TreeSearch", "BestOfN"}:
        raise ValueError("Unsupported strategy.")
    if best_of_n is not None and (
        strategy != "BestOfN" or isinstance(best_of_n, bool) or not isinstance(best_of_n, int) or best_of_n < 1
    ):
        raise ValueError("BestOfN requires a positive integer candidate count.")
    if early_stop is not None and (
        strategy != "TreeSearch" or not math.isfinite(early_stop) or not 0 <= early_stop <= 1
    ):
        raise ValueError("TreeSearch cutoff must be finite and between 0 and 1.")
    args = ["executions", "run", "-q", query, "--strategy", strategy]
    if model:
        args += ["--model", model]
    if best_of_n is not None:
        args += ["--best-of-n", str(best_of_n)]
    if early_stop is not None:
        args += ["--early-stop-score", str(early_stop)]
    return args


class Store:
    def __init__(self, root: Path = DATA):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, record: dict) -> None:
        target = self.root / f"{identifier(record['localId'])}.json"
        temporary = target.with_suffix(f".{uuid4()}.tmp")
        try:
            temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)

    def all(self) -> list[dict]:
        return sorted(
            (json.loads(path.read_text(encoding="utf-8")) for path in self.root.glob("*.json")),
            key=lambda record: record["createdUtc"], reverse=True,
        )

    def load(self, local_id: str) -> dict:
        return json.loads((self.root / f"{identifier(local_id)}.json").read_text(encoding="utf-8"))

    @contextmanager
    def lock(self) -> Generator[None]:
        path = self.root / "operation.lock"
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ValueError(
                "Another submission/reset holds the local operation lock. If the app crashed, "
                "reconcile service activity before manually removing .local\\frontier-console\\operation.lock."
            ) from exc
        try:
            with os.fdopen(fd, "w") as stream:
                stream.write(f"pid={os.getpid()} utc={utc_now()}")
            yield
        finally:
            path.unlink()

    def assert_reconciled(self) -> None:
        pending = [
            row["localId"] for row in self.all()
            if (
                row.get("kind") == "execution"
                and row.get("state", "unknown").lower() not in TERMINAL | {"reconciled"}
            ) or (
                row.get("kind") == "database" and row.get("resetAttempted")
                and row.get("state") not in {"reset verified", "reconciled"}
            )
        ]
        if pending:
            raise ValueError(
                "Refresh/reconcile saved unfinished submissions before submitting or resetting: " + ", ".join(pending)
            )


def new_record(kind: str, env: str) -> dict:
    return {"localId": str(uuid4()), "kind": kind, "env": identifier(env), "createdUtc": utc_now()}


def execution_id(payload: dict) -> str:
    value = field(payload, "executionId", "id", "Id")
    if not value:
        raise ValueError("Submission did not return an execution ID. Reconcile via executions list; do not retry.")
    return identifier(value)


def sql(script: str) -> Reply:
    if script not in {"db-baseline.sql", "db-actions-snapshot.sql", "db-reset-actions.sql"}:
        raise ValueError("SQL script is not allowed.")
    executable = shutil.which("powershell.exe")
    if not executable:
        raise ValueError("Database controls require Windows PowerShell and Azure CLI sign-in.")
    return invoke(
        [executable, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(ROOT / "scripts" / "sql-run.ps1"), "-File", str(ROOT / "scripts" / script)],
        timeout=600, parse=False,
    )


def baseline_counts(output: str) -> tuple[int, int, int, int]:
    if not all(name in output for name in ("drafts", "evidence_requests", "escalations", "claims_not_seeded")):
        raise ValueError("Database baseline output is missing the expected columns.")
    matches = re.findall(r"(?m)^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", output)
    if len(matches) != 1:
        raise ValueError("Could not unambiguously read the four database baseline counts.")
    a, b, c, d = matches[0]
    return int(a), int(b), int(c), int(d)


def assert_warranty_env(env: str) -> None:
    if identifier(env) != WARRANTY_ENV:
        raise ValueError("Database controls are bound to the Contoso warranty environment, not the selected environment.")


def submit(cli: CLI, store: Store, env: str, args: list[str], context: dict) -> dict:
    with store.lock():
        store.assert_reconciled()
        checks = cli.assert_idle(env)
        assert_warranty_env(env)
        baseline = sql("db-baseline.sql")
        if baseline_counts(baseline.stdout) != (0, 0, 0, 0):
            raise ValueError("Database is not clean. Snapshot/reset after confirming all jobs have ended.")
        record = new_record("execution", env)
        record.update(
            state="submitting", command=cli.command(args, env), query=args[args.index("-q") + 1],
            contextBefore=context, idleChecks=checks, baseline=baseline.stdout,
        )
        # Persist the attempt before the write: a crash or ambiguous response must never cause an automatic retry.
        store.save(record)
        try:
            reply = invoke(record["command"], timeout=180)
            if not isinstance(reply.payload, dict):
                raise ValueError("Submission response was not an execution object.")
            record.update(result=reply.payload, stdout=reply.stdout, stderr=reply.stderr)
            record.update(
                executionId=execution_id(reply.payload),
                state=field(reply.payload, "status", "Status", default="Pending"),
            )
        except (CommandError, ValueError) as exc:
            record.update(state="unknown", error=str(exc))
            if isinstance(exc, CommandError):
                record.update(stdout=exc.stdout, stderr=exc.stderr)
            store.save(record)
            raise
        store.save(record)
        return record


def refresh(cli: CLI, store: Store, record: dict, execution: str | None = None) -> dict:
    eid = identifier(execution or record["executionId"])
    reply = cli.read(["executions", "get", eid], record["env"])
    if not isinstance(reply.payload, dict):
        raise ValueError("Execution response was not an object.")
    if execution_id(reply.payload) != eid:
        raise ValueError("Returned execution ID does not match the requested execution.")
    record.update(
        executionId=eid, result=reply.payload, stdout=reply.stdout, stderr=reply.stderr,
        state=field(reply.payload, "status", "Status", default="unknown"), refreshedUtc=utc_now(),
    )
    store.save(record)
    return record


def database_action(cli: CLI, store: Store, env: str, reset: bool = False) -> dict:
    assert_warranty_env(env)
    with store.lock():
        store.assert_reconciled()
        checks = cli.assert_idle(env)
        record = new_record("database", env)
        record.update(state="snapshotting", idleChecks=checks)
        store.save(record)
        try:
            snapshot = sql("db-actions-snapshot.sql")
            record.update(snapshot=snapshot.stdout, snapshotCommand=snapshot.command, state="snapshotted")
            store.save(record)
            if reset:
                # Snapshot must be on disk, and service activity rechecked, before deleting any rows.
                record["resetIdleChecks"] = cli.assert_idle(env)
                record["state"] = "resetting"
                record["resetAttempted"] = True
                store.save(record)
                reply = sql("db-reset-actions.sql")
                record.update(reset=reply.stdout, resetCommand=reply.command)
                baseline = sql("db-baseline.sql")
                record["baseline"] = baseline.stdout
                if baseline_counts(baseline.stdout) != (0, 0, 0, 0):
                    raise ValueError("Reset did not restore the clean database baseline.")
                record["state"] = "reset verified"
        except (CommandError, ValueError) as exc:
            record.update(state="error - inspect before retry", error=str(exc))
            if isinstance(exc, CommandError):
                record.update(stdout=exc.stdout, stderr=exc.stderr)
            store.save(record)
            raise
        store.save(record)
        return record


def response_text(payload: dict) -> str:
    value = field(payload, "response", "Response", default="")
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n\n".join(
            str(field(part, "Content", "content", "text", default="")) for part in value if isinstance(part, dict)
        )
    return ""


def rubric_rows(payload: dict) -> list[dict]:
    skill_results = field(payload, "skillResults", default=[])
    source = field(payload, "rubricResults", "RubricResults", default=[])
    if not source:
        source = [rubric for skill in skill_results for rubric in skill.get("rubricResults", [])]
    result = []
    for rubric in source:
        snapshot = field(rubric, "snapshotData", default=rubric)
        score = field(rubric, "score", "Score")
        # CLI 1.x uses zero plus an empty reason to represent a skipped rubric in flattened results.
        skipped = score is None or (
            "displayName" in rubric and score == 0 and not field(rubric, "scoreReason", "reasoning")
        )
        result.append({
            "Rubric": field(snapshot, "displayName", "rubricName", "RubricName", "name", default="Unnamed"),
            "Importance": field(snapshot, "importance", "Importance", default=""),
            "Score": None if skipped else score,
            "Grading": "Unscored / not applicable" if skipped else "Scored",
        })
    return result


def score_ground_truth(store: Store, record: dict) -> str:
    if record.get("state", "").lower() != "completed":
        raise ValueError("Ground-truth scoring requires a completed execution.")
    payload = record["result"]
    query = record.get("query") or field(payload, "query", "userQuery", "UserQuery", default="")
    if not re.search(r"\bC-\d{4}-\d{5}\b", query + " " + response_text(payload)):
        raise ValueError("No Contoso claim ID found; ground-truth scoring does not apply to this response.")
    folder = store.root / identifier(record["localId"])
    folder.mkdir(exist_ok=True)
    source = folder / "execution.json"
    source.write_text(json.dumps({"prompt": query, "execution": payload}), encoding="utf-8")
    reply = invoke(
        [sys.executable, str(ROOT / "scripts" / "score_ground_truth.py"), str(source), "--out", str(folder)],
        parse=False,
    )
    report = (folder / "ground-truth-check.md").read_text(encoding="utf-8")
    record.update(groundTruth=report, groundTruthLog=reply.stderr)
    store.save(record)
    return report
