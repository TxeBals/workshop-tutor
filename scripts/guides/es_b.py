"""Guía paso a paso para el alumnado (español) de los labs 05, 06, 07 y 08.

Esquema: ver los usos en scripts/guides/__init__.py. Todas las cadenas son Markdown.
"""
from __future__ import annotations

GUIDE: dict[str, dict] = {
    # ------------------------------------------------------------------ LAB 05
    "05": {
        "before": [
            "Abre `forja/cli.py`. Casi todo lo que contiene es fontanería de UI que ya se te da hecha (`RichEvents`, `repl`, `main`, `doctor`). "
            "Solo escribes cuatro funciones pequeñas: `summarize_call`, `diff_styles`, `ask_approval` y `handle_slash`. "
            "Lee primero `RichEvents.on_tool_start` / `on_tool_end`: muestran exactamente dónde se llaman tus funciones.",
            "La UI llama a tus funciones a través de `_safe(...)`, que solo se traga `NotImplementedError`. Cualquier otra excepción "
            "(p. ej. un `KeyError` porque el modelo omitió un argumento) rompería el turno, así que sé defensivo con `dict.get`.",
            "Librerías usadas: `rich` (`console.print`, `Panel`, `Text`), ya importadas. No necesitas aprender rich a fondo: "
            "`console.print(Panel(Text(\"...\"), title=\"...\", border_style=\"yellow\"))` es todo lo que necesita el 05.3.",
            "Cómo se conecta con el harness: `Forja.gate` (en `forja/harness.py`) llama a `self.approver(tool, args, why)` cuando "
            "los permisos responden `ask`; `build_app` pasa tu `ask_approval` como ese approver. `handle_slash` recibe el objeto `Forja`, "
            "así que lee los atributos que usa: `app.mode`, `app.set_mode()`, `app.registry.tools`, `app.todos`, "
            "`app.context_tokens()`, `app.compact_now()`, `app.usage`, `app.undo()`, `app.transcript.folder`, `app.history`, "
            "`app.settings.context_window`.",
            "Este lab termina con el **hito del día 1** (ver la sección del hito): tu propio agente arregla los 3 tests que fallan en "
            "`playground/`. Resérvate 15 minutos para ello.",
        ],
        "order": (
            "Haz primero el 05.2 (5 minutos, lógica pura de cadenas, da confianza), luego el 05.1 (formateo de cadenas con muchos casos, "
            "y el 05.3 lo reutiliza), después el 05.3 (mínimo una vez existe el 05.1), y termina con el 05.4, que es el más largo y requiere "
            "una lectura rápida de `Forja` en `forja/harness.py`. Ejecuta el test de cada TODO sobre la marcha; luego ejecuta el lab completo con "
            "`python scripts/tasks.py test 05` y pasa al hito."
        ),
        "todos": {
            "05.1": {
                "where": "`forja/cli.py` · `summarize_call(name, args, width=100) -> str`",
                "contract": (
                    "Recibe el nombre de la herramienta y el dict de argumentos (en bruto, posiblemente incompleto) que envió el modelo. Devuelve UNA línea, "
                    "de como máximo `width` caracteres. Formatos exactos que comprueba `test_summarize_call`:\n"
                    "- `read_file` -> `Read a.py`; con `offset` distinto de 1 -> `Read a.py (from line 50)`\n"
                    "- `write_file` -> `Write n.md (2 lines)` (número de líneas de `content`)\n"
                    "- `edit_file` -> `Edit path`\n"
                    "- `bash` -> `$ pytest -q` (el comando, con los espacios colapsados)\n"
                    "- `grep` -> `Grep 'def x' in src (*.py)` (path por defecto `.`; ` (include)` solo si include tiene valor)\n"
                    "- `glob` -> `Glob pattern`\n"
                    "- `task` -> `Task[explore] find VAT` (`subagent_type` por defecto `explore`)\n"
                    "- `todo_write` -> `Todos (N)` (número de elementos)\n"
                    "- cualquier otra -> `name(k=v, k2=v2)`, p. ej. `mcp__x__y(id=3)`\n"
                    "Toda secuencia de espacios en blanco (espacios, saltos de línea) se convierte en un único espacio. Si la línea supera `width`, córtala "
                    "para que el resultado tenga exactamente `width` caracteres, terminando en `…`."
                ),
                "steps": [
                    "Ramifica según `name` con una cadena `if/elif` y construye una cadena `s` para cada herramienta conocida, leyendo los argumentos con `args.get(key, default)`.",
                    "Para `read_file`, empieza con `Read <path>` y añade ` (from line N)` solo cuando `args.get(\"offset\", 1) != 1`.",
                    "Para `write_file`, cuenta las líneas con `str(content).splitlines()`; para `grep`, añade el sufijo ` (<include>)` solo cuando include sea truthy.",
                    "Para el caso por defecto, une pares `f\"{k}={v}\"` con `\", \"` dentro de `name(...)` (opcionalmente recorta los valores largos a ~30 caracteres cada uno).",
                    "Colapsa los espacios de la cadena final: `\" \".join(s.split())`.",
                    "Trunca al final: si `len(s) > width`, quédate con los primeros `width - 1` caracteres y añade `…`.",
                ],
                "gotchas": [
                    "Colapsa los espacios ANTES de truncar; si no, la comprobación de longitud usa la cadena equivocada (`test_summarize_call` comprueba `len(...) == 50` con `width=50`).",
                    "El corte debe dar exactamente `width` caracteres incluyendo el `…` (un carácter), ni `width + 1` ni `...` (tres puntos).",
                    "`args` viene directamente del JSON del modelo (sin validar): pueden faltar claves. Usa `.get()` en todas partes; un `KeyError` aquí rompe el turno.",
                    "`bash` con `\"pytest  -q\\n\"` debe convertirse en `$ pytest -q`: los espacios dobles y el salto de línea final desaparecen.",
                ],
                "hints": [
                    "Piénsalo como una tabla de 9 formatos más dos pasos de postprocesado (colapsar, truncar) aplicados a lo que hayas construido.",
                    "Los valores por defecto importan para las cadenas esperadas: path de grep `'.'`, tipo de task `'explore'`, offset de read `1`, todos `[]`.",
                    "Esqueleto:\n```python\nif name == \"read_file\":\n    s = f\"Read {args.get('path')}\"\n    # if offset != 1: append \" (from line N)\"\nelif name == \"bash\":\n    s = ...\n# elif ... write_file / edit_file / grep / glob / task / todo_write\nelse:\n    s = f\"{name}(...)\"   # k=v pairs\ns = ...                  # collapse whitespace\nreturn ...               # truncate to width with '…'\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k summarize -v",
            },
            "05.2": {
                "where": "`forja/cli.py` · `diff_styles(diff: str) -> list[tuple[str, str]]`",
                "contract": (
                    "Recibe un diff unificado como una sola cadena (el `diff` que `write_file`/`edit_file` ponen en `ToolResult.meta`). "
                    "Devuelve una tupla `(line, style)` por línea, en orden, con el texto de la línea sin cambios (sin salto de línea). Estilos: "
                    "`'+++'` o `'---'` -> `'bold'`; `'@@'` -> `'cyan'`; `'+'` -> `'green'`; `'-'` -> `'red'`; todo lo demás -> `'dim'`. "
                    "`test_diff_styles` espera `[\"bold\", \"bold\", \"cyan\", \"red\", \"green\", \"dim\"]` para un diff de 6 líneas."
                ),
                "steps": [
                    "Divide el diff en líneas con `str.splitlines()`.",
                    "Para cada línea, prueba los prefijos del más específico al menos específico: cabeceras (`+++`, `---`), luego hunk (`@@`), luego `+` y luego `-`.",
                    "Añade `(line, style)` a la lista de salida; el estilo por defecto es `dim`.",
                    "Devuelve la lista (un diff vacío da `[]`).",
                ],
                "gotchas": [
                    "El orden importa: `'--- a/x'` también empieza por `'-'`. Si pruebas `'-'` primero, las cabeceras salen en rojo y el test falla.",
                    "`str.startswith` acepta una tupla: `line.startswith((\"+++\", \"---\"))`.",
                    "No hagas strip de las líneas: una línea de contexto empieza por un espacio y la UI la imprime tal cual.",
                ],
                "hints": [
                    "Es un bucle con una cadena `if/elif` sobre prefijos.",
                    "Comprueba los prefijos de 3 caracteres antes que los de 1 carácter.",
                    "Esqueleto:\n```python\nout = []\nfor line in diff.splitlines():\n    if line.startswith((\"+++\", \"---\")):\n        style = \"bold\"\n    # elif '@@' ... elif '+' ... elif '-' ...\n    else:\n        style = \"dim\"\n    out.append(...)\nreturn out\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k diff_styles -v",
            },
            "05.3": {
                "where": "`forja/cli.py` · `ask_approval(tool, args, reason, read=input) -> Approval`",
                "contract": (
                    "La llama `Forja.gate` cuando la decisión de permisos es `ask`. Muestra al usuario lo que se va a ejecutar "
                    "(un `Panel` con `summarize_call(tool.name, args, ...)`) y por qué se pregunta (`reason`, p. ej. "
                    "`requires approval`). Lee UNA respuesta llamando a `read(prompt_text)`. Devuelve la cadena literal "
                    "`\"yes\"` para `y`/`yes`, `\"always\"` para `a`/`always` y `\"no\"` para cualquier otra cosa, incluida una respuesta "
                    "vacía. `test_ask_approval` pasa `read=lambda _: \"y\"`, `\"a\"` y `\"\"`. Con `always`, el harness "
                    "(no tú) añade una regla mediante `permissions.suggest_rule`."
                ),
                "steps": [
                    "Construye el resumen con `summarize_call(tool.name, args, width=...)`; usa un ancho grande (p. ej. 400) para que el usuario vea el comando completo antes de aprobarlo.",
                    "Imprímelo con `console.print(Panel(Text(summary), title=..., border_style=\"yellow\"))`; pon `tool.name` y `reason` en el título.",
                    "Llama a `read(\"  [y]es / [n]o / [a]lways this session > \")` y normaliza la respuesta con `str(...).strip().lower()`.",
                    "Traduce la respuesta a `\"yes\"`, `\"always\"` o `\"no\"` y devuélvela.",
                ],
                "gotchas": [
                    "Usa el parámetro `read`, nunca `input()` ni `console.input()` directamente: los tests inyectan `read`, y bajo pytest un `input()` real falla porque stdin está capturado.",
                    "Devuelve exactamente `\"yes\"` / `\"no\"` / `\"always\"` (el literal `Approval`), ni booleanos ni `\"y\"`.",
                    "Por defecto es NO: una respuesta vacía (solo Enter), `nope` o cualquier cosa desconocida -> `\"no\"`. Seguro por defecto. Normaliza primero, para que ` Y ` siga contando como sí.",
                    "Envuelve el resumen en `Text(...)`: si pasas una cadena sin más, rich interpreta los `[brackets]` (corchetes) de los comandos como markup.",
                ],
                "hints": [
                    "Dos partes: imprimir algo y luego traducir una respuesta a una de tres cadenas.",
                    "Bastan pruebas de pertenencia: `ans in (\"y\", \"yes\")`, `ans in (\"a\", \"always\")`.",
                    "Esqueleto:\n```python\nsummary = summarize_call(tool.name, args, width=400)\nconsole.print(Panel(Text(summary), title=f\"Allow {tool.name}? (...)\", border_style=\"yellow\"))\nans = ...  # read(...) normalised\nif ...:\n    return \"yes\"\n# always?\nreturn \"no\"\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k approval -v",
            },
            "05.4": {
                "where": "`forja/cli.py` · `handle_slash(app: Forja, line: str) -> str | None`",
                "contract": (
                    "Recibe la línea en bruto tecleada en el REPL (empieza por `/`). Devuelve el texto a imprimir, o `None` para `/exit`. "
                    "Actúa directamente sobre el harness, nunca llama al modelo. Lo comprueba `test_slash_commands`:\n"
                    "- `/exit` -> `None`; `/help` -> `HELP` (contiene `/mode`)\n"
                    "- `/mode` solo -> el modo actual y la lista `MODES`; `/mode plan` -> exactamente `mode -> plan` y `app.mode == \"plan\"` "
                    "(usa `app.set_mode`, que lanza `ValueError` para modos desconocidos; el REPL la captura e imprime `error: ...`)\n"
                    "- `/tools` -> una línea por herramienta con su riesgo entre corchetes, p. ej. `bash   [exec]`\n"
                    "- `/todos` -> `app.todos.render()` (contiene `▶ a` para un elemento en curso)\n"
                    "- `/context` -> texto que contenga `tokens` (usa `app.context_tokens()`, opcionalmente `app.settings.context_window` y `len(app.history)`)\n"
                    "- `/compact` -> `app.compact_now(force=True)` (o un texto alternativo si devuelve vacío)\n"
                    "- `/cost` -> texto que contenga `input` (a partir de `app.usage['prompt_tokens']` y `['completion_tokens']`)\n"
                    "- `/undo` -> `app.undo()` devuelve una lista de `Path`; muéstralas relativas (`app.ws.rel(p)`) o indica que no hay nada que deshacer\n"
                    "- `/sessions` -> `Transcript.list_sessions(app.transcript.folder)` da `[(id, first_message)]`\n"
                    "- `/clear` -> vacía `app.history` (y la lista de tareas) y devuelve exactamente `new conversation`\n"
                    "- cualquier otra cosa -> un mensaje que contenga `unknown`"
                ),
                "steps": [
                    "Separa la línea en comando y argumento: `line.strip().split(maxsplit=1)`; el argumento es el resto (o `\"\"`).",
                    "Gestiona primero `/exit` y `/help` (returns triviales).",
                    "`/mode`: sin argumento describe el modo actual; con argumento llama a `app.set_mode(arg)` y devuelve `f\"mode -> {app.mode}\"`.",
                    "Comandos de solo lectura: `/tools` (itera `app.registry.tools.values()`, cada `Tool` tiene `.name` y `.risk`), `/todos`, `/context`, `/cost`, `/sessions`; construye una cadena para cada uno.",
                    "Comandos con efectos: `/compact`, `/undo`, `/clear` (asigna `app.history = []` y `app.todos.items = []`).",
                    "Termina con el caso por defecto para comandos desconocidos, sugiriendo `/help`.",
                ],
                "gotchas": [
                    "`/mode plan` debe devolver exactamente `mode -> plan` (`->` en ASCII, un espacio a cada lado).",
                    "`/clear` debe devolver exactamente `new conversation` y dejar `app.history == []` (asigna una lista nueva).",
                    "No captures tú el `ValueError` de `set_mode` para devolver `None`: `None` significa salir y cerraría el REPL. Deja que se propague o devuelve un texto de error.",
                    "`app.compact_now(force=True)` puede devolver `\"\"` (nada que compactar); devuelve un texto alternativo legible en lugar de una línea vacía.",
                    "`/undo` y `/compact` dependen de los labs 11 y 07: hasta entonces el harness hace un fallback silencioso (lista vacía / nada compactado). Es lo esperado.",
                ],
                "hints": [
                    "Aquí se lee mejor una secuencia plana de `if cmd == \"/...\": return ...` que un dict de lambdas.",
                    "Todo lo que necesitas ya está en `app`: `app.registry.tools`, `app.todos.render()`, `app.context_tokens()`, `app.usage`, `app.transcript.folder`.",
                    "Esqueleto:\n```python\ncmd, *rest = line.strip().split(maxsplit=1)\narg = rest[0].strip() if rest else \"\"\nif cmd == \"/exit\":\n    return None\nif cmd == \"/mode\":\n    if not arg:\n        return ...            # current mode + MODES\n    app.set_mode(arg)\n    return f\"mode -> {app.mode}\"\n# /help /tools /todos /context /compact /cost /undo /sessions /clear\nreturn f\"unknown command: {cmd} (/help)\"\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k slash -v",
            },
        },
        "try_it": [
            "Comprueba primero el modelo: `forja doctor`. Esperado: `backend=ollama url=... model=...`, `answered in N.Ns` y luego `✔ the model calls tools (ping)`.",
            "Arranca el REPL sobre el playground: `forja --cwd playground --mode accept_edits`. Verás un panel cian `Forja <version> · <model> · mode accept_edits` y el prompt `accept_edits ›`.",
            "Escribe `/tools`: una línea por herramienta, p. ej. `read_file   [read]`, `edit_file   [edit]`, `bash   [exec]`. Luego `/mode`: `current mode: accept_edits (available: default, accept_edits, plan, bypass)`.",
            "Pide: `fix the amount rounding bug and check with the tests`. Deberías ver una línea azul por acción (`⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`), un diff enmarcado en verde/rojo tras cada edición y un panel amarillo `Allow bash? (requires approval)` antes de cada comando. Responde `a` una vez: aparece una nota tenue `rule added for this session: allow bash(python -m pytest*)` y las siguientes ejecuciones de pytest ya no preguntan.",
            "Tras el turno: `(N steps · M tools)` en gris. Escribe `/cost` (`input ... · output ... tokens`) y `/context` (`~N tokens of 32768 (M messages)`).",
            "Pulsa Ctrl+C durante una respuesta larga: `interrupting…` y el agente se detiene en el siguiente límite de paso. Después `/exit`.",
        ],
        "troubleshooting": [
            ["`test_ask_approval` se cuelga o falla con `OSError: pytest: reading from stdin while output is captured`",
             "Llamaste a `input()`/`console.input()` en lugar de al parámetro `read` → llama a `read(prompt)`."],
            ["`test_summarize_call` falla en la aserción de longitud (51 != 50) o en `$ pytest  -q`",
             "El truncado añade `…` sin quitar un carácter, o truncas antes de colapsar los espacios → colapsa primero y luego `s[:width - 1] + \"…\"`."],
            ["`test_diff_styles` da `['red', 'green', ...]` para las cabeceras",
             "Pruebas `-`/`+` antes que `---`/`+++` → comprueba primero los prefijos de 3 caracteres."],
            ["El REPL se cierra al escribir `/mode foo`",
             "`handle_slash` devolvió `None` ante un error → solo `/exit` devuelve `None`; deja que el `ValueError` de `set_mode` se propague (el REPL imprime `error: unknown mode: foo`)."],
            ["`KeyError` / fallo en las líneas `⏺` cuando el modelo envía argumentos raros",
             "`summarize_call` usa `args['x']` → usa `args.get('x', default)`; los argumentos llegan del modelo sin validar."],
            ["`forja` no se reconoce (Windows) / `command not found` (macOS/Linux)",
             "El venv no está activo o no se ejecutó el setup → PowerShell `.venv\\Scripts\\Activate.ps1` (si está bloqueado: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`), macOS/Linux `source .venv/bin/activate`, y luego `python scripts/tasks.py setup`. `python -m forja ...` también funciona."],
            ["Windows: el agente ejecuta `ls`, `cat` o `python3` y obtiene errores",
             "La herramienta bash usa `cmd.exe` en Windows → es normal; el modelo debería adaptarse tras el error. Díselo: `use python -m pytest -q; this is Windows cmd`."],
            ["Los colores o `⏺` se ven como basura en consolas antiguas de Windows",
             "Usa Windows Terminal (o el terminal de VS Code) en lugar de la ventana clásica de `cmd.exe`; `chcp 65001` ayuda con UTF-8."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 05` → 4 passed.",
            "[ ] En el REPL ves resúmenes de una línea, diffs en color y el panel de aprobación y/n/a; `/tools`, `/mode`, `/cost` y `/context` funcionan.",
            "[ ] Hito del día 1: tu agente hizo pasar los 3 tests que fallaban en el playground, y anotaste modelo, éxito, pasos y tiempo.",
        ],
        "milestone": [
            "**Objetivo (15:15):** con TU Forja y TU modelo local, pasan los 3 tests que fallan en `playground/`. Después compara resultados con una pareja que use otro modelo.",
            "**1. Resetea el playground.** Desde la raíz del repo: `python scripts/tasks.py reset` (el mismo comando en Windows y en macOS/Linux). "
            "Comprueba el punto de partida: `cd playground`, luego `python -m pytest -q` y después `cd ..`. Resumen esperado: `3 failed, 4 passed` "
            "(`test_round_half_up`, `test_total_with_vat_cent`, `test_due_date_sunday_moves_to_monday`).",
            "**2. Comprueba el modelo.** `forja doctor` debe terminar con `✔ the model calls tools`. Si imprime `! the model answered without calling the tool`, cambia de modelo "
            "(`FORJA_MODEL` en `.env`) o usa el servidor del aula antes de seguir.",
            "**3. Arranca el agente.** `forja --cwd playground --mode accept_edits` (las ediciones se aprueban solas, los comandos preguntan). Pon en marcha un cronómetro al pulsar Enter en el prompt.",
            "**4. Prompt a usar** (pégalo en una sola línea). El lab 06 aún no está hecho, así que el agente NO ve `playground/AGENTS.md`: el propio prompt lleva las reglas del proyecto:\n"
            "> Ejecuta los tests con `python -m pytest -q`, averigua por qué fallan 3 tests y arregla el código en `invoices/` (nunca cambies los tests). "
            "Los importes tienen 2 decimales con redondeo half-up usando `decimal`, nunca `round()` sobre floats. Las fechas de vencimiento que caen en sábado o domingo pasan al lunes siguiente. "
            "Cuando termines, vuelve a ejecutar los tests y enséñame el resultado.",
            "**5. Aprobaciones.** Cuando el panel amarillo `Allow bash?` muestre `$ python -m pytest -q`, responde `a` (always): solo pytest obtiene una regla de sesión. "
            "Responde `n` a cualquier cosa que no ejecutarías en tu propia máquina (instalar paquetes, borrar ficheros).",
            "**6. Cómo es una ejecución BUENA:** `⏺ $ python -m pytest -q` (3 fallos) → `⏺ Read invoices/amounts.py` / `⏺ Read invoices/dates.py` → "
            "`⏺ Edit invoices/amounts.py` con un diff que redondea mediante `Decimal(str(value))` + `ROUND_HALF_UP` → `⏺ Edit invoices/dates.py` con un diff que también trata el domingo "
            "→ `⏺ $ python -m pytest -q` mostrando `7 passed` → un resumen breve que cita los ficheros. Normalmente 6–15 pasos, un turno, sin ediciones bajo `tests/`.",
            "**7. Cómo es una ejecución MALA** (anótala, son datos, no un fracaso): el modelo edita `tests/` para que pasen; usa `Decimal(value)` sobre el float "
            "(2.675 se queda en 2.67) o añade apaños tipo `+ 0.0001`; afirma `all tests pass` sin volver a ejecutar pytest; repite el mismo `edit_file` fallido hasta que el detector de bucles lo para; "
            "reescribe un fichero entero con `write_file` y se deja funciones; responde con un bloque de código en lugar de llamar a herramientas; llega a `max_steps`. "
            "Da como mucho dos prompts correctivos de seguimiento (p. ej. `the tests still fail, run them and read the error`) y cuéntalos.",
            "**8. Verifica fuera del agente.** `/exit`, luego `cd playground` y `python -m pytest -q` → `7 passed`. Comprueba que solo cambió `invoices/`: `git status playground` "
            "(o `git diff --stat playground`). Si cambió un fichero de test, la ejecución no cuenta como éxito.",
            "**9. Anota tu resultado** (en tu cuaderno o en la hoja compartida): **modelo** (tag exacto, p. ej. `qwen3:8b`, más el backend: Ollama local / servidor del aula / OpenRouter), "
            "**éxito** (sí/no y tests que pasan de 7; indica si necesitaste prompts de seguimiento), **pasos** (la línea gris `(N steps · M tools)`; súmalas si hubo varios turnos), "
            "**tiempo** (cronómetro desde Enter hasta la respuesta final; opcionalmente los tokens de `/cost`). Luego compara con un compañero que haya usado otro modelo: ¿quién necesitó menos pasos?, ¿quién rompió una regla?",
            "**10. Opcional: una ejecución headless reproducible.** `python scripts/tasks.py reset` y luego cronométrala: PowerShell `Measure-Command { forja --cwd playground --mode bypass -p \"<same prompt>\" }`, "
            "macOS/Linux `time forja --cwd playground --mode bypass -p \"<same prompt>\"`. En headless no hay usuario: en `accept_edits` todo comando sería DENEGADO, de ahí `bypass` "
            "(las reglas deny siguen aplicándose). El código de salida 0 significa que el agente terminó con una respuesta final, no que los tests pasen: ejecuta pytest tú mismo.",
        ],
    },
    # ------------------------------------------------------------------ LAB 06
    "06": {
        "before": [
            "Abre `forja/context.py`. Lee primero las partes que se dan hechas: `BASE_PROMPT`, `MODE_REMINDERS` (un dict modo -> texto), "
            "`INSTRUCTION_FILES = (\"AGENTS.md\", \"FORJA.md\")`, `MENTION_RE` y `git_info(root)`. Escribes tres funciones.",
            "Mira `Forja.system_prompt()` y `Forja.turn()` en `forja/harness.py`: el harness llama a `build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos])` "
            "en CADA paso, y a `expand_mentions(text, self.ws)` en cada mensaje del usuario. Hasta que termines este lab usa el `FALLBACK_PROMPT` de una línea, así que tu agente nunca ha visto `AGENTS.md`.",
            "Stdlib que necesitas: `pathlib.Path` (`/`, `.is_file()`, `.resolve()`, `.parent`, `.read_text(encoding=\"utf-8\")`, `.is_relative_to()`), "
            "`re.Pattern.findall`, `dict.fromkeys(...)` (deduplicación que conserva el orden), `platform.system()`, `datetime.date.today().isoformat()`.",
            "Del lab 02 reutilizas el `Workspace` (`forja/fs_tools.py`): `ws.root`, `ws.resolve(path)` (lanza `PermissionError` fuera del sandbox), "
            "`ws.rel(p)` y `ws.mark_read(p)` (registra el fichero en `ws.read_state` para que un `edit_file` posterior no se queje de que no se ha leído).",
        ],
        "order": (
            "Primero el 06.1: el 06.2 lo llama para obtener los ficheros de instrucciones. Luego el 06.2, el prompt por capas, que es lo que activa AGENTS.md en tu CLI. "
            "El 06.3 es independiente; déjalo para el final. Cuando el 06.2 pase, el `test_plan_mode_flow` del lab 08 también depende de él (comprueba `PLAN mode` y la lista de tareas en el system prompt)."
        ),
        "todos": {
            "06.1": {
                "where": "`forja/context.py` · `find_instruction_files(cwd, home=None, stop=None) -> list[Path]`",
                "contract": (
                    "Devuelve los ficheros de instrucciones que aplican a `cwd`, en el orden en que deben aparecer en el prompt: primero el global del usuario "
                    "`home/.forja/AGENTS.md` (solo si se pasa `home` y el fichero existe), luego cada `AGENTS.md`/`FORJA.md` encontrado subiendo desde `cwd`, "
                    "devueltos desde la carpeta MÁS ALTA hasta `cwd` (el más específico al final). El recorrido se detiene tras comprobar `stop` (incluido) o en la raíz del sistema de ficheros. "
                    "`test_find_instruction_files_order` crea `home/.forja/AGENTS.md`, `repo/AGENTS.md`, `repo/pkg/AGENTS.md` y espera los contenidos `[\"global\", \"root\", \"package\"]` "
                    "al llamarla con `cwd=repo/pkg, stop=tmp_path`."
                ),
                "steps": [
                    "Empieza una lista `found` con el fichero global si `home` tiene valor y `home / \".forja\" / \"AGENTS.md\"` es un fichero.",
                    "Asigna `d = cwd.resolve()` y haz un bucle: para cada nombre de `INSTRUCTION_FILES`, si `d / name` es un fichero, añádelo a una lista `chain`.",
                    "Para el bucle cuando `d` sea igual al `stop` resuelto, o cuando `d.parent == d` (estás en la raíz); si no, pasa a `d.parent`.",
                    "`chain` está ahora de abajo arriba; inviértela para que la carpeta más alta vaya primero.",
                    "Devuelve `found + reversed chain` (es decir, `found` más `chain` invertida).",
                ],
                "gotchas": [
                    "Resuelve TANTO `cwd` como `stop` antes de comparar. En macOS `tmp_path` está bajo `/var`, que es un symlink a `/private/var`: comparar una ruta resuelta con otra sin resolver nunca coincide, y llegas hasta `/`.",
                    "Detección de la raíz: `d.parent == d` también funciona en Windows (`C:\\` es su propio padre). No compares con `Path(\"/\")`.",
                    "Comprueba `stop` DESPUÉS de recoger los ficheros de esa carpeta: `stop` es inclusivo.",
                    "El fichero global va primero, antes de la cadena invertida, no mezclado con ella.",
                ],
                "hints": [
                    "Es un recorrido `while True` desde `cwd` hasta la raíz, recogiendo ficheros, y luego una inversión.",
                    "Recoge de abajo arriba (lo natural al subir) e invierte una vez al final, en lugar de insertar en el índice 0.",
                    "Esqueleto:\n```python\nfound = []\nif home and (home / \".forja\" / \"AGENTS.md\").is_file():\n    found.append(...)\nchain, d = [], cwd.resolve()\nwhile True:\n    # collect INSTRUCTION_FILES present in d\n    if ... or d.parent == d:   # reached stop (resolved) or root\n        break\n    d = d.parent\nreturn found + ...\n```",
                ],
                "test": "python -m pytest tests/test_l06_context.py -k find_instruction -v",
            },
            "06.2": {
                "where": "`forja/context.py` · `build_system_prompt(ws, mode, model, home=None, skills_catalog=\"\", extra=None) -> str`",
                "contract": (
                    "Devuelve el system prompt completo: las capas no vacías unidas con una línea en blanco (`\"\\n\\n\"`), en este orden: `BASE_PROMPT`; "
                    "`MODE_REMINDERS[mode]`; un bloque por fichero de `find_instruction_files(ws.root, home=home)`, cada uno con una cabecera `## ... instructions` seguida del contenido del fichero; "
                    "`skills_catalog` si no está vacío; cada cadena no vacía de `extra` (el harness pasa aquí la lista de tareas); y por último un bloque `## Environment` con el directorio de trabajo "
                    "(`ws.root`), `git_info(ws.root)`, el SO (`platform.system()`), la fecha (`date.today().isoformat()`) y `model`. "
                    "`test_system_prompt_layers` comprueba que están presentes `You are Forja`, `PLAN mode`, `half-up` (de `playground/AGENTS.md`), `## Skills`, `## Extra`, el nombre del modelo y `str(project)`, "
                    "y que `PLAN mode` va antes que `half-up`, que a su vez va antes que `## Environment`."
                ),
                "steps": [
                    "Empieza una lista `layers` con `BASE_PROMPT` y el recordatorio de `mode` (`MODE_REMINDERS.get(mode, \"\")` es seguro).",
                    "Para cada fichero de `find_instruction_files(ws.root, home=home)`, añade `\"## <label>\\n<content>\"`. Una etiqueta útil: `User global instructions` para el fichero bajo `home/.forja`, `Project instructions (<relative path>)` para los demás.",
                    "Añade `skills_catalog` si no está vacío y luego cada elemento no vacío de `extra or []`.",
                    "Añade el bloque `## Environment` (directorio, `git_info(ws.root)`, SO, fecha, modelo) como una única cadena multilínea.",
                    "Devuelve `\"\\n\\n\".join(...)` sobre las capas no vacías.",
                ],
                "gotchas": [
                    "Lee los ficheros con `read_text(encoding=\"utf-8\")`. En Windows la codificación por defecto es cp1252 y los AGENTS.md con tildes o `—` lanzan `UnicodeDecodeError` o salen con caracteres corruptos.",
                    "`extra` puede ser `None` y puede contener `\"\"` (el test pasa `[\"## Extra\", \"\"]`, el harness pasa `[\"\"]` cuando no hay tareas): filtra las cadenas vacías para no tener secciones en blanco sueltas.",
                    "Llama a `find_instruction_files` con `ws.root`, no con `Path.cwd()`: con `forja --cwd playground` el cwd del proceso es la raíz del repo.",
                    "`f.relative_to(ws.root)` lanza `ValueError` para ficheros por encima del workspace o en home: protégete con `f.is_relative_to(ws.root)`.",
                    "El test necesita `str(project)` en el prompt: imprime `ws.root` tal cual (absoluto), no `.`.",
                ],
                "hints": [
                    "Construye una lista de cadenas en orden y únela una sola vez; no concatenes con `+=` olvidando los separadores.",
                    "El harness ya te da todo: `ws.root`, `mode`, `model`, `skills_catalog`, `extra`. Tú solo añades los ficheros y el entorno.",
                    "Esqueleto:\n```python\nlayers = [BASE_PROMPT, MODE_REMINDERS.get(mode, \"\")]\nfor f in find_instruction_files(ws.root, home=home):\n    label = ...   # global vs project (relative path)\n    layers.append(f\"## {label}\\n{...}\")\n# skills_catalog, extra (non-empty only)\nlayers.append(f\"## Environment\\nWorking directory: {ws.root}\\n{git_info(ws.root)}\\n...\")\nreturn \"\\n\\n\".join(x for x in layers if x)\n```",
                ],
                "test": "python -m pytest tests/test_l06_context.py -k system_prompt -v",
            },
            "06.3": {
                "where": "`forja/context.py` · `expand_mentions(text, ws, max_chars=20_000) -> str`",
                "contract": (
                    "Encuentra menciones `@path` con `MENTION_RE` (ya ignora direcciones de e-mail como `joe@mail.com`). Para cada mención ÚNICA que se resuelve dentro del "
                    "workspace a un FICHERO existente: léelo (como máximo `max_chars` caracteres), llama a `ws.mark_read(p)` y añade un bloque "
                    "`<file path=\"<relative path>\">\\n<content>\\n</file>` al FINAL del texto original (el texto en sí no se modifica). "
                    "Las menciones fuera del sandbox (`@../../etc/passwd` -> `PermissionError`), los ficheros inexistentes (`@nobody`) y las carpetas se omiten en silencio. "
                    "Sin ninguna mención válida, devuelve `text` sin cambios (`expand_mentions(\"no mentions\", ws) == \"no mentions\"`). "
                    "`test_expand_mentions` espera exactamente un bloque `<file` con `path=\"invoices/dates.py\"`, el contenido del fichero (`def due_date`) y la ruta en `ws.read_state`."
                ),
                "steps": [
                    "Obtén las menciones con `MENTION_RE.findall(text)` y deduplica conservando el orden (`dict.fromkeys(...)`).",
                    "Quita la puntuación final de cada mención: la regex se detiene en `,` pero admite `.`, así que `look at @src/app.py.` captura `src/app.py.`. Usa `ref.rstrip(\".,;:\")`.",
                    "Resuelve con `ws.resolve(ref)` dentro de `try/except PermissionError: continue`; omítela si `not p.is_file()`.",
                    "Lee con `read_text(encoding=\"utf-8\", errors=\"replace\")`, corta a `max_chars` (añade una marca `…[truncated]`), `ws.mark_read(p)`, y construye el bloque `<file path=...>`.",
                    "Si tienes bloques, devuelve `text + \"\\n\\n\" + \"\\n\\n\".join(blocks)`; si no, devuelve `text`.",
                ],
                "gotchas": [
                    "Una mención al final de una frase (`look at @src/app.py.`) captura el punto final: quita los `.,;:` finales o el fichero no se encuentra.",
                    "Usa `ws.rel(p)` para el atributo `path`: ya devuelve una ruta POSIX (`invoices/dates.py`) también en Windows, que es lo que busca el test.",
                    "Llama a `ws.mark_read(p)` por cada fichero incluido: el test comprueba `ws.read_state`, y en el CLI permite al modelo hacer `edit_file` directamente sin un viaje de ida y vuelta con `read_file`.",
                    "No sustituyas la mención dentro del texto: mantén intacta la frase del usuario y añade los bloques detrás.",
                    "No dejes que una mención mala aborte las demás: `continue`, nunca `return` dentro del bucle.",
                ],
                "hints": [
                    "Recorre las menciones, filtra las válidas, construye una lista de bloques y añádelos al final.",
                    "El sandbox ya está hecho (lab 02): que `ws.resolve` lance `PermissionError` es tu filtro para las rutas `../`.",
                    "Esqueleto:\n```python\nblocks = []\nfor ref in dict.fromkeys(MENTION_RE.findall(text)):\n    try:\n        p = ws.resolve(ref.rstrip(\".,;:\"))\n    except PermissionError:\n        continue\n    # skip non-files; read (cap max_chars); ws.mark_read(p)\n    blocks.append(f'<file path=\"{...}\">\\n{...}\\n</file>')\nreturn ...  # text unchanged if no blocks\n```",
                ],
                "test": "python -m pytest tests/test_l06_context.py -k mentions -v",
            },
        },
        "try_it": [
            "Resetea primero: `python scripts/tasks.py reset`. Arranca `forja --cwd playground`. La nota tenue `context: lab 06 pending ...` YA NO debería aparecer.",
            "Pide: `review @invoices/amounts.py and tell me whether it follows AGENTS.md`. Esperado: NINGUNA línea `⏺ Read invoices/amounts.py` (el fichero llegó con el mensaje) y una respuesta que cite las reglas: redondeo half-up con `decimal`, no `round()` sobre floats, no cambiar los tests.",
            "Pregunta sin mencionar las reglas: `what are the rules of this project?`. El agente responde a partir de `AGENTS.md` sin llamar a ninguna herramienta.",
            "Escribe `/context` antes y después de un mensaje con una mención `@` grande: el número de tokens crece aproximadamente el tamaño del fichero / 4.",
            "Opcional: crea `~/.forja/AGENTS.md` (Windows: `%USERPROFILE%\\.forja\\AGENTS.md`) con `Always answer in Spanish.`; reinicia Forja y saluda. Cambia el idioma de la respuesta: la capa global funciona.",
        ],
        "troubleshooting": [
            ["`test_find_instruction_files_order` devuelve `['global', 'package', 'root']`",
             "No invertiste el recorrido (o invertiste también el fichero global) → recoge de abajo arriba, invierte solo la cadena y luego antepón el fichero global."],
            ["`test_find_instruction_files_order` encuentra ficheros de más o nunca se detiene (macOS)",
             "Comparas `cwd` resuelto con `stop` sin resolver (`/var` frente a `/private/var`) → resuelve también `stop`."],
            ["`test_system_prompt_layers` falla en `half-up` in sp",
             "No se incluyó el AGENTS.md del playground → llama a `find_instruction_files(ws.root, home=home)` y añade el CONTENIDO del fichero, no solo su ruta."],
            ["`UnicodeDecodeError: 'charmap' codec can't decode` (Windows)",
             "`read_text()` sin encoding → `read_text(encoding=\"utf-8\")` (y `errors=\"replace\"` para los ficheros mencionados)."],
            ["`test_expand_mentions`: `out.count(\"<file\") == 2` o un fallo con `@../../etc/passwd`",
             "Falta el `except PermissionError` o la comprobación `is_file()` → omite las menciones no válidas con `continue`."],
            ["En el CLI el agente sigue ignorando AGENTS.md",
             "Ejecutaste Forja desde otra carpeta, o el AGENTS.md no está bajo `--cwd` → arranca con `forja --cwd playground`; los modelos pequeños también pueden necesitar que se repita la regla en el prompt (menos es más: mantén AGENTS.md corto)."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 06` → 3 passed.",
            "[ ] En el CLI el agente cita las reglas de `playground/AGENTS.md` (half-up, no tocar los tests) sin que se lo digas.",
            "[ ] Una mención `@file` se responde sin una línea `⏺ Read` adicional.",
        ],
    },
    # ------------------------------------------------------------------ LAB 07
    "07": {
        "before": [
            "Abre `forja/compaction.py`. Se dan hechos: `SUMMARY_PROMPT`, `CLEARED = \"[old tool result cleared]\"`, `estimate_tokens(messages)` (~4 caracteres por token), "
            "`user_turn_starts(history)` (índices de los mensajes `user`) y `should_compact(...)` (verdadero por encima del 80% de la ventana). Tú escribes `microcompact` y `compact`.",
            "Conoce el formato del historial (chat de OpenAI): `{\"role\": \"user\", \"content\": ...}`, `{\"role\": \"assistant\", \"content\": ..., \"tool_calls\": [{\"id\", \"type\", \"function\": {\"name\", \"arguments\"}}]}`, "
            "`{\"role\": \"tool\", \"tool_call_id\": ..., \"name\": ..., \"content\": ...}`. Un mensaje assistant con `tool_calls` DEBE ir seguido de un mensaje `tool` por llamada: romper ese par hace que la API rechace la petición.",
            "Un \"turno\" empieza en un mensaje `user`. Cortar solo en los índices de `user_turn_starts(...)` es lo que garantiza que nunca separas un mensaje `tool_calls` de sus resultados.",
            "Cómo se conecta: `Forja.compact_now()` en `forja/harness.py` se ejecuta antes de cada turno: si `should_compact` → `microcompact(self.history)` (gratis); si sigue siendo demasiado grande → `compact(self.history, self.llm)` (una llamada al LLM). "
            "`/compact` llama a `compact_now(force=True)`. La llamada al LLM es `llm.chat(messages, temperature=0)` y devuelve un `ChatResponse` cuyo `.content` es el texto (en los tests, `FakeLLM` la registra en `llm.calls`).",
        ],
        "order": (
            "Primero el 07.1: es un bucle puro que modifica en sitio, sin LLM, y te enseña el punto de corte (`starts[-keep_recent_turns]`) que reutiliza el 07.2. "
            "Luego el 07.2. `test_harness_autocompacts` (se ejecuta con el 07.2) ejercita ambos a través del harness con una ventana diminuta, así que solo pasa cuando los dos están bien."
        ),
        "todos": {
            "07.1": {
                "where": "`forja/compaction.py` · `microcompact(history, keep_recent_turns=2, min_chars=500) -> int`",
                "contract": (
                    "Modifica `history` EN SITIO: cada mensaje `tool` situado ANTES del inicio de los últimos `keep_recent_turns` turnos, cuyo contenido tenga al menos "
                    "`min_chars` caracteres y no sea ya `CLEARED`, pasa a `content = CLEARED`. Devuelve cuántos mensajes se limpiaron. Si hay "
                    "`keep_recent_turns` turnos o menos, no hace nada y devuelve 0. Los mensajes nunca se eliminan ni se reordenan, así que los pares siguen siendo válidos. "
                    "`test_microcompact` (4 turnos, salidas de herramientas de 2000 caracteres) espera 2 limpiados (turnos 0 y 1), los dos últimos intactos, tokens por debajo del 60% de antes, "
                    "y que una segunda llamada devuelva 0."
                ),
                "steps": [
                    "Calcula `starts = user_turn_starts(history)`; si `len(starts) <= keep_recent_turns`, devuelve 0.",
                    "La zona protegida empieza en `limit = starts[-keep_recent_turns]`.",
                    "Recorre `history[:limit]` (el slice es una lista nueva pero contiene los MISMOS objetos dict, así que mutarlos cambia `history`).",
                    "Para cada mensaje con rol `tool`, longitud de contenido `>= min_chars` y contenido `!= CLEARED`: ponlo a `CLEARED` y cuéntalo.",
                    "Devuelve el contador.",
                ],
                "gotchas": [
                    "Muta los dicts; no construyas una lista nueva para devolverla. La función devuelve un `int` y el harness confía en que `self.history` cambie en sitio.",
                    "Solo mensajes `tool`: nunca vacíes el contenido de user o assistant (eso es la conversación en sí).",
                    "`content` puede ser `None`: usa `len(m.get(\"content\") or \"\")`.",
                    "`>= min_chars`, no `>`: una salida de exactamente 500 caracteres cuenta.",
                ],
                "hints": [
                    "Encuentra el índice donde empieza la parte reciente; todo lo anterior es terreno libre.",
                    "`starts[-keep_recent_turns]` es el índice del primer mensaje de usuario que quieres mantener intacto.",
                    "Esqueleto:\n```python\nstarts = user_turn_starts(history)\nif len(starts) <= keep_recent_turns:\n    return 0\nlimit = ...\nn = 0\nfor m in history[:limit]:\n    if m[\"role\"] == \"tool\" and ...:   # long enough, not yet CLEARED\n        ...\nreturn n\n```",
                ],
                "test": "python -m pytest tests/test_l07_compaction.py -k microcompact -v",
            },
            "07.2": {
                "where": "`forja/compaction.py` · `compact(history, llm, keep_recent_turns=2) -> tuple[list, bool]`",
                "contract": (
                    "Si hay `keep_recent_turns` turnos o menos, devuelve `(history, False)` sin llamar al LLM. Si no, corta en `starts[-keep_recent_turns]`: "
                    "`old = history[:cut]`, `recent = history[cut:]`. Convierte `old` en texto plano (una línea por mensaje: rol y contenido; para los assistant también las herramientas llamadas "
                    "con los argumentos truncados; para los mensajes tool un resultado truncado), y llama a `llm.chat([{system: SUMMARY_PROMPT}, {user: that text}], temperature=0)`. "
                    "Devuelve `([{\"role\": \"user\", \"content\": \"[Summary of the previous session]\\n\" + summary}, {\"role\": \"assistant\", \"content\": <short ack>}, *recent], True)`. "
                    "`test_compact_keeps_pairs_and_recent` comprueba: el primer mensaje empieza por `[Summary` y contiene el resumen falso; `new[2:] == h[8:]` (los 2 últimos turnos intactos); "
                    "los pares son válidos; el texto enviado como `messages[1]` contiene `question 0` pero NO `question 3` (los turnos recientes no se resumen); `compact(history(1), llm)[1] is False`."
                ),
                "steps": [
                    "Calcula `starts`; devuelve `(history, False)` pronto cuando no hay suficiente que compactar.",
                    "Divide en `old` y `recent` en `cut = starts[-keep_recent_turns]`.",
                    "Construye una lista de líneas de texto a partir de `old`: para los mensajes `tool` algo como `[result of <name>] <first 1500 chars>`; para los demás `<role>: <content>` más `[tools: name(args…)]` sacado de `m.get(\"tool_calls\", [])` → `t[\"function\"][\"name\"]` / `[\"arguments\"]`.",
                    "Une las líneas y limita el total (quédate con el FINAL, p. ej. los últimos 60.000 caracteres: el trabajo antiguo más reciente es el que más importa).",
                    "Llama a `llm.chat([...system SUMMARY_PROMPT..., ...user transcript...], temperature=0)` y toma `.content or \"\"`.",
                    "Devuelve el nuevo historial: el resumen como mensaje `user`, un acuse de recibo `assistant` (p. ej. `Understood. I'll continue from here.`) y luego `*recent`; y `True`.",
                ],
                "gotchas": [
                    "El nuevo historial debe empezar con `user` y luego `assistant`: dos mensajes `user` seguidos (resumen + siguiente turno) o un mensaje `tool` huérfano rompen algunas plantillas de chat. El acuse de recibo arregla la alternancia.",
                    "Nunca resumas los turnos recientes: el test comprueba que `question 3` no está en el prompt enviado al modelo.",
                    "Mantén `recent` tal cual (`new[2:] == h[8:]`): no copies, limpies ni vuelvas a truncar esos mensajes.",
                    "`content` puede ser `None` (mensajes assistant con solo llamadas a herramientas): usa `m.get(\"content\") or \"\"` al formatear.",
                    "El prompt de resumen va como `messages[0]` con rol `system` y la transcripción como `messages[1]` con rol `user`: el test lee `llm.calls[0][\"messages\"][1][\"content\"]`.",
                ],
                "hints": [
                    "El mismo punto de corte que en el 07.1, pero en lugar de vaciar sustituyes toda la parte antigua por un único resumen.",
                    "El LLM nunca ve los dicts de mensajes en bruto: primero los aplanas a texto, que es también donde truncas los resultados grandes de las herramientas.",
                    "Esqueleto:\n```python\nstarts = user_turn_starts(history)\nif len(starts) <= keep_recent_turns:\n    return history, False\ncut = starts[-keep_recent_turns]\nold, recent = history[:cut], history[cut:]\nlines = []\nfor m in old:\n    ...  # tool -> truncated result; others -> role: content [tools: ...]\nsummary = llm.chat([...], temperature=0).content or \"\"\nreturn [ ...summary user msg..., ...assistant ack..., *recent ], True\n```",
                ],
                "test": "python -m pytest tests/test_l07_compaction.py -k \"keeps_pairs or autocompacts\" -v",
            },
        },
        "try_it": [
            "`python scripts/tasks.py reset` y luego `forja --cwd playground`. Pide: `read every file in the project and summarise them` (aprueba con `y` si pregunta; las lecturas no deberían preguntar).",
            "Escribe `/context`: algo como `~6000 tokens of 32768 (N messages)`. Haz dos preguntas cortas más (p. ej. `which function computes VAT?`, `where is the due date logic?`) para tener al menos 3 turnos: la compactación siempre conserva los 2 últimos.",
            "Escribe `/compact`. Esperado: `compacted: summary + recent turns (~N tokens)`. Si solo tenías 1–2 turnos obtienes `nothing to compact` (o `microcompaction: N old outputs cleared`): es el comportamiento correcto.",
            "Vuelve a escribir `/context`: el número baja claramente. Pregunta `what were we doing?`: el agente sigue conociendo los ficheros y el objetivo (los lee del resumen).",
            "Opcional: crea `playground/.forja/settings.json` con `{\"contextWindow\": 6000}`, reinicia y trabaja unos cuantos turnos: aparece automáticamente una nota tenue `· microcompaction: ...` o `· compacted: ...` antes de un turno. Borra el fichero después.",
        ],
        "troubleshooting": [
            ["`test_microcompact`: `assert 4 == 2` (se limpia todo)",
             "Recorres el historial entero → solo `history[:starts[-keep_recent_turns]]`."],
            ["`test_microcompact`: la segunda llamada devuelve 2 en lugar de 0, o el contador es correcto pero los contenidos no cambian",
             "No compruebas `!= CLEARED`, o modificas una copia (`dict(m)`) → muta los dicts originales y omite los ya limpiados."],
            ["`test_compact_keeps_pairs_and_recent`: se encuentra `question 3` en el prompt",
             "Resumes el historial entero → solo `old = history[:cut]`."],
            ["`test_compact_keeps_pairs_and_recent`: `KeyError: 'tool_calls'` o `TypeError: can only concatenate str (not \"NoneType\")`",
             "Usa `m.get(\"tool_calls\", [])` y `m.get(\"content\") or \"\"`."],
            ["`test_harness_autocompacts`: falla `assert any(\"compact\" in n for n in app.notes)`",
             "`compact` devuelve `(history, False)` demasiado a menudo, o el 07.1 lanza una excepción → comprueba primero ambas funciones con el test del 07.1; el harness solo añade la nota cuando se compactó algo."],
            ["Modelo real: tras `/compact` el agente olvida qué ficheros cambió",
             "La compactación pierde información → asegúrate de que el texto de tu transcripción incluye los nombres de las herramientas y sus argumentos (¡las rutas!), no solo los contenidos; mídelo más adelante con evals (lab 12)."],
            ["Modelo real: `/compact` tarda mucho",
             "Es una llamada completa al LLM sobre hasta 60k caracteres → normal en un portátil; un límite menor en la transcripción lo hace más rápido."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 07` → 3 passed.",
            "[ ] `/context` baja tras `/compact` y el agente sigue sabiendo lo que estaba haciendo.",
        ],
    },
    # ------------------------------------------------------------------ LAB 08
    "08": {
        "before": [
            "Abre `forja/planning.py`. Se dan hechos: `TodoItem` (modelo pydantic con `content: str` y `status: \"pending\" | \"in_progress\" | \"completed\"`, por defecto `pending`), "
            "`ICON` y `TodoStore` con `.items` y `.render()` (una línea `☐/▶/☑ content` por elemento, o `(empty list)`). Tú escribes los CUERPOS de dos herramientas, dentro de funciones factoría.",
            "Ambas herramientas se crean con `@tool(risk=\"read\")` del lab 02: el docstring y las anotaciones de tipo se convierten en el JSON schema que lee el modelo, así que no los cambies. "
            "Lanzar una excepción dentro de una herramienta es la forma correcta de rechazar una entrada incorrecta: `ToolRegistry.execute` la convierte en `ERROR in '<tool>': ValueError: <message>` y el modelo puede corregirse.",
            "Los argumentos llegan a tu función DESPUÉS de la validación de pydantic y de `model_dump()`, así que `todos` normalmente llega como una lista de dicts simples; pero el código también puede llamar a la función con objetos `TodoItem`. Acepta ambos (`TodoItem.model_validate(d)`).",
            "Cómo se conecta: `Forja._build_registry` registra `make_todo_tool(self.todos)` y `make_exit_plan_tool(self._approve_plan, lambda: self.set_mode(\"default\"))`. "
            "La lista de tareas vuelve al system prompt en cada paso mediante `extra` en `build_system_prompt` (lab 06). El modo plan es de solo lectura porque `permissions.decide` (lab 04) deniega las herramientas que no son de lectura en `plan`, no porque el modelo se porte bien.",
        ],
        "order": (
            "Primero el 08.1 (lógica de validación, totalmente cubierta por `test_todo_write_validation`), luego el 08.2 (corto). `test_plan_mode_flow`, seleccionado con el 08.2, "
            "conduce un turno completo en modo plan a través del harness y necesita que el 08.1, el 08.2, el lab 04 (deny en modo plan) y el lab 06 (las capas del prompt) funcionen."
        ),
        "todos": {
            "08.1": {
                "where": "`forja/planning.py` · `make_todo_tool(store)` → interna `todo_write(todos: list[TodoItem]) -> str`",
                "contract": (
                    "Sustituye la lista ENTERA de `store.items` por los elementos recibidos, tras validar: cada elemento se convierte a `TodoItem`; más de un `in_progress` → `ValueError` "
                    "(su mensaje debe contener `one task`, p. ej. `only one task can be in_progress at a time`); un elemento con `content` vacío/en blanco → `ValueError`. "
                    "La validación ocurre ANTES de tocar el store: si hay error, la lista anterior se mantiene. Devuelve `\"List updated (X/N completed):\\n\" + store.render()` "
                    "(X = completados, N = total). `test_todo_write_validation` espera `1/3` en la salida, las líneas renderizadas `[\"☑ read\", \"▶ edit\", \"☐ tests\"]`, "
                    "y tras la llamada con doble `in_progress`: `ok` falso, `one task` en la salida y todavía 3 elementos en el store."
                ),
                "steps": [
                    "Convierte: `items = [t if isinstance(t, TodoItem) else TodoItem.model_validate(t) for t in todos]`.",
                    "Cuenta los elementos con `status == \"in_progress\"`; si hay más de 1, lanza `ValueError` con un mensaje sobre el que el modelo pueda actuar.",
                    "Si algún elemento cumple `not t.content.strip()`, lanza `ValueError`.",
                    "Solo ahora asigna `store.items = items`.",
                    "Cuenta los elementos completados y devuelve la línea de cabecera más `store.render()`.",
                ],
                "gotchas": [
                    "Asigna `store.items` solo cuando pasen todas las comprobaciones: el test comprueba que una llamada rechazada deja los 3 elementos antiguos.",
                    "El texto del error debe contener `one task` (el test hace `\"one task\" in two.output`).",
                    "Un `content` con solo espacios también está vacío: usa `.strip()`.",
                    "Lanza la excepción, no devuelvas una cadena de error: una cadena devuelta cuenta como éxito (`ok=True`) y el test espera `not two.ok`.",
                    "Mantén la forma de factoría: `todo_write` debe seguir siendo una función interna que captura `store` en su closure y se devuelve al final.",
                ],
                "hints": [
                    "Tres fases: normalizar, validar, confirmar. Confirmar al final.",
                    "`sum(t.status == \"in_progress\" for t in items)` cuenta booleanos.",
                    "Esqueleto:\n```python\nitems = [...]               # dict or TodoItem -> TodoItem\nif sum(...) > 1:\n    raise ValueError(\"only one task can be in_progress at a time\")\nif any(...):                # blank content\n    raise ValueError(...)\nstore.items = items\ndone = ...\nreturn f\"List updated ({done}/{len(items)} completed):\\n{store.render()}\"\n```",
                ],
                "test": "python -m pytest tests/test_l08_planning.py -k todo_write -v",
            },
            "08.2": {
                "where": "`forja/planning.py` · `make_exit_plan_tool(approve, on_approved)` → interna `exit_plan_mode(plan: str) -> str`",
                "contract": (
                    "`plan` vacío/en blanco → `ValueError`. Si no, llama a `approve(plan)` exactamente una vez (en el CLI muestra el plan como Markdown y pregunta `Approve the plan and start? [y/N]`; "
                    "en headless o en los tests es una función que devuelve `bool`). Si se aprueba: llama a `on_approved()` (el harness cambia al modo `default`) y devuelve un texto que contenga `APPROVED` "
                    "y que diga al modelo que ya no está en modo plan y que debe implementar el plan paso a paso y verificarlo. Si se rechaza: NO llames a `on_approved` y devuelve un texto que contenga "
                    "`REJECTED` indicando que sigue en modo plan y que debe preguntar qué cambiar o proponer una alternativa. `test_exit_plan_tool` comprueba ambas ramas y que el callback solo se ejecutó al aprobar; "
                    "`test_plan_mode_flow` comprueba que tras la aprobación `app.mode == \"default\"`."
                ),
                "steps": [
                    "Valida `plan.strip()`; lanza `ValueError` si está vacío.",
                    "Llama a `approve(plan)` una vez y guarda el booleano.",
                    "Si es verdadero: llama a `on_approved()` y luego devuelve la instrucción APPROVED.",
                    "Si es falso: devuelve la instrucción REJECTED.",
                ],
                "gotchas": [
                    "Las palabras `APPROVED` y `REJECTED` deben ir en mayúsculas en el texto: los tests las buscan, y las mayúsculas también ayudan a los modelos pequeños a notar el cambio de estado.",
                    "Llama a `on_approved()` solo en la rama aprobada, y solo una vez.",
                    "El texto devuelto es una instrucción para el MODELO, no para el usuario: di claramente qué hacer a continuación (implementar + verificar, o preguntar/proponer). Un `ok` vago hace que los modelos pequeños replanifiquen eternamente.",
                    "No cambies el modo tú aquí: la herramienta no conoce el harness; lo hace el callback `on_approved`.",
                ],
                "hints": [
                    "Es una cláusula de guarda más un if/else alrededor de un callback.",
                    "Los dos callbacks se inyectan para que la herramienta se pueda probar sin UI ni harness.",
                    "Esqueleto:\n```python\nif not plan.strip():\n    raise ValueError(...)\nif approve(plan):\n    ...                     # callback\n    return \"The user APPROVED the plan. ...\"\nreturn \"The user REJECTED the plan. ...\"\n```",
                ],
                "test": "python -m pytest tests/test_l08_planning.py -k \"exit_plan or plan_mode_flow\" -v",
            },
        },
        "try_it": [
            "`python scripts/tasks.py reset` y luego `forja --cwd playground --mode plan`. El prompt muestra `plan ›`.",
            "Pide: `add percentage discounts to invoices (before VAT) with tests`. Esperado: solo acciones de lectura (`⏺ Read ...`, `⏺ Grep ...`, `⏺ Glob ...`). Si el modelo intenta una edición verás un `⎿ DENIED (plan mode: read-only) ...` en rojo y volverá a investigar.",
            "Aparece un panel magenta `Proposed plan` con los ficheros a tocar, los cambios y cómo verificarlo, seguido de `Approve the plan and start? [y/N] >`. Responde `n` una vez: el modelo recibe `REJECTED` y pregunta qué cambiar. Dile qué ajustar y aprueba con `y` la siguiente vez.",
            "Tras `y`: el modo del REPL pasa a `default` (el siguiente prompt muestra `default ›`), las ediciones ahora piden aprobación y ves líneas `⏺ Todos (N)` a medida que el agente marca tareas. Escribe `/todos` cuando quieras: `☑ ...`, `▶ ...`, `☐ ...`.",
            "Al final el agente ejecuta los tests; compruébalo tú con `cd playground` y `python -m pytest -q`. Luego `python scripts/tasks.py reset` para limpiar.",
        ],
        "troubleshooting": [
            ["`test_todo_write_validation`: falla `assert len(store.items) == 3` (es 2)",
             "Asignaste `store.items` antes de validar → valida primero, confirma al final."],
            ["`test_todo_write_validation`: falla `not two.ok`",
             "Devolviste una cadena de error en lugar de lanzar una excepción → `raise ValueError(...)`."],
            ["`AttributeError: 'dict' object has no attribute 'status'`",
             "El registry pasa dicts → convierte con `TodoItem.model_validate(d)` (deja las instancias de `TodoItem` como están)."],
            ["`test_plan_mode_flow`: falla `assert \"PLAN mode\" in llm.calls[0][\"messages\"][0][\"content\"]`",
             "El lab 06 no está hecho, así que el harness usa `FALLBACK_PROMPT` → termina el 06.2 (o ejecuta `python scripts/tasks.py catchup 07`)."],
            ["`test_plan_mode_flow`: el primer resultado de herramienta no es `DENIED`",
             "El `decide` del lab 04 no deniega las herramientas que no son de lectura en modo plan → revisa el TODO 04.x; el mensaje debe contener `plan mode`."],
            ["El modelo real nunca llama a `exit_plan_mode` y se limita a escribir el plan como texto",
             "Los modelos pequeños hacen eso → díselo explícitamente: `when you have the plan, present it with exit_plan_mode`; o prueba un modelo más potente."],
            ["El modelo real pone varias tareas `in_progress` y entra en bucle con el error",
             "Haz que el mensaje del `ValueError` sea accionable (`only one task can be in_progress at a time`); el modelo lo lee y reintenta con una sola."],
            ["En headless (`forja -p ... --mode plan`) siempre se rechaza el plan",
             "Sin usuario, `plan_approver` es `None` → es lo esperado; el modo plan está pensado para uso interactivo."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 08` → 3 passed.",
            "[ ] En modo plan el agente investiga, presenta un plan con `exit_plan_mode` y, tras `y`, lo ejecuta marcando tareas (`/todos` muestra el progreso).",
            "[ ] Viste al menos un `DENIED (plan mode: read-only)` o un `REJECTED` y el agente se recuperó.",
        ],
    },
}
