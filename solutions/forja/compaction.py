"""LAB 07 — Context management: fitting a long session into a small window.

A typical local model works with 16–32k tokens. A coding agent fills them fast:
every read_file, every pytest output… Two levels, from cheapest to most expensive:

  1. Microcompaction (no LLM): blank OLD tool outputs. The model already used them;
     if it needs them, it can read the file again.
  2. Full compaction (1 LLM call): summarise the old turns and keep the recent ones.

Sacred invariant: never separate an assistant message with tool_calls from its tool messages.
Only cut right before a 'user' message.
"""
from __future__ import annotations

import json
from typing import Any

from .types import ChatModel

SUMMARY_PROMPT = """Summarise this coding-agent work session so it can be continued without the history.
Include, in this order and without inventing anything:
1. The user's goal and explicit requests.
2. Relevant files and what was changed in each (exact paths).
3. Commands run and their results (passing/failing tests, important errors).
4. Decisions taken and why.
5. Pending tasks and the next step.
300 words maximum."""

CLEARED = "[old tool result cleared]"


def estimate_tokens(messages: list[dict[str, Any]]) -> int:
    """~4 characters per token. Cheap and good enough to decide when to compact."""
    return sum(len(json.dumps(m, ensure_ascii=False)) for m in messages) // 4


def user_turn_starts(history: list[dict[str, Any]]) -> list[int]:
    return [i for i, m in enumerate(history) if m["role"] == "user"]


# ---- TODO 07.1 (starter): microcompaction -----------------------------------------
def microcompact(history: list[dict[str, Any]], keep_recent_turns: int = 2, min_chars: int = 500) -> int:
    """Blanks (in place) long tool outputs older than the last `keep_recent_turns` turns.
    Returns how many were blanked."""
    starts = user_turn_starts(history)
    if len(starts) <= keep_recent_turns:
        return 0
    limit = starts[-keep_recent_turns]
    n = 0
    for m in history[:limit]:
        if m["role"] == "tool" and m.get("content") != CLEARED and len(m.get("content") or "") >= min_chars:
            m["content"] = CLEARED
            n += 1
    return n


# ---- TODO 07.2 (starter): full compaction with a summary ------------------------------
def compact(history: list[dict[str, Any]], llm: ChatModel, keep_recent_turns: int = 2) -> tuple[list[dict[str, Any]], bool]:
    """Returns (new_history, compacted?). Summarises everything before the last turns."""
    starts = user_turn_starts(history)
    if len(starts) <= keep_recent_turns:
        return history, False
    cut = starts[-keep_recent_turns]
    old, recent = history[:cut], history[cut:]
    lines = []
    for m in old:
        if m["role"] == "tool":
            lines.append(f"[result of {m.get('name')}] {(m.get('content') or '')[:1500]}")
        else:
            calls = [f"{t['function']['name']}({t['function']['arguments'][:200]})" for t in m.get("tool_calls", [])]
            lines.append(f"{m['role']}: {m.get('content') or ''}" + (f" [tools: {'; '.join(calls)}]" if calls else ""))
    summary = llm.chat([{"role": "system", "content": SUMMARY_PROMPT}, {"role": "user", "content": "\n".join(lines)[-60_000:]}],
                       temperature=0).content or ""
    new = [{"role": "user", "content": f"[Summary of the previous session]\n{summary}"},
           {"role": "assistant", "content": "Understood. I'll continue from here."}, *recent]
    return new, True


def should_compact(system: str, history: list[dict[str, Any]], window: int, threshold: float = 0.8) -> bool:
    return estimate_tokens([{"role": "system", "content": system}, *history]) > window * threshold
