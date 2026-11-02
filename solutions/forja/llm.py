"""LAB 01 — Streaming LLM client (Ollama, vLLM, LM Studio, OpenRouter).

A coding agent feels "alive" because text arrives token by token. But when
streaming, tool calls also arrive in pieces: first the id and the name, then
the JSON arguments in fragments, sometimes from several calls interleaved by index.
Assembling them correctly is the first serious piece of the harness.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx
import openai
from openai import OpenAI

from .config import Backend, check_model_allowed
from .types import ChatResponse, Done, StreamEvent, TextDelta, ToolCall

RETRYABLE = (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError, openai.InternalServerError)
TEXT_TOOLCALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)


# ---- TODO 01.1 (starter): assemble tool calls that arrive in pieces ------------
@dataclass
class ToolCallAccumulator:
    """Receives each chunk's `delta.tool_calls` and rebuilds the complete calls.

    Each fragment carries `index` (which call), and optionally `id`, `function.name`
    and a piece of `function.arguments` that must be CONCATENATED.
    """

    _parts: dict[int, dict[str, str]] = field(default_factory=dict)

    def add(self, deltas: list[Any] | None) -> None:
        for d in deltas or []:
            slot = self._parts.setdefault(d.index, {"id": "", "name": "", "arguments": ""})
            if d.id:
                slot["id"] = d.id
            fn = d.function
            if fn is not None:
                if fn.name:
                    slot["name"] += fn.name
                if fn.arguments:
                    slot["arguments"] += fn.arguments

    def finish(self) -> list[ToolCall]:
        out = []
        for i in sorted(self._parts):
            p = self._parts[i]
            if not p["name"]:
                continue
            out.append(ToolCall(p["id"] or f"call_{uuid.uuid4().hex[:8]}", p["name"], p["arguments"] or "{}"))
        return out


# ---- TODO 01.2 (starter): filter <think>…</think> while streaming ------------------
@dataclass
class ThinkFilter:
    """Reasoning models (qwen3, deepseek-r1) emit <think>…</think>. When streaming,
    the tags can be split across chunks ("<thi" + "nk>"): a buffer is needed."""

    in_think: bool = False
    buf: str = ""

    def feed(self, text: str) -> str:
        self.buf += text
        out = []
        while self.buf:
            if self.in_think:
                end = self.buf.find("</think>")
                if end == -1:
                    keep = len("</think>") - 1  # a closing tag might be starting
                    self.buf = self.buf[-keep:] if len(self.buf) > keep else self.buf
                    return "".join(out)
                self.buf = self.buf[end + len("</think>"):].lstrip("\n")
                self.in_think = False
            else:
                start = self.buf.find("<think>")
                if start == -1:
                    # is the end of the buffer the start of "<think>"? Hold it back.
                    for k in range(min(len("<think>") - 1, len(self.buf)), 0, -1):
                        if "<think>".startswith(self.buf[-k:]):
                            out.append(self.buf[:-k])
                            self.buf = self.buf[-k:]
                            return "".join(out)
                    out.append(self.buf)
                    self.buf = ""
                else:
                    out.append(self.buf[:start])
                    self.buf = self.buf[start + len("<think>"):]
                    self.in_think = True
        return "".join(out)

    def flush(self) -> str:
        rest, self.buf = ("" if self.in_think else self.buf), ""
        return rest


def rescue_text_tool_calls(text: str) -> tuple[str, list[ToolCall]]:
    """Some local models write the call as text: <tool_call>{…}</tool_call>."""
    calls = []
    for raw in TEXT_TOOLCALL_RE.findall(text or ""):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get("name"):
            args = obj.get("arguments", {})
            calls.append(ToolCall(f"txt_{uuid.uuid4().hex[:8]}", obj["name"], args if isinstance(args, str) else json.dumps(args)))
    return TEXT_TOOLCALL_RE.sub("", text or "").strip(), calls


class LLMClient:
    def __init__(self, backend: Backend, *, timeout: float = 300.0, max_retries: int = 3, temperature: float = 0.2,
                 max_tokens: int = 8192, http_client: httpx.Client | None = None):
        check_model_allowed(backend.model)
        self.backend = backend
        self.model = backend.model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self._client = OpenAI(base_url=backend.base_url, api_key=backend.api_key or "x", timeout=timeout, max_retries=0,
                              default_headers=backend.extra_headers or None, http_client=http_client)

    def _params(self, messages: list[dict], tools: list[dict] | None, **kw: Any) -> dict[str, Any]:
        p: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": kw.pop("temperature", self.temperature),
                             "max_tokens": kw.pop("max_tokens", self.max_tokens), "stream": True,
                             "stream_options": {"include_usage": True}}
        if tools:
            p["tools"] = tools
            p["tool_choice"] = "auto"
        if self.backend.extra_body:
            p["extra_body"] = self.backend.extra_body
        p.update(kw)
        return p

    # ---- TODO 01.3 (starter): streaming with retries and final assembly ---------
    def stream(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> Iterator[StreamEvent]:
        params = self._params(messages, tools, **kw)
        delay = 1.0
        for attempt in range(self.max_retries + 1):
            try:
                chunks = self._client.chat.completions.create(**params)
                break
            except RETRYABLE:
                if attempt == self.max_retries:
                    raise
                time.sleep(delay)
                delay *= 2
        acc, think = ToolCallAccumulator(), ThinkFilter()
        text, usage, finish, model = [], {}, None, self.model
        for ch in chunks:
            if ch.usage:
                usage = {"prompt_tokens": ch.usage.prompt_tokens or 0, "completion_tokens": ch.usage.completion_tokens or 0}
            if ch.model:
                model = ch.model
            if not ch.choices:
                continue
            c = ch.choices[0]
            finish = c.finish_reason or finish
            visible = think.feed(c.delta.content or "") if c.delta.content else ""
            if visible:
                text.append(visible)
                yield TextDelta(visible)
            acc.add(c.delta.tool_calls)
        tail = think.flush()
        if tail:
            text.append(tail)
            yield TextDelta(tail)
        content, calls = "".join(text), acc.finish()
        if not calls:
            content, calls = rescue_text_tool_calls(content)
        yield Done(ChatResponse(content or None, calls, usage, model, "tool_calls" if calls else finish))

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> ChatResponse:
        for ev in self.stream(messages, tools, **kw):
            if isinstance(ev, Done):
                return ev.response
        raise RuntimeError("stream without a Done event")
