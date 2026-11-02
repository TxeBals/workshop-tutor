"""LAB 06 — Context engineering: what the model sees on each turn.

The system prompt is assembled in layers, every turn:
  1. Base prompt of the coding agent (how to work)
  2. Permission mode reminder
  3. Project instructions: AGENTS.md (an open convention shared by several tools),
     searched from the current directory upwards, plus the user's global one
  4. Skills catalogue (lab 10)
  5. Environment: directory, git branch and status, OS, date, model
And in the user message, `@path` mentions are expanded with the file's content.
"""
from __future__ import annotations

import platform
import re
import subprocess
from datetime import date
from pathlib import Path

from .fs_tools import Workspace

BASE_PROMPT = """You are Forja, a software engineering agent working in the user's terminal on their project.

How you work:
- Explore before changing: use glob and grep to locate code and read_file to read it. Don't assume contents.
- Read a file before editing it. For partial changes use edit_file (exact, unique text); use write_file only for new files or full rewrites.
- Follow the style and conventions of the existing code. Don't add dependencies unnecessarily.
- Verify your work: run the tests or the relevant command with bash and check the output.
- If a tool returns ERROR, read the message, fix and retry; don't repeat the same call.
- For multi-step tasks, keep a list with todo_write and update it as you progress.
- Be concise: explain in a few sentences what you did and what remains. Cite files as path:line.
- Never make up test or command results."""

MODE_REMINDERS = {
    "default": "DEFAULT mode: you can read freely; edits and commands will ask the user for approval.",
    "accept_edits": "ACCEPT_EDITS mode: you can read and edit files; shell commands ask for approval.",
    "plan": ("PLAN mode: READ-ONLY. Investigate the code and, when you have a concrete plan (files, changes, how to verify), "
             "present it with the exit_plan_mode tool. Don't try to edit or run commands."),
    "bypass": "BYPASS mode: all actions allowed except those denied by policy. Act carefully.",
}

INSTRUCTION_FILES = ("AGENTS.md", "FORJA.md")
MENTION_RE = re.compile(r"(?<![\w/])@([\w./\-]+)")


# ---- TODO 06.1 (starter): find project instructions ----------------------------------
def find_instruction_files(cwd: Path, home: Path | None = None, stop: Path | None = None) -> list[Path]:
    """The user's global file first (~/.forja/AGENTS.md), then from the HIGHEST root down to `cwd`,
    so that the closest (most specific) instructions come last and weigh more."""
    found: list[Path] = []
    if home:
        g = home / ".forja" / "AGENTS.md"
        if g.is_file():
            found.append(g)
    chain: list[Path] = []
    d = cwd.resolve()
    while True:
        for name in INSTRUCTION_FILES:
            if (d / name).is_file():
                chain.append(d / name)
        if (stop and d == stop.resolve()) or d.parent == d:
            break
        d = d.parent
    return found + list(reversed(chain))


def git_info(root: Path) -> str:
    def run(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=5).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return ""

    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    if not branch:
        return "Git repository: no"
    status = run("status", "--short").splitlines()
    shown = "\n".join(status[:20]) + (f"\n…({len(status) - 20} more)" if len(status) > 20 else "")
    return f"Git repository: yes · branch {branch}\nUncommitted changes:\n{shown or '(none)'}"


# ---- TODO 06.2 (starter): assemble the system prompt ---------------------------------
def build_system_prompt(ws: Workspace, mode: str, model: str, home: Path | None = None, skills_catalog: str = "",
                        extra: list[str] | None = None) -> str:
    layers = [BASE_PROMPT, MODE_REMINDERS.get(mode, "")]
    for f in find_instruction_files(ws.root, home=home):
        label = "User global instructions" if home and f.is_relative_to(home / ".forja") else f"Project instructions ({f.relative_to(ws.root) if f.is_relative_to(ws.root) else f})"
        layers.append(f"## {label}\n{f.read_text(encoding='utf-8').strip()}")
    if skills_catalog:
        layers.append(skills_catalog)
    layers += [e for e in (extra or []) if e]
    layers.append(f"## Environment\nWorking directory: {ws.root}\n{git_info(ws.root)}\n"
                  f"OS: {platform.system()} · Date: {date.today().isoformat()} · Model: {model}")
    return "\n\n".join(x for x in layers if x)


# ---- TODO 06.3 (starter): expand @file mentions -------------------------------------
def expand_mentions(text: str, ws: Workspace, max_chars: int = 20_000) -> str:
    """`Review @src/app.py` -> the original message + a block with the file's content.
    Mentions that are not workspace files are left as they are."""
    blocks = []
    for ref in dict.fromkeys(MENTION_RE.findall(text)):
        try:
            p = ws.resolve(ref.rstrip(".,;:"))
        except PermissionError:
            continue
        if not p.is_file():
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        if len(content) > max_chars:
            content = content[:max_chars] + "\n…[truncated]"
        ws.mark_read(p)
        blocks.append(f'<file path="{ws.rel(p)}">\n{content}\n</file>')
    return text if not blocks else text + "\n\n" + "\n\n".join(blocks)
