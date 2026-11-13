# Lab 03 · El bucle del agente

🇬🇧 [English](README.en.md) · Día 1 · 11:30–12:15

**Objetivo:** Escribir el bucle que convierte un modelo en un agente: pensar → actuar → observar, hasta terminar.

## Conceptos
- **Diez líneas:** pedir respuesta con tools → si no pide tools, fin → ejecutar → añadir resultados → repetir. Todo framework de agentes es esto con más capas.
- **El historial es el estado:** cada `assistant` con `tool_calls` va seguido de un mensaje `tool` por cada `tool_call_id`. Romper ese par = error 400 en casi cualquier backend.
- **Lecturas en paralelo, escrituras en orden:** varias `read_file`/`grep` a la vez se ejecutan en paralelo; una edición y un `pytest` nunca.
- **Paradas explícitas:** respuesta final, máximo de pasos, bucle detectado (misma tool + mismos argumentos) e interrupción del usuario (Ctrl+C).
- **El bucle no sabe de permisos ni de interfaz:** recibe una función `execute` (la puerta del harness) y unos `events`. Por eso lo reutilizamos para subagentes y evals.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: lecturas consecutivas en paralelo, orden preservado |
| 03.2 | `forja/agent.py` | run: el bucle con streaming, paradas y detección de bucles |

## Antes de empezar
- Abre `forja/agent.py` (`Events`, `AgentResult`, `Agent` y tus dos TODOs), `forja/fake_llm.py` (`FakeLLM`, `say`, `call`, `calls`: el modelo con guion que usan los tests) y `tests/test_l03_agent.py`.
- Protocolo de mensajes (Chat Completions): un mensaje del assistant con `tool_calls` debe ir seguido de un mensaje `{"role": "tool", "tool_call_id": …}` por cada llamada, antes del siguiente mensaje del assistant. `ChatResponse.to_message()` y `ToolResult.to_message()` (ya hechos) te construyen esos dicts.
- `self.llm.stream(messages, tools=...)` emite `TextDelta` y un `Done` final (tu lab 01, o `FakeLLM` en los tests, que emite el texto en trozos de 8 caracteres). `self.tools.schemas()` (lab 02) es la lista `tools`.
- Stdlib: `concurrent.futures.ThreadPoolExecutor` (`ex.map(fn, iterable)`), `collections.Counter`, `threading.Event.is_set()`.
- Cómo encaja: el harness crea `Agent(llm, registry, execute=self.gate, events=RichEvents(), …)`. El bucle no sabe nada de permisos ni de UI — solo llama a `execute` y a `events`. La misma clase se reutiliza para subagentes (lab 09) y evals (lab 12).

## Paso a paso
Empieza por el camino sin herramientas de 03.2 (stream, añadir el mensaje del assistant, devolver `"final"`, más la comprobación de cancelación): eso pone en verde `test_final_answer`, `test_streaming_events` y `test_cancel`. Después escribe 03.1 `_run_calls` y completa 03.2 con la ejecución de herramientas, `max_steps` y la detección de bucles. Todos los tests de 03.1 pasan por `run`, así que necesitas ambos.

### TODO 03.1 · `forja/agent.py` · `Agent._run_calls(calls)`

**Qué debe hacer:** `_run_calls(calls: list[ToolCall]) -> list[ToolResult]`, resultados en el MISMO orden que `calls`. Usa `self.execute` si está definido; si no, `self.tools.execute`. Para cada llamada: `self.events.on_tool_start(call)`, ejecutar, `self.events.on_tool_end(call, result)`. Las secuencias de llamadas CONSECUTIVAS de riesgo read (`self._is_read(call)`) se ejecutan en paralelo en un `ThreadPoolExecutor` cuando `self.parallel_reads`; todo lo demás se ejecuta secuencialmente y en orden.

**Pasos:**
1. Elige la función de ejecución: `self.execute or self.tools.execute`.
2. Reserva `results = [None] * len(calls)` y escribe una pequeña función interna `run(i)` que lance el evento de inicio, ejecute `calls[i]` guardándolo en `results[i]` y lance el evento de fin.
3. Recorre las llamadas con un índice `i`. Si `calls[i]` es una lectura, avanza `j` mientras las llamadas sean lecturas.
4. Si el bloque tiene más de una lectura, ejecuta los índices `i..j-1` con un `ThreadPoolExecutor` (p. ej. hasta 8 workers); una sola lectura se ejecuta sin más. Pon `i = j`.
5. Llamadas que no son lectura: `run(i)` e `i += 1`.
6. Devuelve la lista de resultados.

**Cuidado con:**
- `test_parallel_reads_keep_order`: tres lecturas de 0.2 s + una escritura deben tardar < 0.5 s Y producir los contenidos de tool `["r1", "r2", "r3", "wa"]` con los ids en el orden original. Guarda por índice; el orden de `as_completed` es aleatorio.
- Solo lecturas CONSECUTIVAS: `[read, write, read]` no debe ejecutar la segunda lectura antes de la escritura.
- `test_custom_execute_gate` comprueba que se usa tu gate: llamar directamente a `self.tools.execute` se salta los permisos en la CLI real.
- Consume `ex.map(...)` (p. ej. `list(...)`) o las excepciones de los workers se pierden en silencio; salir del bloque `with` espera a que terminen todos.

<details><summary>💡 Pista 1</summary>

Escribir por índice (`results[i] = …`) es lo que mantiene el orden, sin importar qué hilo termine primero.

</details>

<details><summary>💡 Pista 2</summary>

`with ThreadPoolExecutor(max_workers=min(8, j - i)) as ex: list(ex.map(run, range(i, j)))`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
execute = self.execute or self.tools.execute
results = [None] * len(calls)
def run(i): ...   # start event, execute, end event
i = 0
while i < len(calls):
    if self.parallel_reads and self._is_read(calls[i]):
        ...  # find j, pool or single
    else:
        ...
return results
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l03_agent.py -k "parallel or gate" -v
```

### TODO 03.2 · `forja/agent.py` · `Agent.run(messages)`

**Qué debe hacer:** `run(messages: list[dict]) -> AgentResult(answer, stop_reason, steps, usage, tool_calls)`. `messages` se MODIFICA IN SITU (el harness lo lee después). Motivos de parada: `"final"` (sin tool calls; answer = `resp.content or ""`, steps = paso actual), `"interrupted"` (`self.cancel` activado al inicio de un paso; steps = step - 1), `"loop"` (mismo nombre de herramienta + misma cadena de argumentos pedida más de `self.max_repeats` veces en esta ejecución), `"max_steps"` (steps = `self.max_steps`). `usage` suma todas las respuestas; `tool_calls` cuenta las llamadas ejecutadas. El historial debe seguir siendo válido en todos los casos: cada id de `tool_call` recibe un mensaje `tool`.

**Pasos:**
1. Crea un `Counter` para usage, un `Counter` para los pares `(name, arguments)` y un contador de llamadas.
2. `for step in range(1, self.max_steps + 1)`: primero, si `self.cancel.is_set()`, devuelve el resultado `"interrupted"`.
3. Stream: `self.llm.stream(messages, tools=self.tools.schemas() or None)`; reenvía cada `TextDelta` a `self.events.on_text` y quédate con la respuesta del `Done`.
4. Suma su usage, `messages.append(resp.to_message())`, llama a `self.events.on_assistant(resp)`.
5. Sin `resp.tool_calls` → devuelve `"final"`.
6. Detección de bucles: cuenta cada `(c.name, c.arguments)`; si alguno supera `self.max_repeats`, añade un `ToolResult(cc.id, cc.name, False, "Not executed: loop detected.").to_message()` fallido para CADA llamada de esta respuesta y devuelve `"loop"`.
7. Si no, `results = self._run_calls(resp.tool_calls)`, actualiza el contador y extiende `messages` con `r.to_message()` de cada resultado. Tras el `for`, devuelve `"max_steps"`.

**Cuidado con:**
- `test_final_answer` espera `steps == 1` y que el último mensaje sea el del assistant.
- `test_streaming_events` comprueba que `on_text` recibió MÁS DE UN trozo: reenvía cada `TextDelta`, no emitas el texto completo al final.
- Usa `resp.to_message()`: un `{"role": "assistant", "content": …}` hecho a mano sin `tool_calls` rompe el emparejamiento y los backends reales responden HTTP 400.
- `test_max_steps_and_loop` recorre el historial tras una parada `"loop"` y comprueba que no queda ningún id de tool_call abierto → cierra todas las llamadas pendientes antes de retornar.
- Pasa `tools=None` cuando no haya esquemas: algunos servidores rechazan `tools=[]`.

<details><summary>💡 Pista 1</summary>

Escribe primero la versión de diez líneas (stream → añadir → ¿sin herramientas? retornar → ejecutar llamadas → añadir → repetir), y después añade la cancelación, la detección de bucles y los contadores.

</details>

<details><summary>💡 Pista 2</summary>

`Counter.update(dict)` suma los valores clave a clave — perfecto para `resp.usage`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
usage, seen, n_calls = Counter(), Counter(), 0
for step in range(1, self.max_steps + 1):
    if self.cancel.is_set(): return AgentResult(...)
    resp = None
    for ev in self.llm.stream(...):
        ...  # TextDelta -> on_text, Done -> resp
    ...  # usage, append, on_assistant, final?
    ...  # loop detection (close pending calls!)
    ...  # run calls, append tool messages
return AgentResult(..., "max_steps", self.max_steps, ...)
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l03_agent.py -k "final or streaming or cancel or max_steps" -v
```

## Ejecuta
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explícame cómo se calcula el total de una factura
```

## Pruébalo en tu agente
1. `python scripts/tasks.py test 03` → `6 passed`.
2. `forja --cwd playground` y pregunta `explain how an invoice total is calculated`. Deberías VER líneas azules por cada tool call, p. ej. `⏺ grep {"pattern": "def total", …}` seguidas de un `⎿ invoices/invoice.py:…` atenuado (args en JSON crudo hasta que el lab 05 los ponga bonitos), y después una respuesta en streaming con referencias `path:line` y `(N steps · M tools)`.
3. Pregunta `read amounts.py and dates.py and summarise both`: si el modelo pide las dos lecturas en una sola respuesta, se ejecutan en paralelo (las dos líneas `⏺` aparecen antes que los resultados).
4. Pídele que cambie algo, p. ej. `add a docstring to total_with_vat`. Hasta el lab 04/05 obtienes un prompt rudimentario `Allow edit_file {…}? [y/N]` — responde `n` y observa cómo reacciona el modelo a `DENIED by the user`.
5. Pulsa Ctrl+C mientras trabaja: `interrupting…`, y el turno se detiene en el siguiente paso con `(interrupted by the user)`.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_parallel_reads_keep_order` falla por tiempo (≈0.6 s o más) | Las lecturas se ejecutan secuencialmente → revisa la agrupación con `_is_read` y que usas el pool para bloques > 1. |
| `test_parallel_reads_keep_order` falla por orden (`['r2', 'r1', …]`) | Resultados añadidos según terminan los hilos → escribe en `results[i]`. |
| `AssertionError: assert not open_ids` en `test_max_steps_and_loop` | En `"loop"` has retornado sin responder a los tool_calls pendientes → añade un mensaje tool fallido para cada uno. |
| Backend real: `400 … tool_call_id … not found` / `messages with role 'tool' must be a response…` | Historial roto: mensaje del assistant construido a mano, o mensajes tool ausentes/desordenados → usa los helpers `to_message()` y respeta el orden. |
| La CLI llama a herramientas pero `bash` responde `ERROR in 'bash': NotImplementedError: TODO 04.2` | Es lo esperado: la herramienta bash es el lab 04. Normalmente el modelo lo reintentará con herramientas de lectura. |
| El modelo responde sin llamar a ninguna herramienta, o escribe `<tool_call>{…}` como texto | Modelo pequeño o herramientas no enviadas → comprueba `tools=self.tools.schemas() or None`; prueba `forja doctor`; `qwen3:8b` a veces necesita un prompt explícito como `use grep to find…`. |
| El agente repite el mismo `read_file` una y otra vez | Para eso está la detección de bucles → debería parar con `I stopped: I repeated read_file…` tras `max_repeats` (3). |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 03` → los 6 tests en verde.
- [ ] [ ] En `forja --cwd playground` el agente explora con glob/grep/read_file y responde con referencias `path:line`.
- [ ] [ ] Sabes explicar por qué cada `tool_call` necesita un mensaje `tool`, incluso cuando el bucle se detiene.

## Checkpoint
Forja explora el playground (glob, grep, read_file) y responde con referencias `ruta:línea`. Las ediciones aún piden permiso de forma rudimentaria: eso es el lab 04.

## Retos
1. Haz que el agente avise al usuario si lleva más de 15 pasos.
2. ¿Qué pasa si el modelo pide 10 lecturas a la vez con un modelo lento? Mide.

**Tests:** `tests/test_l03_agent.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 04`

---
[← anterior](../L02_file_tools/README.md) · [siguiente →](../L04_bash_permissions/README.md)
