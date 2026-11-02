# Guía del tutor · Forja: construye tu propio agente de código con modelos locales

🇬🇧 [English](tutor_guide.md) · Material del alumno: [`docs/alumno/cuaderno_alumno.md`](../alumno/cuaderno_alumno.md) · Labs: [`labs/`](../../labs)

## 1. Qué consiguen los asistentes

Al terminar, cada asistente tiene **su propio agente de código de terminal** —el mismo tipo de herramienta que Claude Code, Codex CLI u OpenCode— funcionando con **modelos abiertos en local**, y sabe explicar y modificar cada pieza:

| Capa | Pieza | Lab |
|---|---|---|
| Modelo | Cliente streaming para Ollama / vLLM / LM Studio / OpenRouter | 01 |
| Agente | Tools de ficheros, bucle, bash | 02, 03, 04 |
| Harness | Permisos y aprobación, CLI, contexto, compactación, plan, subagentes, hooks, skills, MCP, sesiones, undo | 04–11 |
| Calidad | Evals con tareas reales y tests ocultos | 12 |

**Resultados de aprendizaje (lo que deben saber explicar):**
1. Por qué un agente es *modelo + tools + bucle* y todo lo demás es harness.
2. Cómo llegan las tool calls en streaming y por qué el historial tiene pares `tool_calls`/`tool` que no se pueden romper.
3. Por qué `edit_file` es sustitución exacta y por qué se exige leer antes de editar.
4. Cómo se decide un permiso (deny > plan > allow > modo > preguntar) y por qué las reglas de bash se evalúan por subcomando.
5. Qué entra en el contexto cada turno y cómo se compacta sin romper el historial.
6. Cuándo planificar, cuándo delegar en un subagente y cuándo una política debe ser un hook y no una instrucción.
7. Cómo medir un agente con evals y comparar modelos con datos.

## 2. Formato

- **2 días**, 7 h efectivas cada uno. Día 1 = *un agente que funciona*; día 2 = *un harness profesional*.
- **Versión de 1 día:** labs 00–05 completos + demos en vivo (sin práctica) de 06, 08 y 10 con `python scripts/tasks.py demo`.
- **Cada lab:** 10–15 min de teoría con el deck → 25–45 min de práctica con tests → 2 min de checkpoint en voz alta.
- **Parejas recomendadas** (uno escribe, otro lee el cuaderno y los tests), rotando cada lab.
- **Sin asistentes de IA en el IDE** durante los labs: el objetivo es entender, y los tests ya dan feedback inmediato.

### Agenda
| Día 1 | | Día 2 | |
|---|---|---|---|
| 09:00 | L00 Setup y tour | 09:00 | L06 Contexto |
| 09:30 | L01 Cliente streaming | 09:40 | L07 Compactación |
| 10:15 | L02 Tools de ficheros | 10:25 | L08 Plan y tareas |
| 11:15 | *Pausa* | 11:10 | *Pausa* |
| 11:30 | L03 Bucle | 11:25 | L09 Subagentes |
| 12:15 | L04 Bash y permisos | 12:10 | L10 Hooks, skills, MCP |
| 13:00 | *Comida* | 13:20 | *Comida* |
| 14:00 | L05 CLI | 14:20 | L11 Sesiones y undo |
| 15:00 | *Pausa* | 14:55 | L12 Evals |
| 15:15 | **Hito: tu agente arregla el playground** | 16:00 | **Proyecto final + demos** |
| 16:30 | Retro del día | 17:00 | Cierre |

## 3. Preparación

| Cuándo | Qué | ✔ |
|---|---|---|
| T-14 | Confirmar hardware de los asistentes con la tabla de `docs/hardware.png` (o el checklist). Decidir si hace falta **servidor compartido** | ☐ |
| T-14 | Si hay servidor: GPU NVIDIA 24 GB+ con vLLM sirviendo `Qwen/Qwen3-Coder-30B-A3B-Instruct` (o Ollama con `qwen3-coder:30b` y `OLLAMA_NUM_PARALLEL`) | ☐ |
| T-10 | Enviar `docs/checklist_setup.md` (EN: `docs/setup_checklist.md`): descargar modelos antes (≈ 5–19 GB según nivel) | ☐ |
| T-7 | Clave de OpenRouter del workshop con límite de gasto, solo modelos open-weight (plan B) | ☐ |
| T-3 | Verificar que los tags de Ollama y los ids de OpenRouter de `.env.example` siguen existiendo | ☐ |
| T-2 | `python scripts/tasks.py starters` y `python scripts/tasks.py solutions` → todo verde | ☐ |
| T-2 | Ensayo completo con modelo real: `python scripts/tasks.py demo` sobre `playground/` (arreglar los 3 tests, modo plan con descuentos, subagente, hooks con `examples/project/.forja`) | ☐ |
| T-2 | `python scripts/tasks.py evals --repeat 3` con 2 modelos: tus cifras de referencia (no se enseñan; sirven para detectar problemas) | ☐ |
| T-1 | Repo del alumno (`TxeBals/devopsday-workshop`, sin soluciones) publicado. Lleva `forja-solutions.zip` (está en tu carpeta) en USB/Teams: `catchup` lo necesita en la raíz del repo del alumno o con `--from` | ☐ |
| T-1 | Repo en un git accesible (o USB). Plan B de red: wheelhouse (`pip download -r … -d wheels`) y modelos en USB (`~/.ollama/models`) | ☐ |
| T-0 | Decks ES/EN abiertos, terminal con fuente grande, `playground` limpio (`python scripts/tasks.py reset`) | ☐ |

**Windows:** la tool `bash` usa `cmd.exe` (el agente lo sabe por la descripción de la tool). Todo el repo funciona con `python scripts/tasks.py …` sin `make`. Para copiar carpetas: `xcopy /E /I`.

## 4. Gestión del aula

- **Semáforo:** al empezar la práctica, cada pareja marca verde (tests pasan), ámbar (atascada <10 min) o rojo. A los 2/3 del tiempo, quien esté en rojo hace `python scripts/tasks.py catchup NN+1` y sigue. **Nunca esperes al último**: el diseño progresivo permite que todos lleguen al hito.
- **Ritmos distintos:** los rápidos hacen los *retos* del lab; no adelantan labs (rompe la puesta en común).
- **Modelos lentos:** quien no llegue a ~15 tok/s, al servidor compartido (`FORJA_BACKEND=openai_compat`).
- **Lo que más enseña:** proyectar la CLI de un alumno cuando el modelo hace algo raro y preguntar a la sala «¿qué pieza del harness lo arreglaría?».

## 5. Guion por lab

Para cada lab: **mensaje clave**, **demo** (con la solución: `python scripts/tasks.py demo`), **dónde se atascan**, **preguntas de control** y **si sobra tiempo**.

### L00 · Setup y tour (30 min)
- **Mensaje:** «El modelo es una pieza intercambiable. Hoy construimos el harness, que es lo que hace útil a un agente.»
- **Demo (5 min):** `python scripts/tasks.py demo` → *"haz que pasen los tests"*. Que vean diffs, permisos, tests en verde. «Mañana por la tarde esto lo habréis escrito vosotros.»
- **Contexto que conviene dar:** existen proyectos como OpenClaude (un fork del código filtrado de Claude Code), OpenCode, Aider o Pi. No usamos ninguno: construimos uno propio desde cero con la misma arquitectura, que está documentada públicamente. Así entendemos cada pieza y evitamos problemas de licencia y marca en un entorno corporativo.
- **Atascos:** Ollama sin arrancar; modelo sin plantilla de tools (`llama3`, `deepseek-r1:8b`); PowerShell que bloquea `activate` (`Set-ExecutionPolicy -Scope Process Bypass`).

### L01 · Cliente streaming (45 min)
- **Mensaje:** «En streaming, las tool calls también llegan troceadas. Ensamblarlas bien es la primera pieza seria.»
- **Demo:** `curl` con `"stream": true` contra Ollama pidiendo una tool: enseñar los chunks crudos con `index`, `id`, fragmentos de `arguments`.
- **Atascos:** `ThinkFilter` con etiquetas partidas (el test parametrizado lo cubre: que lean el caso que falla); olvidar `flush()`.
- **Preguntas:** ¿por qué no reintentar un 400? ¿Qué hace `data_collection: deny` en OpenRouter?
- **Si sobra tiempo:** medir *time-to-first-token* local frente a OpenRouter.

### L02 · Tools de ficheros (60 min)
- **Mensaje:** «La descripción de la tool es el prompt. Y los errores son datos: un buen mensaje de error ahorra un paso del bucle.»
- **Demo:** enseñar el JSON Schema generado (`/tools` en la demo) y un `edit_file` fallido por incluir números de línea, con el mensaje de pista.
- **Atascos:** `edit_file`: contar apariciones antes de sustituir; `check_fresh` (mtime) — explicar por qué existe (el humano o un formatter tocan el fichero). `Workspace.resolve`: `is_relative_to` tras `resolve()` para cubrir symlinks.
- **Preguntas:** ¿por qué no un formato diff? ¿Por qué numerar líneas en `read_file` pero prohibirlas en `old_string`?

### L03 · Bucle (45 min)
- **Mensaje:** «Un agente cabe en diez líneas. Escribidlas en la pizarra antes de abrir el fichero.»
- **Demo:** con la solución, una pregunta que provoque lecturas paralelas (*"resume todos los ficheros de invoices/"*): se ven varias `⏺ Read` seguidas.
- **Atascos:** romper el par `tool_calls`/`tool` al detectar un bucle (el test lo comprueba); mantener el orden de resultados en paralelo.
- **Preguntas:** ¿por qué solo paralelizar lecturas? ¿Qué pasa si el modelo llama dos veces a lo mismo?

### L04 · Bash y permisos (45 min)
- **Mensaje:** «La tool ejecuta; los permisos deciden. Y una regla allow nunca debe colar un segundo comando encadenado.»
- **Demo:** en la solución, `/mode default` → pedir *"ejecuta los tests"*, responder *a* (siempre) y ver la regla sugerida; luego pedir *"borra la carpeta invoices con rm -rf"* en modo bypass con el deny de `examples/project`.
- **Atascos:** `decide` por subcomando; `suggest_rule` para `python -m pytest`.
- **Preguntas:** ¿por qué `bypass` solo en sandbox? ¿Qué no puede deshacer `/undo` (lab 11)?

### L05 · CLI (60 min) + Hito (75 min)
- **Mensaje:** «La experiencia es parte del producto: ver qué hace, cómo cambia el código y poder pararlo.»
- **Hito:** todos con su propia Forja arreglan los 3 tests del `playground`. Antes: `python scripts/tasks.py reset`. Recoge en la pizarra: modelo · ¿lo consiguió? · pasos · tiempo. Esa tabla introduce el lab 12.
- **Atascos:** Ctrl+C en Windows dentro de `input()`; `handle_slash` con `/mode` sin argumento.
- **Retro (16:30):** ¿qué ha fallado más: el modelo o el harness? (Spoiler: casi siempre el harness: errores poco claros, contexto, permisos.)

### L06 · Contexto (40 min)
- **Mensaje:** «El system prompt se reconstruye cada turno. Lo que no está en el contexto, no existe para el modelo.»
- **Demo:** imprimir `app.system_prompt()` de la solución y señalar cada capa; borrar el `AGENTS.md` del playground y repetir la pregunta del redondeo: el agente vuelve a usar `round()`.
- **Atascos:** orden de los AGENTS.md (más específico al final); `@menciones` que no son ficheros (emails).

### L07 · Compactación (45 min)
- **Mensaje:** «Microcompactar es gratis; resumir cuesta una llamada y pierde información. Y nunca se corta entre una tool call y su resultado.»
- **Demo:** `.forja/settings.json` con `"contextWindow": 6000`, trabajar hasta que salte la nota de compactación, `/context` antes y después.
- **Preguntas:** ¿qué debe conservar el resumen sí o sí? ¿Cómo comprobarías que la compactación no empeora al agente? (→ lab 12).

### L08 · Plan y tareas (45 min)
- **Mensaje:** «Con modelos pequeños, una lista de tareas visible marca la diferencia en tareas largas. El modo plan es solo lectura por permisos, no por educación.»
- **Demo:** `--mode plan` → *"añade descuentos a las facturas con tests"*: investigación, plan, aprobación y ejecución marcando tareas.

### L09 · Subagentes (45 min)
- **Mensaje:** «Delegar es comprar contexto: el subagente gasta 30k tokens y te devuelve 300.»
- **Demo:** `/context` antes y después de una exploración con subagente frente a hacerla en el principal.
- **Atascos:** el subagente no ve la conversación: el prompt de `task` debe ser autocontenido (que lo vean en la descripción de la tool).

### L10 · Hooks, skills, MCP (70 min)
- **Mensaje:** «AGENTS.md pide; un hook impide. Es la misma convención que usan los agentes comerciales (JSON por stdin, exit 2 bloquea).»
- **Demo:** copiar `examples/project/.forja` al playground: hook Stop que no deja terminar con tests en rojo, skill de commits y MCP de issues (*"arregla la issue #12 y coméntala"*).
- **Atascos:** exit 1 ≠ bloquear (solo exit 2); rutas relativas de los comandos de hooks (se ejecutan en la raíz del proyecto).

### L11 · Sesiones y undo (35 min)
- **Mensaje:** «Todo lo que hace el agente debe poder auditarse y deshacerse. Lo que no se puede deshacer (bash), pasa por permisos.»
- **Demo:** una edición, `/undo`, `/sessions`, `--resume`.

### L12 · Evals (65 min)
- **Mensaje:** «Sin medir, todo es opinión. Y los tests ocultos evitan que el agente haga trampa.»
- **Demo:** `python scripts/tasks.py evals --repeat 3` con dos modelos (lanzarlo al empezar el lab: tarda).
- **Cierre:** recuperar la tabla del hito del día 1 y compararla con las evals: ¿coincide la intuición con los datos?

### Proyecto final (60 min)
Rúbrica (sobre 10): AGENTS.md útil (1) · skill propia (2) · hook que garantiza algo real (2) · subagente especializado (2) · tarea de eval propia con informe de 2 modelos (3). Demos de 3 minutos.

## 6. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `Connection refused :11434` | Ollama parado | `ollama serve` o abrir la app |
| `does not support tools` | modelo sin plantilla de tools | `qwen3:8b`, `qwen3-coder:30b`, `devstral` |
| El modelo no llama tools / las olvida | contexto corto por defecto | `OLLAMA_CONTEXT_LENGTH=32768` y reiniciar Ollama |
| Respuestas de > 60 s | CPU o swap | modelo más pequeño o servidor compartido |
| `NotImplementedError: TODO NN.x` | lab pendiente | es lo esperado; `catchup` si hace falta |
| Avisos «lab NN pendiente» en la CLI | diseño progresivo | desaparecen al completar el lab |
| HTTP 400 con `tool_call_id` | historial roto | revisar 03.2 (cierre de llamadas al detectar bucle) y 07.2 |
| `edit_file` falla una y otra vez | el modelo copia números de línea o cambia indentación | mirar el mensaje de pista; modelos más grandes fallan menos |
| bash en Windows: `ls` no existe | cmd.exe | el agente debería usar `dir`; o `powershell -Command` |
| PowerShell no activa el venv | política de ejecución | `Set-ExecutionPolicy -Scope Process Bypass` |
| MCP no arranca | ruta del comando relativa | los comandos se ejecutan en el directorio desde el que lanzas `forja` |
| Hook no bloquea | devuelve exit 1 | solo exit 2 bloquea |

## 7. Material del tutor

- `solutions/forja/`: implementación de referencia completa. `python scripts/tasks.py demo` la ejecuta sobre el playground.
- `scripts/make_starters.py`: regenera `forja/` (alumno) desde la solución. Si cambias la solución: `python scripts/tasks.py starters`.
- `scripts/labs_content.py` + `scripts/build_docs.py`: fuente única de los README de lab y los cuadernos. Edita el contenido allí y regenera.
- Guion completo del ponente (todas las notas): [guion_ponente.md](guion_ponente.md)
- Decks: [ES](https://claude.ai/artifact/GkGG788cUiMgA9Xs238Yag) · [EN](https://claude.ai/artifact/CV6PaTZE4j8D58Gtpw2nKt) — notas del ponente en cada diapositiva con el mensaje y la demo.

## 8. Después del workshop
- Encuesta ([enlace]).
- Reto a 2 semanas: usar su Forja en un repo real con un AGENTS.md, una skill y un hook, y traer el informe de evals.
