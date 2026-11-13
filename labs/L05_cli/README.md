# Lab 05 · La CLI: tu agente de terminal

🇬🇧 [English](README.en.md) · Día 1 · 14:00–15:00

**Objetivo:** Convertir el harness en una herramienta agradable: streaming, resumen de acciones, diffs, aprobaciones y comandos slash.

## Conceptos
- **La experiencia es parte del producto:** el usuario tiene que ver QUÉ hace el agente (una línea por tool), CÓMO cambia el código (diff) y poder pararlo (Ctrl+C) o corregirlo.
- **Aprobaciones claras:** qué se va a ejecutar, por qué se pregunta (motivo de la decisión) y tres respuestas: `y` (sí), `n` (no), `a` (siempre).
- **Comandos slash:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. Operan sobre el harness sin pasar por el modelo.
- **Headless:** `forja -p "…"` ejecuta y sale: scripts, CI y evals (lab 12). Sin usuario, lo que pide permiso se deniega.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: una línea legible por tool call |
| 05.2 | `forja/cli.py` | diff_styles: colorear el diff |
| 05.3 | `forja/cli.py` | ask_approval: y / n / a (sí / no / siempre) |
| 05.4 | `forja/cli.py` | handle_slash: comandos slash |

## Antes de empezar
- Abre `forja/cli.py`. Casi todo lo que contiene es fontanería de UI que ya se te da hecha (`RichEvents`, `repl`, `main`, `doctor`). Solo escribes cuatro funciones pequeñas: `summarize_call`, `diff_styles`, `ask_approval` y `handle_slash`. Lee primero `RichEvents.on_tool_start` / `on_tool_end`: muestran exactamente dónde se llaman tus funciones.
- La UI llama a tus funciones a través de `_safe(...)`, que solo se traga `NotImplementedError`. Cualquier otra excepción (p. ej. un `KeyError` porque el modelo omitió un argumento) rompería el turno, así que sé defensivo con `dict.get`.
- Librerías usadas: `rich` (`console.print`, `Panel`, `Text`), ya importadas. No necesitas aprender rich a fondo: `console.print(Panel(Text("..."), title="...", border_style="yellow"))` es todo lo que necesita el 05.3.
- Cómo se conecta con el harness: `Forja.gate` (en `forja/harness.py`) llama a `self.approver(tool, args, why)` cuando los permisos responden `ask`; `build_app` pasa tu `ask_approval` como ese approver. `handle_slash` recibe el objeto `Forja`, así que lee los atributos que usa: `app.mode`, `app.set_mode()`, `app.registry.tools`, `app.todos`, `app.context_tokens()`, `app.compact_now()`, `app.usage`, `app.undo()`, `app.transcript.folder`, `app.history`, `app.settings.context_window`.
- Este lab termina con el **hito del día 1** (ver la sección del hito): tu propio agente arregla los 3 tests que fallan en `playground/`. Resérvate 15 minutos para ello.

## Paso a paso
Haz primero el 05.2 (5 minutos, lógica pura de cadenas, da confianza), luego el 05.1 (formateo de cadenas con muchos casos, y el 05.3 lo reutiliza), después el 05.3 (mínimo una vez existe el 05.1), y termina con el 05.4, que es el más largo y requiere una lectura rápida de `Forja` en `forja/harness.py`. Ejecuta el test de cada TODO sobre la marcha; luego ejecuta el lab completo con `python scripts/tasks.py test 05` y pasa al hito.

### TODO 05.1 · `forja/cli.py` · `summarize_call(name, args, width=100) -> str`

**Qué debe hacer:** Recibe el nombre de la herramienta y el dict de argumentos (en bruto, posiblemente incompleto) que envió el modelo. Devuelve UNA línea, de como máximo `width` caracteres. Formatos exactos que comprueba `test_summarize_call`:
- `read_file` -> `Read a.py`; con `offset` distinto de 1 -> `Read a.py (from line 50)`
- `write_file` -> `Write n.md (2 lines)` (número de líneas de `content`)
- `edit_file` -> `Edit path`
- `bash` -> `$ pytest -q` (el comando, con los espacios colapsados)
- `grep` -> `Grep 'def x' in src (*.py)` (path por defecto `.`; ` (include)` solo si include tiene valor)
- `glob` -> `Glob pattern`
- `task` -> `Task[explore] find VAT` (`subagent_type` por defecto `explore`)
- `todo_write` -> `Todos (N)` (número de elementos)
- cualquier otra -> `name(k=v, k2=v2)`, p. ej. `mcp__x__y(id=3)`
Toda secuencia de espacios en blanco (espacios, saltos de línea) se convierte en un único espacio. Si la línea supera `width`, córtala para que el resultado tenga exactamente `width` caracteres, terminando en `…`.

**Pasos:**
1. Ramifica según `name` con una cadena `if/elif` y construye una cadena `s` para cada herramienta conocida, leyendo los argumentos con `args.get(key, default)`.
2. Para `read_file`, empieza con `Read <path>` y añade ` (from line N)` solo cuando `args.get("offset", 1) != 1`.
3. Para `write_file`, cuenta las líneas con `str(content).splitlines()`; para `grep`, añade el sufijo ` (<include>)` solo cuando include sea truthy.
4. Para el caso por defecto, une pares `f"{k}={v}"` con `", "` dentro de `name(...)` (opcionalmente recorta los valores largos a ~30 caracteres cada uno).
5. Colapsa los espacios de la cadena final: `" ".join(s.split())`.
6. Trunca al final: si `len(s) > width`, quédate con los primeros `width - 1` caracteres y añade `…`.

**Cuidado con:**
- Colapsa los espacios ANTES de truncar; si no, la comprobación de longitud usa la cadena equivocada (`test_summarize_call` comprueba `len(...) == 50` con `width=50`).
- El corte debe dar exactamente `width` caracteres incluyendo el `…` (un carácter), ni `width + 1` ni `...` (tres puntos).
- `args` viene directamente del JSON del modelo (sin validar): pueden faltar claves. Usa `.get()` en todas partes; un `KeyError` aquí rompe el turno.
- `bash` con `"pytest  -q\n"` debe convertirse en `$ pytest -q`: los espacios dobles y el salto de línea final desaparecen.

<details><summary>💡 Pista 1</summary>

Piénsalo como una tabla de 9 formatos más dos pasos de postprocesado (colapsar, truncar) aplicados a lo que hayas construido.

</details>

<details><summary>💡 Pista 2</summary>

Los valores por defecto importan para las cadenas esperadas: path de grep `'.'`, tipo de task `'explore'`, offset de read `1`, todos `[]`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
if name == "read_file":
    s = f"Read {args.get('path')}"
    # if offset != 1: append " (from line N)"
elif name == "bash":
    s = ...
# elif ... write_file / edit_file / grep / glob / task / todo_write
else:
    s = f"{name}(...)"   # k=v pairs
s = ...                  # collapse whitespace
return ...               # truncate to width with '…'
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k summarize -v
```

### TODO 05.2 · `forja/cli.py` · `diff_styles(diff: str) -> list[tuple[str, str]]`

**Qué debe hacer:** Recibe un diff unificado como una sola cadena (el `diff` que `write_file`/`edit_file` ponen en `ToolResult.meta`). Devuelve una tupla `(line, style)` por línea, en orden, con el texto de la línea sin cambios (sin salto de línea). Estilos: `'+++'` o `'---'` -> `'bold'`; `'@@'` -> `'cyan'`; `'+'` -> `'green'`; `'-'` -> `'red'`; todo lo demás -> `'dim'`. `test_diff_styles` espera `["bold", "bold", "cyan", "red", "green", "dim"]` para un diff de 6 líneas.

**Pasos:**
1. Divide el diff en líneas con `str.splitlines()`.
2. Para cada línea, prueba los prefijos del más específico al menos específico: cabeceras (`+++`, `---`), luego hunk (`@@`), luego `+` y luego `-`.
3. Añade `(line, style)` a la lista de salida; el estilo por defecto es `dim`.
4. Devuelve la lista (un diff vacío da `[]`).

**Cuidado con:**
- El orden importa: `'--- a/x'` también empieza por `'-'`. Si pruebas `'-'` primero, las cabeceras salen en rojo y el test falla.
- `str.startswith` acepta una tupla: `line.startswith(("+++", "---"))`.
- No hagas strip de las líneas: una línea de contexto empieza por un espacio y la UI la imprime tal cual.

<details><summary>💡 Pista 1</summary>

Es un bucle con una cadena `if/elif` sobre prefijos.

</details>

<details><summary>💡 Pista 2</summary>

Comprueba los prefijos de 3 caracteres antes que los de 1 carácter.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
out = []
for line in diff.splitlines():
    if line.startswith(("+++", "---")):
        style = "bold"
    # elif '@@' ... elif '+' ... elif '-' ...
    else:
        style = "dim"
    out.append(...)
return out
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k diff_styles -v
```

### TODO 05.3 · `forja/cli.py` · `ask_approval(tool, args, reason, read=input) -> Approval`

**Qué debe hacer:** La llama `Forja.gate` cuando la decisión de permisos es `ask`. Muestra al usuario lo que se va a ejecutar (un `Panel` con `summarize_call(tool.name, args, ...)`) y por qué se pregunta (`reason`, p. ej. `requires approval`). Lee UNA respuesta llamando a `read(prompt_text)`. Devuelve la cadena literal `"yes"` para `y`/`yes`, `"always"` para `a`/`always` y `"no"` para cualquier otra cosa, incluida una respuesta vacía. `test_ask_approval` pasa `read=lambda _: "y"`, `"a"` y `""`. Con `always`, el harness (no tú) añade una regla mediante `permissions.suggest_rule`.

**Pasos:**
1. Construye el resumen con `summarize_call(tool.name, args, width=...)`; usa un ancho grande (p. ej. 400) para que el usuario vea el comando completo antes de aprobarlo.
2. Imprímelo con `console.print(Panel(Text(summary), title=..., border_style="yellow"))`; pon `tool.name` y `reason` en el título.
3. Llama a `read("  [y]es / [n]o / [a]lways this session > ")` y normaliza la respuesta con `str(...).strip().lower()`.
4. Traduce la respuesta a `"yes"`, `"always"` o `"no"` y devuélvela.

**Cuidado con:**
- Usa el parámetro `read`, nunca `input()` ni `console.input()` directamente: los tests inyectan `read`, y bajo pytest un `input()` real falla porque stdin está capturado.
- Devuelve exactamente `"yes"` / `"no"` / `"always"` (el literal `Approval`), ni booleanos ni `"y"`.
- Por defecto es NO: una respuesta vacía (solo Enter), `nope` o cualquier cosa desconocida -> `"no"`. Seguro por defecto. Normaliza primero, para que ` Y ` siga contando como sí.
- Envuelve el resumen en `Text(...)`: si pasas una cadena sin más, rich interpreta los `[brackets]` (corchetes) de los comandos como markup.

<details><summary>💡 Pista 1</summary>

Dos partes: imprimir algo y luego traducir una respuesta a una de tres cadenas.

</details>

<details><summary>💡 Pista 2</summary>

Bastan pruebas de pertenencia: `ans in ("y", "yes")`, `ans in ("a", "always")`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
summary = summarize_call(tool.name, args, width=400)
console.print(Panel(Text(summary), title=f"Allow {tool.name}? (...)", border_style="yellow"))
ans = ...  # read(...) normalised
if ...:
    return "yes"
# always?
return "no"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k approval -v
```

### TODO 05.4 · `forja/cli.py` · `handle_slash(app: Forja, line: str) -> str | None`

**Qué debe hacer:** Recibe la línea en bruto tecleada en el REPL (empieza por `/`). Devuelve el texto a imprimir, o `None` para `/exit`. Actúa directamente sobre el harness, nunca llama al modelo. Lo comprueba `test_slash_commands`:
- `/exit` -> `None`; `/help` -> `HELP` (contiene `/mode`)
- `/mode` solo -> el modo actual y la lista `MODES`; `/mode plan` -> exactamente `mode -> plan` y `app.mode == "plan"` (usa `app.set_mode`, que lanza `ValueError` para modos desconocidos; el REPL la captura e imprime `error: ...`)
- `/tools` -> una línea por herramienta con su riesgo entre corchetes, p. ej. `bash   [exec]`
- `/todos` -> `app.todos.render()` (contiene `▶ a` para un elemento en curso)
- `/context` -> texto que contenga `tokens` (usa `app.context_tokens()`, opcionalmente `app.settings.context_window` y `len(app.history)`)
- `/compact` -> `app.compact_now(force=True)` (o un texto alternativo si devuelve vacío)
- `/cost` -> texto que contenga `input` (a partir de `app.usage['prompt_tokens']` y `['completion_tokens']`)
- `/undo` -> `app.undo()` devuelve una lista de `Path`; muéstralas relativas (`app.ws.rel(p)`) o indica que no hay nada que deshacer
- `/sessions` -> `Transcript.list_sessions(app.transcript.folder)` da `[(id, first_message)]`
- `/clear` -> vacía `app.history` (y la lista de tareas) y devuelve exactamente `new conversation`
- cualquier otra cosa -> un mensaje que contenga `unknown`

**Pasos:**
1. Separa la línea en comando y argumento: `line.strip().split(maxsplit=1)`; el argumento es el resto (o `""`).
2. Gestiona primero `/exit` y `/help` (returns triviales).
3. `/mode`: sin argumento describe el modo actual; con argumento llama a `app.set_mode(arg)` y devuelve `f"mode -> {app.mode}"`.
4. Comandos de solo lectura: `/tools` (itera `app.registry.tools.values()`, cada `Tool` tiene `.name` y `.risk`), `/todos`, `/context`, `/cost`, `/sessions`; construye una cadena para cada uno.
5. Comandos con efectos: `/compact`, `/undo`, `/clear` (asigna `app.history = []` y `app.todos.items = []`).
6. Termina con el caso por defecto para comandos desconocidos, sugiriendo `/help`.

**Cuidado con:**
- `/mode plan` debe devolver exactamente `mode -> plan` (`->` en ASCII, un espacio a cada lado).
- `/clear` debe devolver exactamente `new conversation` y dejar `app.history == []` (asigna una lista nueva).
- No captures tú el `ValueError` de `set_mode` para devolver `None`: `None` significa salir y cerraría el REPL. Deja que se propague o devuelve un texto de error.
- `app.compact_now(force=True)` puede devolver `""` (nada que compactar); devuelve un texto alternativo legible en lugar de una línea vacía.
- `/undo` y `/compact` dependen de los labs 11 y 07: hasta entonces el harness hace un fallback silencioso (lista vacía / nada compactado). Es lo esperado.

<details><summary>💡 Pista 1</summary>

Aquí se lee mejor una secuencia plana de `if cmd == "/...": return ...` que un dict de lambdas.

</details>

<details><summary>💡 Pista 2</summary>

Todo lo que necesitas ya está en `app`: `app.registry.tools`, `app.todos.render()`, `app.context_tokens()`, `app.usage`, `app.transcript.folder`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
cmd, *rest = line.strip().split(maxsplit=1)
arg = rest[0].strip() if rest else ""
if cmd == "/exit":
    return None
if cmd == "/mode":
    if not arg:
        return ...            # current mode + MODES
    app.set_mode(arg)
    return f"mode -> {app.mode}"
# /help /tools /todos /context /compact /cost /undo /sessions /clear
return f"unknown command: {cmd} (/help)"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k slash -v
```

## Ejecuta
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> arregla el bug del redondeo de importes y comprueba con los tests
/tools
/cost
```

## Pruébalo en tu agente
1. Comprueba primero el modelo: `forja doctor`. Esperado: `backend=ollama url=... model=...`, `answered in N.Ns` y luego `✔ the model calls tools (ping)`.
2. Arranca el REPL sobre el playground: `forja --cwd playground --mode accept_edits`. Verás un panel cian `Forja <version> · <model> · mode accept_edits` y el prompt `accept_edits ›`.
3. Escribe `/tools`: una línea por herramienta, p. ej. `read_file   [read]`, `edit_file   [edit]`, `bash   [exec]`. Luego `/mode`: `current mode: accept_edits (available: default, accept_edits, plan, bypass)`.
4. Pide: `fix the amount rounding bug and check with the tests`. Deberías ver una línea azul por acción (`⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`), un diff enmarcado en verde/rojo tras cada edición y un panel amarillo `Allow bash? (requires approval)` antes de cada comando. Responde `a` una vez: aparece una nota tenue `rule added for this session: allow bash(python -m pytest*)` y las siguientes ejecuciones de pytest ya no preguntan.
5. Tras el turno: `(N steps · M tools)` en gris. Escribe `/cost` (`input ... · output ... tokens`) y `/context` (`~N tokens of 32768 (M messages)`).
6. Pulsa Ctrl+C durante una respuesta larga: `interrupting…` y el agente se detiene en el siguiente límite de paso. Después `/exit`.

## Hito del día 1
1. **Objetivo (15:15):** con TU Forja y TU modelo local, pasan los 3 tests que fallan en `playground/`. Después compara resultados con una pareja que use otro modelo.
2. **1. Resetea el playground.** Desde la raíz del repo: `python scripts/tasks.py reset` (el mismo comando en Windows y en macOS/Linux). Comprueba el punto de partida: `cd playground`, luego `python -m pytest -q` y después `cd ..`. Resumen esperado: `3 failed, 4 passed` (`test_round_half_up`, `test_total_with_vat_cent`, `test_due_date_sunday_moves_to_monday`).
3. **2. Comprueba el modelo.** `forja doctor` debe terminar con `✔ the model calls tools`. Si imprime `! the model answered without calling the tool`, cambia de modelo (`FORJA_MODEL` en `.env`) o usa el servidor del aula antes de seguir.
4. **3. Arranca el agente.** `forja --cwd playground --mode accept_edits` (las ediciones se aprueban solas, los comandos preguntan). Pon en marcha un cronómetro al pulsar Enter en el prompt.
5. **4. Prompt a usar** (pégalo en una sola línea). El lab 06 aún no está hecho, así que el agente NO ve `playground/AGENTS.md`: el propio prompt lleva las reglas del proyecto:
> Ejecuta los tests con `python -m pytest -q`, averigua por qué fallan 3 tests y arregla el código en `invoices/` (nunca cambies los tests). Los importes tienen 2 decimales con redondeo half-up usando `decimal`, nunca `round()` sobre floats. Las fechas de vencimiento que caen en sábado o domingo pasan al lunes siguiente. Cuando termines, vuelve a ejecutar los tests y enséñame el resultado.
6. **5. Aprobaciones.** Cuando el panel amarillo `Allow bash?` muestre `$ python -m pytest -q`, responde `a` (always): solo pytest obtiene una regla de sesión. Responde `n` a cualquier cosa que no ejecutarías en tu propia máquina (instalar paquetes, borrar ficheros).
7. **6. Cómo es una ejecución BUENA:** `⏺ $ python -m pytest -q` (3 fallos) → `⏺ Read invoices/amounts.py` / `⏺ Read invoices/dates.py` → `⏺ Edit invoices/amounts.py` con un diff que redondea mediante `Decimal(str(value))` + `ROUND_HALF_UP` → `⏺ Edit invoices/dates.py` con un diff que también trata el domingo → `⏺ $ python -m pytest -q` mostrando `7 passed` → un resumen breve que cita los ficheros. Normalmente 6–15 pasos, un turno, sin ediciones bajo `tests/`.
8. **7. Cómo es una ejecución MALA** (anótala, son datos, no un fracaso): el modelo edita `tests/` para que pasen; usa `Decimal(value)` sobre el float (2.675 se queda en 2.67) o añade apaños tipo `+ 0.0001`; afirma `all tests pass` sin volver a ejecutar pytest; repite el mismo `edit_file` fallido hasta que el detector de bucles lo para; reescribe un fichero entero con `write_file` y se deja funciones; responde con un bloque de código en lugar de llamar a herramientas; llega a `max_steps`. Da como mucho dos prompts correctivos de seguimiento (p. ej. `the tests still fail, run them and read the error`) y cuéntalos.
9. **8. Verifica fuera del agente.** `/exit`, luego `cd playground` y `python -m pytest -q` → `7 passed`. Comprueba que solo cambió `invoices/`: `git status playground` (o `git diff --stat playground`). Si cambió un fichero de test, la ejecución no cuenta como éxito.
10. **9. Anota tu resultado** (en tu cuaderno o en la hoja compartida): **modelo** (tag exacto, p. ej. `qwen3:8b`, más el backend: Ollama local / servidor del aula / OpenRouter), **éxito** (sí/no y tests que pasan de 7; indica si necesitaste prompts de seguimiento), **pasos** (la línea gris `(N steps · M tools)`; súmalas si hubo varios turnos), **tiempo** (cronómetro desde Enter hasta la respuesta final; opcionalmente los tokens de `/cost`). Luego compara con un compañero que haya usado otro modelo: ¿quién necesitó menos pasos?, ¿quién rompió una regla?
11. **10. Opcional: una ejecución headless reproducible.** `python scripts/tasks.py reset` y luego cronométrala: PowerShell `Measure-Command { forja --cwd playground --mode bypass -p "<same prompt>" }`, macOS/Linux `time forja --cwd playground --mode bypass -p "<same prompt>"`. En headless no hay usuario: en `accept_edits` todo comando sería DENEGADO, de ahí `bypass` (las reglas deny siguen aplicándose). El código de salida 0 significa que el agente terminó con una respuesta final, no que los tests pasen: ejecuta pytest tú mismo.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_ask_approval` se cuelga o falla con `OSError: pytest: reading from stdin while output is captured` | Llamaste a `input()`/`console.input()` en lugar de al parámetro `read` → llama a `read(prompt)`. |
| `test_summarize_call` falla en la aserción de longitud (51 != 50) o en `$ pytest  -q` | El truncado añade `…` sin quitar un carácter, o truncas antes de colapsar los espacios → colapsa primero y luego `s[:width - 1] + "…"`. |
| `test_diff_styles` da `['red', 'green', ...]` para las cabeceras | Pruebas `-`/`+` antes que `---`/`+++` → comprueba primero los prefijos de 3 caracteres. |
| El REPL se cierra al escribir `/mode foo` | `handle_slash` devolvió `None` ante un error → solo `/exit` devuelve `None`; deja que el `ValueError` de `set_mode` se propague (el REPL imprime `error: unknown mode: foo`). |
| `KeyError` / fallo en las líneas `⏺` cuando el modelo envía argumentos raros | `summarize_call` usa `args['x']` → usa `args.get('x', default)`; los argumentos llegan del modelo sin validar. |
| `forja` no se reconoce (Windows) / `command not found` (macOS/Linux) | El venv no está activo o no se ejecutó el setup → PowerShell `.venv\Scripts\Activate.ps1` (si está bloqueado: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`), macOS/Linux `source .venv/bin/activate`, y luego `python scripts/tasks.py setup`. `python -m forja ...` también funciona. |
| Windows: el agente ejecuta `ls`, `cat` o `python3` y obtiene errores | La herramienta bash usa `cmd.exe` en Windows → es normal; el modelo debería adaptarse tras el error. Díselo: `use python -m pytest -q; this is Windows cmd`. |
| Los colores o `⏺` se ven como basura en consolas antiguas de Windows | Usa Windows Terminal (o el terminal de VS Code) en lugar de la ventana clásica de `cmd.exe`; `chcp 65001` ayuda con UTF-8. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 05` → 4 passed.
- [ ] [ ] En el REPL ves resúmenes de una línea, diffs en color y el panel de aprobación y/n/a; `/tools`, `/mode`, `/cost` y `/context` funcionan.
- [ ] [ ] Hito del día 1: tu agente hizo pasar los 3 tests que fallaban en el playground, y anotaste modelo, éxito, pasos y tiempo.

## Checkpoint
**Hito del día 1** (15:15): Forja arregla los 3 tests que fallan en `playground/` con tu modelo local. Compara con el compañero que usa otro modelo.

## Retos
1. Añade `/model <nombre>` para cambiar de modelo en caliente.
2. Muestra en el prompt de la REPL el % de contexto usado.

**Tests:** `tests/test_l05_cli.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 06`

---
[← anterior](../L04_bash_permissions/README.md) · [siguiente →](../L06_context/README.md)
