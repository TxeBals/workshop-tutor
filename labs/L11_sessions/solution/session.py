"""LAB 11 — Sessions and checkpoints: resume work and undo what the agent did.

* Append-only JSONL transcript in .forja/sessions/<id>.jsonl: one message per line.
  Used to resume (`forja --resume <id>`), to audit and to debug.
* Checkpoints: before a tool modifies a file, we save its original content
  (or the fact that it didn't exist). `/undo` restores the files touched in the last turn.
  It doesn't depend on git: it also works in folders without a repository.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Transcript:
    folder: Path
    session_id: str = field(default_factory=lambda: time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4])

    @property
    def path(self) -> Path:
        return self.folder / f"{self.session_id}.jsonl"

    # ---- TODO 11.1 (starter): append-only ---------------------------------------
    def append(self, *messages: dict[str, Any]) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            for m in messages:
                f.write(json.dumps({"ts": round(time.time(), 3), "message": m}, ensure_ascii=False) + "\n")

    def mark_compaction(self, history: list[dict[str, Any]]) -> None:
        """After compaction the "live" history is no longer the sum of the lines: we save a marker with the new state."""
        self.folder.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": round(time.time(), 3), "compacted": history}, ensure_ascii=False) + "\n")

    # ---- TODO 11.2 (starter): rebuild the history -------------------------------------
    @staticmethod
    def load(folder: Path, session_id: str) -> list[dict[str, Any]]:
        history: list[dict[str, Any]] = []
        p = folder / f"{session_id}.jsonl"
        if not p.is_file():
            raise FileNotFoundError(f"session {session_id} does not exist")
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if "compacted" in rec:
                history = list(rec["compacted"])
            else:
                history.append(rec["message"])
        return history

    @staticmethod
    def list_sessions(folder: Path) -> list[tuple[str, str]]:
        """[(id, first user message)] from newest to oldest."""
        out = []
        for p in sorted(folder.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
            first = ""
            for line in p.read_text(encoding="utf-8").splitlines():
                m = json.loads(line).get("message", {})
                if m.get("role") == "user":
                    first = (m.get("content") or "")[:80]
                    break
            out.append((p.stem, first))
        return out


@dataclass
class Checkpoints:
    """Stack of turns; each turn stores {path: original_content | None (did not exist)}."""

    stack: list[dict[Path, bytes | None]] = field(default_factory=list)

    def begin_turn(self) -> None:
        self.stack.append({})

    # ---- TODO 11.3 (starter): save the original the FIRST time it is touched -------------
    def before_write(self, path: Path) -> None:
        if not self.stack:
            self.begin_turn()
        turn = self.stack[-1]
        if path not in turn:
            turn[path] = path.read_bytes() if path.exists() else None

    # ---- TODO 11.4 (starter): undo the last turn with changes ---------------------------
    def undo(self) -> list[Path]:
        while self.stack and not self.stack[-1]:
            self.stack.pop()
        if not self.stack:
            return []
        turn = self.stack.pop()
        for path, original in turn.items():
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(original)
        return sorted(turn)
