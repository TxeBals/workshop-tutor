# Lab 12 · Evals: medir tu agente

🇬🇧 [English](README.en.md) · Día 2 · 14:55–16:00

**Objetivo:** Comparar modelos y cambios del harness con tareas reales y comprobaciones objetivas.

## Conceptos
- **Sin medir, todo es opinión.** ¿Es mejor `qwen3-coder:30b` que `qwen3:8b`? ¿Tu nuevo prompt ayuda? Se mide.
- **Tarea = prompt + comprobación objetiva** sobre una COPIA limpia del proyecto: tests (`command`), tests OCULTOS que se copian después (`hidden`, para que no haga trampa), contenido de la respuesta (`answer_contains`) y no modificar nada (`forbid_changes`).
- **Headless + bypass dentro de la copia:** el sandbox es la carpeta temporal.
- **Varias repeticiones:** los modelos no son deterministas. Mira pass rate, pasos, tiempo y tokens.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: aplicar las comprobaciones |
| 12.2 | `forja/evals.py` | summarize: pass rate, por tarea, pasos, tiempo, tokens |

## Antes de empezar
- Abre `forja/evals.py` (tus TODOs: `grade` y `summarize`) y `evals/tasks.yaml` (las tareas). Ya escritas para ti: `load_tasks`, `snapshot(root)` (dict `relative path -> sha1`, ignorando `.forja`, `.git`, `__pycache__`, `.pytest_cache`), `norm(s)` (minúsculas + quitar acentos) y `run_task`, que copia `playground/` a un directorio temporal, ejecuta UN turno headless en modo `bypass` y luego llama a tu `grade(task, work, answer, before, repo_root)`.
- El runner es `evals/run_evals.py` (vía `python scripts/tasks.py evals ...`): flags `--model`, `--backend`, `--repeat N`, `--only <id>`, `--max-steps`, `--config <carpeta .forja>` (usa tus settings, hooks, skills y subagentes en cada tarea), `--mcp` y `--label <sufijo>` para el nombre del informe. Imprime una línea `PASS`/`FAIL` por ejecución, llama a tu `summarize` y escribe `out/evals_<model>.json` (`/` y `:` en el nombre del modelo se convierten en `_`).
- Stdlib: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, timeout=...)` y `subprocess.TimeoutExpired`; `shutil.copy(src, dst)`; `statistics.mean`; `dataclasses.asdict`. Campos de `TaskResult`: `id, passed, reason, steps, tool_calls, tokens, seconds, stop_reason, answer`.
- El dict `check` de una tarea puede contener: `command` (salida 0 = pass, `timeout` opcional, 120 s por defecto), `hidden` (`{repo-relative source: workdir-relative destination}`, copiado DESPUÉS de que el agente termine), `answer_contains` (lista de strings), `forbid_changes` (bool).
- Las evals usan TODO tu agente (labs 01-11). `test_run_task_pass_and_fail` maneja `read_file`, `edit_file` y `bash` a través del harness, así que esos labs deben pasar.

## Paso a paso
12.1 primero (`test_grade_answer_and_forbid_changes`, `test_hidden_tests_copied_after`, luego `test_run_task_pass_and_fail`), porque `run_task` y el runner dependen de ello. 12.2 es aritmética independiente (`test_summarize`). Después ejecuta evals reales: empieza con `--only vat_question` (rápida, solo lectura).

### TODO 12.1 · `forja/evals.py` · `grade(task, workdir, answer, before, repo_root) -> tuple[bool, str]`

**Qué debe hacer:** Aplica las comprobaciones en ESTE orden y vuelve en el primer fallo: (1) `forbid_changes` y `snapshot(workdir) != before` → `(False, <reason containing 'modified'>)`; (2) `answer_contains`: cada string, comparado con `norm()` en ambos lados, debe estar en la respuesta, si no `(False, <reason listing the missing ones>)`; (3) copia cada fichero `hidden` de `repo_root / src` a `workdir / dst` (crea las carpetas padre); (4) si hay `command`: ejecútalo en `workdir` con `shell=True`; timeout → `(False, ...)`; salida distinta de cero → `(False, <reason containing 'failed'> + the last 3 lines of stdout+stderr)`. Todo bien → exactamente `(True, "ok")` (el test compara la tupla).

**Pasos:**
1. Lee `chk = task.check`.
2. Si `chk.get("forbid_changes")` y la instantánea actual difiere de `before`, falla con un motivo 'modified files…'.
3. Recoge los strings de `answer_contains` cuyo `norm(str(s))` no esté en `norm(answer)`; si hay alguno, falla y lístalos.
4. Para cada `(src, dst)` en `chk.get("hidden") or {}`: crea `(workdir / dst).parent` y `shutil.copy(repo_root / src, workdir / dst)`.
5. Si hay un `command`, ejecútalo en `workdir` con `capture_output=True, text=True, timeout=chk.get("timeout", 120)`; gestiona `TimeoutExpired`.
6. Si la salida no es cero, une en el motivo las últimas 3 líneas no vacías (tras trim) de `stdout + stderr` (p. ej. `"check failed: " + " | ".join(tail)`).
7. Devuelve `(True, "ok")`.

**Cuidado con:**
- Copiar los ficheros `hidden` ANTES de la comprobación de `forbid_changes`: tu propia copia cuenta como cambio. El orden importa.
- No usar `norm()`: `"VAT"` debe casar con `"the vat"` en la respuesta del test (sin distinguir mayúsculas; también se quitan los acentos).
- Copiar los tests ocultos solo cuando el comando pasa: `test_hidden_tests_copied_after` comprueba que el fichero existe aunque la comprobación falle.
- Olvidar `cwd=workdir`: el comando se ejecuta contra el playground REAL (o la raíz del repo) y el resultado no significa nada.
- Windows: strings de `command` como `python -m pytest -q` necesitan `python` en el PATH → activa el venv en el terminal donde ejecutes las evals.

<details><summary>💡 Pista 1</summary>

Primero las comprobaciones baratas, luego los efectos secundarios (copiar ficheros), luego la cara (ejecutar el comando).

</details>

<details><summary>💡 Pista 2</summary>

`missing = [s for s in chk.get("answer_contains", []) if norm(str(s)) not in norm(answer)]`; `tail = (p.stdout + p.stderr).strip().splitlines()[-3:]`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
chk = task.check
if chk.get("forbid_changes") and ...: return False, "modified files in a read-only task"
missing = ...
if missing: return False, f"the answer is missing: {missing}"
for src, dst in ...: ...   # mkdir + copy
if chk.get("command"):
    try: p = subprocess.run(...)
    except subprocess.TimeoutExpired: return False, ...
    if p.returncode != 0: return False, "check failed: " + ...
return True, "ok"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l12_evals.py -k "grade or hidden or run_task" -v
```

### TODO 12.2 · `forja/evals.py` · `summarize(results: list[TaskResult], model: str) -> dict`

**Qué debe hacer:** Devuelve un dict con las claves: `model`; `runs` = número de resultados; `pass_rate` = passed / runs redondeado a 3 decimales; `per_task` = `{task id: pass rate rounded to 2}` (agrupando las repeticiones del mismo id); `avg_steps` y `avg_seconds` = medias redondeadas a 1 decimal (0 si no hay resultados); `total_tokens` = suma de tokens; `results` = `[asdict(r) for r in results]`. Test: 3 resultados → `pass_rate == 0.667`, `per_task == {"a": 0.5, "b": 1.0}`, `avg_steps == 4.0`, `total_tokens == 350`, `len(results) == 3`.

**Pasos:**
1. Agrupa los resultados por `r.id` en un dict de listas (`setdefault` viene bien).
2. Calcula la tasa de aciertos global; protégete contra la división por cero con una lista vacía.
3. Calcula la tasa de aciertos por tarea a partir de cada grupo.
4. Calcula las medias de `steps` y `seconds` (protege la entrada vacía), y la suma de tokens.
5. Monta el dict exactamente con las claves de arriba; `results` vía `asdict`.

**Cuidado con:**
- Redondeo: `pass_rate` 3 decimales (`0.667`), `per_task` 2 decimales, medias 1 decimal. El test usa `==`.
- `statistics.mean([])` lanza `StatisticsError` → protege las listas vacías (el runner con un `--only` erróneo da cero resultados).
- `sum(r.passed for r in ...)` funciona porque `True == 1`; no cuentes `reason == "ok"` en su lugar.
- `run_evals.py` lee `rep["pass_rate"]`, `rep["avg_steps"]`, `rep["avg_seconds"]`, `rep["total_tokens"]`, `rep["per_task"]`, `rep["model"]` — una errata en el nombre de una clave hace que el runner pete después de todas las ejecuciones (lentas).

<details><summary>💡 Pista 1</summary>

Agrupa y luego agrega. Todo es una suma, un conteo o una media.

</details>

<details><summary>💡 Pista 2</summary>

`by_task.setdefault(r.id, []).append(r)`; `round(statistics.mean(r.steps for r in results), 1)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
by_task = {}
for r in results: ...
n = len(results) or 1
return {
    "model": model, "runs": ...,
    "pass_rate": round(..., 3),
    "per_task": {k: round(..., 2) for k, v in by_task.items()},
    "avg_steps": ..., "avg_seconds": ..., "total_tokens": ...,
    "results": [asdict(r) for r in results],
}
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l12_evals.py -k summarize -v
```

## Ejecuta
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config   # con tus hooks, skills y subagentes
```

## Pruébalo en tu agente
1. `python scripts/tasks.py evals --only vat_question` (solo lectura, la más rápida). Esperado: `» …run_evals.py --only vat_question`, luego una línea como `PASS  vat_question           18.4s   4 steps` (o `FAIL … the answer is missing: ['calculate_vat']`), y después el resumen `qwen3:8b: pass_rate 100% · 4.0 steps · 18.4s/task · 9123 tokens`, `per task: {...}` y `-> out/evals_qwen3_8b.json`.
2. `python scripts/tasks.py evals --only fix_rounding` → una línea FAIL muestra como motivo las últimas 3 líneas de la salida de pytest. Fíjate en que tu `playground/` real nunca se modifica.
3. `python scripts/tasks.py evals --repeat 3` (las 5 tareas × 3; tarda un rato en un portátil — lánzalo y sigue leyendo). Mira `per_task`: ¿qué tareas son inestables (0.33, 0.67)?
4. Si tienes un segundo modelo: `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (o el servidor del aula con `--backend openai_compat`). Abre los dos ficheros `out/evals_*.json` y compara `pass_rate`, `avg_steps`, `avg_seconds`, `total_tokens`.
5. Inspecciona un fallo: en el JSON, `results[i].answer` (primeros 500 caracteres) y `stop_reason` (`max_steps`, `loop`, `error`…) suelen decirte por qué.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `grade(...) == (True, 'ok')` falla con `(False, 'modified files…')` en el test de forbid | Copiaste los ficheros ocultos o ejecutaste el comando antes de la comprobación `forbid_changes`, o comparaste contra una instantánea nueva → comprueba primero `snapshot(workdir) != before`. |
| `test_grade_answer_and_forbid_changes`: 'the answer is missing: [VAT]' | La comparación distingue mayúsculas → aplica `norm()` tanto al string esperado como a la respuesta. |
| `test_hidden_tests_copied_after`: el fichero oculto no existe | Vuelves antes de copiar, o solo copias si hay éxito → copia los ficheros ocultos antes de ejecutar el comando, sea cual sea el resultado. |
| `test_run_task_pass_and_fail`: `ok.passed` es False / `steps != 5` | Labs anteriores están rotos en tu harness (edit_file, bash, permisos en bypass) → ejecuta `python scripts/tasks.py test 03` y `test 04`; o `catchup 12` si vas justo de tiempo. |
| Todas las evals reales dan FAIL con `EXCEPTION …` o `stop_reason: error` | El backend no es accesible o el modelo no está descargado → `forja doctor`, `ollama list`, revisa `.env`. |
| Windows: `check failed: 'python' is not recognized…` | El comando de comprobación se ejecuta con cmd.exe y el venv no está activo en ese terminal → `.venv\Scripts\activate` antes de ejecutar las evals. |
| `StatisticsError: mean requires at least one data point` | `--only` con un id desconocido da cero resultados → protege las listas vacías en `summarize` (y revisa cómo se escribe el id). |
| Los resultados varían mucho entre ejecuciones | Los modelos no son deterministas → compara siempre con `--repeat 3` o más y mira `per_task`, no una sola ejecución. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 12` → 5 passed.
- [ ] [ ] Tienes al menos un `out/evals_<model>.json` generado con `--repeat 3`.
- [ ] [ ] Puedes decir, con números (tasa de aciertos, pasos, segundos, tokens), qué modelo usarías para qué tareas.

## Proyecto final paso a paso

Proyecto final (16:00–17:00): personaliza Forja para tu forma de trabajar y demuéstralo con números. Cinco entregables, todos pequeños. Trabaja en `playground/` (o en un repo real tuyo para 1–4) y lleva una lista corta de `NOTES` con lo que cambiaste para la demo de 3 minutos. Presupuesto: ~10 min por entregable, 15 min para las evals.

### AGENTS.md: preferencias globales + uno por repo

**Dónde:** Global: `~/.forja/AGENTS.md` (macOS/Linux) · `%USERPROFILE%\.forja\AGENTS.md` (Windows; en PowerShell `$HOME\.forja\AGENTS.md`). Proyecto: `AGENTS.md` (o `FORJA.md`) en la raíz del repo; los ficheros se recogen desde la raíz del sistema de ficheros hasta `--cwd`, primero el global, así que el más cercano es el más específico.

1. Crea la carpeta: macOS/Linux `mkdir -p ~/.forja` · PowerShell `New-Item -ItemType Directory -Force $HOME\.forja`.
2. Escribe 5–10 viñetas de preferencias PERSONALES (idioma, verbosidad, hábitos de testing). Que sea breve: se envía en cada turno.
3. En un repo real tuyo, escribe `AGENTS.md` con: cómo ejecutar los tests, el comando de build/lint, las convenciones y las cosas que nunca deben hacerse.
4. Comprueba que se carga: arranca `forja --cwd <repo>` y pregunta `which instructions are you following?` — debería citar ambas capas (el prompt contiene `## User global instructions` y `## Project instructions (AGENTS.md)`).

<details><summary>📄 Plantilla</summary>

```markdown
# AGENTS.md — <project>

- Stack: <language/version>, <framework>.
- Tests: `<command>`. Run them after every code change.
- Lint/format: `<command>`.
- Conventions: <naming, error handling, logging>.
- Never: <edit generated files / touch migrations / change public APIs without asking>.
- When unsure, ask before large refactors.
```

</details>

> ⚠️ Las evals se ejecutan con un home temporal, así que `run_evals.py` NO usa `~/.forja/AGENTS.md`; solo `playground/AGENTS.md` (copiado con el proyecto). Si quieres medir un cambio en las instrucciones, ponlo en `playground/AGENTS.md`.

### Una skill de equipo

**Dónde:** `<project>/.forja/skills/<skill-name>/SKILL.md` (proyecto) o `~/.forja/skills/<skill-name>/SKILL.md` (personal; si coinciden los nombres gana el proyecto). Los ficheros extra (scripts, plantillas) pueden vivir en la misma carpeta: la herramienta `skill` le dice al modelo la ruta de la carpeta.

1. Elige un procedimiento que expliques una y otra vez: checklist de release, rúbrica de code review, cómo añadir un endpoint, pasos de migración de BD…
2. Escribe el frontmatter: `name` (kebab-case, = nombre de la carpeta) y una `description` que diga QUÉ es y CUÁNDO cargarla.
3. Escribe el cuerpo como pasos numerados con comandos exactos. Mantenlo por debajo de ~60 líneas.
4. Comprueba el descubrimiento: `/tools` muestra `skill`, y un prompt que la necesite produce `⏺ skill <name>` como una de las primeras llamadas.

<details><summary>📄 Plantilla</summary>

```markdown
---
name: add-endpoint
description: How to add a REST endpoint in this repo (routing, validation, tests). Load it before creating or changing an endpoint.
---
# Adding an endpoint

1. Route in `<file>`; handler in `<folder>/<name>.py`.
2. Validate input with <library>; return <error format> on failure.
3. Add a test in `tests/<...>` covering success and one error.
4. Run `<test command>` before finishing.
```

</details>

> ⚠️ Si el modelo nunca la carga, la descripción es demasiado vaga. Di cuándo: 'Load it before …'. Mira `examples/project/.forja/skills/conventional-commits/SKILL.md`.

### Un hook que garantiza algo que ahora pides por favor

**Dónde:** Script en `<project>/.forja/hooks/<name>.py`; registro en `<project>/.forja/settings.json` bajo `hooks.<Event>` (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`). Los comandos se ejecutan con `cwd` = raíz del proyecto a través del shell (cmd.exe en Windows).

1. Elige el evento: bloquear algo → `PreToolUse`; dar feedback tras una edición (lint, compilación, comprobación de formato) → `PostToolUse`; 'no termines hasta X' → `Stop`; inyectar contexto o filtrar prompts → `UserPromptSubmit`.
2. Escribe el script: lee el evento con `json.load(sys.stdin)` (`tool_name`, `tool_input`, y `tool_response` para PostToolUse; `prompt` para UserPromptSubmit), decide, imprime el motivo en stderr y haz `sys.exit(2)` para bloquear/dar feedback, `sys.exit(0)` en caso contrario.
3. Regístralo con un `matcher` regex (coincidencia completa con el nombre de la herramienta, p. ej. `edit_file|write_file`, `bash`, `mcp__issues__.*`); omite el matcher para aplicarlo a todas.
4. Prueba primero el script solo. macOS/Linux: `echo '{"tool_name":"bash","tool_input":{"command":"cat .env"}}' | python .forja/hooks/<name>.py; echo $?` · PowerShell: `'{"tool_name":"bash","tool_input":{"command":"cat .env"}}' | python .forja\hooks\<name>.py; $LASTEXITCODE`.
5. Después dispáralo desde el CLI y comprueba que ves `BLOCKED by hook: …` (Pre) o `[hook PostToolUse] …` en el resultado de la herramienta (Post).

<details><summary>📄 Plantilla</summary>

```python
"""PostToolUse (edit_file|write_file): <what it guarantees>. Exit 2 = feedback to the model."""
import json, subprocess, sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("path", "")
if not path.endswith(".py"):
    sys.exit(0)
p = subprocess.run(["ruff", "check", "--quiet", path], capture_output=True, text=True)
if p.returncode != 0:
    print(f"Lint errors in {path}:\n{p.stdout[-2000:]}", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
```
```json
"hooks": {"PostToolUse": [{"matcher": "edit_file|write_file", "command": "python .forja/hooks/lint.py", "timeout": 30}]}
```

</details>

> ⚠️ La salida 1 NO bloquea (se registra como error del hook y se ignora): usa la salida 2. Un hook `Stop` lento se ejecuta en cada respuesta final — que sea rápido (`-x`, un subconjunto de tests).

### Un perfil de subagente especializado

**Dónde:** `<project>/.forja/agents/<name>.md`. Claves de frontmatter que lee `load_profiles`: `name`, `description` (obligatorias), `tools` (lista o string `a, b`; por defecto `read_file, grep, glob`), `max_steps` (por defecto 25). Nombres de herramienta válidos: `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `bash`, `todo_write`, `skill`, `mcp__<server>__<tool>` (`task` se elimina siempre). El cuerpo es su system prompt.

1. Elige un trabajo acotado en el que ayude un contexto limpio: triaje de tests fallidos, revisión de seguridad, redactor de documentación, auditor de dependencias, un `tester` que solo ejecuta pytest.
2. Dale las herramientas MÍNIMAS. Roles de solo lectura: `read_file, grep, glob` (+ `bash` si necesita `git diff`/pytest, y añade las reglas `allow` correspondientes en settings).
3. Escribe la descripción desde el punto de vista del agente principal: qué hace y cuándo delegar en él.
4. Escribe el cuerpo: rol, método (numerado) y el formato de salida exacto que quieres recibir (es lo único que verá el agente principal).
5. Comprueba: el perfil aparece en la descripción de la herramienta `task`; pide `use the <name> subagent to …` y busca llamadas con prefijo `[<name>]`.

<details><summary>📄 Plantilla</summary>

```markdown
---
name: tester
description: Runs the test suite and explains failures with the likely cause and file:line. Use it after code changes or when tests fail.
tools: read_file, grep, glob, bash
max_steps: 15
---
You are a test triage specialist. Only run `python -m pytest` commands with bash; never modify files.
1. Run the suite (`python -m pytest -q -x`).
2. For each failure, read the test and the code under test.
Answer with: a one-line verdict, then per failure `test name — cause — path:line — suggested fix (1 sentence)`.
```

</details>

> ⚠️ La restricción de herramientas es por NOMBRE; un subagente con `bash` puede ejecutar cualquier comando que tus permisos permitan. Para restringir comandos, apóyate en las reglas `allow`/`deny` (p. ej. `bash(python -m pytest*)`) y en las aprobaciones — las llamadas del subagente pasan por la misma puerta que las del agente principal.

### Una tarea de eval para tu trabajo diario + un informe de 2 modelos

**Dónde:** Añade la tarea a `evals/tasks.yaml` (al FINAL: `test_tasks_file` espera que `fix_rounding` y `fix_due_date` sigan siendo las primeras). Los tests ocultos van en `evals/hidden/` y se referencian como `{"evals/hidden/<file>.py": "tests/<dest>.py"}`. Los informes van a `out/evals_<model>.json`. Las tareas siempre se ejecutan sobre una copia de `playground/`, así que expresa tu trabajo diario sobre el proyecto de facturas.

1. Elige un tipo de tarea que hagas cada semana: un bug fix pequeño, una feature con tests, un refactor que debe mantener los tests en verde, o una pregunta sobre el código.
2. Escribe el prompt como un ticket (qué, no cómo). Elige una comprobación OBJETIVA: `command` (tests), `hidden` (tests que el agente no puede ver — lo mejor para features), `answer_contains` (+ `forbid_changes: true` para preguntas).
3. Para una comprobación `hidden`, escribe el fichero de test oculto en `evals/hidden/` y verifica que FALLA sobre el playground sin tocar (si no, la tarea no mide nada).
4. Ejecútala sola: `python scripts/tasks.py evals --only <id> --repeat 3`. Itera el prompt/la comprobación hasta que un pass signifique 'hecho bien'.
5. Ejecuta la misma tarea (o la suite completa) con dos modelos: `python scripts/tasks.py evals --model qwen3:8b --repeat 3` y `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (o `--backend openai_compat` / `--backend openrouter --model <open-weight model>`).
6. Escribe el informe: una tabla a partir de los dos ficheros JSON (pass rate, per_task de tu tarea, avg steps, avg seconds, total tokens) + 2–3 frases de conclusión.

<details><summary>📄 Plantilla</summary>

```yaml
- id: my_overdue_flag
  prompt: "Add a method Invoice.is_overdue(today) that returns True when today is after the due date. Add a test."
  check: {command: "python -m pytest -q tests/test_overdue_hidden.py", hidden: {"evals/hidden/test_overdue.py": "tests/test_overdue_hidden.py"}}

- id: my_question
  prompt: "Without modifying anything: where is the due date computed and what happens on weekends?"
  check: {answer_contains: ["dates.py", "due_date"], forbid_changes: true}
```
Esqueleto del informe (Markdown):
```markdown
| model | pass rate | my task | avg steps | avg s | tokens |
|---|---|---|---|---|---|
| qwen3:8b | 0.60 | 0.33 | 9.1 | 41.0 | 120k |
| qwen3-coder:30b | … | … | … | … | … |

Conclusion: <which model for which task, and why>.
```
Para imprimir los números: `python -c "import json,glob; [print(r['model'], r['pass_rate'], r['per_task'], r['avg_steps'], r['avg_seconds'], r['total_tokens']) for r in map(lambda f: json.load(open(f, encoding='utf-8')), glob.glob('out/evals_*.json'))]"`

</details>

> ⚠️ Por defecto `run_task` copia el playground SIN `.forja/` (solo cuenta `playground/AGENTS.md`). Para medir tu configuración ejecuta dos veces y compara: `python scripts/tasks.py evals --repeat 3 --label base` y `python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config`. `~/.forja/AGENTS.md` nunca se usa (home temporal). Las rutas MCP de `settings.json` se resuelven desde la copia temporal: usa rutas absolutas con `--mcp`.

### Demo de 3 minutos
1. 3 minutos por persona/pareja: 30 s qué has añadido (enseña los ficheros), 90 s un prompt en directo donde se vea actuar una skill/hook/subagente, 60 s la tabla de evals y tu conclusión.
2. Trae números, no impresiones: 'la tasa de aciertos en mi tarea pasó de 0.33 a 1.0 con qwen3-coder:30b a 2× el tiempo'.

### Has terminado cuando
- [ ] [ ] Existen el `AGENTS.md` global y el de proyecto, y el agente puede citarlos.
- [ ] [ ] El agente carga una skill (`⏺ skill <name>`) cuando procede.
- [ ] [ ] Un hook bloquea o da feedback de forma visible (`BLOCKED by hook` / `[hook PostToolUse]`).
- [ ] [ ] Un perfil de subagente aparece en la descripción de `task` y se usa (llamadas `[<name>]`).
- [ ] [ ] Una tarea nueva en `evals/tasks.yaml`, `python scripts/tasks.py test 12` sigue pasando, y dos informes `out/evals_*.json` comparados en una tabla.

## Checkpoint
Tienes un informe en `out/` y puedes decir, con números, qué modelo usarías y para qué tareas.

## Retos
1. Añade una tarea propia a `evals/tasks.yaml`.
2. Compara tu harness con y sin `todo_write` en el prompt base.

**Tests:** `tests/test_l12_evals.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup end`

---
[← anterior](../L11_sessions/README.md)
