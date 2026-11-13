# Lab 09 · Subagentes

🇬🇧 [English](README.en.md) · Día 2 · 11:25–12:10

**Objetivo:** Delegar exploraciones y revisiones en agentes con contexto propio y tools restringidas.

## Conceptos
- **El problema:** explorar un repo cuesta 20 lecturas y 30k tokens que se quedan en el contexto del agente principal para siempre.
- **La solución:** la tool `task` lanza un subagente con contexto LIMPIO (system + prompt) que devuelve solo la conclusión. El principal paga ~300 tokens.
- **Mismo bucle, otras tools:** reutilizamos `Agent` del lab 03 con un subconjunto de tools y la MISMA puerta de permisos. Un subagente no lanza subagentes.
- **Perfiles en Markdown:** `.forja/agents/reviewer.md` con frontmatter (name, description, tools). La descripción es lo que lee el modelo para decidir cuándo delegar.
- **El prompt del subagente debe ser autocontenido:** no ve la conversación.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: perfiles desde Markdown |
| 09.2 | `forja/subagents.py` | task: lanzar un subagente con contexto limpio |

## Antes de empezar
- Abre `forja/subagents.py` (tus TODOs) y ten abiertos al lado `forja/agent.py` (lab 03) y `forja/harness.py` (`_build_registry`). El harness ya llama a `subagents.load_profiles(root / ".forja" / "agents")` y registra `subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events)`: tú solo rellenas las dos funciones.
- Lo que reutilizas: `Agent(llm, tools, execute=..., events=..., max_steps=...)` y su `run(messages) -> AgentResult` (campos `answer`, `stop_reason`, `steps`, `tool_calls`, `usage`). `ToolRegistry.subset(names)` construye un registro solo con los nombres que existen (los nombres desconocidos se omiten en silencio).
- Stdlib / librerías usadas: `Path.glob("*.md")`, `Path.read_text(encoding="utf-8")`, la regex precompilada `FRONTMATTER` (grupo 1 = YAML entre las líneas `---`, grupo 2 = cuerpo) y `yaml.safe_load` (devuelve un dict, o `None` para un YAML vacío). `tools: read_file, grep` en YAML es un *string*; `tools: [read_file, grep]` es una *lista*.
- Idea clave: el subagente parte de una lista `messages` NUEVA (system + prompt del usuario). Nunca ve el historial principal; el agente principal solo recibe el string que devuelve tu herramienta `task`. Aun así, cada llamada a herramienta del subagente pasa por `execute` = la puerta del harness (hooks, permisos, aprobaciones, checkpoints).
- Mira `examples/project/.forja/agents/reviewer.md` para ver un perfil real (tiene `tools` y `max_steps`).

## Paso a paso
Haz primero 09.1: es puro parseo, tiene su propio test aislado (`test_load_profiles`) y el harness lo necesita para construir la lista de subagentes que aparece en la descripción de la herramienta `task`. Después 09.2, cuyos tests (`test_task_isolated_context`, `test_unknown_subagent`) pasan por el harness completo, así que los labs 02-04 ya deben pasar.

### TODO 09.1 · `forja/subagents.py` · `load_profiles(folder: Path) -> dict[str, AgentProfile]`

**Qué debe hacer:** Recibe la carpeta de agentes (puede no existir). Devuelve un dict `name -> AgentProfile` que SIEMPRE contiene el perfil integrado `explore` (parte de una copia de `BUILTIN`, nunca mutes el propio `BUILTIN`). Por cada fichero `*.md` con frontmatter válido que tenga `name` y `description`, añade `AgentProfile(name, description, system=<body stripped>, tools=<list[str]>, max_steps=<int, default 25>)`. Los ficheros sin frontmatter o sin `name`/`description` se omiten en silencio. El test comprueba: `set(p) == {"explore", "reviewer"}`, `tools == ["read_file", "grep"]` (a partir del string `read_file, grep`), `max_steps == 5`, `system == "You are a reviewer."`, y que una carpeta inexistente devuelve exactamente `BUILTIN`.

**Pasos:**
1. Crea `profiles = dict(BUILTIN)`; si la carpeta no es un directorio, devuélvelo directamente.
2. Recorre los ficheros `*.md` en un orden estable (`sorted`). Lee cada uno como UTF-8 y aplica `FRONTMATTER.match`.
3. Sin coincidencia → omítelo. Con coincidencia → `yaml.safe_load(group 1)`, y trata `None` como `{}`.
4. Omítelo si falta `name` o `description` o están vacíos.
5. Normaliza `tools`: por defecto `["read_file", "grep", "glob"]`; si es un string, divídelo por comas y haz strip de cada elemento, descartando los vacíos; si ya es una lista, mantenla.
6. Construye el perfil: el cuerpo (grupo 2) con `.strip()` es el system prompt; `max_steps` con `int(...)` y valor por defecto 25. Guárdalo bajo su `name` (un fichero puede sobrescribir `explore` si usa ese nombre).

**Cuidado con:**
- Devolver el propio `BUILTIN` y luego añadirle cosas muta la constante del módulo: el siguiente test (`load_profiles(missing) == BUILTIN`) o la siguiente instancia del harness verán perfiles obsoletos. Cópialo.
- `tools: read_file, grep` es el string `'read_file, grep'`. Si olvidas dividirlo obtienes `['r','e','a',...]` al iterarlo, o un único nombre de herramienta desconocido — y `subset()` descarta en silencio los nombres desconocidos, así que el subagente acaba SIN herramientas.
- `system` debe ser el cuerpo *sin* el frontmatter y con strip: el test lo compara exactamente.
- `yaml.safe_load` sobre un frontmatter que solo contiene comentarios devuelve `None`: hacer `.get` sobre él lanza `AttributeError`.

<details><summary>💡 Pista 1</summary>

Es el mismo parseo "frontmatter + cuerpo" que volverás a hacer para las skills en el lab 10. La regex ya está compilada para ti.

</details>

<details><summary>💡 Pista 2</summary>

`m = FRONTMATTER.match(text)`; `meta = yaml.safe_load(m.group(1)) or {}`; `m.group(2).strip()` es el system prompt. `isinstance(tools, str)` te dice cuándo dividir.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
profiles = dict(BUILTIN)
if not folder.is_dir(): return profiles
for f in sorted(folder.glob("*.md")):
    m = ...            # FRONTMATTER.match on the file text
    if not m: continue
    meta = ...         # yaml, never None
    if <missing name or description>: continue
    tools = ...        # default list; split 'a, b' strings
    profiles[meta["name"]] = AgentProfile(...)
return profiles
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l09_subagents.py -k load_profiles -v
```

### TODO 09.2 · `forja/subagents.py` · `make_task_tool(...)` → herramienta interna `task(description, prompt, subagent_type="explore") -> str`

**Qué debe hacer:** `make_task_tool` ya está escrita salvo el cuerpo de `task`. Dentro de `task`: busca `profiles[subagent_type]`; si no existe lanza `ValueError` cuyo mensaje contenga `unknown` y liste los nombres disponibles (el registro lo convierte en un resultado de herramienta fallido; `test_unknown_subagent` comprueba que contiene `"unknown"`). Construye el registro del subagente con `parent_tools.subset(...)` usando las herramientas del perfil MENOS `"task"`. Crea un `Agent` con el mismo `llm`, ese subregistro, `execute=execute`, `max_steps=prof.max_steps` y `events=events_factory(prof.name)` si se pasó una factoría, si no `Events()`. Ejecútalo sobre una lista NUEVA `[{"role": "system", "content": prof.system}, {"role": "user", "content": prompt}]`. Devuelve una cabecera que contenga `subagent <name>` (el test busca `"subagent explore"`), p. ej. `[subagent explore · <description> · N steps · M tools · <stop_reason>]`, luego un salto de línea y `res.answer`. El test también comprueba que la primera llamada al LLM del subagente tuvo exactamente 2 mensajes empezando por el system prompt de explore, que se le ofrecieron exactamente `{read_file, grep, glob}`, y que el historial principal solo contiene UN mensaje de herramienta (`task`).

**Pasos:**
1. Busca el perfil; si no está, `raise ValueError(f"unknown subagent: ... Available: ...")`.
2. Calcula los nombres de herramientas permitidos: las `tools` del perfil sin `"task"` (sin recursión).
3. `sub_tools = parent_tools.subset(those names)`.
4. Elige el objeto de eventos: `events_factory(prof.name)` cuando la factoría no es `None`, si no `Events()`. En el CLI esta factoría imprime las llamadas a herramientas del subagente con el prefijo `[explore]`.
5. Envuelve `execute` en un pequeño `sub_execute(call)`: si `call.name` no está en `sub_tools.tools`, devuelve `ToolResult(call.id, call.name, False, "ERROR: tool '...' is not available to subagent '...'")`; si no, delega en `execute` (o en `sub_tools.execute` cuando `execute` es `None`). La lista de esquemas solo *ofrece* herramientas; el modelo puede llamar a otras igualmente.
6. Crea el `Agent` (mismo `llm`, `execute=sub_execute`, `max_steps=prof.max_steps`) y llama a `run` con una lista NUEVA de dos mensajes.
7. Formatea y devuelve la línea de cabecera + el `answer` del subagente (usa `res.steps`, `res.tool_calls`, `res.stop_reason`).

**Cuidado con:**
- Reutilizar o copiar el historial del padre: el subagente debe empezar limpio (`len(messages) == 2` en su primera llamada).
- Pasar `parent_tools` en vez del subconjunto: el subagente tendría `write_file`, `bash`, `task`… y `test_task_isolated_context` falla en el conjunto de herramientas.
- Olvidar pasar por `execute`: el subagente se saltaría la puerta (sin permisos, sin hooks, sin checkpoints).
- Fiarse de la lista de herramientas ofrecida: `test_subagent_cannot_use_tools_outside_its_profile` hace que el modelo llame a `write_file` desde `explore`; tu wrapper debe rechazarlo y el fichero no debe existir.
- El mismo `FakeLLM` sirve al agente principal y al subagente en orden de llamada: si tu `task` hace una llamada extra al LLM (o ninguna), todas las respuestas guionizadas se desplazan y las aserciones fallan de formas confusas.
- No toques `task.description`: se asigna después de la función e incluye el catálogo que lee el modelo para elegir subagente.

<details><summary>💡 Pista 1</summary>

Todo el subagente es simplemente el `Agent` del lab 03 con un registro más pequeño y una lista de mensajes nueva.

</details>

<details><summary>💡 Pista 2</summary>

`parent_tools.subset([t for t in prof.tools if t != "task"])`; `Agent(llm, sub_tools, execute=sub_execute, max_steps=..., events=...)`; `res = agent.run(messages)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
prof = profiles.get(subagent_type)
if prof is None: raise ValueError(...)  # 'unknown', list names
sub_tools = ...                 # subset, never 'task'
def sub_execute(call): ...     # refuse names not in sub_tools.tools
events = ...                    # factory(name) or Events()
agent = Agent(...)
res = agent.run([...])         # system + user ONLY
return f"[subagent {prof.name} · ...]\n{res.answer}"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l09_subagents.py -k "task_isolated or unknown_subagent or outside_its_profile" -v
```

## Ejecuta
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> usa un subagente para averiguar todos los sitios donde se redondea
> pide al subagente reviewer que revise mis cambios sin commitear
```

## Pruébalo en tu agente
1. Copia la configuración del proyecto de ejemplo al playground. macOS/Linux: `cp -r examples/project/.forja playground/` · PowerShell: `Copy-Item -Recurse examples\project\.forja playground\.forja` · cmd: `xcopy /E /I examples\project\.forja playground\.forja`.
2. `forja --cwd playground`, y luego `/tools`: deberías ver `task [read]` al final de la lista, y ninguna nota `subagents: lab 09 pending` al arrancar.
3. Escribe `use a subagent to find every place where amounts are rounded`. Esperado: `⏺ task …`, luego líneas sangradas `  [explore] ⏺ grep …` / `  [explore] ⏺ read_file …` (las llamadas del subagente; su texto no se muestra en streaming), y finalmente la respuesta del agente principal listando ubicaciones `path:line`.
4. Ejecuta `/context` antes y después: el contexto principal crece unos cientos de tokens, no el tamaño de cada fichero que leyó el subagente.
5. Edita algo a mano en `playground/invoices/` y luego: `ask the reviewer subagent to review my uncommitted changes`. Deberías ver `  [reviewer] ⏺ bash git diff …` (permitido por `bash(git diff*)` en settings) y una revisión con secciones numeradas.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_task_isolated_context` falla con `StopIteration` / FakeLLM 'no more responses' | Tu `task` llama al LLM un número distinto de veces (p. ej. ejecutaste `agent.run` dos veces, o el bucle principal del lab 03 está roto) → un `Agent.run` por llamada a task; ejecuta antes `tests/test_l03_agent.py`. |
| Aserción sobre `{t['function']['name'] ...} == {'read_file','grep','glob'}` | Pasaste el registro completo del padre, o incluiste `task` → usa `parent_tools.subset(...)` filtrando `task`. |
| El subagente no tiene herramientas / responde sin leer nada | En 09.1 no se dividió `tools` (string `'read_file, grep'`), así que `subset()` descartó todos los nombres → divide por comas y haz strip. |
| `reviewer` no aparece en la descripción de `task` / 'unknown subagent: reviewer' | El fichero del perfil no tiene frontmatter `---` en la primerísima línea, o le falta `description` → arregla el fichero; los perfiles se leen de `<project>/.forja/agents/`, así que comprueba que copiaste `.forja` en `playground/`. |
| Sin prefijo `[explore]` en el CLI, las llamadas del subagente parecen del principal | Ignoraste `events_factory` y usaste siempre `Events()` (entonces no ves nada) o pasaste los eventos principales → usa `events_factory(prof.name)` cuando no sea `None`. |
| El modelo pequeño nunca delega | Los modelos de 8B suelen preferir hacerlo ellos mismos → pídelo explícitamente ('use a subagent…'); la descripción de `task` es lo único que lee para decidir. |
| Windows: `cp -r` falla en cmd.exe | `cp` solo existe en PowerShell (como alias) → usa `xcopy /E /I examples\project\.forja playground\.forja` en cmd. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 09` → 3 passed.
- [ ] [ ] En el CLI ves llamadas a herramientas con prefijo `[explore]` y `/context` apenas crece tras una búsqueda delegada.
- [ ] [ ] El perfil `reviewer` de `.forja/agents/` aparece en la descripción de la herramienta `task` y se puede invocar por nombre.

## Checkpoint
Ves las tool calls del subagente con prefijo `[explore]` y el contexto del principal apenas crece (`/context`).

## Retos
1. Crea un subagente `tester` que solo pueda ejecutar `python -m pytest*`.
2. Ejecuta el subagente con un modelo más pequeño y rápido.

**Tests:** `tests/test_l09_subagents.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 10`

---
[← anterior](../L08_planning/README.md) · [siguiente →](../L10_extensions/README.md)
