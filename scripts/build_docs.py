"""Generates each lab's README and the student workbooks (ES/EN) from labs_content.py.

    python scripts/build_docs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from labs_content import CAPSTONE, GLOSSARY, LABS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
T = {
    "es": dict(goal="Objetivo", concepts="Conceptos", todo="Lo que implementas", file="Fichero", what="Qué", run="Ejecuta",
               check="Checkpoint", chal="Retos", test="Tests", behind="¿Te has quedado atrás?", day="Día", other="🇬🇧 [English](README.en.md)",
               nav_prev="← anterior", nav_next="siguiente →", none="Este lab no tiene TODOs."),
    "en": dict(goal="Goal", concepts="Concepts", todo="What you implement", file="File", what="What", run="Run",
               check="Checkpoint", chal="Challenges", test="Tests", behind="Fallen behind?", day="Day", other="🇪🇸 [Español](README.md)",
               nav_prev="← previous", nav_next="next →", none="This lab has no TODOs."),
}


def i(lang: str) -> int:
    return 0 if lang == "es" else 1


def lab_dir(lab: dict) -> str:
    return f"L{lab['id']}_{lab['slug']}"


def lab_md(lab: dict, lang: str, level: int = 1, nav: bool = True) -> str:
    t, k = T[lang], i(lang)
    h = "#" * level
    out = [f"{h} Lab {lab['id']} · {lab['title'][k]}", ""]
    if nav and level == 1:
        out += [f"{t['other']} · {t['day']} {lab['day']} · {lab['time']}", ""]
    else:
        out += [f"*{t['day']} {lab['day']} · {lab['time']}*", ""]
    out += [f"**{t['goal']}:** {lab['goal'][k]}", "", f"{h}# {t['concepts']}", *[f"- {c}" for c in lab["concepts"][k]], ""]
    out += [f"{h}# {t['todo']}"]
    if lab["todos"]:
        out += [f"| TODO | {t['file']} | {t['what']} |", "|---|---|---|"]
        out += [f"| {tid} | `forja/{f}` | {es if lang == 'es' else en} |" for tid, f, es, en in lab["todos"]]
    else:
        out.append(t["none"])
    out += ["", f"{h}# {t['run']}", "```bash", lab["steps"][k] or lab["steps"][0], "```", "", f"{h}# {t['check']}", lab["checkpoint"][k], "",
            f"{h}# {t['chal']}", *[f"{n}. {c}" for n, c in enumerate(lab["challenges"][k], 1)], ""]
    if lab["test"]:
        out += [f"**{t['test']}:** `tests/{lab['test']}` · **{t['behind']}** `python scripts/tasks.py catchup {int(lab['id']) + 1:02d}`"
                if int(lab["id"]) < 12 else f"**{t['test']}:** `tests/{lab['test']}` · **{t['behind']}** `python scripts/tasks.py catchup end`", ""]
    return "\n".join(out)


def workbook(lang: str) -> str:
    k = i(lang)
    if lang == "es":
        head = """# Cuaderno del alumno · Forja: construye tu propio agente de código

> Workshop de 2 días. Al terminar tendrás **tu propio agente de código de terminal** —como los comerciales— funcionando con modelos abiertos en tu máquina, y entenderás cada pieza porque la habrás escrito tú.

## Cómo usar este cuaderno
- Cada lab: **objetivo → conceptos → lo que implementas → ejecuta → checkpoint → retos**.
- El código a completar está en `forja/` (busca `TODO NN.x`). Los tests de cada lab están en `tests/test_lNN_*.py`: `python scripts/tasks.py test NN`.
- Cuando los tests de un lab pasan, la capacidad se activa sola en tu CLI (`forja`). Los labs pendientes aparecen como avisos.
- ¿Te has quedado atrás? `python scripts/tasks.py catchup NN` copia la solución de los labs anteriores (con copia de seguridad de lo tuyo).
- Proyecto de prácticas: `playground/` (una mini librería de facturas con bugs a propósito). Para dejarlo como al principio: `python scripts/tasks.py reset`.

## Mapa
| Día | Lab | Tema | Lo que gana tu agente |
|---|---|---|---|
"""
    else:
        head = """# Student workbook · Forja: build your own coding agent

> A 2-day workshop. By the end you'll have **your own terminal coding agent** —like the commercial ones— running on open models on your machine, and you'll understand every piece because you wrote it.


## How to use this workbook
- Each lab: **goal → concepts → what you implement → run → checkpoint → challenges**.
- The code to complete is in `forja/` (look for `TODO NN.x`). Each lab's tests are in `tests/test_lNN_*.py`: `python scripts/tasks.py test NN`.
- When a lab's tests pass, the capability lights up in your CLI (`forja`). Pending labs appear as notes.
- Fallen behind? `python scripts/tasks.py catchup NN` copies the solutions of earlier labs (backing up yours).
- Practice project: `playground/` (a mini invoicing library with deliberate bugs). To reset it: `python scripts/tasks.py reset`.

## Map
| Day | Lab | Topic | What your agent gains |
|---|---|---|---|
"""
    gains = {"00": ("—", "—"), "01": ("chat en streaming", "streaming chat"), "02": ("leer, buscar y editar", "read, search and edit"),
             "03": ("actuar en bucle", "act in a loop"), "04": ("ejecutar comandos con permisos", "run commands with permissions"),
             "05": ("interfaz completa", "full interface"), "06": ("conoce tu proyecto", "knows your project"),
             "07": ("sesiones largas", "long sessions"), "08": ("planifica", "plans"), "09": ("delega", "delegates"),
             "10": ("hooks, skills, MCP", "hooks, skills, MCP"), "11": ("reanudar y deshacer", "resume and undo"), "12": ("se mide", "is measured")}
    rows = "\n".join(f"| {l['day']} | {l['id']} | {l['title'][k]} | {gains[l['id']][k]} |" for l in LABS)
    body = "\n\n---\n\n".join(lab_md(l, lang, level=2, nav=False) for l in LABS)
    gl_title = "## Glosario" if lang == "es" else "## Glossary"
    gl = "\n".join(f"- **{g[k]}** — {g[2 + k]}" for g in GLOSSARY)
    return f"{head}{rows}\n\n---\n\n{body}\n\n---\n\n{CAPSTONE[lang]}\n\n---\n\n{gl_title}\n{gl}\n"


def main() -> None:
    for n, lab in enumerate(LABS):
        d = ROOT / "labs" / lab_dir(lab)
        d.mkdir(parents=True, exist_ok=True)
        for lang, name in (("es", "README.md"), ("en", "README.en.md")):
            md = lab_md(lab, lang)
            prev = f"[{T[lang]['nav_prev']}](../{lab_dir(LABS[n - 1])}/{name})" if n else ""
            nxt = f"[{T[lang]['nav_next']}](../{lab_dir(LABS[n + 1])}/{name})" if n + 1 < len(LABS) else ""
            (d / name).write_text(md + f"\n---\n{prev}{' · ' if prev and nxt else ''}{nxt}\n", encoding="utf-8")
    (ROOT / "docs" / "alumno").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "student").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "alumno" / "cuaderno_alumno.md").write_text(workbook("es"), encoding="utf-8")
    (ROOT / "docs" / "student" / "student_workbook.md").write_text(workbook("en"), encoding="utf-8")
    print(f"{len(LABS)} labs + workbooks generated")


if __name__ == "__main__":
    main()
