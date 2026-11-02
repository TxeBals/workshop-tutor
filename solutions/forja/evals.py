"""LAB 12 — Evals: measure your agent (and your models) with real tasks.

Each task = a prompt + an objective check, run on a clean COPY of the practice
project. Checks:
  * command          a command that must finish with exit 0 (usually tests)
  * hidden           HIDDEN tests copied in after the agent has worked
                     (so it can't "cheat" by reading or editing them)
  * answer_contains  the answer must contain certain facts (questions about the code)
  * forbid_changes   the task must not modify any file
The agent runs headless in bypass mode INSIDE the copy: the sandbox is the temp folder.
"""
from __future__ import annotations

import hashlib
import shutil
import statistics
import subprocess
import tempfile
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .config import Settings
from .harness import Forja
from .types import ChatModel


@dataclass
class EvalTask:
    id: str
    prompt: str
    check: dict[str, Any]


@dataclass
class TaskResult:
    id: str
    passed: bool
    reason: str
    steps: int
    tool_calls: int
    tokens: int
    seconds: float
    stop_reason: str
    answer: str = ""


def load_tasks(path: Path) -> list[EvalTask]:
    return [EvalTask(t["id"], t["prompt"], t.get("check", {})) for t in yaml.safe_load(path.read_text(encoding="utf-8"))]


def snapshot(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in {".forja", "__pycache__", ".pytest_cache"} for part in p.parts):
            out[str(p.relative_to(root))] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# ---- TODO 12.1 (starter): grade a task ---------------------------------------------------
def grade(task: EvalTask, workdir: Path, answer: str, before: dict[str, str], repo_root: Path) -> tuple[bool, str]:
    chk = task.check
    if chk.get("forbid_changes") and snapshot(workdir) != before:
        return False, "modified files in a read-only task"
    missing = [s for s in chk.get("answer_contains", []) if norm(str(s)) not in norm(answer)]
    if missing:
        return False, f"the answer is missing: {missing}"
    for src, dst in (chk.get("hidden") or {}).items():
        target = workdir / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(repo_root / src, target)
    if chk.get("command"):
        try:
            p = subprocess.run(chk["command"], shell=True, cwd=workdir, capture_output=True, text=True, timeout=chk.get("timeout", 120))
        except subprocess.TimeoutExpired:
            return False, "timeout in the check"
        if p.returncode != 0:
            tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
            return False, "check failed: " + " | ".join(tail)
    return True, "ok"


def run_task(task: EvalTask, llm: ChatModel, playground: Path, repo_root: Path, max_steps: int = 30) -> TaskResult:
    with tempfile.TemporaryDirectory(prefix=f"forja-eval-{task.id}-") as tmp:
        work = Path(tmp) / "project"
        shutil.copytree(playground, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".forja"))
        before = snapshot(work)
        app = Forja(llm, work, mode="bypass", settings=Settings(max_steps=max_steps), home=Path(tmp) / "home",
                    persist=False, use_mcp=False)
        t0 = time.time()
        try:
            r = app.turn(task.prompt)
            answer, steps, calls, stop = r.answer, r.steps, r.tool_calls, r.stop_reason
        except Exception as e:  # noqa: BLE001
            answer, steps, calls, stop = f"EXCEPTION {type(e).__name__}: {e}", 0, 0, "error"
        secs = round(time.time() - t0, 1)
        passed, reason = grade(task, work, answer, before, repo_root)
        return TaskResult(task.id, passed, reason, steps, calls, sum(app.usage.values()), secs, stop, answer[:500])


# ---- TODO 12.2 (starter): summarise results -----------------------------------------------
def summarize(results: list[TaskResult], model: str) -> dict[str, Any]:
    by_task: dict[str, list[TaskResult]] = {}
    for r in results:
        by_task.setdefault(r.id, []).append(r)
    n = len(results) or 1
    return {
        "model": model,
        "runs": len(results),
        "pass_rate": round(sum(r.passed for r in results) / n, 3),
        "per_task": {k: round(sum(r.passed for r in v) / len(v), 2) for k, v in by_task.items()},
        "avg_steps": round(statistics.mean(r.steps for r in results), 1) if results else 0,
        "avg_seconds": round(statistics.mean(r.seconds for r in results), 1) if results else 0,
        "total_tokens": sum(r.tokens for r in results),
        "results": [asdict(r) for r in results],
    }
