"""Guía paso a paso para el alumno (español) de los labs 09-12 y el proyecto final.

Esquema: ver los otros módulos de guías. Todas las cadenas son Markdown.
"""
from __future__ import annotations

GUIDE: dict[str, dict] = {
    # =====================================================================================
    "09": {
        "before": [
            "Abre `forja/subagents.py` (tus TODOs) y ten abiertos al lado `forja/agent.py` (lab 03) y `forja/harness.py` "
            "(`_build_registry`). El harness ya llama a `subagents.load_profiles(root / \".forja\" / \"agents\")` "
            "y registra `subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events)`: "
            "tú solo rellenas las dos funciones.",
            "Lo que reutilizas: `Agent(llm, tools, execute=..., events=..., max_steps=...)` y su `run(messages) -> AgentResult` "
            "(campos `answer`, `stop_reason`, `steps`, `tool_calls`, `usage`). `ToolRegistry.subset(names)` construye un registro "
            "solo con los nombres que existen (los nombres desconocidos se omiten en silencio).",
            "Stdlib / librerías usadas: `Path.glob(\"*.md\")`, `Path.read_text(encoding=\"utf-8\")`, la regex precompilada "
            "`FRONTMATTER` (grupo 1 = YAML entre las líneas `---`, grupo 2 = cuerpo) y `yaml.safe_load` (devuelve un dict, o "
            "`None` para un YAML vacío). `tools: read_file, grep` en YAML es un *string*; `tools: [read_file, grep]` es una *lista*.",
            "Idea clave: el subagente parte de una lista `messages` NUEVA (system + prompt del usuario). Nunca ve el historial principal; "
            "el agente principal solo recibe el string que devuelve tu herramienta `task`. Aun así, cada llamada a herramienta del subagente pasa por "
            "`execute` = la puerta del harness (hooks, permisos, aprobaciones, checkpoints).",
            "Mira `examples/project/.forja/agents/reviewer.md` para ver un perfil real (tiene `tools` y `max_steps`).",
        ],
        "order": "Haz primero 09.1: es puro parseo, tiene su propio test aislado (`test_load_profiles`) y el harness lo necesita para "
                 "construir la lista de subagentes que aparece en la descripción de la herramienta `task`. Después 09.2, cuyos tests "
                 "(`test_task_isolated_context`, `test_unknown_subagent`) pasan por el harness completo, así que los labs 02-04 ya deben pasar.",
        "todos": {
            "09.1": {
                "where": "`forja/subagents.py` · `load_profiles(folder: Path) -> dict[str, AgentProfile]`",
                "contract": "Recibe la carpeta de agentes (puede no existir). Devuelve un dict `name -> AgentProfile` que SIEMPRE contiene "
                            "el perfil integrado `explore` (parte de una copia de `BUILTIN`, nunca mutes el propio `BUILTIN`). Por cada "
                            "fichero `*.md` con frontmatter válido que tenga `name` y `description`, añade "
                            "`AgentProfile(name, description, system=<body stripped>, tools=<list[str]>, max_steps=<int, default 25>)`. "
                            "Los ficheros sin frontmatter o sin `name`/`description` se omiten en silencio. El test comprueba: "
                            "`set(p) == {\"explore\", \"reviewer\"}`, `tools == [\"read_file\", \"grep\"]` (a partir del string `read_file, grep`), "
                            "`max_steps == 5`, `system == \"You are a reviewer.\"`, y que una carpeta inexistente devuelve exactamente `BUILTIN`.",
                "steps": [
                    "Crea `profiles = dict(BUILTIN)`; si la carpeta no es un directorio, devuélvelo directamente.",
                    "Recorre los ficheros `*.md` en un orden estable (`sorted`). Lee cada uno como UTF-8 y aplica `FRONTMATTER.match`.",
                    "Sin coincidencia → omítelo. Con coincidencia → `yaml.safe_load(group 1)`, y trata `None` como `{}`.",
                    "Omítelo si falta `name` o `description` o están vacíos.",
                    "Normaliza `tools`: por defecto `[\"read_file\", \"grep\", \"glob\"]`; si es un string, divídelo por comas y haz strip de cada "
                    "elemento, descartando los vacíos; si ya es una lista, mantenla.",
                    "Construye el perfil: el cuerpo (grupo 2) con `.strip()` es el system prompt; `max_steps` con `int(...)` y valor por defecto 25. "
                    "Guárdalo bajo su `name` (un fichero puede sobrescribir `explore` si usa ese nombre).",
                ],
                "gotchas": [
                    "Devolver el propio `BUILTIN` y luego añadirle cosas muta la constante del módulo: el siguiente test (`load_profiles(missing) == BUILTIN`) "
                    "o la siguiente instancia del harness verán perfiles obsoletos. Cópialo.",
                    "`tools: read_file, grep` es el string `'read_file, grep'`. Si olvidas dividirlo obtienes `['r','e','a',...]` al iterarlo, "
                    "o un único nombre de herramienta desconocido — y `subset()` descarta en silencio los nombres desconocidos, así que el subagente acaba SIN herramientas.",
                    "`system` debe ser el cuerpo *sin* el frontmatter y con strip: el test lo compara exactamente.",
                    "`yaml.safe_load` sobre un frontmatter que solo contiene comentarios devuelve `None`: hacer `.get` sobre él lanza `AttributeError`.",
                ],
                "hints": [
                    "Es el mismo parseo \"frontmatter + cuerpo\" que volverás a hacer para las skills en el lab 10. La regex ya está compilada para ti.",
                    "`m = FRONTMATTER.match(text)`; `meta = yaml.safe_load(m.group(1)) or {}`; `m.group(2).strip()` es el system prompt. "
                    "`isinstance(tools, str)` te dice cuándo dividir.",
                    "```python\nprofiles = dict(BUILTIN)\nif not folder.is_dir(): return profiles\nfor f in sorted(folder.glob(\"*.md\")):\n"
                    "    m = ...            # FRONTMATTER.match on the file text\n    if not m: continue\n    meta = ...         # yaml, never None\n"
                    "    if <missing name or description>: continue\n    tools = ...        # default list; split 'a, b' strings\n"
                    "    profiles[meta[\"name\"]] = AgentProfile(...)\nreturn profiles\n```",
                ],
                "test": "python -m pytest tests/test_l09_subagents.py -k load_profiles -v",
            },
            "09.2": {
                "where": "`forja/subagents.py` · `make_task_tool(...)` → herramienta interna `task(description, prompt, subagent_type=\"explore\") -> str`",
                "contract": "`make_task_tool` ya está escrita salvo el cuerpo de `task`. Dentro de `task`: busca `profiles[subagent_type]`; "
                            "si no existe lanza `ValueError` cuyo mensaje contenga `unknown` y liste los nombres disponibles (el registro lo convierte "
                            "en un resultado de herramienta fallido; `test_unknown_subagent` comprueba que contiene `\"unknown\"`). Construye el registro del subagente con "
                            "`parent_tools.subset(...)` usando las herramientas del perfil MENOS `\"task\"`. Crea un `Agent` con el mismo `llm`, ese subregistro, "
                            "`execute=execute`, `max_steps=prof.max_steps` y `events=events_factory(prof.name)` si se pasó una factoría, si no `Events()`. "
                            "Ejecútalo sobre una lista NUEVA `[{\"role\": \"system\", \"content\": prof.system}, {\"role\": \"user\", \"content\": prompt}]`. "
                            "Devuelve una cabecera que contenga `subagent <name>` (el test busca `\"subagent explore\"`), p. ej. "
                            "`[subagent explore · <description> · N steps · M tools · <stop_reason>]`, luego un salto de línea y `res.answer`. "
                            "El test también comprueba que la primera llamada al LLM del subagente tuvo exactamente 2 mensajes empezando por el system prompt de explore, "
                            "que se le ofrecieron exactamente `{read_file, grep, glob}`, y que el historial principal solo contiene UN mensaje de herramienta (`task`).",
                "steps": [
                    "Busca el perfil; si no está, `raise ValueError(f\"unknown subagent: ... Available: ...\")`.",
                    "Calcula los nombres de herramientas permitidos: las `tools` del perfil sin `\"task\"` (sin recursión).",
                    "`sub_tools = parent_tools.subset(those names)`.",
                    "Elige el objeto de eventos: `events_factory(prof.name)` cuando la factoría no es `None`, si no `Events()`. "
                    "En el CLI esta factoría imprime las llamadas a herramientas del subagente con el prefijo `[explore]`.",
                    "Envuelve `execute` en un pequeño `sub_execute(call)`: si `call.name` no está en `sub_tools.tools`, devuelve "
                    "`ToolResult(call.id, call.name, False, \"ERROR: tool '...' is not available to subagent '...'\")`; si no, delega en "
                    "`execute` (o en `sub_tools.execute` cuando `execute` es `None`). La lista de esquemas solo *ofrece* herramientas; el modelo puede llamar a otras igualmente.",
                    "Crea el `Agent` (mismo `llm`, `execute=sub_execute`, `max_steps=prof.max_steps`) y llama a `run` con una lista NUEVA de dos mensajes.",
                    "Formatea y devuelve la línea de cabecera + el `answer` del subagente (usa `res.steps`, `res.tool_calls`, `res.stop_reason`).",
                ],
                "gotchas": [
                    "Reutilizar o copiar el historial del padre: el subagente debe empezar limpio (`len(messages) == 2` en su primera llamada).",
                    "Pasar `parent_tools` en vez del subconjunto: el subagente tendría `write_file`, `bash`, `task`… y "
                    "`test_task_isolated_context` falla en el conjunto de herramientas.",
                    "Olvidar pasar por `execute`: el subagente se saltaría la puerta (sin permisos, sin hooks, sin checkpoints).",
                    "Fiarse de la lista de herramientas ofrecida: `test_subagent_cannot_use_tools_outside_its_profile` hace que el modelo llame a `write_file` "
                    "desde `explore`; tu wrapper debe rechazarlo y el fichero no debe existir.",
                    "El mismo `FakeLLM` sirve al agente principal y al subagente en orden de llamada: si tu `task` hace una llamada extra al LLM (o ninguna), "
                    "todas las respuestas guionizadas se desplazan y las aserciones fallan de formas confusas.",
                    "No toques `task.description`: se asigna después de la función e incluye el catálogo que lee el modelo para elegir subagente.",
                ],
                "hints": [
                    "Todo el subagente es simplemente el `Agent` del lab 03 con un registro más pequeño y una lista de mensajes nueva.",
                    "`parent_tools.subset([t for t in prof.tools if t != \"task\"])`; `Agent(llm, sub_tools, execute=sub_execute, max_steps=..., events=...)`; "
                    "`res = agent.run(messages)`.",
                    "```python\nprof = profiles.get(subagent_type)\nif prof is None: raise ValueError(...)  # 'unknown', list names\n"
                    "sub_tools = ...                 # subset, never 'task'\ndef sub_execute(call): ...     # refuse names not in sub_tools.tools\nevents = ...                    # factory(name) or Events()\n"
                    "agent = Agent(...)\nres = agent.run([...])         # system + user ONLY\nreturn f\"[subagent {prof.name} · ...]\\n{res.answer}\"\n```",
                ],
                "test": "python -m pytest tests/test_l09_subagents.py -k \"task_isolated or unknown_subagent or outside_its_profile\" -v",
            },
        },
        "try_it": [
            "Copia la configuración del proyecto de ejemplo al playground. macOS/Linux: `cp -r examples/project/.forja playground/` · "
            "PowerShell: `Copy-Item -Recurse examples\\project\\.forja playground\\.forja` · cmd: `xcopy /E /I examples\\project\\.forja playground\\.forja`.",
            "`forja --cwd playground`, y luego `/tools`: deberías ver `task [read]` al final de la lista, y ninguna "
            "nota `subagents: lab 09 pending` al arrancar.",
            "Escribe `use a subagent to find every place where amounts are rounded`. Esperado: `⏺ task …`, luego líneas sangradas "
            "`  [explore] ⏺ grep …` / `  [explore] ⏺ read_file …` (las llamadas del subagente; su texto no se muestra en streaming), y finalmente la "
            "respuesta del agente principal listando ubicaciones `path:line`.",
            "Ejecuta `/context` antes y después: el contexto principal crece unos cientos de tokens, no el tamaño de cada fichero que leyó el subagente.",
            "Edita algo a mano en `playground/invoices/` y luego: `ask the reviewer subagent to review my uncommitted changes`. "
            "Deberías ver `  [reviewer] ⏺ bash git diff …` (permitido por `bash(git diff*)` en settings) y una revisión con secciones numeradas.",
        ],
        "troubleshooting": [
            ["`test_task_isolated_context` falla con `StopIteration` / FakeLLM 'no more responses'",
             "Tu `task` llama al LLM un número distinto de veces (p. ej. ejecutaste `agent.run` dos veces, o el bucle principal del lab 03 está roto) → un `Agent.run` por llamada a task; ejecuta antes `tests/test_l03_agent.py`."],
            ["Aserción sobre `{t['function']['name'] ...} == {'read_file','grep','glob'}`",
             "Pasaste el registro completo del padre, o incluiste `task` → usa `parent_tools.subset(...)` filtrando `task`."],
            ["El subagente no tiene herramientas / responde sin leer nada",
             "En 09.1 no se dividió `tools` (string `'read_file, grep'`), así que `subset()` descartó todos los nombres → divide por comas y haz strip."],
            ["`reviewer` no aparece en la descripción de `task` / 'unknown subagent: reviewer'",
             "El fichero del perfil no tiene frontmatter `---` en la primerísima línea, o le falta `description` → arregla el fichero; los perfiles se leen de `<project>/.forja/agents/`, así que comprueba que copiaste `.forja` en `playground/`."],
            ["Sin prefijo `[explore]` en el CLI, las llamadas del subagente parecen del principal",
             "Ignoraste `events_factory` y usaste siempre `Events()` (entonces no ves nada) o pasaste los eventos principales → usa `events_factory(prof.name)` cuando no sea `None`."],
            ["El modelo pequeño nunca delega",
             "Los modelos de 8B suelen preferir hacerlo ellos mismos → pídelo explícitamente ('use a subagent…'); la descripción de `task` es lo único que lee para decidir."],
            ["Windows: `cp -r` falla en cmd.exe",
             "`cp` solo existe en PowerShell (como alias) → usa `xcopy /E /I examples\\project\\.forja playground\\.forja` en cmd."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 09` → 3 passed.",
            "[ ] En el CLI ves llamadas a herramientas con prefijo `[explore]` y `/context` apenas crece tras una búsqueda delegada.",
            "[ ] El perfil `reviewer` de `.forja/agents/` aparece en la descripción de la herramienta `task` y se puede invocar por nombre.",
        ],
    },
    # =====================================================================================
    "10": {
        "before": [
            "Tres ficheros pequeños, tres ideas: `forja/hooks.py` (10.1, 10.2), `forja/skills.py` (10.3, 10.4) y `forja/mcp_tools.py` (10.5). "
            "El harness (`forja/harness.py`) ya los llama: `self.hooks.run(\"PreToolUse\", {...}, tool.name)` en `gate`, "
            "`\"PostToolUse\"` tras ejecutar, `\"UserPromptSubmit\"` y `\"Stop\"` en `turn`; `skills.discover_skills(home/.forja/skills, root/.forja/skills)` "
            "al arrancar; `mcp_tool_name` dentro de `connect_servers`.",
            "API de hooks: `subprocess.run(cmd, shell=True, cwd=..., input=<json str>, capture_output=True, text=True, timeout=...)` devuelve un "
            "`CompletedProcess` con `returncode`, `stdout`, `stderr`; lanza `subprocess.TimeoutExpired` si se agota el tiempo. `re.fullmatch(pattern, s)` "
            "casa con el string ENTERO (así `edit_file|write_file` funciona como alternativa). Con `shell=True` el shell es cmd.exe en Windows y "
            "`/bin/sh` en macOS/Linux.",
            "Convención de códigos de salida (la misma que los agentes comerciales): `0` = OK (stdout puede ser contexto útil), `2` = BLOQUEO (stderr, o stdout si está vacío, es el "
            "mensaje para el modelo), cualquier otro = error del hook (se registra, nunca bloquea). `HookOutcome` tiene `block`, `message`, `context`, `errors`.",
            "Las skills reutilizan el parseo de frontmatter que escribiste en 09.1 (`FRONTMATTER` + `yaml.safe_load`). `catalog()` ya está escrita: solo necesita "
            "`Skill.name` y `Skill.description`.",
            "Mira `examples/project/.forja/settings.json` y `examples/project/.forja/hooks/*.py`: un hook PreToolUse real lee el evento con "
            "`json.load(sys.stdin)` y sale con 2 y un mensaje en stderr.",
        ],
        "order": "10.1 → 10.2 (un test cubre ambos: `test_hook_matching_and_exit_codes`; luego `test_hooks_in_harness` comprueba la integración), "
                 "después 10.5 (una línea, victoria rápida), y luego 10.3 → 10.4 (ambos comprobados por `test_skills`). Deja `test_mcp_end_to_end` para el final: "
                 "arranca un subproceso de servidor MCP real y necesita que los labs 02-04 funcionen.",
        "todos": {
            "10.1": {
                "where": "`forja/hooks.py` · `HookRunner.matching(event: str, tool_name: str | None = None) -> list[dict]`",
                "contract": "Devuelve, en el orden de la configuración, los dicts de hook de `self.config.get(event, [])` que aplican. Un hook SIN `matcher` aplica siempre. "
                            "Un hook CON `matcher` aplica solo si `tool_name` no es `None` y `re.fullmatch(matcher, tool_name)` casa. Evento desconocido → `[]`. "
                            "Test: `[h.get(\"matcher\") for h in runner.matching(\"PreToolUse\", \"bash\")] == [\"bash\", None]`, "
                            "`len(matching(\"PreToolUse\", \"write_file\")) == 2`, `matching(\"Stop\") == []`.",
                "steps": [
                    "Obtén la lista del evento con `.get(event, [])` (que falten eventos es normal).",
                    "Para cada hook lee `h.get(\"matcher\")`.",
                    "Sin matcher → consérvalo.",
                    "Matcher pero sin `tool_name` (eventos como `Stop`/`UserPromptSubmit`) → omítelo.",
                    "Matcher y `tool_name` → consérvalo solo si `re.fullmatch` tiene éxito. Mantén el orden original.",
                ],
                "gotchas": [
                    "`re.match`/`re.search` en lugar de `fullmatch`: `bash` casaría también con `bash_tool`, y `edit_file|write_file` con `re.match` "
                    "acepta prefijos. El test espera exactamente 2 hooks para `write_file`.",
                    "`self.config[event]` lanza `KeyError` para eventos que nadie configuró — `matching(\"Stop\")` debe devolver `[]`.",
                    "Los matchers son REGEX, no globs: en settings escribe `mcp__issues__.*`, no `mcp__issues__*` (esa es la sintaxis de las reglas de permisos).",
                ],
                "hints": [
                    "Tres casos por hook: sin matcher, matcher sin nombre de herramienta, matcher con nombre de herramienta.",
                    "`re.fullmatch(matcher, tool_name)` devuelve un objeto match o `None`.",
                    "```python\nout = []\nfor h in self.config.get(event, []):\n    matcher = h.get(\"matcher\")\n"
                    "    if matcher and <no tool_name or no fullmatch>:\n        continue\n    out.append(h)\nreturn out\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k hook_matching -v",
            },
            "10.2": {
                "where": "`forja/hooks.py` · `HookRunner.run(event: str, payload: dict, tool_name: str | None = None) -> HookOutcome`",
                "contract": "Serializa `{\"hook_event_name\": event, \"cwd\": str(self.cwd), **payload}` a JSON (`ensure_ascii=False, default=str`) y lo envía por "
                            "stdin a CADA hook que case (se ejecutan todos, incluso después de un bloqueo). Por hook: salida 2 → `block=True` y añade `stderr` (o `stdout`, o "
                            "un texto por defecto) con strip + salto de línea a `message`; salida 0 → añade el `stdout` no vacío con strip a `context`; otros códigos → añade una "
                            "descripción a `errors`; `TimeoutExpired` → añade a `errors` y continúa. Usa `h.get(\"timeout\", self.timeout)`. Al final haz strip de "
                            "`message` y `context`. Tests: PreToolUse con hooks que salen con 2 / 0 / 1 → `block` y `message == \"no\"` y `len(errors) == 1`; "
                            "UserPromptSubmit que imprime `ctx:` + prompt → `context == \"ctx:hello\"`, sin bloquear, 1 error. En el harness "
                            "(`test_hooks_in_harness`): `BLOCKED by hook` en el resultado de la herramienta y el hook Stop fuerza una ronda más.",
                "steps": [
                    "Crea un `HookOutcome()` vacío y construye el string JSON una sola vez.",
                    "Para cada hook de `self.matching(event, tool_name)` llama a `subprocess.run` con `h[\"command\"]`, `shell=True`, `cwd=self.cwd`, "
                    "el JSON como `input`, `capture_output=True`, `text=True` y el timeout.",
                    "Envuelve la llamada en `try/except subprocess.TimeoutExpired` → registra un error, `continue`.",
                    "Ramifica según `returncode`: 2 → bloqueo + mensaje; 0 → contexto si stdout tiene texto; resto → errors (incluye el código y un trozo de stderr).",
                    "Tras el bucle, haz `.strip()` de `message` y `context` para que los saltos de línea finales no rompan las comparaciones exactas.",
                ],
                "gotchas": [
                    "Parar en el primer hook que bloquea: la configuración del test tiene un tercer hook (salida 1) que debe ejecutarse igualmente, dando `len(errors) == 1`.",
                    "Olvidar `text=True`: entonces `input` debe ser bytes y `stdout` vuelve como bytes → `TypeError` o `b'no'` != `'no'`.",
                    "No hacer strip: `message` sería `'no\\n'`; el test compara con `== \"no\"`.",
                    "Sin `cwd=self.cwd` los comandos de hook relativos (`python .forja/hooks/x.py`) y el hook Stop del test (`pathlib.Path('DONE')`) buscan en la carpeta equivocada.",
                    "Windows: el test construye comandos como `\"C:/path/python.exe\" -c \"...\"`; eso solo funciona con `shell=True` (cmd.exe interpreta las comillas).",
                ],
                "hints": [
                    "Ejecuta cada comando una vez con el evento en stdin y fíjate solo en `returncode`, `stdout`, `stderr`.",
                    "`p = subprocess.run(h[\"command\"], shell=True, cwd=self.cwd, input=data, capture_output=True, text=True, timeout=h.get(\"timeout\", self.timeout))`.",
                    "```python\noutcome = HookOutcome()\ndata = json.dumps({...}, ensure_ascii=False, default=str)\nfor h in self.matching(event, tool_name):\n"
                    "    try: p = subprocess.run(...)\n    except subprocess.TimeoutExpired: outcome.errors.append(...); continue\n"
                    "    if p.returncode == 2: ...          # block, message += stderr or stdout\n    elif p.returncode == 0: ...        # context += stdout\n"
                    "    else: ...                          # errors\n# strip message and context\nreturn outcome\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k hook -v",
            },
            "10.3": {
                "where": "`forja/skills.py` · `discover_skills(*folders: Path) -> dict[str, Skill]`",
                "contract": "Para cada carpeta que exista, mira `<folder>/*/SKILL.md` (ordenados). Parsea el frontmatter; conserva solo los ficheros con `name` y `description`. "
                            "Guarda `Skill(name, description_normalised, path_to_SKILL.md)` bajo `name`; las carpetas posteriores sobrescriben a las anteriores (el harness pasa primero la carpeta "
                            "del usuario y después la del proyecto, así que gana el proyecto). Normaliza los espacios de la descripción: la descripción YAML del test ocupa dos líneas "
                            "y debe quedar exactamente `\"How to make commits here.\"`. Un `SKILL.md` sin frontmatter se omite (`list(sk) == [\"commits\"]`).",
                "steps": [
                    "Empieza con un dict vacío; recorre las carpetas en el orden dado y omite las que no sean directorios.",
                    "`sorted(folder.glob(\"*/SKILL.md\"))` — un nivel de subcarpetas, exactamente ese nombre de fichero.",
                    "Aplica `FRONTMATTER`; sin coincidencia → omítelo. Carga el YAML (protégete contra `None`).",
                    "Exige `name` y `description`; colapsa todos los espacios en blanco de la descripción en espacios simples.",
                    "Guarda `Skill(...)` con la ruta del propio fichero `SKILL.md` (10.4 lo vuelve a leer).",
                ],
                "gotchas": [
                    "Un valor YAML multilínea (`description: How to make\\n  commits here.`) lo pliega YAML, pero sé explícito: `\" \".join(str(d).split())` "
                    "garantiza espacios simples y ningún salto de línea, que es lo que `catalog()` necesita para producir `- commits: How to make commits here.`.",
                    "Salir antes de tiempo cuando falta la primera carpeta: la carpeta del usuario (`~/.forja/skills`) normalmente no existe — omítela y sigue.",
                    "Guardar la carpeta en vez de la ruta de `SKILL.md`: entonces 10.4 no consigue leer el cuerpo.",
                ],
                "hints": [
                    "Es otra vez 09.1 con otro glob y otra dataclass.",
                    "`folder.glob(\"*/SKILL.md\")`, `FRONTMATTER.match(f.read_text(encoding=\"utf-8\"))`, `\" \".join(str(meta[\"description\"]).split())`.",
                    "```python\nout = {}\nfor folder in folders:\n    if not folder.is_dir(): continue\n    for f in sorted(folder.glob(...)):\n"
                    "        m = ...; meta = ...            # None-safe\n        if <valid>:\n            out[meta[\"name\"]] = Skill(..., ..., f)\nreturn out\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k skills -v",
            },
            "10.4": {
                "where": "`forja/skills.py` · `make_skill_tool(skills)` → herramienta interna `skill(name: str) -> str`",
                "contract": "Nombre desconocido → `ValueError` listando las skills disponibles (o `none`). Nombre conocido → vuelve a leer `skill.path`, quita el frontmatter y devuelve "
                            "`# Skill: <name>`, una línea con la carpeta (`(folder: <path.parent>)`, para que el modelo encuentre scripts/plantillas junto a `SKILL.md`), una línea "
                            "en blanco y el CUERPO con strip. El test comprueba que el resultado contiene `Use conventional commits.` y NO contiene `---`. No cambies "
                            "el docstring: se convierte en la descripción de la herramienta y la sección `Args:` documenta `name`.",
                "steps": [
                    "Busca `skills.get(name)`; si no está, lanza `ValueError` con la lista de nombres.",
                    "Vuelve a leer el fichero (el cuerpo no se cachea: eso es la revelación progresiva).",
                    "Aplica `FRONTMATTER.match` y quédate con el grupo 2 con strip; si por lo que sea no casa, usa el texto entero como alternativa.",
                    "Devuelve la cabecera, la línea de la carpeta y el cuerpo.",
                ],
                "gotchas": [
                    "Devolver el fichero entero: las líneas `---` del frontmatter se cuelan en el resultado y el test falla en `\"---\" not in out`.",
                    "Devolver un string de error en vez de lanzar: \"funciona\", pero el resultado de la herramienta se marca como ok y el modelo no sabe que falló.",
                    "Si `test_skills` falla en `\"commits\" in llm.calls[0][\"messages\"][0][\"content\"]`, el catálogo no está llegando al system prompt: eso requiere que "
                    "`build_system_prompt` del lab 06 incluya `skills_catalog`.",
                ],
                "hints": [
                    "El catálogo (solo descripciones) ya está en el prompt; esta herramienta devuelve la parte que se dejó fuera.",
                    "`m = FRONTMATTER.match(s.path.read_text(encoding=\"utf-8\"))`; `m.group(2).strip()`.",
                    "```python\ns = skills.get(name)\nif s is None:\n    raise ValueError(f\"unknown skill: {name}. Available: ...\")\n"
                    "body = ...    # text without frontmatter\nreturn f\"# Skill: {s.name}\\n(folder: ...)\\n\\n{body}\"\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k skills -v",
            },
            "10.5": {
                "where": "`forja/mcp_tools.py` · `mcp_tool_name(server: str, tool: str) -> str`",
                "contract": "Devuelve `mcp__<server>__<tool>` donde cada carácter fuera de `[a-zA-Z0-9_]` en server Y en tool se sustituye por `_` (usa la regex precompilada "
                            "`NAME_RE`). Tests: `(\"issues\", \"get_issue\") -> \"mcp__issues__get_issue\"`, `(\"my-wiki\", \"search.docs\") -> \"mcp__my_wiki__search_docs\"`. "
                            "`connect_servers` (ya escrita) la usa para renombrar cada herramienta MCP; las herramientas MCP tienen riesgo `exec`, así que pasan por los permisos.",
                "steps": [
                    "Sanea el nombre del servidor con `NAME_RE.sub(\"_\", ...)`.",
                    "Sanea el nombre de la herramienta de la misma forma.",
                    "Únelos con el prefijo `mcp__` y un doble guion bajo entre ellos.",
                ],
                "gotchas": [
                    "Guiones bajos simples (`mcp_issues_get_issue`): las reglas de permisos como `mcp__issues__*` en `settings.json` no casarán nunca.",
                    "Sanear solo el nombre de la herramienta: un servidor llamado `my-wiki` produce un nombre de herramienta inválido que algunos modelos/servidores rechazan.",
                ],
                "hints": [
                    "Una línea con un f-string.",
                    "`NAME_RE.sub(\"_\", server)` sustituye cada carácter prohibido.",
                    "```python\nreturn f\"mcp__{...}__{...}\"\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k mcp -v",
            },
        },
        "try_it": [
            "Asegúrate de que existe `playground/.forja/` (copiado en el lab 09). La ruta del servidor MCP en `settings.json` (`../examples/mcp/issues_server.py`) "
            "se resuelve desde la raíz del proyecto (`playground/`), así que `forja --cwd playground` desde la raíz del repo funciona. Si el servidor falla verás "
            "una nota al arrancar `· MCP 'issues': …` y ninguna herramienta MCP.",
            "`/tools` → deberías ver `mcp__issues__list_issues`, `mcp__issues__get_issue`, `mcp__issues__comment_issue` con `[exec]`, y `skill [read]`.",
            "`list the open issues, fix #12 and comment on the issue what you changed`. Esperado: `⏺ mcp__issues__list_issues` (sin pedir aprobación: `mcp__issues__*` está "
            "en `allow`), lecturas/ediciones en `invoices/amounts.py`, una comprobación de compilación PostToolUse tras cada edición y, finalmente, `mcp__issues__comment_issue`.",
            "Observa el hook Stop (`.forja/hooks/stop_tests.py`): solo se ejecuta si hay cambios sin commitear en el proyecto (git), así que las preguntas no le afectan. "
            "Si el agente editó ficheros y dice que ha terminado con los tests en rojo, verás que sigue trabajando (se inyecta un mensaje de usuario `[Stop hook] You are not done yet…` "
            "con el final de la salida de pytest). Se rinde tras 3 rondas extra.",
            "`commit following the repo's convention` → la primera llamada debería ser `⏺ skill conventional-commits`, luego `git status`/`git diff`, y después un mensaje "
            "de commit como `fix(amounts): …`. (Se te pedirá aprobar `git commit`: no está en `allow`.)",
            "Prueba el hook PreToolUse: `run cat .env` → el resultado muestra `BLOCKED by hook: Command blocked by policy: it may expose secrets…`.",
        ],
        "troubleshooting": [
            ["`test_hook_matching_and_exit_codes`: `assert out.message == 'no'` falla con `'no\\n'`",
             "No hiciste strip → haz `.strip()` de `message`/`context` acumulados al final."],
            ["`len(out.errors) == 1` falla (0 errores)",
             "Haces `break` tras el hook que bloquea, así que el hook con salida 1 nunca se ejecuta → ejecuta todos los hooks que casen."],
            ["`TypeError: a bytes-like object is required` en `subprocess.run`",
             "Falta `text=True` → añádelo (input/stdout/stderr pasan a ser `str`)."],
            ["Windows: el test de hooks falla con `'C:/…/python.exe' is not recognized` o errores de comillas",
             "Si ejecutas sin `shell=True`, cmd.exe nunca interpreta el comando entrecomillado → mantén `shell=True` y pasa el comando como un único string."],
            ["Las respuestas terminan con `[Stop hook] You are not done yet…` aunque solo hayas hecho una pregunta",
             "`stop_tests.py` ejecuta los tests siempre que haya cambios sin commitear en `playground/` (p. ej. un arreglo a medias de un lab anterior) → termina el arreglo o haz `python scripts/tasks.py reset`. Fuera de git se ejecuta siempre."],
            ["No hay herramientas `mcp__issues__*`; nota al arrancar `· MCP 'issues': …`",
             "El servidor no arrancó → comprueba que la ruta es relativa a la raíz del proyecto (`playground/`), que `mcp` está instalado (`pip show mcp`), y ejecuta el servidor a mano: `python examples/mcp/issues_server.py`."],
            ["El hook PostToolUse/PreToolUse nunca se dispara para herramientas MCP",
             "El matcher es una regex con `fullmatch` → usa `mcp__issues__.*`, no el glob `mcp__issues__*`."],
            ["El modelo nunca llama a `skill`",
             "Los modelos pequeños ignoran los catálogos → haz que la descripción de la skill diga CUÁNDO cargarla ('Load it before running git commit') y menciónala en el prompt."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 10` → 5 passed (incluido `test_mcp_end_to_end`).",
            "[ ] En el CLI: `cat .env` queda bloqueado por el hook PreToolUse, y el hook Stop hace que el agente continúe mientras los tests están en rojo.",
            "[ ] `/tools` lista `skill` y las herramientas `mcp__issues__*`, y el agente carga `conventional-commits` antes de hacer commit.",
        ],
    },
    # =====================================================================================
    "11": {
        "before": [
            "Abre `forja/session.py`. Dos clases independientes: `Transcript` (11.1, 11.2: un fichero JSONL por sesión en `<project>/.forja/sessions/<id>.jsonl`) y "
            "`Checkpoints` (11.3, 11.4: una pila en memoria de turnos, cada uno `{Path: original bytes | None}`). `mark_compaction` y `list_sessions` ya están escritas: "
            "léelas, te dicen el formato de línea (`{\"ts\": ..., \"message\": m}` y `{\"ts\": ..., \"compacted\": [...]}`).",
            "Cómo las usa el harness: al final de `Forja.turn` llama a `self.transcript.append(*self.history[start:])` (solo los mensajes NUEVOS); `resume(id)` "
            "llama a `Transcript.load(folder, id)`. `Forja.turn` llama a `self.checkpoints.begin_turn()`, y `Workspace` llama a `checkpoints.before_write(path)` justo "
            "ANTES de que `write_file`/`edit_file` toquen un fichero (ver `forja/fs_tools.py`). `/undo` llama a `Checkpoints.undo()`.",
            "Stdlib: `json.dumps(obj, ensure_ascii=False)`, `json.loads(line)`, `Path.open(\"a\", encoding=\"utf-8\")` (modo append), `Path.read_bytes()` / "
            "`write_bytes()` (bytes, para que codificaciones y finales de línea se restauren exactamente), `Path.unlink(missing_ok=True)`, `Path.mkdir(parents=True, exist_ok=True)`.",
            "Límite a tener en cuenta: solo las herramientas de ficheros crean checkpoints. Lo que haga `bash` (`rm`, `pip install`, `sed -i`) no se puede deshacer.",
        ],
        "order": "11.1 y 11.2 juntos (un test de ida y vuelta: `test_transcript_roundtrip`), luego 11.3 y 11.4 juntos (`test_checkpoints`). Termina con "
                 "`test_harness_resume_and_undo`, que lo ejercita todo a través del harness real (necesita los labs 02-04 para `edit_file` en `accept_edits`).",
        "todos": {
            "11.1": {
                "where": "`forja/session.py` · `Transcript.append(self, *messages: dict) -> None`",
                "contract": "Crea `self.folder` si hace falta, abre `self.path` en modo APPEND (UTF-8) y escribe una línea por mensaje: "
                            "`json.dumps({\"ts\": <time.time() rounded>, \"message\": m}, ensure_ascii=False) + \"\\n\"`. Nunca reescribe líneas anteriores. "
                            "Se llama varias veces sobre el mismo fichero (el test añade 2 mensajes, luego 1 más, luego un marcador de compactación, luego 1 más).",
                "steps": [
                    "`self.folder.mkdir(parents=True, exist_ok=True)`.",
                    "Abre `self.path` con modo `\"a\"` y `encoding=\"utf-8\"` en un bloque `with`.",
                    "Para cada mensaje escribe un objeto JSON por línea con las claves `ts` y `message`.",
                ],
                "gotchas": [
                    "El modo `\"w\"` trunca el fichero: tras el segundo `append` solo sobrevive el último mensaje y la ida y vuelta falla.",
                    "Olvidar el `\"\\n\"` final: dos registros en una línea → `json.JSONDecodeError: Extra data` en `load`.",
                    "Windows: sin `encoding=\"utf-8\"` la página de códigos por defecto (cp1252) falla con `€`, `→` o texto acentuado en los mensajes.",
                    "Usa exactamente la clave `message`: `list_sessions` (ya escrita) lee `.get(\"message\")`.",
                ],
                "hints": [
                    "JSON Lines = un documento JSON completo por línea, que solo se va añadiendo.",
                    "`with self.path.open(\"a\", encoding=\"utf-8\") as f:` y luego `f.write(json.dumps({...}, ensure_ascii=False) + \"\\n\")`.",
                    "```python\nself.folder.mkdir(...)\nwith self.path.open(...) as f:\n    for m in messages:\n        f.write(...)   # {'ts': ..., 'message': m} + newline\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k transcript -v",
            },
            "11.2": {
                "where": "`forja/session.py` · `Transcript.load(folder: Path, session_id: str) -> list[dict]` (staticmethod)",
                "contract": "Lee `<folder>/<session_id>.jsonl`; si no existe lanza `FileNotFoundError`. Reconstruye el historial línea a línea: un registro con "
                            "`compacted` SUSTITUYE el historial entero por esa lista; un registro con `message` se añade. Omite las líneas en blanco. Test: tras "
                            "`[hello, how are you, second]` + compactación `[[Summary] x]` + `continuing`, el resultado es `[\"[Summary] x\", \"continuing\"]`. "
                            "El test del harness comprueba `app2.history == app.history` tras `resume`, así que los mensajes deben volver sin cambios (incluidos los `tool_calls`).",
                "steps": [
                    "Construye la ruta `folder / f\"{session_id}.jsonl\"`; lanza `FileNotFoundError` si no es un fichero.",
                    "Empieza con una lista vacía y lee el fichero como UTF-8, línea a línea.",
                    "Omite las líneas vacías; aplica `json.loads` al resto.",
                    "Si el registro tiene `compacted` → sustituye el historial por una copia de esa lista; si no, añade `record[\"message\"]`.",
                    "Devuelve el historial.",
                ],
                "gotchas": [
                    "Añadir la lista compactada en vez de sustituir: obtienes `hello, how are you, second, [Summary] x, continuing`.",
                    "Comprobar primero `if \"message\" in rec` e ignorar el resto descarta en silencio los marcadores de compactación — comprueba `compacted` primero.",
                    "Una línea vacía al final hace que `json.loads(\"\")` lance excepción — omite las líneas en blanco.",
                ],
                "hints": [
                    "El fichero es un log de eventos; reprodúcelo para reconstruir el estado.",
                    "`for line in p.read_text(encoding=\"utf-8\").splitlines():` y `rec = json.loads(line)`; ramifica según `\"compacted\" in rec`.",
                    "```python\np = folder / f\"{session_id}.jsonl\"\nif not p.is_file(): raise FileNotFoundError(...)\nhistory = []\nfor line in ...:\n"
                    "    if not line.strip(): continue\n    rec = ...\n    if \"compacted\" in rec: history = ...\n    else: history.append(...)\nreturn history\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k transcript -v",
            },
            "11.3": {
                "where": "`forja/session.py` · `Checkpoints.before_write(self, path: Path) -> None`",
                "contract": "Registra el estado ORIGINAL de `path` en el turno actual (el último) de `self.stack`: `path.read_bytes()` si existe, `None` si no. "
                            "Solo la PRIMERA vez que se ve una ruta dada en ese turno (escrituras posteriores en el mismo turno no deben sobrescribir el original). Si aún no hay "
                            "turno (`self.stack` vacío), llama antes a `self.begin_turn()`. Test: `a.txt` escrito dos veces en un turno debe deshacerse a `\"original\"`; "
                            "`new.txt` creado en el turno debe borrarse al deshacer.",
                "steps": [
                    "Si `self.stack` está vacío, `self.begin_turn()`.",
                    "Toma el dict del turno actual: `self.stack[-1]`.",
                    "Si `path` ya es una clave, no hagas nada.",
                    "Si no, guarda `path.read_bytes()` si `path.exists()`, o `None` en caso contrario.",
                ],
                "gotchas": [
                    "Sobrescribir el valor guardado en cada llamada: tras `v1` → `v2` deshacer restauraría `v1`, no `original`.",
                    "Guardar texto (`read_text`) en vez de bytes: los finales de línea CRLF en Windows y los ficheros no UTF-8 no vuelven exactamente igual.",
                    "Llamar a `begin_turn()` incondicionalmente aquí: cada escritura abriría un turno nuevo y `/undo` solo revertiría la última escritura.",
                ],
                "hints": [
                    "`None` significa \"este fichero no existía antes\" — deshacer lo borrará.",
                    "`turn = self.stack[-1]`; `if path not in turn: turn[path] = ...`.",
                    "```python\nif not self.stack: ...\nturn = self.stack[-1]\nif path not in turn:\n    turn[path] = ...  # bytes or None\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k checkpoints -v",
            },
            "11.4": {
                "where": "`forja/session.py` · `Checkpoints.undo(self) -> list[Path]`",
                "contract": "Descarta los turnos VACÍOS de la cima de la pila (turnos en los que no se escribió nada), luego saca el último turno no vacío y restaura cada "
                            "fichero que contiene: bytes originales → vuelve a escribirlos (creando las carpetas padre); `None` → borra el fichero (sin error si ya no está). Devuelve "
                            "las rutas restauradas ORDENADAS. Nada que deshacer → `[]`. Test: un turno vacío en la cima se omite, ambos ficheros se restauran, y un segundo "
                            "`undo()` devuelve `[]`. El `/undo` del CLI imprime `restored: <paths>` o `nothing to undo`.",
                "steps": [
                    "Mientras la pila no esté vacía y su último turno esté vacío, sácalo.",
                    "Si la pila queda vacía, devuelve `[]`.",
                    "Saca el último turno.",
                    "Para cada `(path, original)`: si `original is None` → `unlink(missing_ok=True)`; si no, `mkdir` del padre y `write_bytes(original)`.",
                    "Devuelve `sorted(...)` de las rutas del turno.",
                ],
                "gotchas": [
                    "No omitir los turnos vacíos: el harness llama a `begin_turn()` en CADA turno, así que una pregunta tras una edición haría que `/undo` dijera 'nothing to undo'.",
                    "Mirar (`self.stack[-1]`) en vez de sacar: un segundo `undo()` restauraría otra vez el mismo turno en vez de devolver `[]`.",
                    "Reescribir un fichero cuya carpeta se borró mientras tanto → `FileNotFoundError`; crea antes los padres.",
                ],
                "hints": [
                    "Piensa en la pila como una lista de instantáneas solo de los ficheros que tocó cada turno.",
                    "`while self.stack and not self.stack[-1]: self.stack.pop()`.",
                    "```python\n# drop empty turns from the end\nif not self.stack: return []\nturn = self.stack.pop()\nfor path, original in turn.items():\n"
                    "    if original is None: ...   # delete\n    else: ...                  # mkdir parent + write bytes\nreturn sorted(turn)\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k \"checkpoints or resume_and_undo\" -v",
            },
        },
        "try_it": [
            "`forja --cwd playground --mode accept_edits` y escribe `change the default due-date period to 60 days`. Esperado: un `edit_file invoices/dates.py` con un panel "
            "de diff (`days: int = 30` → `60`), sin pedir aprobación (accept_edits).",
            "`/undo` → `restored: invoices/dates.py`. Comprueba el fichero: vuelve a poner `30`. `/undo` otra vez → `nothing to undo`.",
            "Haz una pregunta simple (`what does due_date do?`), haz otra edición, otra pregunta, y luego `/undo`: sigue revirtiendo el último turno CON cambios (los turnos vacíos se omiten).",
            "`/sessions` → líneas como `20261103-143012-a1b2  change the default due-date period to 60 days`. Mira el fichero en bruto: macOS/Linux "
            "`cat playground/.forja/sessions/<id>.jsonl` · PowerShell `Get-Content playground\\.forja\\sessions\\<id>.jsonl` — un objeto JSON por línea.",
            "`/exit`, luego `forja --cwd playground --resume <id>` y pregunta `what did you change before?` → el agente responde a partir del historial restaurado.",
            "Fíjate en lo que NO se deshace: pide al agente `create a file tmp.txt using bash` y `/undo` → `tmp.txt` sigue ahí (`/undo` dice `nothing to undo`, o revierte en su lugar un turno de edición ANTERIOR). Limpia con `python scripts/tasks.py reset` si hace falta.",
        ],
        "troubleshooting": [
            ["`json.decoder.JSONDecodeError: Extra data` en `load`",
             "Dos registros en la misma línea → añade `\"\\n\"` tras cada `json.dumps` en `append`."],
            ["La ida y vuelta devuelve solo el último mensaje",
             "Abriste el fichero con `\"w\"` → usa el modo append `\"a\"`."],
            ["`test_checkpoints`: `a.txt` se restaura a `v1` en vez de `original`",
             "`before_write` sobrescribe el original guardado → guárdalo solo la primera vez que aparece la ruta en el turno."],
            ["`/undo` siempre dice `nothing to undo` tras una pregunta posterior",
             "No se omiten los turnos vacíos de la cima de la pila → saca los turnos vacíos antes de sacar el real."],
            ["`test_harness_resume_and_undo`: falla `app2.history == app.history`",
             "Los mensajes se modifican por el camino (p. ej. guardaste `str(m)` o solo `content`) → vuelca el dict entero como JSON y cárgalo de vuelta sin cambios."],
            ["`UnicodeEncodeError` / texto corrupto en `.jsonl` en Windows",
             "La página de códigos por defecto no es UTF-8 → pasa `encoding=\"utf-8\"` al abrir y al leer, y mantén `ensure_ascii=False`."],
            ["`--resume` dice que la sesión no existe",
             "Las sesiones viven en `<project>/.forja/sessions/` → reanuda con el mismo `--cwd` que usaste al crearla, y copia el id de `/sessions`."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 11` → 3 passed.",
            "[ ] `/undo` restaura un fichero editado por el agente y borra un fichero que creó, sin git.",
            "[ ] `forja --cwd playground --resume <id>` continúa la conversación anterior.",
        ],
    },
    # =====================================================================================
    "12": {
        "before": [
            "Abre `forja/evals.py` (tus TODOs: `grade` y `summarize`) y `evals/tasks.yaml` (las tareas). Ya escritas para ti: `load_tasks`, `snapshot(root)` "
            "(dict `relative path -> sha1`, ignorando `.forja`, `.git`, `__pycache__`, `.pytest_cache`), `norm(s)` (minúsculas + quitar acentos) y `run_task`, que copia "
            "`playground/` a un directorio temporal, ejecuta UN turno headless en modo `bypass` y luego llama a tu `grade(task, work, answer, before, repo_root)`.",
            "El runner es `evals/run_evals.py` (vía `python scripts/tasks.py evals ...`): flags `--model`, `--backend`, `--repeat N`, `--only <id>`, `--max-steps`, `--config <carpeta .forja>` (usa tus settings, hooks, skills y subagentes en cada tarea), `--mcp` y `--label <sufijo>` para el nombre del informe. Imprime una "
            "línea `PASS`/`FAIL` por ejecución, llama a tu `summarize` y escribe `out/evals_<model>.json` (`/` y `:` en el nombre del modelo se convierten en `_`).",
            "Stdlib: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, timeout=...)` y `subprocess.TimeoutExpired`; `shutil.copy(src, dst)`; "
            "`statistics.mean`; `dataclasses.asdict`. Campos de `TaskResult`: `id, passed, reason, steps, tool_calls, tokens, seconds, stop_reason, answer`.",
            "El dict `check` de una tarea puede contener: `command` (salida 0 = pass, `timeout` opcional, 120 s por defecto), `hidden` (`{repo-relative source: workdir-relative destination}`, "
            "copiado DESPUÉS de que el agente termine), `answer_contains` (lista de strings), `forbid_changes` (bool).",
            "Las evals usan TODO tu agente (labs 01-11). `test_run_task_pass_and_fail` maneja `read_file`, `edit_file` y `bash` a través del harness, así que esos labs deben pasar.",
        ],
        "order": "12.1 primero (`test_grade_answer_and_forbid_changes`, `test_hidden_tests_copied_after`, luego `test_run_task_pass_and_fail`), porque `run_task` y el "
                 "runner dependen de ello. 12.2 es aritmética independiente (`test_summarize`). Después ejecuta evals reales: empieza con `--only vat_question` (rápida, solo lectura).",
        "todos": {
            "12.1": {
                "where": "`forja/evals.py` · `grade(task, workdir, answer, before, repo_root) -> tuple[bool, str]`",
                "contract": "Aplica las comprobaciones en ESTE orden y vuelve en el primer fallo: (1) `forbid_changes` y `snapshot(workdir) != before` → `(False, <reason containing "
                            "'modified'>)`; (2) `answer_contains`: cada string, comparado con `norm()` en ambos lados, debe estar en la respuesta, si no `(False, <reason listing the "
                            "missing ones>)`; (3) copia cada fichero `hidden` de `repo_root / src` a `workdir / dst` (crea las carpetas padre); (4) si hay `command`: ejecútalo en `workdir` "
                            "con `shell=True`; timeout → `(False, ...)`; salida distinta de cero → `(False, <reason containing 'failed'> + the last 3 lines of stdout+stderr)`. "
                            "Todo bien → exactamente `(True, \"ok\")` (el test compara la tupla).",
                "steps": [
                    "Lee `chk = task.check`.",
                    "Si `chk.get(\"forbid_changes\")` y la instantánea actual difiere de `before`, falla con un motivo 'modified files…'.",
                    "Recoge los strings de `answer_contains` cuyo `norm(str(s))` no esté en `norm(answer)`; si hay alguno, falla y lístalos.",
                    "Para cada `(src, dst)` en `chk.get(\"hidden\") or {}`: crea `(workdir / dst).parent` y `shutil.copy(repo_root / src, workdir / dst)`.",
                    "Si hay un `command`, ejecútalo en `workdir` con `capture_output=True, text=True, timeout=chk.get(\"timeout\", 120)`; gestiona `TimeoutExpired`.",
                    "Si la salida no es cero, une en el motivo las últimas 3 líneas no vacías (tras trim) de `stdout + stderr` (p. ej. `\"check failed: \" + \" | \".join(tail)`).",
                    "Devuelve `(True, \"ok\")`.",
                ],
                "gotchas": [
                    "Copiar los ficheros `hidden` ANTES de la comprobación de `forbid_changes`: tu propia copia cuenta como cambio. El orden importa.",
                    "No usar `norm()`: `\"VAT\"` debe casar con `\"the vat\"` en la respuesta del test (sin distinguir mayúsculas; también se quitan los acentos).",
                    "Copiar los tests ocultos solo cuando el comando pasa: `test_hidden_tests_copied_after` comprueba que el fichero existe aunque la comprobación falle.",
                    "Olvidar `cwd=workdir`: el comando se ejecuta contra el playground REAL (o la raíz del repo) y el resultado no significa nada.",
                    "Windows: strings de `command` como `python -m pytest -q` necesitan `python` en el PATH → activa el venv en el terminal donde ejecutes las evals.",
                ],
                "hints": [
                    "Primero las comprobaciones baratas, luego los efectos secundarios (copiar ficheros), luego la cara (ejecutar el comando).",
                    "`missing = [s for s in chk.get(\"answer_contains\", []) if norm(str(s)) not in norm(answer)]`; "
                    "`tail = (p.stdout + p.stderr).strip().splitlines()[-3:]`.",
                    "```python\nchk = task.check\nif chk.get(\"forbid_changes\") and ...: return False, \"modified files in a read-only task\"\n"
                    "missing = ...\nif missing: return False, f\"the answer is missing: {missing}\"\nfor src, dst in ...: ...   # mkdir + copy\n"
                    "if chk.get(\"command\"):\n    try: p = subprocess.run(...)\n    except subprocess.TimeoutExpired: return False, ...\n"
                    "    if p.returncode != 0: return False, \"check failed: \" + ...\nreturn True, \"ok\"\n```",
                ],
                "test": "python -m pytest tests/test_l12_evals.py -k \"grade or hidden or run_task\" -v",
            },
            "12.2": {
                "where": "`forja/evals.py` · `summarize(results: list[TaskResult], model: str) -> dict`",
                "contract": "Devuelve un dict con las claves: `model`; `runs` = número de resultados; `pass_rate` = passed / runs redondeado a 3 decimales; `per_task` = `{task id: pass rate "
                            "rounded to 2}` (agrupando las repeticiones del mismo id); `avg_steps` y `avg_seconds` = medias redondeadas a 1 decimal (0 si no hay resultados); "
                            "`total_tokens` = suma de tokens; `results` = `[asdict(r) for r in results]`. Test: 3 resultados → `pass_rate == 0.667`, "
                            "`per_task == {\"a\": 0.5, \"b\": 1.0}`, `avg_steps == 4.0`, `total_tokens == 350`, `len(results) == 3`.",
                "steps": [
                    "Agrupa los resultados por `r.id` en un dict de listas (`setdefault` viene bien).",
                    "Calcula la tasa de aciertos global; protégete contra la división por cero con una lista vacía.",
                    "Calcula la tasa de aciertos por tarea a partir de cada grupo.",
                    "Calcula las medias de `steps` y `seconds` (protege la entrada vacía), y la suma de tokens.",
                    "Monta el dict exactamente con las claves de arriba; `results` vía `asdict`.",
                ],
                "gotchas": [
                    "Redondeo: `pass_rate` 3 decimales (`0.667`), `per_task` 2 decimales, medias 1 decimal. El test usa `==`.",
                    "`statistics.mean([])` lanza `StatisticsError` → protege las listas vacías (el runner con un `--only` erróneo da cero resultados).",
                    "`sum(r.passed for r in ...)` funciona porque `True == 1`; no cuentes `reason == \"ok\"` en su lugar.",
                    "`run_evals.py` lee `rep[\"pass_rate\"]`, `rep[\"avg_steps\"]`, `rep[\"avg_seconds\"]`, `rep[\"total_tokens\"]`, `rep[\"per_task\"]`, `rep[\"model\"]` — "
                    "una errata en el nombre de una clave hace que el runner pete después de todas las ejecuciones (lentas).",
                ],
                "hints": [
                    "Agrupa y luego agrega. Todo es una suma, un conteo o una media.",
                    "`by_task.setdefault(r.id, []).append(r)`; `round(statistics.mean(r.steps for r in results), 1)`.",
                    "```python\nby_task = {}\nfor r in results: ...\nn = len(results) or 1\nreturn {\n    \"model\": model, \"runs\": ...,\n"
                    "    \"pass_rate\": round(..., 3),\n    \"per_task\": {k: round(..., 2) for k, v in by_task.items()},\n"
                    "    \"avg_steps\": ..., \"avg_seconds\": ..., \"total_tokens\": ...,\n    \"results\": [asdict(r) for r in results],\n}\n```",
                ],
                "test": "python -m pytest tests/test_l12_evals.py -k summarize -v",
            },
        },
        "try_it": [
            "`python scripts/tasks.py evals --only vat_question` (solo lectura, la más rápida). Esperado: `» …run_evals.py --only vat_question`, luego una línea como "
            "`PASS  vat_question           18.4s   4 steps` (o `FAIL … the answer is missing: ['calculate_vat']`), y después el resumen "
            "`qwen3:8b: pass_rate 100% · 4.0 steps · 18.4s/task · 9123 tokens`, `per task: {...}` y `-> out/evals_qwen3_8b.json`.",
            "`python scripts/tasks.py evals --only fix_rounding` → una línea FAIL muestra como motivo las últimas 3 líneas de la salida de pytest. Fíjate en que tu `playground/` real nunca se modifica.",
            "`python scripts/tasks.py evals --repeat 3` (las 5 tareas × 3; tarda un rato en un portátil — lánzalo y sigue leyendo). Mira `per_task`: ¿qué tareas son inestables (0.33, 0.67)?",
            "Si tienes un segundo modelo: `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (o el servidor del aula con `--backend openai_compat`). "
            "Abre los dos ficheros `out/evals_*.json` y compara `pass_rate`, `avg_steps`, `avg_seconds`, `total_tokens`.",
            "Inspecciona un fallo: en el JSON, `results[i].answer` (primeros 500 caracteres) y `stop_reason` (`max_steps`, `loop`, `error`…) suelen decirte por qué.",
        ],
        "troubleshooting": [
            ["`grade(...) == (True, 'ok')` falla con `(False, 'modified files…')` en el test de forbid",
             "Copiaste los ficheros ocultos o ejecutaste el comando antes de la comprobación `forbid_changes`, o comparaste contra una instantánea nueva → comprueba primero `snapshot(workdir) != before`."],
            ["`test_grade_answer_and_forbid_changes`: 'the answer is missing: [VAT]'",
             "La comparación distingue mayúsculas → aplica `norm()` tanto al string esperado como a la respuesta."],
            ["`test_hidden_tests_copied_after`: el fichero oculto no existe",
             "Vuelves antes de copiar, o solo copias si hay éxito → copia los ficheros ocultos antes de ejecutar el comando, sea cual sea el resultado."],
            ["`test_run_task_pass_and_fail`: `ok.passed` es False / `steps != 5`",
             "Labs anteriores están rotos en tu harness (edit_file, bash, permisos en bypass) → ejecuta `python scripts/tasks.py test 03` y `test 04`; o `catchup 12` si vas justo de tiempo."],
            ["Todas las evals reales dan FAIL con `EXCEPTION …` o `stop_reason: error`",
             "El backend no es accesible o el modelo no está descargado → `forja doctor`, `ollama list`, revisa `.env`."],
            ["Windows: `check failed: 'python' is not recognized…`",
             "El comando de comprobación se ejecuta con cmd.exe y el venv no está activo en ese terminal → `.venv\\Scripts\\activate` antes de ejecutar las evals."],
            ["`StatisticsError: mean requires at least one data point`",
             "`--only` con un id desconocido da cero resultados → protege las listas vacías en `summarize` (y revisa cómo se escribe el id)."],
            ["Los resultados varían mucho entre ejecuciones",
             "Los modelos no son deterministas → compara siempre con `--repeat 3` o más y mira `per_task`, no una sola ejecución."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 12` → 5 passed.",
            "[ ] Tienes al menos un `out/evals_<model>.json` generado con `--repeat 3`.",
            "[ ] Puedes decir, con números (tasa de aciertos, pasos, segundos, tokens), qué modelo usarías para qué tareas.",
        ],
        # ---------------------------------------------------------------------------------
        "capstone": {
            "intro": "Proyecto final (16:00–17:00): personaliza Forja para tu forma de trabajar y demuéstralo con números. Cinco entregables, todos pequeños. Trabaja en `playground/` "
                     "(o en un repo real tuyo para 1–4) y lleva una lista corta de `NOTES` con lo que cambiaste para la demo de 3 minutos. Presupuesto: ~10 min por entregable, 15 min para las evals.",
            "deliverables": {
                "1_agents_md": {
                    "title": "AGENTS.md: preferencias globales + uno por repo",
                    "where": "Global: `~/.forja/AGENTS.md` (macOS/Linux) · `%USERPROFILE%\\.forja\\AGENTS.md` (Windows; en PowerShell `$HOME\\.forja\\AGENTS.md`). "
                             "Proyecto: `AGENTS.md` (o `FORJA.md`) en la raíz del repo; los ficheros se recogen desde la raíz del sistema de ficheros hasta `--cwd`, primero el global, "
                             "así que el más cercano es el más específico.",
                    "steps": [
                        "Crea la carpeta: macOS/Linux `mkdir -p ~/.forja` · PowerShell `New-Item -ItemType Directory -Force $HOME\\.forja`.",
                        "Escribe 5–10 viñetas de preferencias PERSONALES (idioma, verbosidad, hábitos de testing). Que sea breve: se envía en cada turno.",
                        "En un repo real tuyo, escribe `AGENTS.md` con: cómo ejecutar los tests, el comando de build/lint, las convenciones y las cosas que nunca deben hacerse.",
                        "Comprueba que se carga: arranca `forja --cwd <repo>` y pregunta `which instructions are you following?` — debería citar ambas capas "
                        "(el prompt contiene `## User global instructions` y `## Project instructions (AGENTS.md)`).",
                    ],
                    "template": "```markdown\n# AGENTS.md — <project>\n\n- Stack: <language/version>, <framework>.\n- Tests: `<command>`. Run them after every code change.\n"
                                "- Lint/format: `<command>`.\n- Conventions: <naming, error handling, logging>.\n- Never: <edit generated files / touch migrations / change public APIs without asking>.\n"
                                "- When unsure, ask before large refactors.\n```",
                    "pitfall": "Las evals se ejecutan con un home temporal, así que `run_evals.py` NO usa `~/.forja/AGENTS.md`; solo `playground/AGENTS.md` (copiado con el proyecto). "
                               "Si quieres medir un cambio en las instrucciones, ponlo en `playground/AGENTS.md`.",
                },
                "2_skill": {
                    "title": "Una skill de equipo",
                    "where": "`<project>/.forja/skills/<skill-name>/SKILL.md` (proyecto) o `~/.forja/skills/<skill-name>/SKILL.md` (personal; si coinciden los nombres gana el proyecto). "
                             "Los ficheros extra (scripts, plantillas) pueden vivir en la misma carpeta: la herramienta `skill` le dice al modelo la ruta de la carpeta.",
                    "steps": [
                        "Elige un procedimiento que expliques una y otra vez: checklist de release, rúbrica de code review, cómo añadir un endpoint, pasos de migración de BD…",
                        "Escribe el frontmatter: `name` (kebab-case, = nombre de la carpeta) y una `description` que diga QUÉ es y CUÁNDO cargarla.",
                        "Escribe el cuerpo como pasos numerados con comandos exactos. Mantenlo por debajo de ~60 líneas.",
                        "Comprueba el descubrimiento: `/tools` muestra `skill`, y un prompt que la necesite produce `⏺ skill <name>` como una de las primeras llamadas.",
                    ],
                    "template": "```markdown\n---\nname: add-endpoint\ndescription: How to add a REST endpoint in this repo (routing, validation, tests). Load it before creating or changing an endpoint.\n---\n"
                                "# Adding an endpoint\n\n1. Route in `<file>`; handler in `<folder>/<name>.py`.\n2. Validate input with <library>; return <error format> on failure.\n"
                                "3. Add a test in `tests/<...>` covering success and one error.\n4. Run `<test command>` before finishing.\n```",
                    "pitfall": "Si el modelo nunca la carga, la descripción es demasiado vaga. Di cuándo: 'Load it before …'. Mira `examples/project/.forja/skills/conventional-commits/SKILL.md`.",
                },
                "3_hook": {
                    "title": "Un hook que garantiza algo que ahora pides por favor",
                    "where": "Script en `<project>/.forja/hooks/<name>.py`; registro en `<project>/.forja/settings.json` bajo `hooks.<Event>` "
                             "(`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`). Los comandos se ejecutan con `cwd` = raíz del proyecto a través del shell (cmd.exe en Windows).",
                    "steps": [
                        "Elige el evento: bloquear algo → `PreToolUse`; dar feedback tras una edición (lint, compilación, comprobación de formato) → `PostToolUse`; "
                        "'no termines hasta X' → `Stop`; inyectar contexto o filtrar prompts → `UserPromptSubmit`.",
                        "Escribe el script: lee el evento con `json.load(sys.stdin)` (`tool_name`, `tool_input`, y `tool_response` para PostToolUse; `prompt` para UserPromptSubmit), "
                        "decide, imprime el motivo en stderr y haz `sys.exit(2)` para bloquear/dar feedback, `sys.exit(0)` en caso contrario.",
                        "Regístralo con un `matcher` regex (coincidencia completa con el nombre de la herramienta, p. ej. `edit_file|write_file`, `bash`, `mcp__issues__.*`); omite el matcher para aplicarlo a todas.",
                        "Prueba primero el script solo. macOS/Linux: `echo '{\"tool_name\":\"bash\",\"tool_input\":{\"command\":\"cat .env\"}}' | python .forja/hooks/<name>.py; echo $?` · "
                        "PowerShell: `'{\"tool_name\":\"bash\",\"tool_input\":{\"command\":\"cat .env\"}}' | python .forja\\hooks\\<name>.py; $LASTEXITCODE`.",
                        "Después dispáralo desde el CLI y comprueba que ves `BLOCKED by hook: …` (Pre) o `[hook PostToolUse] …` en el resultado de la herramienta (Post).",
                    ],
                    "template": "```python\n\"\"\"PostToolUse (edit_file|write_file): <what it guarantees>. Exit 2 = feedback to the model.\"\"\"\nimport json, subprocess, sys\n\n"
                                "event = json.load(sys.stdin)\npath = event.get(\"tool_input\", {}).get(\"path\", \"\")\nif not path.endswith(\".py\"):\n    sys.exit(0)\n"
                                "p = subprocess.run([\"ruff\", \"check\", \"--quiet\", path], capture_output=True, text=True)\nif p.returncode != 0:\n"
                                "    print(f\"Lint errors in {path}:\\n{p.stdout[-2000:]}\", file=sys.stderr)\n    sys.exit(2)\nsys.exit(0)\n```\n"
                                "```json\n\"hooks\": {\"PostToolUse\": [{\"matcher\": \"edit_file|write_file\", \"command\": \"python .forja/hooks/lint.py\", \"timeout\": 30}]}\n```",
                    "pitfall": "La salida 1 NO bloquea (se registra como error del hook y se ignora): usa la salida 2. Un hook `Stop` lento se ejecuta en cada respuesta final — que sea rápido (`-x`, un subconjunto de tests).",
                },
                "4_subagent": {
                    "title": "Un perfil de subagente especializado",
                    "where": "`<project>/.forja/agents/<name>.md`. Claves de frontmatter que lee `load_profiles`: `name`, `description` (obligatorias), `tools` (lista o string `a, b`; "
                             "por defecto `read_file, grep, glob`), `max_steps` (por defecto 25). Nombres de herramienta válidos: `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `bash`, `todo_write`, "
                             "`skill`, `mcp__<server>__<tool>` (`task` se elimina siempre). El cuerpo es su system prompt.",
                    "steps": [
                        "Elige un trabajo acotado en el que ayude un contexto limpio: triaje de tests fallidos, revisión de seguridad, redactor de documentación, auditor de dependencias, un `tester` que solo ejecuta pytest.",
                        "Dale las herramientas MÍNIMAS. Roles de solo lectura: `read_file, grep, glob` (+ `bash` si necesita `git diff`/pytest, y añade las reglas `allow` correspondientes en settings).",
                        "Escribe la descripción desde el punto de vista del agente principal: qué hace y cuándo delegar en él.",
                        "Escribe el cuerpo: rol, método (numerado) y el formato de salida exacto que quieres recibir (es lo único que verá el agente principal).",
                        "Comprueba: el perfil aparece en la descripción de la herramienta `task`; pide `use the <name> subagent to …` y busca llamadas con prefijo `[<name>]`.",
                    ],
                    "template": "```markdown\n---\nname: tester\ndescription: Runs the test suite and explains failures with the likely cause and file:line. Use it after code changes or when tests fail.\n"
                                "tools: read_file, grep, glob, bash\nmax_steps: 15\n---\nYou are a test triage specialist. Only run `python -m pytest` commands with bash; never modify files.\n"
                                "1. Run the suite (`python -m pytest -q -x`).\n2. For each failure, read the test and the code under test.\n"
                                "Answer with: a one-line verdict, then per failure `test name — cause — path:line — suggested fix (1 sentence)`.\n```",
                    "pitfall": "La restricción de herramientas es por NOMBRE; un subagente con `bash` puede ejecutar cualquier comando que tus permisos permitan. Para restringir comandos, apóyate en las reglas `allow`/`deny` "
                               "(p. ej. `bash(python -m pytest*)`) y en las aprobaciones — las llamadas del subagente pasan por la misma puerta que las del agente principal.",
                },
                "5_eval": {
                    "title": "Una tarea de eval para tu trabajo diario + un informe de 2 modelos",
                    "where": "Añade la tarea a `evals/tasks.yaml` (al FINAL: `test_tasks_file` espera que `fix_rounding` y `fix_due_date` sigan siendo las primeras). Los tests ocultos van en "
                             "`evals/hidden/` y se referencian como `{\"evals/hidden/<file>.py\": \"tests/<dest>.py\"}`. Los informes van a `out/evals_<model>.json`. "
                             "Las tareas siempre se ejecutan sobre una copia de `playground/`, así que expresa tu trabajo diario sobre el proyecto de facturas.",
                    "steps": [
                        "Elige un tipo de tarea que hagas cada semana: un bug fix pequeño, una feature con tests, un refactor que debe mantener los tests en verde, o una pregunta sobre el código.",
                        "Escribe el prompt como un ticket (qué, no cómo). Elige una comprobación OBJETIVA: `command` (tests), `hidden` (tests que el agente no puede ver — lo mejor para features), "
                        "`answer_contains` (+ `forbid_changes: true` para preguntas).",
                        "Para una comprobación `hidden`, escribe el fichero de test oculto en `evals/hidden/` y verifica que FALLA sobre el playground sin tocar (si no, la tarea no mide nada).",
                        "Ejecútala sola: `python scripts/tasks.py evals --only <id> --repeat 3`. Itera el prompt/la comprobación hasta que un pass signifique 'hecho bien'.",
                        "Ejecuta la misma tarea (o la suite completa) con dos modelos: `python scripts/tasks.py evals --model qwen3:8b --repeat 3` y "
                        "`python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (o `--backend openai_compat` / `--backend openrouter --model <open-weight model>`).",
                        "Escribe el informe: una tabla a partir de los dos ficheros JSON (pass rate, per_task de tu tarea, avg steps, avg seconds, total tokens) + 2–3 frases de conclusión.",
                    ],
                    "template": "```yaml\n- id: my_overdue_flag\n  prompt: \"Add a method Invoice.is_overdue(today) that returns True when today is after the due date. Add a test.\"\n"
                                "  check: {command: \"python -m pytest -q tests/test_overdue_hidden.py\", hidden: {\"evals/hidden/test_overdue.py\": \"tests/test_overdue_hidden.py\"}}\n\n"
                                "- id: my_question\n  prompt: \"Without modifying anything: where is the due date computed and what happens on weekends?\"\n"
                                "  check: {answer_contains: [\"dates.py\", \"due_date\"], forbid_changes: true}\n```\n"
                                "Esqueleto del informe (Markdown):\n```markdown\n| model | pass rate | my task | avg steps | avg s | tokens |\n|---|---|---|---|---|---|\n"
                                "| qwen3:8b | 0.60 | 0.33 | 9.1 | 41.0 | 120k |\n| qwen3-coder:30b | … | … | … | … | … |\n\nConclusion: <which model for which task, and why>.\n```\n"
                                "Para imprimir los números: `python -c \"import json,glob; [print(r['model'], r['pass_rate'], r['per_task'], r['avg_steps'], r['avg_seconds'], r['total_tokens']) "
                                "for r in map(lambda f: json.load(open(f, encoding='utf-8')), glob.glob('out/evals_*.json'))]\"`",
                    "pitfall": "Por defecto `run_task` copia el playground SIN `.forja/` (solo cuenta `playground/AGENTS.md`). Para medir tu configuración ejecuta dos veces y compara: "
                               "`python scripts/tasks.py evals --repeat 3 --label base` y `python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config`. "
                               "`~/.forja/AGENTS.md` nunca se usa (home temporal). Las rutas MCP de `settings.json` se resuelven desde la copia temporal: usa rutas absolutas con `--mcp`.",
                },
            },
            "demo": [
                "3 minutos por persona/pareja: 30 s qué has añadido (enseña los ficheros), 90 s un prompt en directo donde se vea actuar una skill/hook/subagente, 60 s la tabla de evals y tu conclusión.",
                "Trae números, no impresiones: 'la tasa de aciertos en mi tarea pasó de 0.33 a 1.0 con qwen3-coder:30b a 2× el tiempo'.",
            ],
            "done_when": [
                "[ ] Existen el `AGENTS.md` global y el de proyecto, y el agente puede citarlos.",
                "[ ] El agente carga una skill (`⏺ skill <name>`) cuando procede.",
                "[ ] Un hook bloquea o da feedback de forma visible (`BLOCKED by hook` / `[hook PostToolUse]`).",
                "[ ] Un perfil de subagente aparece en la descripción de `task` y se usa (llamadas `[<name>]`).",
                "[ ] Una tarea nueva en `evals/tasks.yaml`, `python scripts/tasks.py test 12` sigue pasando, y dos informes `out/evals_*.json` comparados en una tabla.",
            ],
        },
    },
}
