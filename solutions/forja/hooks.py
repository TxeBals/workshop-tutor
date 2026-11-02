"""LAB 10a — Hooks: deterministic policy around a probabilistic model.

AGENTS.md *asks* ("run the tests"); a hook *guarantees*. Hooks are shell commands
configured in .forja/settings.json that the harness runs at fixed points:

    PreToolUse        before running a tool                 exit 2 => BLOCKED (stderr goes to the model)
    PostToolUse       after running it                      exit 2 => stderr is appended to the result (feedback)
    UserPromptSubmit  when a message is sent                exit 2 => blocked; stdout is added as context
    Stop              when the agent thinks it is done      exit 2 => keeps working with stderr as guidance

Each hook receives a JSON with the event on stdin. Exit 0 = all good; exit 2 = block;
any other code = hook error (reported, doesn't block). It's the convention commercial
coding agents already use: once you know it, it works in all of them.

    "hooks": {
      "PreToolUse":  [{"matcher": "bash", "command": "python .forja/hooks/no_secrets.py"}],
      "PostToolUse": [{"matcher": "edit_file|write_file", "command": "ruff check --quiet ."}],
      "Stop":        [{"command": "pytest -q -x"}]
    }
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop")


@dataclass
class HookOutcome:
    block: bool = False
    message: str = ""  # stderr (block / feedback)
    context: str = ""  # useful stdout (UserPromptSubmit)
    errors: list[str] = field(default_factory=list)


@dataclass
class HookRunner:
    config: dict[str, list[dict[str, Any]]]
    cwd: Path
    timeout: int = 60

    # ---- TODO 10.1 (starter): select hooks by event and matcher -------------------------
    def matching(self, event: str, tool_name: str | None = None) -> list[dict[str, Any]]:
        out = []
        for h in self.config.get(event, []):
            matcher = h.get("matcher")
            if matcher and tool_name is not None and not re.fullmatch(matcher, tool_name):
                continue
            if matcher and tool_name is None:
                continue
            out.append(h)
        return out

    # ---- TODO 10.2 (starter): run and map exit codes -------------------------------------
    def run(self, event: str, payload: dict[str, Any], tool_name: str | None = None) -> HookOutcome:
        outcome = HookOutcome()
        data = json.dumps({"hook_event_name": event, "cwd": str(self.cwd), **payload}, ensure_ascii=False, default=str)
        for h in self.matching(event, tool_name):
            try:
                p = subprocess.run(h["command"], shell=True, cwd=self.cwd, input=data, capture_output=True, text=True,
                                   timeout=h.get("timeout", self.timeout))
            except subprocess.TimeoutExpired:
                outcome.errors.append(f"hook '{h['command']}' timed out")
                continue
            if p.returncode == 2:
                outcome.block = True
                outcome.message += (p.stderr or p.stdout or "blocked by hook").strip() + "\n"
            elif p.returncode == 0:
                if p.stdout.strip():
                    outcome.context += p.stdout.strip() + "\n"
            else:
                outcome.errors.append(f"hook '{h['command']}' exited with code {p.returncode}: {p.stderr.strip()[:300]}")
        outcome.message, outcome.context = outcome.message.strip(), outcome.context.strip()
        return outcome
