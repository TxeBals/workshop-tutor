# Lab 01 · Cliente LLM con streaming

🇬🇧 [English](README.en.md) · Día 1 · 09:30–10:15

**Objetivo:** Hablar con cualquier backend OpenAI-compatible en streaming y reconstruir las tool calls que llegan troceadas.

## Conceptos
- **Un protocolo, muchos backends:** Ollama, vLLM, LM Studio, llama.cpp y OpenRouter hablan Chat Completions. El SDK `openai` es solo un cliente HTTP; el modelo es abierto.
- **Streaming:** el texto llega token a token (la CLI se siente viva). Las **tool calls también llegan troceadas**: `index`, luego `id` y `name`, luego el JSON de argumentos en pedazos, a veces de varias llamadas intercaladas.
- **Rarezas de modelos locales:** bloques `<think>…</think>` que pueden partirse entre chunks; tool calls escritas como texto `<tool_call>{…}</tool_call>`.
- **Reintentos:** solo errores transitorios (conexión, 429, 5xx) con backoff exponencial. Un 400 no se arregla reintentando.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenar fragmentos por índice |
| 01.2 | `forja/llm.py` | ThinkFilter: quitar <think> aunque la etiqueta llegue partida |
| 01.3 | `forja/llm.py` | LLMClient.stream: reintentos, eventos TextDelta y Done |

## Antes de empezar
- Abre `forja/llm.py` (tus tres TODOs), `forja/types.py` (`ToolCall`, `ChatResponse`, `TextDelta`, `Done` — ya hechos) y `tests/test_l01_llm.py`.
- Aquí el SDK `openai` es solo un cliente HTTP. Con `stream=True`, `client.chat.completions.create(**params)` devuelve un iterador de *chunks*. Cada chunk tiene `.model`, `.usage` (normalmente solo en el ÚLTIMO chunk, que tiene `choices == []`) y `.choices[0].delta` con `.content` (un trozo de texto o `None`) y `.tool_calls` (una lista de fragmentos o `None`). `.choices[0].finish_reason` viene informado en el último chunk de contenido.
- Un fragmento de tool call tiene `.index` (qué llamada), `.id` y `.function.name` (normalmente solo en el primer fragmento) y `.function.arguments` (un *trozo* de una cadena JSON). El test los simula con la clase `D`.
- Cómo encaja: `LLMClient.stream()` es el generador que consume el bucle del agente (lab 03). Emite `TextDelta(text)` para la UI durante el streaming y termina con UN `Done(ChatResponse(...))` con todo ensamblado. `chat()` (ya hecho) simplemente devuelve la respuesta del `Done`.
- Helpers ya hechos que reutilizarás: `self._params(messages, tools, **kw)` (construye el cuerpo de la petición, incluyendo `stream`, `stream_options`, `tools`, `tool_choice` y `extra_body`), `RETRYABLE` (las clases de excepción transitorias) y `rescue_text_tool_calls(text)`.

## Paso a paso
Haz primero 01.1 (acumulador): es pequeño, puro y se prueba de forma aislada. Luego 01.2 (filtro de think), también puro pero más delicado — dibuja en papel los estados del buffer. Termina con 01.3, que conecta ambos con el stream real; sus tests usan un `httpx.MockTransport`, así que sigues sin necesitar modelo. Ejecuta el comando de test de cada TODO antes de pasar al siguiente.

### TODO 01.1 · `forja/llm.py` · `ToolCallAccumulator.add(deltas)` / `ToolCallAccumulator.finish()`

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

### TODO 01.2 · `forja/llm.py` · `ThinkFilter.feed(text)` (`flush()` ya está hecho)

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

### TODO 01.3 · `forja/llm.py` · `LLMClient.stream(messages, tools=None, **kw)`

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

## Ejecuta
```bash
python scripts/tasks.py test 01
forja doctor                      # ¿el modelo llama tools?
forja                             # ya es un chat en streaming (aún sin tools)
```

## Pruébalo en tu agente
1. `python scripts/tasks.py test 01` → `14 passed`.
2. `forja --cwd playground` y pregunta `explain in 3 lines what an invoice due date is`. Deberías VER la respuesta aparecer progresivamente (token a token) y después un `(1 steps · 0 tools)` atenuado. No debe imprimirse texto de `<think>`.
3. Antes del prompt verás notas atenuadas como `· tools: lab 02 pending — running without this capability` y `· agent: lab 03 pending — chat mode without tools`: es lo esperado, por ahora es un chat sin más.
4. Comprueba los reintentos: apunta a un puerto muerto y observa cómo espera 1+2+4 s antes de fallar.
  - PowerShell: `$env:OLLAMA_BASE_URL="http://localhost:9999/v1"; forja --cwd playground` (después `Remove-Item Env:OLLAMA_BASE_URL`)
  - macOS/Linux: `OLLAMA_BASE_URL=http://localhost:9999/v1 forja --cwd playground`
  - Escribe `hi` → tras ~7 s, en rojo `APIConnectionError: Connection error.`
5. `forja doctor` sigue mostrando `✔ the model calls tools` (no usa tu cliente, así que es tu referencia cuando algo parece ir mal).

## Si algo falla
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

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 01` → los 14 tests en verde.
- [ ] [ ] `forja --cwd playground` responde en streaming sin texto `<think>`.
- [ ] [ ] Sabes explicar por qué un 400 no se reintenta y un 503 sí.

## Checkpoint
`forja doctor` dice ✔ y `forja` responde en streaming. Aparecen avisos «lab NN pending»: es normal.

## Retos
1. Mide el *time-to-first-token* local frente a OpenRouter.
2. ¿Qué pasa si el modelo emite dos tool calls con el mismo `index`? ¿Puede ocurrir?

**Tests:** `tests/test_l01_llm.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 02`

---
[← anterior](../L00_setup/README.md) · [siguiente →](../L02_file_tools/README.md)
