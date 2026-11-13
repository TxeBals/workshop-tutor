"""(Tutor) Build the student repo: English only, no solutions, no tutor material.

    python scripts/export_student.py ../devopsday-workshop      # target folder (its .git is kept)
    python scripts/export_student.py ../devopsday-workshop --zip  # also writes forja-solutions.zip next to this repo

What it does:
- copies forja/, tests/, playground/, examples/, evals/, pyproject.toml, .env.example
- labs/LNN_*/README.en.md -> README.md (Spanish READMEs dropped)
- docs: student_workbook.md, setup_checklist.md, hardware.png
- scripts: tasks.py (without tutor commands) and catchup.py (reads forja-solutions.zip)
- README.md for students, Makefile and .gitignore
Everything in the target except .git is replaced.
"""
from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def IGNORE(folder, names):
    skip = {"__pycache__", ".pytest_cache", "out", ".catchup_backup"}
    if Path(folder).name == "playground":
        skip.add(".forja")  # local sessions/settings from rehearsals; examples/project/.forja IS copied
    return [n for n in names if n in skip or n.endswith(".pyc")]
COPY_DIRS = ["forja", "tests", "playground", "examples", "evals"]
COPY_FILES = ["pyproject.toml", ".env.example"]

GITIGNORE = """.venv/
__pycache__/
.pytest_cache/
.env
out/
.catchup_backup/
playground/.forja/
.forja/sessions/
forja-solutions.zip
solutions/
*.egg-info/
"""

MAKEFILE = """# Shortcuts for Linux/macOS. On Windows: python scripts/tasks.py <task>
.PHONY: setup test catchup evals reset
setup:   ; python scripts/tasks.py setup
test:    ; python scripts/tasks.py test $(LAB)
lab%:    ; python scripts/tasks.py test $*
catchup: ; python scripts/tasks.py catchup $(LAB)
evals:   ; python scripts/tasks.py evals $(ARGS)
reset:   ; python scripts/tasks.py reset
"""


def fix_links(text: str) -> str:
    text = re.sub(r"^🇪🇸 \[Español\]\([^)]*\)( · )?", "", text, flags=re.M)
    text = re.sub(r" ?· ?🇪🇸 \[Español\]\([^)]*\)", "", text)
    text = text.replace("README.en.md", "README.md")
    text = text.replace("git clone [repo] forja-workshop && cd forja-workshop",
                        "git clone https://github.com/TxeBals/devopsday-workshop && cd devopsday-workshop")
    return text


def student_readme() -> str:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from labs_content import LABS  # noqa: E402

    rows = "\n".join(f"| [L{l['id']}](labs/L{l['id']}_{l['slug']}/README.md) | {l['day']} · {l['time']} | {l['title'][1]} |" for l in LABS)
    return f"""# Forja · Build your own coding agent with local models

Hands-on workshop where you build **Forja**, a terminal coding agent —like Claude Code, Codex CLI or OpenCode— from scratch,
in Python, on **local open models** (Ollama, vLLM, LM Studio) or OpenRouter with open-weight models.
Anthropic and OpenAI models are blocked in code.

Each lab fills in one piece. The harness is **progressive**: the CLI works from lab 01 and gains capabilities as you complete labs.

## Where to start
1. [Setup checklist](docs/setup_checklist.md) — **before the day**.
2. [Student workbook](docs/student_workbook.md).
3. The labs, in order.

## Labs
| Lab | Day · time | Topic |
|---|---|---|
{rows}
| — | 2 · 16:00 | Final project (see the workbook) |

## Commands (Windows, macOS and Linux)
```bash
python scripts/tasks.py setup          # install and create .env
python scripts/tasks.py test 03        # lab 03 tests against your code
forja                                  # your agent, on the current directory
python scripts/tasks.py evals          # evals with your agent
python scripts/tasks.py catchup 05     # catch up: solves labs 01–04 (needs the tutor's forja-solutions.zip)
python scripts/tasks.py reset          # restore playground/ (git)
```

## Layout
```
devopsday-workshop/
├── docs/          setup_checklist.md · student_workbook.md · hardware.png
├── labs/          L00…L12, one README per lab
├── forja/         your code: functions with TODO NN.x
├── tests/         test_lNN_*.py (offline, FakeLLM: no GPU needed)
├── playground/    small invoices project with bugs for your agent
├── examples/      settings, hooks, skill, subagent, MCP server
├── evals/         tasks.yaml · hidden/ · run_evals.py
└── scripts/       tasks.py · catchup.py
```

## Notes
- Synthetic data and practice project.
- Forja is an independent implementation of the publicly documented architecture of coding agents.
- Tests need no model or GPU. Model tags change: check them before the workshop.
"""


def student_tasks() -> str:
    s = (ROOT / "scripts" / "tasks.py").read_text(encoding="utf-8")
    s = "\n".join(l for l in s.split("\n") if not re.search(r"tasks\.py (solutions|demo|starters)\b", l))
    s = re.sub(r'    if cmd == "(solutions|starters|demo)":\n(        .*\n)+?', "", s)
    return s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--zip", action="store_true", help="also write forja-solutions.zip next to this repo")
    a = ap.parse_args()
    dst = Path(a.target).resolve()
    dst.mkdir(parents=True, exist_ok=True)
    for item in dst.iterdir():
        if item.name == ".git":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()

    for d in COPY_DIRS:
        shutil.copytree(ROOT / d, dst / d, ignore=IGNORE)
    for f in COPY_FILES:
        shutil.copy2(ROOT / f, dst / f)

    for lab in sorted((ROOT / "labs").iterdir()):
        (dst / "labs" / lab.name).mkdir(parents=True)
        (dst / "labs" / lab.name / "README.md").write_text(fix_links((lab / "README.en.md").read_text(encoding="utf-8")), encoding="utf-8")

    (dst / "docs").mkdir()
    (dst / "docs" / "student_workbook.md").write_text(fix_links((ROOT / "docs/student/student_workbook.md").read_text(encoding="utf-8")).replace("../../labs/", "../labs/"), encoding="utf-8")
    (dst / "docs" / "setup_checklist.md").write_text(fix_links((ROOT / "docs/setup_checklist.md").read_text(encoding="utf-8")), encoding="utf-8")
    shutil.copy2(ROOT / "docs/hardware.png", dst / "docs/hardware.png")

    (dst / "scripts").mkdir()
    shutil.copy2(ROOT / "scripts/catchup.py", dst / "scripts/catchup.py")
    (dst / "scripts/tasks.py").write_text(student_tasks(), encoding="utf-8")
    (dst / "README.md").write_text(student_readme(), encoding="utf-8")
    (dst / "Makefile").write_text(MAKEFILE, encoding="utf-8")
    (dst / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    print(f"student repo -> {dst}")

    if a.zip:
        z = ROOT.parent / "forja-solutions.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted((ROOT / "solutions" / "forja").glob("*.py")):
                zf.write(f, f"forja/{f.name}")
        print(f"solutions zip -> {z}")


if __name__ == "__main__":
    main()
