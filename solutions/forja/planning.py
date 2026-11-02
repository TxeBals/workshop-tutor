"""LAB 08 — Plan before acting: task list and plan mode.

* todo_write: the agent keeps a task list visible to the user. It forces the model
  to decompose the work, and lets the user see progress. With small local models
  it greatly improves persistence on long tasks.
* Plan mode: read-only. The agent investigates and proposes a plan with exit_plan_mode; if
  the user approves it, the harness switches to default mode (or accept_edits) and it is executed.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

from .tools import Tool, tool

Status = Literal["pending", "in_progress", "completed"]
ICON = {"pending": "☐", "in_progress": "▶", "completed": "☑"}


class TodoItem(BaseModel):
    content: str
    status: Status = "pending"


@dataclass
class TodoStore:
    items: list[TodoItem] = field(default_factory=list)

    def render(self) -> str:
        if not self.items:
            return "(empty list)"
        return "\n".join(f"{ICON[i.status]} {i.content}" for i in self.items)


# ---- TODO 08.1 (starter): the todo_write tool with validation --------------------------
def make_todo_tool(store: TodoStore) -> Tool:
    @tool(risk="read")
    def todo_write(todos: list[TodoItem]) -> str:
        """Creates or updates your task list (replaces the whole list). Use it for tasks with 3+ steps:
        at the start, split the work; mark a task in_progress before starting it and completed when done.
        Only ONE task can be in_progress at a time.

        Args:
            todos: Full list of tasks with content and status (pending, in_progress, completed).
        """
        items = [t if isinstance(t, TodoItem) else TodoItem.model_validate(t) for t in todos]
        if sum(t.status == "in_progress" for t in items) > 1:
            raise ValueError("only one task can be in_progress at a time")
        if any(not t.content.strip() for t in items):
            raise ValueError("every task needs content")
        store.items = items
        done = sum(t.status == "completed" for t in items)
        return f"List updated ({done}/{len(items)} completed):\n{store.render()}"

    return todo_write


# ---- TODO 08.2 (starter): leave plan mode with user approval --------------------------
def make_exit_plan_tool(approve: Callable[[str], bool], on_approved: Callable[[], None]) -> Tool:
    @tool(risk="read")
    def exit_plan_mode(plan: str) -> str:
        """In plan mode, presents your implementation plan to the user (markdown: files to touch, changes,
        how to verify) and asks for approval to start executing it.

        Args:
            plan: The plan, concrete and brief.
        """
        if not plan.strip():
            raise ValueError("the plan is empty")
        if approve(plan):
            on_approved()
            return "The user APPROVED the plan. You are no longer in plan mode: implement it step by step and verify."
        return "The user REJECTED the plan. You are still in plan mode: ask what to change or propose an alternative."

    return exit_plan_mode
