# Lab 10 · Extensibilidad: hooks, skills y MCP

🇬🇧 [English](README.en.md) · Día 2 · 12:10–13:20

**Objetivo:** Que el equipo extienda el agente sin tocar su código: política determinista, conocimiento bajo demanda y herramientas externas.

## Conceptos
- **Hooks = garantías:** AGENTS.md *pide*, un hook *impide*. Comandos de shell en `settings.json` que reciben el evento como JSON por stdin. Exit 2 bloquea; exit 0 sigue. Es la convención que usan los agentes comerciales: lo que aprendáis aquí os sirve allí.
- **Eventos:** `PreToolUse` (bloquear), `PostToolUse` (feedback, p. ej. linter), `UserPromptSubmit` (filtrar o añadir contexto), `Stop` (no terminar hasta que pasen los tests).
- **Skills = divulgación progresiva:** en el prompt solo va el catálogo (nombre + descripción); el cuerpo se carga con la tool `skill` cuando hace falta. Formato portable `SKILL.md`.
- **MCP:** servidores que exponen tools (issues, BD, wiki, CI). Forja los arranca desde `settings.json` y los registra como `mcp__servidor__tool`, con riesgo `exec`: pasan por permisos.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks por evento y matcher |
| 10.2 | `forja/hooks.py` | run: ejecutar y traducir códigos de salida |
| 10.3 | `forja/skills.py` | discover_skills: catálogo de SKILL.md |
| 10.4 | `forja/skills.py` | skill: cargar el cuerpo bajo demanda |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: espacio de nombres mcp__server__tool |

## Antes de empezar
- Tres ficheros pequeños, tres ideas: `forja/hooks.py` (10.1, 10.2), `forja/skills.py` (10.3, 10.4) y `forja/mcp_tools.py` (10.5). El harness (`forja/harness.py`) ya los llama: `self.hooks.run("PreToolUse", {...}, tool.name)` en `gate`, `"PostToolUse"` tras ejecutar, `"UserPromptSubmit"` y `"Stop"` en `turn`; `skills.discover_skills(home/.forja/skills, root/.forja/skills)` al arrancar; `mcp_tool_name` dentro de `connect_servers`.
- API de hooks: `subprocess.run(cmd, shell=True, cwd=..., input=<json str>, capture_output=True, text=True, timeout=...)` devuelve un `CompletedProcess` con `returncode`, `stdout`, `stderr`; lanza `subprocess.TimeoutExpired` si se agota el tiempo. `re.fullmatch(pattern, s)` casa con el string ENTERO (así `edit_file|write_file` funciona como alternativa). Con `shell=True` el shell es cmd.exe en Windows y `/bin/sh` en macOS/Linux.
- Convención de códigos de salida (la misma que los agentes comerciales): `0` = OK (stdout puede ser contexto útil), `2` = BLOQUEO (stderr, o stdout si está vacío, es el mensaje para el modelo), cualquier otro = error del hook (se registra, nunca bloquea). `HookOutcome` tiene `block`, `message`, `context`, `errors`.
- Las skills reutilizan el parseo de frontmatter que escribiste en 09.1 (`FRONTMATTER` + `yaml.safe_load`). `catalog()` ya está escrita: solo necesita `Skill.name` y `Skill.description`.
- Mira `examples/project/.forja/settings.json` y `examples/project/.forja/hooks/*.py`: un hook PreToolUse real lee el evento con `json.load(sys.stdin)` y sale con 2 y un mensaje en stderr.

## Paso a paso
10.1 → 10.2 (un test cubre ambos: `test_hook_matching_and_exit_codes`; luego `test_hooks_in_harness` comprueba la integración), después 10.5 (una línea, victoria rápida), y luego 10.3 → 10.4 (ambos comprobados por `test_skills`). Deja `test_mcp_end_to_end` para el final: arranca un subproceso de servidor MCP real y necesita que los labs 02-04 funcionen.

### TODO 10.1 · `forja/hooks.py` · `HookRunner.matching(event: str, tool_name: str | None = None) -> list[dict]`

**Qué debe hacer:** Devuelve, en el orden de la configuración, los dicts de hook de `self.config.get(event, [])` que aplican. Un hook SIN `matcher` aplica siempre. Un hook CON `matcher` aplica solo si `tool_name` no es `None` y `re.fullmatch(matcher, tool_name)` casa. Evento desconocido → `[]`. Test: `[h.get("matcher") for h in runner.matching("PreToolUse", "bash")] == ["bash", None]`, `len(matching("PreToolUse", "write_file")) == 2`, `matching("Stop") == []`.

**Pasos:**
1. Obtén la lista del evento con `.get(event, [])` (que falten eventos es normal).
2. Para cada hook lee `h.get("matcher")`.
3. Sin matcher → consérvalo.
4. Matcher pero sin `tool_name` (eventos como `Stop`/`UserPromptSubmit`) → omítelo.
5. Matcher y `tool_name` → consérvalo solo si `re.fullmatch` tiene éxito. Mantén el orden original.

**Cuidado con:**
- `re.match`/`re.search` en lugar de `fullmatch`: `bash` casaría también con `bash_tool`, y `edit_file|write_file` con `re.match` acepta prefijos. El test espera exactamente 2 hooks para `write_file`.
- `self.config[event]` lanza `KeyError` para eventos que nadie configuró — `matching("Stop")` debe devolver `[]`.
- Los matchers son REGEX, no globs: en settings escribe `mcp__issues__.*`, no `mcp__issues__*` (esa es la sintaxis de las reglas de permisos).

<details><summary>💡 Pista 1</summary>

Tres casos por hook: sin matcher, matcher sin nombre de herramienta, matcher con nombre de herramienta.

</details>

<details><summary>💡 Pista 2</summary>

`re.fullmatch(matcher, tool_name)` devuelve un objeto match o `None`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
out = []
for h in self.config.get(event, []):
    matcher = h.get("matcher")
    if matcher and <no tool_name or no fullmatch>:
        continue
    out.append(h)
return out
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k hook_matching -v
```

### TODO 10.2 · `forja/hooks.py` · `HookRunner.run(event: str, payload: dict, tool_name: str | None = None) -> HookOutcome`

**Qué debe hacer:** Serializa `{"hook_event_name": event, "cwd": str(self.cwd), **payload}` a JSON (`ensure_ascii=False, default=str`) y lo envía por stdin a CADA hook que case (se ejecutan todos, incluso después de un bloqueo). Por hook: salida 2 → `block=True` y añade `stderr` (o `stdout`, o un texto por defecto) con strip + salto de línea a `message`; salida 0 → añade el `stdout` no vacío con strip a `context`; otros códigos → añade una descripción a `errors`; `TimeoutExpired` → añade a `errors` y continúa. Usa `h.get("timeout", self.timeout)`. Al final haz strip de `message` y `context`. Tests: PreToolUse con hooks que salen con 2 / 0 / 1 → `block` y `message == "no"` y `len(errors) == 1`; UserPromptSubmit que imprime `ctx:` + prompt → `context == "ctx:hello"`, sin bloquear, 1 error. En el harness (`test_hooks_in_harness`): `BLOCKED by hook` en el resultado de la herramienta y el hook Stop fuerza una ronda más.

**Pasos:**
1. Crea un `HookOutcome()` vacío y construye el string JSON una sola vez.
2. Para cada hook de `self.matching(event, tool_name)` llama a `subprocess.run` con `h["command"]`, `shell=True`, `cwd=self.cwd`, el JSON como `input`, `capture_output=True`, `text=True` y el timeout.
3. Envuelve la llamada en `try/except subprocess.TimeoutExpired` → registra un error, `continue`.
4. Ramifica según `returncode`: 2 → bloqueo + mensaje; 0 → contexto si stdout tiene texto; resto → errors (incluye el código y un trozo de stderr).
5. Tras el bucle, haz `.strip()` de `message` y `context` para que los saltos de línea finales no rompan las comparaciones exactas.

**Cuidado con:**
- Parar en el primer hook que bloquea: la configuración del test tiene un tercer hook (salida 1) que debe ejecutarse igualmente, dando `len(errors) == 1`.
- Olvidar `text=True`: entonces `input` debe ser bytes y `stdout` vuelve como bytes → `TypeError` o `b'no'` != `'no'`.
- No hacer strip: `message` sería `'no\n'`; el test compara con `== "no"`.
- Sin `cwd=self.cwd` los comandos de hook relativos (`python .forja/hooks/x.py`) y el hook Stop del test (`pathlib.Path('DONE')`) buscan en la carpeta equivocada.
- Windows: el test construye comandos como `"C:/path/python.exe" -c "..."`; eso solo funciona con `shell=True` (cmd.exe interpreta las comillas).

<details><summary>💡 Pista 1</summary>

Ejecuta cada comando una vez con el evento en stdin y fíjate solo en `returncode`, `stdout`, `stderr`.

</details>

<details><summary>💡 Pista 2</summary>

`p = subprocess.run(h["command"], shell=True, cwd=self.cwd, input=data, capture_output=True, text=True, timeout=h.get("timeout", self.timeout))`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
outcome = HookOutcome()
data = json.dumps({...}, ensure_ascii=False, default=str)
for h in self.matching(event, tool_name):
    try: p = subprocess.run(...)
    except subprocess.TimeoutExpired: outcome.errors.append(...); continue
    if p.returncode == 2: ...          # block, message += stderr or stdout
    elif p.returncode == 0: ...        # context += stdout
    else: ...                          # errors
# strip message and context
return outcome
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k hook -v
```

### TODO 10.3 · `forja/skills.py` · `discover_skills(*folders: Path) -> dict[str, Skill]`

**Qué debe hacer:** Para cada carpeta que exista, mira `<folder>/*/SKILL.md` (ordenados). Parsea el frontmatter; conserva solo los ficheros con `name` y `description`. Guarda `Skill(name, description_normalised, path_to_SKILL.md)` bajo `name`; las carpetas posteriores sobrescriben a las anteriores (el harness pasa primero la carpeta del usuario y después la del proyecto, así que gana el proyecto). Normaliza los espacios de la descripción: la descripción YAML del test ocupa dos líneas y debe quedar exactamente `"How to make commits here."`. Un `SKILL.md` sin frontmatter se omite (`list(sk) == ["commits"]`).

**Pasos:**
1. Empieza con un dict vacío; recorre las carpetas en el orden dado y omite las que no sean directorios.
2. `sorted(folder.glob("*/SKILL.md"))` — un nivel de subcarpetas, exactamente ese nombre de fichero.
3. Aplica `FRONTMATTER`; sin coincidencia → omítelo. Carga el YAML (protégete contra `None`).
4. Exige `name` y `description`; colapsa todos los espacios en blanco de la descripción en espacios simples.
5. Guarda `Skill(...)` con la ruta del propio fichero `SKILL.md` (10.4 lo vuelve a leer).

**Cuidado con:**
- Un valor YAML multilínea (`description: How to make\n  commits here.`) lo pliega YAML, pero sé explícito: `" ".join(str(d).split())` garantiza espacios simples y ningún salto de línea, que es lo que `catalog()` necesita para producir `- commits: How to make commits here.`.
- Salir antes de tiempo cuando falta la primera carpeta: la carpeta del usuario (`~/.forja/skills`) normalmente no existe — omítela y sigue.
- Guardar la carpeta en vez de la ruta de `SKILL.md`: entonces 10.4 no consigue leer el cuerpo.

<details><summary>💡 Pista 1</summary>

Es otra vez 09.1 con otro glob y otra dataclass.

</details>

<details><summary>💡 Pista 2</summary>

`folder.glob("*/SKILL.md")`, `FRONTMATTER.match(f.read_text(encoding="utf-8"))`, `" ".join(str(meta["description"]).split())`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
out = {}
for folder in folders:
    if not folder.is_dir(): continue
    for f in sorted(folder.glob(...)):
        m = ...; meta = ...            # None-safe
        if <valid>:
            out[meta["name"]] = Skill(..., ..., f)
return out
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k skills -v
```

### TODO 10.4 · `forja/skills.py` · `make_skill_tool(skills)` → herramienta interna `skill(name: str) -> str`

**Qué debe hacer:** Nombre desconocido → `ValueError` listando las skills disponibles (o `none`). Nombre conocido → vuelve a leer `skill.path`, quita el frontmatter y devuelve `# Skill: <name>`, una línea con la carpeta (`(folder: <path.parent>)`, para que el modelo encuentre scripts/plantillas junto a `SKILL.md`), una línea en blanco y el CUERPO con strip. El test comprueba que el resultado contiene `Use conventional commits.` y NO contiene `---`. No cambies el docstring: se convierte en la descripción de la herramienta y la sección `Args:` documenta `name`.

**Pasos:**
1. Busca `skills.get(name)`; si no está, lanza `ValueError` con la lista de nombres.
2. Vuelve a leer el fichero (el cuerpo no se cachea: eso es la revelación progresiva).
3. Aplica `FRONTMATTER.match` y quédate con el grupo 2 con strip; si por lo que sea no casa, usa el texto entero como alternativa.
4. Devuelve la cabecera, la línea de la carpeta y el cuerpo.

**Cuidado con:**
- Devolver el fichero entero: las líneas `---` del frontmatter se cuelan en el resultado y el test falla en `"---" not in out`.
- Devolver un string de error en vez de lanzar: "funciona", pero el resultado de la herramienta se marca como ok y el modelo no sabe que falló.
- Si `test_skills` falla en `"commits" in llm.calls[0]["messages"][0]["content"]`, el catálogo no está llegando al system prompt: eso requiere que `build_system_prompt` del lab 06 incluya `skills_catalog`.

<details><summary>💡 Pista 1</summary>

El catálogo (solo descripciones) ya está en el prompt; esta herramienta devuelve la parte que se dejó fuera.

</details>

<details><summary>💡 Pista 2</summary>

`m = FRONTMATTER.match(s.path.read_text(encoding="utf-8"))`; `m.group(2).strip()`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
s = skills.get(name)
if s is None:
    raise ValueError(f"unknown skill: {name}. Available: ...")
body = ...    # text without frontmatter
return f"# Skill: {s.name}\n(folder: ...)\n\n{body}"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k skills -v
```

### TODO 10.5 · `forja/mcp_tools.py` · `mcp_tool_name(server: str, tool: str) -> str`

**Qué debe hacer:** Devuelve `mcp__<server>__<tool>` donde cada carácter fuera de `[a-zA-Z0-9_]` en server Y en tool se sustituye por `_` (usa la regex precompilada `NAME_RE`). Tests: `("issues", "get_issue") -> "mcp__issues__get_issue"`, `("my-wiki", "search.docs") -> "mcp__my_wiki__search_docs"`. `connect_servers` (ya escrita) la usa para renombrar cada herramienta MCP; las herramientas MCP tienen riesgo `exec`, así que pasan por los permisos.

**Pasos:**
1. Sanea el nombre del servidor con `NAME_RE.sub("_", ...)`.
2. Sanea el nombre de la herramienta de la misma forma.
3. Únelos con el prefijo `mcp__` y un doble guion bajo entre ellos.

**Cuidado con:**
- Guiones bajos simples (`mcp_issues_get_issue`): las reglas de permisos como `mcp__issues__*` en `settings.json` no casarán nunca.
- Sanear solo el nombre de la herramienta: un servidor llamado `my-wiki` produce un nombre de herramienta inválido que algunos modelos/servidores rechazan.

<details><summary>💡 Pista 1</summary>

Una línea con un f-string.

</details>

<details><summary>💡 Pista 2</summary>

`NAME_RE.sub("_", server)` sustituye cada carácter prohibido.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
return f"mcp__{...}__{...}"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k mcp -v
```

## Ejecuta
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # si no lo hiciste en el lab 09
forja --cwd playground
> lista las issues abiertas, arregla la #12 y comenta en la issue qué cambiaste
> haz commit siguiendo la convención del repo
```

## Pruébalo en tu agente
1. Asegúrate de que existe `playground/.forja/` (copiado en el lab 09). La ruta del servidor MCP en `settings.json` (`../examples/mcp/issues_server.py`) se resuelve desde la raíz del proyecto (`playground/`), así que `forja --cwd playground` desde la raíz del repo funciona. Si el servidor falla verás una nota al arrancar `· MCP 'issues': …` y ninguna herramienta MCP.
2. `/tools` → deberías ver `mcp__issues__list_issues`, `mcp__issues__get_issue`, `mcp__issues__comment_issue` con `[exec]`, y `skill [read]`.
3. `list the open issues, fix #12 and comment on the issue what you changed`. Esperado: `⏺ mcp__issues__list_issues` (sin pedir aprobación: `mcp__issues__*` está en `allow`), lecturas/ediciones en `invoices/amounts.py`, una comprobación de compilación PostToolUse tras cada edición y, finalmente, `mcp__issues__comment_issue`.
4. Observa el hook Stop (`.forja/hooks/stop_tests.py`): solo se ejecuta si hay cambios sin commitear en el proyecto (git), así que las preguntas no le afectan. Si el agente editó ficheros y dice que ha terminado con los tests en rojo, verás que sigue trabajando (se inyecta un mensaje de usuario `[Stop hook] You are not done yet…` con el final de la salida de pytest). Se rinde tras 3 rondas extra.
5. `commit following the repo's convention` → la primera llamada debería ser `⏺ skill conventional-commits`, luego `git status`/`git diff`, y después un mensaje de commit como `fix(amounts): …`. (Se te pedirá aprobar `git commit`: no está en `allow`.)
6. Prueba el hook PreToolUse: `run cat .env` → el resultado muestra `BLOCKED by hook: Command blocked by policy: it may expose secrets…`.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_hook_matching_and_exit_codes`: `assert out.message == 'no'` falla con `'no\n'` | No hiciste strip → haz `.strip()` de `message`/`context` acumulados al final. |
| `len(out.errors) == 1` falla (0 errores) | Haces `break` tras el hook que bloquea, así que el hook con salida 1 nunca se ejecuta → ejecuta todos los hooks que casen. |
| `TypeError: a bytes-like object is required` en `subprocess.run` | Falta `text=True` → añádelo (input/stdout/stderr pasan a ser `str`). |
| Windows: el test de hooks falla con `'C:/…/python.exe' is not recognized` o errores de comillas | Si ejecutas sin `shell=True`, cmd.exe nunca interpreta el comando entrecomillado → mantén `shell=True` y pasa el comando como un único string. |
| Las respuestas terminan con `[Stop hook] You are not done yet…` aunque solo hayas hecho una pregunta | `stop_tests.py` ejecuta los tests siempre que haya cambios sin commitear en `playground/` (p. ej. un arreglo a medias de un lab anterior) → termina el arreglo o haz `python scripts/tasks.py reset`. Fuera de git se ejecuta siempre. |
| No hay herramientas `mcp__issues__*`; nota al arrancar `· MCP 'issues': …` | El servidor no arrancó → comprueba que la ruta es relativa a la raíz del proyecto (`playground/`), que `mcp` está instalado (`pip show mcp`), y ejecuta el servidor a mano: `python examples/mcp/issues_server.py`. |
| El hook PostToolUse/PreToolUse nunca se dispara para herramientas MCP | El matcher es una regex con `fullmatch` → usa `mcp__issues__.*`, no el glob `mcp__issues__*`. |
| El modelo nunca llama a `skill` | Los modelos pequeños ignoran los catálogos → haz que la descripción de la skill diga CUÁNDO cargarla ('Load it before running git commit') y menciónala en el prompt. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 10` → 5 passed (incluido `test_mcp_end_to_end`).
- [ ] [ ] En el CLI: `cat .env` queda bloqueado por el hook PreToolUse, y el hook Stop hace que el agente continúe mientras los tests están en rojo.
- [ ] [ ] `/tools` lista `skill` y las herramientas `mcp__issues__*`, y el agente carga `conventional-commits` antes de hacer commit.

## Checkpoint
El hook Stop no deja terminar con tests en rojo; el agente carga la skill `conventional-commits` antes de hacer commit; las tools `mcp__issues__*` aparecen en `/tools`.

## Retos
1. Hook PostToolUse que ejecute `ruff` sobre el fichero editado.
2. Conecta un servidor MCP real de tu equipo.

**Tests:** `tests/test_l10_extensions.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 11`

---
[← anterior](../L09_subagents/README.md) · [siguiente →](../L11_sessions/README.md)
