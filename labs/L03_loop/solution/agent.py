"""LAB 03 — The agent loop.

    while not finished:
        response = model(history, tools)          # streaming
        if it requests no tools -> end of turn
        run tools (reads in parallel, the rest in order) -> results into history

The loop knows nothing about permissions, hooks or the UI: it receives an `execute` function
(the harness gate) and an `events` object to notify the UI. That way we reuse it as-is
for subagents (lab 09) and evals (lab 12).
"""
from __future__ import annotations

import threading
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Literal

from .tools import ToolRegistry, ToolResult
from .types import ChatModel, ChatResponse, Done, TextDelta, ToolCall

StopReason = Literal["final", "max_steps", "loop", "interrupted"]


class Events:
    """Callbacks for the UI (no-ops by default)."""

    def on_text(self, delta: str) -> None: ...
    def on_assistant(self, resp: ChatResponse) -> None: ...
    def on_tool_start(self, call: ToolCall) -> None: ...
    def on_tool_end(self, call: ToolCall, result: ToolResult) -> None: ...


@dataclass
class AgentResult:
    answer: str
    stop_reason: StopReason
    steps: int
    usage: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0


@dataclass
class Agent:
    llm: ChatModel
    tools: ToolRegistry
    execute: Callable[[ToolCall], ToolResult] | None = None  # default: tools.execute (no gate)
    events: Events = field(default_factory=Events)
    max_steps: int = 40
    max_repeats: int = 3
    parallel_reads: bool = True
    cancel: threading.Event = field(default_factory=threading.Event)

    def _is_read(self, call: ToolCall) -> bool:
        t = self.tools.tools.get(call.name)
        return bool(t and t.risk == "read")

    # ---- TODO 03.1 (starter): run a batch of tool calls ---------------------------
    def _run_calls(self, calls: list[ToolCall]) -> list[ToolResult]:
        """Consecutive read-only calls run in parallel; the rest, in order.
        Results are returned in the SAME order as the calls."""
        execute = self.execute or self.tools.execute
        results: list[ToolResult | None] = [None] * len(calls)

        def run(i: int) -> None:
            self.events.on_tool_start(calls[i])
            results[i] = execute(calls[i])
            self.events.on_tool_end(calls[i], results[i])

        i = 0
        while i < len(calls):
            if self.parallel_reads and self._is_read(calls[i]):
                j = i
                while j < len(calls) and self._is_read(calls[j]):
                    j += 1
                if j - i > 1:
                    with ThreadPoolExecutor(max_workers=min(8, j - i)) as ex:
                        list(ex.map(run, range(i, j)))
                else:
                    run(i)
                i = j
            else:
                run(i)
                i += 1
        return [r for r in results if r is not None]

    # ---- TODO 03.2 (starter): the loop --------------------------------------------
    def run(self, messages: list[dict[str, Any]]) -> AgentResult:
        """`messages` includes system + history + the new user message.
        It is MODIFIED in place: when done it contains everything that happened in the turn."""
        usage: Counter[str] = Counter()
        seen: Counter[tuple[str, str]] = Counter()
        n_calls = 0
        for step in range(1, self.max_steps + 1):
            if self.cancel.is_set():
                return AgentResult("(interrupted by the user)", "interrupted", step - 1, dict(usage), n_calls)
            resp = None
            for ev in self.llm.stream(messages, tools=self.tools.schemas() or None):
                if isinstance(ev, TextDelta):
                    self.events.on_text(ev.text)
                elif isinstance(ev, Done):
                    resp = ev.response
            assert resp is not None, "the model did not return Done"
            usage.update(resp.usage)
            messages.append(resp.to_message())
            self.events.on_assistant(resp)
            if not resp.tool_calls:
                return AgentResult(resp.content or "", "final", step, dict(usage), n_calls)
            for c in resp.tool_calls:
                seen[(c.name, c.arguments)] += 1
                if seen[(c.name, c.arguments)] > self.max_repeats:
                    # Close the pending tool_calls so the history is not left broken.
                    for cc in resp.tool_calls:
                        messages.append(ToolResult(cc.id, cc.name, False, "Not executed: loop detected.").to_message())
                    return AgentResult(f"I stopped: I repeated {c.name} with the same arguments without making progress.", "loop", step, dict(usage), n_calls)
            results = self._run_calls(resp.tool_calls)
            n_calls += len(results)
            messages.extend(r.to_message() for r in results)
        return AgentResult("I stopped: I reached the maximum number of steps.", "max_steps", self.max_steps, dict(usage), n_calls)
