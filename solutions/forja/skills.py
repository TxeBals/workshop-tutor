"""LAB 10b — Skills: on-demand knowledge (progressive disclosure).

Putting all the team's guides in the system prompt spends context on every turn.
A skill is a folder with SKILL.md (frontmatter name + description + body). Only the
CATALOGUE goes in the prompt (one line per skill); the body is loaded with the `skill` tool
when the model decides it needs it. Same format other tools use: skills are portable.

    .forja/skills/conventional-commits/SKILL.md
    ---
    name: conventional-commits
    description: How to write commit messages in this repo. Use it before running git commit.
    ---
    Format: <type>(<scope>): <imperative summary>…
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .tools import Tool, tool

FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


@dataclass
class Skill:
    name: str
    description: str
    path: Path


# ---- TODO 10.3 (starter): discover skills -------------------------------------------
def discover_skills(*folders: Path) -> dict[str, Skill]:
    """Looks for <folder>/<skill>/SKILL.md. If two folders define the same skill, the last one wins (project > user)."""
    out: dict[str, Skill] = {}
    for folder in folders:
        if not folder.is_dir():
            continue
        for f in sorted(folder.glob("*/SKILL.md")):
            m = FRONTMATTER.match(f.read_text(encoding="utf-8"))
            meta = yaml.safe_load(m.group(1)) if m else None
            if meta and meta.get("name") and meta.get("description"):
                out[meta["name"]] = Skill(meta["name"], " ".join(str(meta["description"]).split()), f)
    return out


def catalog(skills: dict[str, Skill]) -> str:
    if not skills:
        return ""
    lines = "\n".join(f"- {s.name}: {s.description}" for s in skills.values())
    return f"## Available skills (load them with the skill tool when they apply)\n{lines}"


# ---- TODO 10.4 (starter): the tool that loads a skill ---------------------------------
def make_skill_tool(skills: dict[str, Skill]) -> Tool:
    @tool(risk="read")
    def skill(name: str) -> str:
        """Loads the full instructions of a skill from the catalogue.

        Args:
            name: Name of the skill.
        """
        s = skills.get(name)
        if s is None:
            raise ValueError(f"unknown skill: {name}. Available: {', '.join(skills) or 'none'}")
        m = FRONTMATTER.match(s.path.read_text(encoding="utf-8"))
        body = m.group(2).strip() if m else s.path.read_text(encoding="utf-8")
        return f"# Skill: {s.name}\n(folder: {s.path.parent})\n\n{body}"

    return skill
