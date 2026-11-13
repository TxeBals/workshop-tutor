"""LAB 04b — Permissions: adjustable autonomy with rules.

Modes (the same concepts commercial coding agents use):
  default      -> reads free; edits and bash ask
  accept_edits -> reads and edits free; bash asks
  plan         -> READ-only; editing or executing is denied (lab 08)
  bypass       -> everything allowed except deny rules (for sandbox/CI, never on your laptop)

Rules:  "tool_name"  or  "tool_name(pattern)"  — the pattern (fnmatch) is matched against the
call's "subject": the command for bash, the path for file tools.
  allow: ["bash(pytest*)", "bash(git status*)", "edit_file(src/*)"]
  deny:  ["bash(sudo *)", "read_file(.env*)"]
Evaluation order: deny > plan mode > allow > risk/mode > ask.
"""
from __future__ import annotations

import fnmatch
import re
import shlex
from typing import Any, Literal

from .tools import Tool

Mode = Literal["default", "accept_edits", "plan", "bypass"]
Decision = Literal["allow", "ask", "deny"]
MODES: tuple[Mode, ...] = ("default", "accept_edits", "plan", "bypass")
RULE_RE = re.compile(r"^([\w.\-*?]+)(?:\((.*)\))?$")


def parse_rule(rule: str) -> tuple[str, str | None]:
    m = RULE_RE.match(rule.strip())
    if not m:
        raise ValueError(f"invalid rule: {rule!r}")
    return m.group(1), m.group(2)


# ---- TODO 04.3 (starter): does a rule match a call? --------------------------------
def rule_matches(rule: str, tool: Tool, args: dict[str, Any]) -> bool:
    name, pattern = parse_rule(rule)
    if not fnmatch.fnmatchcase(tool.name, name):
        return False
    if pattern is None:
        return True
    subject = tool.subject(args)
    if tool.name == "bash":
        # Each command in a chain (&&, ;, |) must satisfy the rule for allow rules:
        # `decide` checks that. Here we compare the whole text.
        subject = " ".join(subject.split())
    return fnmatch.fnmatchcase(subject, pattern)


def split_commands(command: str) -> list[str]:
    """`pytest -q && rm -rf /` is TWO commands: an allow rule for pytest must not let the second one through."""
    parts = re.split(r"\s*(?:&&|\|\||;|\|)\s*", command.strip())
    return [p for p in parts if p]


# ---- TODO 04.4 (starter): the decision ---------------------------------------------
def decide(tool: Tool, args: dict[str, Any], mode: Mode, allow: list[str], deny: list[str]) -> tuple[Decision, str]:
    for r in deny:
        if rule_matches(r, tool, args):
            return "deny", f"deny rule {r}"
    if tool.name == "bash":  # deny also per subcommand
        for sub in split_commands(args.get("command", "")):
            for r in deny:
                if rule_matches(r, tool, {"command": sub}):
                    return "deny", f"deny rule {r}"
    if mode == "plan" and tool.risk != "read":
        return "deny", "plan mode: read-only"
    if tool.name == "bash":
        subs = split_commands(args.get("command", ""))
        if subs and all(any(rule_matches(r, tool, {"command": s}) for r in allow) for s in subs):
            return "allow", "allow rule"
    elif any(rule_matches(r, tool, args) for r in allow):
        return "allow", "allow rule"
    if tool.risk == "read" or mode == "bypass":
        return "allow", f"risk {tool.risk} / mode {mode}"
    if mode == "accept_edits" and tool.risk == "edit":
        return "allow", "accept_edits mode"
    return "ask", "requires approval"


# ---- TODO 04.5 (starter): suggest a rule for "always approve" --------------------------
def suggest_rule(tool: Tool, args: dict[str, Any]) -> str:
    """When the answer is 'always', we save a sensible rule, not the literal command:
    bash `pytest -q tests/x.py` -> `bash(pytest*)`; edit_file -> `edit_file`."""
    if tool.name == "bash":
        try:
            words = shlex.split(args.get("command", ""))
        except ValueError:
            words = []
        if not words:
            return f"bash({args.get('command', '')})"
        # Tools with subcommands: `git status` yes, `git push` is something else.
        if words[0] in ("python", "python3", "py") and len(words) > 2 and words[1] == "-m":
            return f"bash({words[0]} -m {words[2]}*)"  # `python -m pytest`, not any python
        if words[0] in ("git", "npm", "uv", "pip", "docker", "cargo", "go", "dotnet") and len(words) > 1:
            return f"bash({words[0]} {words[1]}*)"
        return f"bash({words[0]}*)"
    return tool.name
