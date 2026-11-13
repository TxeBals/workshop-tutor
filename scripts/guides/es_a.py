"""Guía paso a paso para el alumno (español) de los labs 00-04.

Esquema: ver los consumidores de scripts/guides/__init__.py (GUIDE[lab_id] -> before / order / todos / try_it /
troubleshooting / done_when; los labs sin TODOs usan steps_noTODO). Todas las cadenas son Markdown.
"""
from __future__ import annotations

GUIDE: dict[str, dict] = {}

# ---------------------------------------------------------------------------------------------
# LAB 00 · Preparación y primer contacto
# ---------------------------------------------------------------------------------------------
GUIDE["00"] = {
    "before": [
        "Necesitas tener instalados **Python 3.11+**, **git** y **Ollama** (o la dirección del servidor compartido de la sala). "
        "Compruébalo con `python --version` (macOS/Linux: `python3 --version`), `git --version` y `ollama --version`.",
        "Todo se ejecuta **desde la raíz del repo** mediante `python scripts/tasks.py …`, así los mismos comandos funcionan en "
        "Windows (PowerShell/cmd) y en macOS/Linux, sin `make`.",
        "Mapa del repo: `forja/` = TU código (funciones stub que lanzan `NotImplementedError(\"TODO NN.x\")` con un comentario "
        "de pista encima), `tests/test_lNN_*.py` = tests offline por lab (usan `forja/fake_llm.py`, no hace falta modelo), "
        "`playground/` = pequeño proyecto de facturas con 3 bugs que arreglará tu agente, `labs/LNN_*/` = enunciados de los labs.",
        "Forja es **progresivo**: `forja/harness.py` captura `NotImplementedError` y sigue funcionando sin la "
        "pieza que falta, mostrando una nota como `· tools: lab 02 pending — running without this capability`. "
        "Cada lab que terminas enciende una capacidad en la CLI.",
    ],
    "order": "Haz los pasos en orden: virtualenv → instalación → modelo → `forja doctor` → tests. "
             "La descarga del modelo es lo lento (~5 GB para `qwen3:8b`), así que lanza `ollama pull` en cuanto tengas Ollama "
             "instalado y haz los pasos de Python mientras se descarga.",
    "todos": {},
    "steps_noTODO": [
        "**Abre un terminal en la raíz del repo** (la carpeta con `pyproject.toml`).\n"
        "  - Windows PowerShell: `cd C:\\path\\to\\forja-workshop`\n"
        "  - macOS/Linux: `cd ~/path/to/forja-workshop`\n"
        "  - Resultado esperado: `dir` / `ls` muestra `forja`, `tests`, `playground`, `scripts`, `pyproject.toml`.",
        "**Crea y activa un virtualenv.**\n"
        "  - Windows PowerShell: `python -m venv .venv` y luego `.venv\\Scripts\\Activate.ps1`\n"
        "    (si te sale *\"running scripts is disabled on this system\"*: "
        "`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y vuelve a activarlo).\n"
        "  - Windows cmd.exe: `python -m venv .venv` y luego `.venv\\Scripts\\activate.bat`\n"
        "  - macOS/Linux: `python3 -m venv .venv` y luego `source .venv/bin/activate`\n"
        "  - Resultado esperado: tu prompt empieza por `(.venv)` y `python --version` muestra 3.11 o superior. "
        "A partir de ahora `python` (no `python3`) es el intérprete del venv en todos los sistemas.",
        "**Instala Forja y crea `.env`:** `python scripts/tasks.py setup` (igual en todos los sistemas).\n"
        "  - Resultado esperado: una primera línea `» …python -m pip install -e .[dev]`, la salida de pip terminando en "
        "`Successfully installed … forja-1.0.0 …`, y `created .env (review it)` la primera vez.\n"
        "  - Comprueba: `forja --help` muestra `usage: forja [-h] [-p PROMPT] [--mode …]`.",
        "**Elige tu backend en `.env`** (ábrelo con cualquier editor).\n"
        "  - Portátil de 16 GB: `FORJA_BACKEND=ollama`, `FORJA_MODEL=qwen3:8b` (el valor por defecto).\n"
        "  - Mac de 32 GB / GPU de 24 GB: `FORJA_MODEL=qwen3-coder:30b`.\n"
        "  - Servidor compartido de la sala: descomenta el bloque `openai_compat` y pon `FORJA_BASE_URL` / `FORJA_MODEL` "
        "que te dé el tutor.\n"
        "  - OpenRouter: solo modelos open-weight — `anthropic/*`, `openai/*`, `gpt-oss`, `o3`… están bloqueados en "
        "`forja/config.py` (`ModelPolicyError`).",
        "**Descarga y prueba el modelo** (sáltatelo si usas el servidor compartido).\n"
        "  - Todos los sistemas: `ollama pull qwen3:8b` → barras de progreso y luego `success`.\n"
        "  - `ollama run qwen3:8b \"hello\"` → un saludo corto (qwen3 puede mostrar antes una sección *Thinking…*).\n"
        "  - Mientras responde, en otro terminal: `ollama ps` → una fila con `qwen3:8b`, su SIZE y "
        "PROCESSOR (`100% GPU`, o un reparto CPU/GPU, que es más lento).",
        "**Comprueba que el modelo sabe llamar a herramientas:** `forja doctor` (habla con el backend usando directamente el SDK "
        "`openai`, así que funciona antes del lab 01).\n"
        "  - Resultado esperado:\n"
        "    ```\n"
        "    backend=ollama url=http://localhost:11434/v1 model=qwen3:8b\n"
        "    answered in 4.2s · ~35 tok/s (includes loading)\n"
        "    ✔ the model calls tools (ping)\n"
        "    ```\n"
        "  - `! the model answered without calling the tool` → el modelo no hace tool calling: elige otro. "
        "`✘ could not talk to the model` → Ollama no está en marcha o la URL de `.env` es incorrecta.",
        "**Ejecuta los tests del taller:** `python scripts/tasks.py test`.\n"
        "  - Resultado esperado: casi todo en rojo — alrededor de `58 failed, 7 passed`, cada fallo terminando en "
        "`NotImplementedError: TODO NN.x`. Es correcto: son tus TODOs.\n"
        "  - Un solo lab: `python scripts/tasks.py test 01` → `9 failed, 5 passed` "
        "(los 5 verdes prueban código que se te da hecho).",
        "**Ejecuta los tests del proyecto de prácticas** (el trabajo para tu agente):\n"
        "  - Windows PowerShell: `cd playground; python -m pytest -q; cd ..`\n"
        "  - macOS/Linux: `cd playground && python -m pytest -q; cd ..`\n"
        "  - Resultado esperado: `3 failed, 4 passed` — `test_round_half_up`, `test_total_with_vat_cent` y "
        "`test_due_date_sunday_moves_to_monday`. No los arregles a mano: lo hará Forja.",
        "**Abre la CLI una vez:** `forja --cwd playground`.\n"
        "  - Resultado esperado: un banner cian `Forja 1.0.0 · qwen3:8b · mode default`, la ruta y `/help for commands`.\n"
        "  - Escribe `hello` → `NotImplementedError: TODO 01.3` en rojo, más notas atenuadas `· … lab NN pending`. "
        "Correcto por ahora: el cliente en streaming es el lab 01. Sal con `/exit` o Ctrl+D (Windows: Ctrl+Z, Enter).",
    ],
    "try_it": [
        "Mira cómo el tutor ejecuta `python scripts/tasks.py demo`: el agente de referencia sobre `playground/`. "
        "Ese es tu agente al final del día 2.",
        "Ejecuta `ollama ps` mientras `ollama run qwen3:8b \"write a haiku\"` está respondiendo: fíjate en GPU vs CPU y en la memoria usada.",
        "Echa un vistazo a `forja/harness.py`, método `Forja.gate`: cada tool call pasa por parse → hook PreToolUse → permisos "
        "→ aprobación → ejecución → hook PostToolUse. Cada paso es un lab.",
        "Abre `forja/llm.py` y busca el primer comentario `# TODO 01.1:`: así es un stub de partida.",
    ],
    "troubleshooting": [
        ["PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled`",
         "Política de ejecución → `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, o usa cmd.exe "
         "con `.venv\\Scripts\\activate.bat`."],
        ["`forja` is not recognized / `command not found: forja`",
         "El venv no está activo o `setup` falló → actívalo y vuelve a ejecutar `python scripts/tasks.py setup`. "
         "`python -m forja` funciona como alternativa."],
        ["`ERROR: Package 'forja' requires a different Python`",
         "Tu Python es anterior a 3.11 → instala 3.11+ y vuelve a crear `.venv` con él "
         "(Windows: `py -3.12 -m venv .venv`)."],
        ["`forja doctor` → `✘ could not talk to the model: APIConnectionError`",
         "Ollama no está en marcha o `OLLAMA_BASE_URL` es incorrecta → arranca la app de Ollama (o `ollama serve`) y "
         "comprueba que `http://localhost:11434` en un navegador dice *Ollama is running*."],
        ["`forja doctor` → `ModelPolicyError: model '…' blocked by policy`",
         "Has elegido un id de modelo cerrado (anthropic/openai/gpt-oss/o3…) → usa un modelo open-weight."],
        ["`forja doctor` va muy lento la primera vez (30–90 s)",
         "El modelo se está cargando en memoria → normal; la segunda llamada es rápida. Si sigue lento, `ollama ps` "
         "probablemente muestra CPU: usa un modelo más pequeño o el servidor compartido."],
        ["macOS: `python: command not found`",
         "Fuera del venv macOS solo tiene `python3` → crea el venv con `python3 -m venv .venv`; una vez "
         "activo, `python` funciona."],
    ],
    "done_when": [
        "[ ] `ollama run <your model> \"hello\"` responde (o el servidor compartido responde a `forja doctor`).",
        "[ ] `forja doctor` muestra `✔ the model calls tools`.",
        "[ ] `python scripts/tasks.py test` se ejecuta y muestra fallos rojos `NotImplementedError: TODO …`.",
        "[ ] Los tests de `playground` muestran exactamente 3 fallos.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 01 · Cliente LLM en streaming
# ---------------------------------------------------------------------------------------------
GUIDE["01"] = {
    "before": [
        "Abre `forja/llm.py` (tus tres TODOs), `forja/types.py` (`ToolCall`, `ChatResponse`, `TextDelta`, `Done` — "
        "ya hechos) y `tests/test_l01_llm.py`.",
        "Aquí el SDK `openai` es solo un cliente HTTP. Con `stream=True`, "
        "`client.chat.completions.create(**params)` devuelve un iterador de *chunks*. Cada chunk tiene `.model`, "
        "`.usage` (normalmente solo en el ÚLTIMO chunk, que tiene `choices == []`) y `.choices[0].delta` con "
        "`.content` (un trozo de texto o `None`) y `.tool_calls` (una lista de fragmentos o `None`). "
        "`.choices[0].finish_reason` viene informado en el último chunk de contenido.",
        "Un fragmento de tool call tiene `.index` (qué llamada), `.id` y `.function.name` (normalmente solo en el primer "
        "fragmento) y `.function.arguments` (un *trozo* de una cadena JSON). El test los simula con la clase `D`.",
        "Cómo encaja: `LLMClient.stream()` es el generador que consume el bucle del agente (lab 03). Emite "
        "`TextDelta(text)` para la UI durante el streaming y termina con UN `Done(ChatResponse(...))` con todo "
        "ensamblado. `chat()` (ya hecho) simplemente devuelve la respuesta del `Done`.",
        "Helpers ya hechos que reutilizarás: `self._params(messages, tools, **kw)` (construye el cuerpo de la petición, "
        "incluyendo `stream`, `stream_options`, `tools`, `tool_choice` y `extra_body`), `RETRYABLE` "
        "(las clases de excepción transitorias) y `rescue_text_tool_calls(text)`.",
    ],
    "order": "Haz primero 01.1 (acumulador): es pequeño, puro y se prueba de forma aislada. Luego 01.2 (filtro de think), "
             "también puro pero más delicado — dibuja en papel los estados del buffer. Termina con 01.3, que conecta ambos con "
             "el stream real; sus tests usan un `httpx.MockTransport`, así que sigues sin necesitar modelo. "
             "Ejecuta el comando de test de cada TODO antes de pasar al siguiente.",
    "todos": {
        "01.1": {
            "where": "`forja/llm.py` · `ToolCallAccumulator.add(deltas)` / `ToolCallAccumulator.finish()`",
            "contract": "`add(deltas: list | None) -> None` recibe el `delta.tool_calls` de UN chunk (puede ser `None`) "
                        "y actualiza `self._parts: dict[int, dict[str, str]]`, un hueco por `index` con las claves "
                        "`'id'`, `'name'`, `'arguments'`. `finish() -> list[ToolCall]` devuelve las llamadas completas "
                        "ordenadas por índice, saltándose los huecos sin nombre; un id ausente se sustituye por uno generado "
                        "no vacío, y los argumentos vacíos pasan a ser `'{}'`. `arguments` sigue siendo una **cadena** JSON en crudo.",
            "steps": [
                "En `add`, trata `None` como una lista vacía (el test llama a `acc.add(None)`).",
                "Para cada fragmento, obtén (o crea) el hueco de `d.index` con cadenas vacías.",
                "Si el fragmento tiene `id`, guárdalo (no sobrescribas un id guardado con `None`).",
                "Si `d.function` no es `None`: CONCATENA `name` y `arguments` al hueco cuando vengan.",
                "En `finish`, recorre los índices ordenados, sáltate los huecos con nombre vacío y construye "
                "`ToolCall(id or generated, name, arguments or '{}')`.",
            ],
            "gotchas": [
                "Los fragmentos de llamadas distintas llegan intercalados (`test_accumulator_interleaved`): índice 0, luego 1, "
                "luego 0 y 1 otra vez en la misma lista. Indexa por `index`, nunca por orden de llegada.",
                "`function.arguments` puede ser `''` o `None`; `'' + None` lanza `TypeError` — compruébalo antes de sumar.",
                "No hagas `json.loads` de los argumentos aquí: `ToolCall.arguments` es la cadena en crudo; la validación se hace "
                "en el lab 02.",
                "`test_accumulator_empty_args_and_missing_id` comprueba `c.arguments == \"{}\"` y que `c.id` sea truthy "
                "(p. ej. `f\"call_{uuid.uuid4().hex[:8]}\"` — `uuid` ya está importado).",
            ],
            "hints": [
                "`dict.setdefault(key, default)` devuelve el valor existente o inserta y devuelve el valor por defecto — "
                "perfecto para “obtener o crear el hueco”.",
                "Todo es concatenación de cadenas con `+=`. Los únicos casos especiales son los valores `None` y "
                "el nombre vacío en `finish`.",
                "Esqueleto:\n```python\ndef add(self, deltas):\n    for d in deltas or []:\n        slot = ...  # setdefault by d.index\n"
                "        # id: store if present\n        # function: += name, += arguments (if present)\n\n"
                "def finish(self):\n    out = []\n    for i in sorted(self._parts):\n        ...  # skip nameless, build ToolCall\n    return out\n```",
            ],
            "test": "python -m pytest tests/test_l01_llm.py -k accumulator -v",
        },
        "01.2": {
            "where": "`forja/llm.py` · `ThinkFilter.feed(text)` (`flush()` ya está hecho)",
            "contract": "`feed(text: str) -> str` devuelve el texto VISIBLE que se puede imprimir ya. El estado vive en "
                        "`self.buf` (texto aún sin decidir) y `self.in_think` (dentro de un bloque `<think>`). El texto dentro de "
                        "`<think>…</think>` se descarta; todo lo que pueda ser el inicio de una etiqueta partida entre chunks "
                        "se retiene en `buf` hasta la siguiente llamada. `flush()` (ya hecho) devuelve lo que queda en `buf` "
                        "si no estamos dentro de un bloque think. Tests: `\"\".join(feed(c) for c in chunks) + flush()` "
                        "sin saltos de línea debe ser igual a `\"Hello\"`, y `\"a < b\"` debe pasar sin tocarse.",
            "steps": [
                "Añade el texto nuevo a `self.buf`, prepara una lista de salida y repite mientras `buf` no esté vacío.",
                "Fuera de un bloque think: busca `\"<think>\"` en `buf`. Si lo encuentras, emite todo lo anterior, corta `buf` "
                "tras la etiqueta, pon `in_think = True` y continúa el bucle.",
                "Fuera y NO encontrado: comprueba si el FINAL de `buf` es un prefijo de `\"<think>\"` (`\"<\"`, `\"<t\"`, …, "
                "`\"<think\"`). Si lo es, emite todo salvo ese sufijo, deja el sufijo en `buf` y retorna. "
                "Si no, emite todo `buf` y vacíalo.",
                "Dentro de un bloque think: busca `\"</think>\"`. Si lo encuentras, descarta todo hasta la etiqueta incluida "
                "(opcionalmente quita los `\\n` iniciales), pon `in_think = False` y continúa el bucle.",
                "Dentro y NO encontrado: descarta el buffer pero conserva sus últimos `len(\"</think>\") - 1` caracteres (puede "
                "estar empezando una etiqueta de cierre) y devuelve lo que hayas emitido.",
                "Devuelve la salida unida.",
            ],
            "gotchas": [
                "Caso `[\"<thi\", \"nk>reasoning</th\", \"ink>Hel\", \"lo\"]`: las dos etiquetas están partidas. Si emites `\"<thi\"` "
                "de inmediato, el test falla.",
                "Caso `[\"Hel\", \"lo<\", \"think>x</think>\"]`: solo debes retener el `\"<\"`, y emitir igualmente `\"lo\"`.",
                "`test_think_filter_keeps_normal_lt`: `\"a < b\"` — el sufijo `\"b\"` no es prefijo de etiqueta, así que no se "
                "retiene nada. Retén solo un sufijo que cumpla `\"<think>\".startswith(...)`.",
                "Un chunk puede contener un bloque entero más texto detrás: usa un bucle `while`, no un único `if`.",
                "Comprueba primero el sufijo más largo posible (de 6 caracteres a 1), y nunca más de `len(buf)`.",
            ],
            "hints": [
                "Piénsalo como una máquina de dos estados (fuera / dentro) con un buffer de caracteres sin decidir.",
                "`str.find` devuelve `-1` si no encuentra. `\"<think>\".startswith(self.buf[-k:])` te dice si los "
                "últimos `k` caracteres podrían ser el inicio de la etiqueta.",
                "Esqueleto:\n```python\nself.buf += text\nout = []\nwhile self.buf:\n    if self.in_think:\n"
                "        end = self.buf.find(\"</think>\")\n        if end == -1:\n            ...  # keep last 7 chars, return\n"
                "        ...  # cut after the tag, in_think = False\n    else:\n        start = self.buf.find(\"<think>\")\n"
                "        if start == -1:\n            ...  # hold back a tag prefix at the end, or emit all\n"
                "        ...  # emit before tag, cut, in_think = True\nreturn \"\".join(out)\n```",
            ],
            "test": "python -m pytest tests/test_l01_llm.py -k think_filter -v",
        },
        "01.3": {
            "where": "`forja/llm.py` · `LLMClient.stream(messages, tools=None, **kw)`",
            "contract": "Un **generador** que emite `StreamEvent`s: cero o más `TextDelta(text)` (solo texto visible, "
                        "tras `ThinkFilter`) y exactamente un `Done(ChatResponse(content or None, tool_calls, "
                        "usage, model, finish_reason))` final. Reintenta solo las excepciones de `RETRYABLE`, como mucho "
                        "`self.max_retries` intentos extra, esperando 1, 2, 4… segundos con `time.sleep`. "
                        "`usage` debe ser exactamente `{\"prompt_tokens\": …, \"completion_tokens\": …}`. Si no llegaron tool "
                        "calls nativas, prueba `rescue_text_tool_calls(content)`. `finish_reason` es `\"tool_calls\"` cuando "
                        "hay llamadas; si no, el último que se haya visto.",
            "steps": [
                "Construye `params = self._params(messages, tools, **kw)`.",
                "Bucle de reintentos: `for attempt in range(self.max_retries + 1)`, llama a "
                "`self._client.chat.completions.create(**params)`; si va bien, `break`; ante una excepción `RETRYABLE` "
                "relánzala si era el último intento; si no, `time.sleep(delay)` y duplica `delay` (empieza en 1).",
                "Crea un `ToolCallAccumulator`, un `ThinkFilter`, una lista para el texto y valores por defecto para usage, "
                "finish reason y model (`self.model`).",
                "Para cada chunk: lee PRIMERO `usage` (si viene) y `model` (si viene); luego sáltate los chunks sin "
                "`choices`; después toma `choices[0]`, guarda `finish_reason`, pasa `delta.content` por el filtro de "
                "think y haz `yield TextDelta(...)` si hay algo visible; pasa `delta.tool_calls` al acumulador.",
                "Tras el bucle: `flush()` del filtro (emite también su cola), une el texto, `finish()` del acumulador; "
                "si no hay llamadas, usa `rescue_text_tool_calls`.",
                "`yield Done(ChatResponse(...))`.",
            ],
            "gotchas": [
                "El chunk de usage tiene `choices == []`: si haces `continue` antes de leer `usage`, "
                "`test_stream_text_and_tool_calls` falla en `r.usage`.",
                "Copia solo `prompt_tokens` y `completion_tokens` (el servidor también envía `total_tokens`; el test "
                "compara el dict entero).",
                "Llama a `time.sleep(...)` a través del módulo (`import time` ya está). Los tests hacen monkeypatch de "
                "`\"time.sleep\"`; con `from time import sleep` dormiría de verdad.",
                "`test_retries_on_503` espera exactamente 3 peticiones con `max_retries=2`. `test_no_retry_on_400` espera "
                "exactamente 1: un 400 lanza `openai.BadRequestError`, que NO está en `RETRYABLE`, así que deja que se propague. "
                "(Con el stub falla como `assert 0 == 1`: se lanza la excepción pero no se ha hecho ninguna petición.)",
                "No añadas tus propios reintentos en el SDK: el cliente se crea con `max_retries=0` a propósito.",
            ],
            "hints": [
                "La función contiene `yield`, así que es un generador: no se ejecuta nada (ni siquiera la petición) hasta que "
                "alguien la itera.",
                "`except RETRYABLE:` funciona porque `RETRYABLE` es una tupla de clases de excepción. El texto y el "
                "contenido de la respuesta final son el mismo texto visible (`\"Looking…\"` en el test).",
                "Esqueleto:\n```python\nparams = self._params(messages, tools, **kw)\ndelay = 1.0\n"
                "for attempt in range(self.max_retries + 1):\n    try: chunks = ...; break\n"
                "    except RETRYABLE: ...  # raise on last attempt, else sleep and double\n"
                "acc, think = ToolCallAccumulator(), ThinkFilter()\nfor ch in chunks:\n    ...  # usage/model, skip no choices, text, tool calls\n"
                "...  # flush, finish, rescue\nyield Done(ChatResponse(...))\n```",
            ],
            "test": "python -m pytest tests/test_l01_llm.py -k \"stream or retr\" -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 01` → `14 passed`.",
        "`forja --cwd playground` y pregunta `explain in 3 lines what an invoice due date is`. Deberías VER la "
        "respuesta aparecer progresivamente (token a token) y después un `(1 steps · 0 tools)` atenuado. No debe "
        "imprimirse texto de `<think>`.",
        "Antes del prompt verás notas atenuadas como `· tools: lab 02 pending — running without this capability` "
        "y `· agent: lab 03 pending — chat mode without tools`: es lo esperado, por ahora es un chat sin más.",
        "Comprueba los reintentos: apunta a un puerto muerto y observa cómo espera 1+2+4 s antes de fallar.\n"
        "  - PowerShell: `$env:OLLAMA_BASE_URL=\"http://localhost:9999/v1\"; forja --cwd playground` "
        "(después `Remove-Item Env:OLLAMA_BASE_URL`)\n"
        "  - macOS/Linux: `OLLAMA_BASE_URL=http://localhost:9999/v1 forja --cwd playground`\n"
        "  - Escribe `hi` → tras ~7 s, en rojo `APIConnectionError: Connection error.`",
        "`forja doctor` sigue mostrando `✔ the model calls tools` (no usa tu cliente, así que es tu referencia "
        "cuando algo parece ir mal).",
    ],
    "troubleshooting": [
        ["`TypeError: can only concatenate str (not \"NoneType\") to str` en `add`",
         "Un fragmento tiene `name` o `arguments` = `None` → concatena solo cuando el valor sea truthy."],
        ["El test del filtro de think falla con una salida como `<thiHello` o `Hel<`",
         "Has emitido un posible prefijo de etiqueta en vez de retenerlo en `self.buf` → retén el sufijo más largo "
         "que cumpla `\"<think>\".startswith(...)`."],
        ["`test_think_filter_keeps_normal_lt` devuelve `\"a \"` o `\"\"`",
         "Retienes todos los `<` (o todo lo que va detrás) → retén solo un sufijo que sea prefijo de `<think>`; "
         "`flush()` devuelve el resto."],
        ["`test_retries_on_503` tarda 3 segundos o más",
         "Has importado `sleep` directamente → llama a `time.sleep(...)` para que se aplique el monkeypatch."],
        ["`test_no_retry_on_400` falla con `assert 2 == 1` o `3 == 1`",
         "Capturas `Exception` (u `openai.APIStatusError`) en el bucle de reintentos → captura solo `RETRYABLE`."],
        ["`AssertionError` en `r.usage == {...}`",
         "Usage leído después del `if not ch.choices: continue`, o has copiado `total_tokens` → lee usage primero y copia dos claves."],
        ["En la CLI la respuesta aparece de golpe al final",
         "Acumulas el texto y solo emites `Done` → haz `yield TextDelta(visible)` dentro del bucle de chunks."],
        ["En la CLI ves texto `<think>…`",
         "El contenido no pasa por `ThinkFilter.feed`, o se llama a `flush()` estando en `in_think` y devuelve "
         "el buffer → revisa ambas cosas. (Algunas versiones de Ollama envían el razonamiento en un campo aparte: entonces no aparece nada, "
         "lo cual también está bien.)"],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 01` → los 14 tests en verde.",
        "[ ] `forja --cwd playground` responde en streaming sin texto `<think>`.",
        "[ ] Sabes explicar por qué un 400 no se reintenta y un 503 sí.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 02 · Herramientas de ficheros
# ---------------------------------------------------------------------------------------------
GUIDE["02"] = {
    "before": [
        "Abre `forja/tools.py` (TODOs 02.1–02.2), `forja/fs_tools.py` (02.3–02.6) y `tests/test_l02_tools.py`. "
        "Lee primero las partes ya hechas: el decorador `@tool` construye un modelo pydantic a partir de los type hints + el docstring "
        "(`Tool.args_model`), `ToolRegistry.parse_args(call)` valida los argumentos JSON, y `read_file` / `glob` "
        "son ejemplos completos de herramientas.",
        "Stdlib/APIs que usarás: pydantic `Model.model_json_schema()`; `json.dumps`; `time.perf_counter()`; "
        "`pathlib.Path.resolve()`, `.is_absolute()`, `.is_relative_to()`; `str.count`, `str.replace(old, new, 1)`; "
        "`re.compile`, `fnmatch.fnmatch`.",
        "Helpers de `Workspace` ya hechos que debes usar: `ws.resolve(path)` (tu 02.3), `ws.rel(p)` (cadena relativa), "
        "`ws.mark_read(p)` (recuerda el mtime), `ws.check_fresh(p)` (lanza `PermissionError` si no se ha leído o ha cambiado "
        "en disco), `ws.walk(base)` (ficheros, saltándose `.git`, `.venv`, `__pycache__`…), `ws.before_write` "
        "(callbacks, que usan los checkpoints del lab 11) y `unified_diff(before, after, path)`.",
        "Idea clave: las herramientas **lanzan** excepciones normales de Python con mensajes útiles; `ToolRegistry.execute` (02.2) "
        "lo captura todo y devuelve el mensaje al modelo como `ToolResult(ok=False, …)`. Así que las aserciones de los tests "
        "como `\"before modifying\" in res.output` comprueban TU texto de error pasado a través de `execute`.",
        "Cómo encaja: `schemas()` es lo que el modelo ve como `tools=[…]`; el gate del harness llama a `execute` "
        "por cada llamada que hace el modelo.",
    ],
    "order": "Primero 02.1 → 02.2 → 02.3: todos los tests de herramientas de ficheros pasan por `registry.execute` y `ws.resolve`, así que "
             "nada más puede pasar antes. Luego 02.4 (`write_file`), 02.5 (`edit_file`, la más grande) "
             "y 02.6 (`grep`). Ten `read_file` abierto como modelo de cómo se escribe una herramienta.",
    "todos": {
        "02.1": {
            "where": "`forja/tools.py` · `Tool.schema()`",
            "contract": "Devuelve `{\"type\": \"function\", \"function\": {\"name\": self.name, \"description\": "
                        "self.description, \"parameters\": params}}` donde `params` es el JSON Schema de pydantic de "
                        "`self.args_model` con: sin `\"title\"` en la raíz, sin `\"title\"` dentro de ninguna propiedad, "
                        "`\"additionalProperties\": False`, y una clave `\"properties\"` incluso para herramientas sin argumentos. "
                        "`test_schema_from_type_hints` comprueba el nombre, la descripción `\"Does something.\"`, "
                        "`required == [\"path\"]`, el default `3` de `n` y la descripción `\"Path.\"` de `path`.",
            "steps": [
                "Obtén el dict del esquema con `self.args_model.model_json_schema()`.",
                "Elimina el `title` raíz (usa `pop` con un valor por defecto para que nunca falle).",
                "Recorre los valores de `params[\"properties\"]` (puede no existir) y elimina cada `title`.",
                "Asegúrate de que `properties` existe y pon `additionalProperties` a `False`.",
                "Envuélvelo en el formato de función de OpenAI y devuélvelo.",
            ],
            "gotchas": [
                "pydantic añade títulos como `\"Path\"`, `\"N\"` a cada propiedad: los modelos pequeños se lían con ellos, "
                "y el test comprueba que no haya título raíz.",
                "Una herramienta sin parámetros no tiene clave `properties`: algunos backends rechazan un esquema sin ella.",
                "pydantic ya genera las descripciones y `required` a partir del decorador `@tool`: no los "
                "reconstruyas a mano.",
            ],
            "hints": [
                "Imprímelo primero: `python -c \"from forja.fs_tools import *; from pathlib import Path; "
                "print(make_fs_tools(Workspace(Path('.')))[0].args_model.model_json_schema())\"`.",
                "`dict.pop(\"title\", None)` y `dict.setdefault(\"properties\", {})` hacen casi todo el trabajo.",
                "Esqueleto:\n```python\nparams = self.args_model.model_json_schema()\n# drop root title\n"
                "for prop in params.get(\"properties\", {}).values():\n    ...\n# ensure properties, additionalProperties\n"
                "return {\"type\": \"function\", \"function\": {...}}\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k schema -v",
        },
        "02.2": {
            "where": "`forja/tools.py` · `ToolRegistry.execute(call)`",
            "contract": "`execute(call: ToolCall) -> ToolResult` y **nunca lanza excepciones**. Usa `self.parse_args(call)` → "
                        "`(tool, args, err)`; si hay `err`, devuelve `ToolResult(call.id, call.name, False, err)`. Si no, "
                        "llama a `tool.fn(**args)`; cualquier `Exception` se convierte en `ok=False` con la salida "
                        "`\"ERROR in '<tool>': <ExceptionType>: <message>\"`. Éxito: un `ToolOutput` aporta `.text` y "
                        "`.meta`; un `str` se usa tal cual; cualquier otra cosa pasa por `json.dumps(..., ensure_ascii=False, "
                        "default=str)`. La salida siempre pasa por `_truncate`; se mide `duration_ms`.",
            "steps": [
                "Toma `t0 = time.perf_counter()` al principio.",
                "Llama a `self.parse_args(call)`; si hay error, devuelve un `ToolResult` fallido con ese mensaje.",
                "Dentro de un `try`, llama a la función de la herramienta con los args validados; ante una `Exception` devuelve un resultado fallido "
                "con el nombre del tipo y el mensaje.",
                "Convierte el valor devuelto en `(text, meta)` según su tipo.",
                "Devuelve `ToolResult(call.id, call.name, ok, _truncate(text), meta, duration_ms)`.",
            ],
            "gotchas": [
                "Cuando la herramienta no existe, `parse_args` devuelve `t = None`: usa `call.name`, no `t.name`, en el "
                "resultado (`test_execute_never_raises` llama a una herramienta llamada `nope`).",
                "Incluye el MENSAJE de la excepción en la salida: tests posteriores buscan `\"outside the workspace\"`, "
                "`\"before modifying\"`, `\"times\"`, `\"line numbers\"`, `\"has changed\"` en `res.output`.",
                "Captura `Exception`, no un `except:` a secas (no quieres tragarte Ctrl+C / `KeyboardInterrupt`).",
                "Un pequeño closure auxiliar `done(ok, out, meta=None)` evita repetir la construcción de `ToolResult(...)`.",
            ],
            "hints": [
                "La lista ordenada de campos de `ToolResult` es `call_id, name, ok, output, meta, duration_ms`.",
                "`isinstance(res, ToolOutput)` / `isinstance(res, str)`; el formato del mensaje es "
                "`f\"ERROR in '{t.name}': {type(e).__name__}: {e}\"`.",
                "Esqueleto:\n```python\nt0 = time.perf_counter()\nt, args, err = self.parse_args(call)\nif err:\n    return ...\n"
                "try:\n    res = t.fn(**args)\nexcept Exception as e:\n    return ...\n# ToolOutput? str? other -> json\n"
                "return ToolResult(..., _truncate(text), meta, int((time.perf_counter() - t0) * 1000))\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k execute_never_raises -v",
        },
        "02.3": {
            "where": "`forja/fs_tools.py` · `Workspace.resolve(path)`",
            "contract": "`resolve(path: str) -> Path`: una ruta relativa se une a `self.root`, una absoluta se mantiene; "
                        "al resultado se le aplica `.resolve()` (elimina `..`, sigue symlinks). Si no es `self.root` ni está "
                        "dentro, lanza `PermissionError(f\"path outside the workspace: {path}\")`. Devuelve el "
                        "`Path` absoluto resuelto. `self.root` ya está resuelto en `__post_init__`.",
            "steps": [
                "Envuelve la cadena en un `Path`.",
                "Construye el candidato: la propia ruta si es absoluta; si no, `self.root / path`.",
                "Llama a `.resolve()` sobre el candidato.",
                "Si es igual a `self.root` o cumple `is_relative_to(self.root)`, devuélvelo; si no, lanza el "
                "`PermissionError`.",
            ],
            "gotchas": [
                "Comprueba DESPUÉS de resolver: `\"invoices/../../secret.txt\"` parece relativa pero se escapa.",
                "No compares cadenas con `startswith`: `/home/me/proj2` empieza por `/home/me/proj`. "
                "`Path.is_relative_to` compara componentes de la ruta.",
                "`test_sandbox` comprueba tanto `\"../secret.txt\"` como `\"/etc/passwd\"` y que el mensaje contenga "
                "`\"outside the workspace\"` (en Windows `/etc/passwd` pasa a ser `C:\\etc\\passwd`: sigue fuera).",
            ],
            "hints": [
                "Tres líneas de lógica: construir, resolver, comprobar.",
                "`Path.is_absolute()`, `Path.resolve()`, `Path.is_relative_to(other)`.",
                "Esqueleto:\n```python\np = Path(path)\ntarget = (...).resolve()\nif target != self.root and not ...:\n"
                "    raise PermissionError(...)\nreturn target\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k \"sandbox or read_numbered\" -v",
        },
        "02.4": {
            "where": "`forja/fs_tools.py` · `make_fs_tools` → `write_file(path, content)` interna",
            "contract": "Devuelve `ToolOutput(text, {\"path\": ws.rel(p), \"diff\": unified_diff(before, content, ws.rel(p))})`. "
                        "Fichero nuevo: crea las carpetas padre y escribe. Fichero existente: primero `ws.check_fresh(p)` (lanza "
                        "`\"read … with read_file before modifying it\"`), guarda el contenido anterior como `before`. Llama a cada "
                        "callback de `ws.before_write` con `p` antes de escribir. Tras escribir, `ws.mark_read(p)`. "
                        "Texto como `\"docs/note.md created (1 lines)\"` / `\"… updated (N lines)\"`. Escribe en UTF-8.",
            "steps": [
                "`p = ws.resolve(path)`; `before = \"\"`.",
                "Si `p` existe: `ws.check_fresh(p)` y lee el texto anterior en `before`.",
                "Llama a cada `cb(p)` de `ws.before_write`.",
                "Crea `p.parent` (parents, exist_ok) y escribe `content` con `encoding=\"utf-8\"`.",
                "`ws.mark_read(p)` y devuelve el `ToolOutput` con la ruta y el diff.",
            ],
            "gotchas": [
                "`test_write_new_and_overwrite_rules` escribe en `docs/note.md` — la carpeta `docs` aún no existe.",
                "Sobrescribir un fichero que nunca se ha leído debe fallar con `\"before modifying\"` en la salida: deja que "
                "`check_fresh` lance la excepción, no la captures.",
                "Sin `mark_read` tras escribir, el siguiente `edit_file` sobre el mismo fichero falla con "
                "`\"has changed since you read it\"` (tu propia escritura cambió el mtime).",
                "Pasa siempre `encoding=\"utf-8\"`: en Windows la codificación por defecto no es UTF-8.",
            ],
            "hints": [
                "Copia la estructura del `read_file` ya hecho: primero resolver, luego trabajar con `p`.",
                "`p.parent.mkdir(parents=True, exist_ok=True)`, `p.write_text(content, encoding=\"utf-8\")`.",
                "Esqueleto:\n```python\np = ws.resolve(path)\nbefore = \"\"\nif p.exists():\n    ...  # fresh check + old content\n"
                "for cb in ws.before_write:\n    ...\n...  # mkdir, write, mark_read\nreturn ToolOutput(f\"...\", {\"path\": ..., \"diff\": ...})\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k write_new -v",
        },
        "02.5": {
            "where": "`forja/fs_tools.py` · `make_fs_tools` → `edit_file(path, old_string, new_string, replace_all=False)` interna",
            "contract": "Devuelve `ToolOutput(\"<rel> edited (N replacement(s), from line L)\", {\"path\": ws.rel(p), \"diff\": …})`. "
                        "Lanza (en este orden): `FileNotFoundError` si no es un fichero (sugiere `write_file`); "
                        "los errores de `check_fresh`; `ValueError` si `old_string == new_string`; `ValueError` "
                        "`\"old_string not found in <path>.\"` + una pista cuando el recuento es 0; `ValueError` "
                        "`\"old_string appears N times in <path>: …\"` cuando el recuento es >1 y no hay `replace_all`. "
                        "Sustituye una aparición (o todas), llama a los callbacks de `ws.before_write`, escribe y hace `mark_read`.",
            "steps": [
                "Resuelve la ruta; si no es un fichero, lanza `FileNotFoundError` mencionando `write_file`.",
                "`ws.check_fresh(p)`; rechaza cadenas old/new idénticas.",
                "Lee el texto y cuenta las apariciones de `old_string`.",
                "Recuento 0: construye una pista — si `old_string` tiene líneas que empiezan por dígitos + `→` (regex "
                "`r\"^\\s*\\d+→\"` con `re.M`), di que contiene **números de línea** de read_file; si no, si su versión "
                "sin espacios en los extremos existe en el texto, di que difieren los espacios/la indentación. Lanza `ValueError`.",
                "Recuento >1 sin `replace_all`: lanza `ValueError` diciendo que aparece N veces y cómo arreglarlo.",
                "Sustituye (una vez con `str.replace(old, new, 1)` o todas), llama a los callbacks de `before_write`, escribe en UTF-8, "
                "`mark_read`.",
                "Calcula la línea de la primera coincidencia (`text[:text.index(old_string)].count(\"\\n\") + 1`) y devuelve "
                "el `ToolOutput` con el diff.",
            ],
            "gotchas": [
                "El orden importa: `test_edit_requires_read_and_unique` edita primero un fichero NO leído y espera "
                "`\"before modifying\"` — `check_fresh` debe ejecutarse antes de contar.",
                "El test de duplicados usa `old_string=\"return\"` y comprueba `\"times\"` en la salida.",
                "El test de números de línea pasa `\"     9→    return round(value, 2)\"` y comprueba `\"line numbers\"` en la "
                "salida: el `→` es el carácter que imprime `read_file`.",
                "`test_edit_detects_external_change` modifica el fichero tras leerlo: basta con llamar a `check_fresh` para obtener "
                "`\"has changed\"`.",
                "El diff debe contener la línea nueva exactamente una vez → por defecto sustituye solo la primera aparición.",
            ],
            "hints": [
                "Estos mensajes de error son prompts para el modelo: di qué ha ido mal Y qué hacer a continuación.",
                "`text.count(old_string)`, `text.replace(old, new, 1)`, `re.search(pattern, old_string, re.M)`.",
                "Esqueleto:\n```python\np = ws.resolve(path)\nif not p.is_file(): raise FileNotFoundError(...)\n"
                "ws.check_fresh(p)\nif old_string == new_string: raise ValueError(...)\ntext = ...\nn = text.count(old_string)\n"
                "if n == 0: ...   # hint: line numbers? whitespace?\nif n > 1 and not replace_all: ...\n"
                "new_text = ...\n# before_write, write, mark_read, line, return ToolOutput\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k \"edit_requires or external_change\" -v",
        },
        "02.6": {
            "where": "`forja/fs_tools.py` · `make_fs_tools` → `grep(pattern, path=\".\", include=None, ignore_case=False, show_content=True)` interna",
            "contract": "Devuelve un `str`. Con `show_content=True`: una línea por coincidencia, `\"<rel>:<lineno>: <line stripped, "
                        "max 300 chars>\"`. Con `show_content=False`: una línea por fichero que coincide (su ruta relativa). "
                        "`include` filtra por NOMBRE de fichero con `fnmatch` (p. ej. `*.py`). Busca en un solo fichero si `path` es "
                        "un fichero; si no, en `ws.walk(base)`. Se salta los ficheros que no son UTF-8. Se detiene a los 300 resultados con una "
                        "nota. Si no encuentra nada: `\"(no matches)\"`.",
            "steps": [
                "Compila la regex con `re.I` cuando haya `ignore_case`.",
                "Resuelve `path`; la lista de ficheros es `[base]` si es un fichero; si no, `ws.walk(base)`.",
                "Para cada fichero: sáltatelo si se da `include` y el nombre no coincide.",
                "Léelo como UTF-8 dentro de `try/except (UnicodeDecodeError, OSError)` y sáltatelo si hay error.",
                "Enumera las líneas desde 1; si `rx.search(line)`: añade la línea formateada o (en modo solo rutas) "
                "añade la ruta una vez y deja de leer ese fichero.",
                "Detente con una nota al llegar a 300 resultados; devuelve las líneas unidas o `\"(no matches)\"`.",
            ],
            "gotchas": [
                "Los números de línea empiezan en 1: `test_grep_and_glob` espera `\"invoices/amounts.py:7:\"` para "
                "`def round_amount`.",
                "Usa `ws.rel(f)` para la ruta, no la ruta absoluta.",
                "`include` se compara con `f.name`, no con la ruta completa.",
                "En modo solo rutas cada fichero debe aparecer una vez aunque coincidan muchas líneas.",
                "Una regex inválida lanza `re.error`; no pasa nada — `execute` lo convierte en un mensaje de error para el modelo.",
            ],
            "hints": [
                "Mira la herramienta `glob` ya hecha justo encima: el mismo recorrido, distinto filtro.",
                "`enumerate(text.splitlines(), 1)`, `fnmatch.fnmatch(f.name, include)`, `rx.search(line)`.",
                "Esqueleto:\n```python\nrx = re.compile(pattern, re.I if ignore_case else 0)\nbase = ws.resolve(path)\n"
                "files = [base] if base.is_file() else ws.walk(base)\nout = []\nfor f in files:\n"
                "    ...  # include filter, read (skip binaries), match lines\n    if len(out) >= 300: ...\n"
                "return \"\\n\".join(out) or \"(no matches)\"\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k grep -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 02` → `8 passed`.",
        "Maneja las herramientas a mano desde un REPL de Python en la raíz del repo (`python`, y luego escribe):\n"
        "```python\nimport json; from pathlib import Path\nfrom forja.fs_tools import Workspace, make_fs_tools\n"
        "from forja.tools import ToolRegistry; from forja.types import ToolCall\n"
        "r = ToolRegistry().register(*make_fs_tools(Workspace(Path(\"playground\"))))\n"
        "x = lambda name, **a: print(r.execute(ToolCall(\"1\", name, json.dumps(a))).output)\n"
        "x(\"grep\", pattern=\"def \", include=\"*.py\")\n```\n"
        "Deberías VER líneas como `invoices/amounts.py:7: def round_amount(value: float) -> float:`.",
        "En el mismo REPL: `x(\"read_file\", path=\"../README.md\")` → `ERROR in 'read_file': PermissionError: path "
        "outside the workspace: ../README.md`; `x(\"edit_file\", path=\"invoices/dates.py\", old_string=\"a\", "
        "new_string=\"b\")` → `… read invoices/dates.py with read_file before modifying it`.",
        "Mira lo que leerá el modelo: `print(json.dumps(r.schemas()[2], indent=2))` → el esquema de `edit_file`, con "
        "su descripción larga, `required` y `\"additionalProperties\": false`, y sin claves `title`.",
        "`forja --cwd playground`: la nota `tools: lab 02 pending` ha desaparecido. Sigue siendo un chat (`agent: lab 03 "
        "pending — chat mode without tools`), así que el modelo aún no puede llamar a tus herramientas — eso es el lab 03.",
    ],
    "troubleshooting": [
        ["Todos los tests de herramientas de ficheros fallan con `NotImplementedError: TODO 02.2` o `TODO 02.3`",
         "Todos los tests pasan por `registry.execute` y `ws.resolve` → termina primero 02.2 y 02.3."],
        ["`AttributeError: 'NoneType' object has no attribute 'name'` en `execute`",
         "Herramienta desconocida → `t` es `None` → usa `call.name` al construir el resultado de error."],
        ["El test espera `\"before modifying\"` pero la salida dice `\"old_string not found\"`",
         "Cuentas las apariciones antes de `ws.check_fresh(p)` → sube la comprobación de frescura."],
        ["`edit_file` funciona una vez y la siguiente edición dice `has changed since you read it`",
         "Falta `ws.mark_read(p)` tras escribir → llámalo al final de write_file y de edit_file."],
        ["`AssertionError: 'line numbers' in …` en el test de edición",
         "Tu regex de pista no coincide con `\"     9→    return …\"` → usa `^\\s*\\d+→` con `re.M`, y copia el carácter `→` "
         "del código de `read_file`."],
        ["`UnicodeDecodeError` / caracteres corruptos al escribir en Windows",
         "Falta `encoding=\"utf-8\"` en `write_text`/`read_text` → pásalo siempre."],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 02` → los 8 tests en verde.",
        "[ ] Desde el REPL obtienes un `read_file` numerado, un `grep` con resultados `path:line:` y un error de sandbox para `../`.",
        "[ ] Los mensajes de error de tu `edit_file` le dicen al modelo cómo corregir su llamada.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 03 · El bucle del agente
# ---------------------------------------------------------------------------------------------
GUIDE["03"] = {
    "before": [
        "Abre `forja/agent.py` (`Events`, `AgentResult`, `Agent` y tus dos TODOs), `forja/fake_llm.py` "
        "(`FakeLLM`, `say`, `call`, `calls`: el modelo con guion que usan los tests) y `tests/test_l03_agent.py`.",
        "Protocolo de mensajes (Chat Completions): un mensaje del assistant con `tool_calls` debe ir seguido de un "
        "mensaje `{\"role\": \"tool\", \"tool_call_id\": …}` por cada llamada, antes del siguiente mensaje del assistant. "
        "`ChatResponse.to_message()` y `ToolResult.to_message()` (ya hechos) te construyen esos dicts.",
        "`self.llm.stream(messages, tools=...)` emite `TextDelta` y un `Done` final (tu lab 01, o `FakeLLM` "
        "en los tests, que emite el texto en trozos de 8 caracteres). `self.tools.schemas()` (lab 02) es la lista `tools`.",
        "Stdlib: `concurrent.futures.ThreadPoolExecutor` (`ex.map(fn, iterable)`), `collections.Counter`, "
        "`threading.Event.is_set()`.",
        "Cómo encaja: el harness crea `Agent(llm, registry, execute=self.gate, events=RichEvents(), …)`. "
        "El bucle no sabe nada de permisos ni de UI — solo llama a `execute` y a `events`. La misma clase se "
        "reutiliza para subagentes (lab 09) y evals (lab 12).",
    ],
    "order": "Empieza por el camino sin herramientas de 03.2 (stream, añadir el mensaje del assistant, devolver `\"final\"`, más "
             "la comprobación de cancelación): eso pone en verde `test_final_answer`, `test_streaming_events` y `test_cancel`. "
             "Después escribe 03.1 `_run_calls` y completa 03.2 con la ejecución de herramientas, `max_steps` y la detección de bucles. "
             "Todos los tests de 03.1 pasan por `run`, así que necesitas ambos.",
    "todos": {
        "03.1": {
            "where": "`forja/agent.py` · `Agent._run_calls(calls)`",
            "contract": "`_run_calls(calls: list[ToolCall]) -> list[ToolResult]`, resultados en el MISMO orden que `calls`. "
                        "Usa `self.execute` si está definido; si no, `self.tools.execute`. Para cada llamada: "
                        "`self.events.on_tool_start(call)`, ejecutar, `self.events.on_tool_end(call, result)`. "
                        "Las secuencias de llamadas CONSECUTIVAS de riesgo read (`self._is_read(call)`) se ejecutan en paralelo en un "
                        "`ThreadPoolExecutor` cuando `self.parallel_reads`; todo lo demás se ejecuta secuencialmente y en orden.",
            "steps": [
                "Elige la función de ejecución: `self.execute or self.tools.execute`.",
                "Reserva `results = [None] * len(calls)` y escribe una pequeña función interna `run(i)` que lance "
                "el evento de inicio, ejecute `calls[i]` guardándolo en `results[i]` y lance el evento de fin.",
                "Recorre las llamadas con un índice `i`. Si `calls[i]` es una lectura, avanza `j` mientras las llamadas sean lecturas.",
                "Si el bloque tiene más de una lectura, ejecuta los índices `i..j-1` con un `ThreadPoolExecutor` (p. ej. hasta 8 "
                "workers); una sola lectura se ejecuta sin más. Pon `i = j`.",
                "Llamadas que no son lectura: `run(i)` e `i += 1`.",
                "Devuelve la lista de resultados.",
            ],
            "gotchas": [
                "`test_parallel_reads_keep_order`: tres lecturas de 0.2 s + una escritura deben tardar < 0.5 s Y producir los "
                "contenidos de tool `[\"r1\", \"r2\", \"r3\", \"wa\"]` con los ids en el orden original. Guarda por índice; "
                "el orden de `as_completed` es aleatorio.",
                "Solo lecturas CONSECUTIVAS: `[read, write, read]` no debe ejecutar la segunda lectura antes de la escritura.",
                "`test_custom_execute_gate` comprueba que se usa tu gate: llamar directamente a `self.tools.execute` se salta "
                "los permisos en la CLI real.",
                "Consume `ex.map(...)` (p. ej. `list(...)`) o las excepciones de los workers se pierden en silencio; salir del "
                "bloque `with` espera a que terminen todos.",
            ],
            "hints": [
                "Escribir por índice (`results[i] = …`) es lo que mantiene el orden, sin importar qué hilo termine primero.",
                "`with ThreadPoolExecutor(max_workers=min(8, j - i)) as ex: list(ex.map(run, range(i, j)))`.",
                "Esqueleto:\n```python\nexecute = self.execute or self.tools.execute\nresults = [None] * len(calls)\n"
                "def run(i): ...   # start event, execute, end event\ni = 0\nwhile i < len(calls):\n"
                "    if self.parallel_reads and self._is_read(calls[i]):\n        ...  # find j, pool or single\n"
                "    else:\n        ...\nreturn results\n```",
            ],
            "test": "python -m pytest tests/test_l03_agent.py -k \"parallel or gate\" -v",
        },
        "03.2": {
            "where": "`forja/agent.py` · `Agent.run(messages)`",
            "contract": "`run(messages: list[dict]) -> AgentResult(answer, stop_reason, steps, usage, tool_calls)`. "
                        "`messages` se MODIFICA IN SITU (el harness lo lee después). Motivos de parada: `\"final\"` "
                        "(sin tool calls; answer = `resp.content or \"\"`, steps = paso actual), `\"interrupted\"` "
                        "(`self.cancel` activado al inicio de un paso; steps = step - 1), `\"loop\"` (mismo nombre de herramienta + misma "
                        "cadena de argumentos pedida más de `self.max_repeats` veces en esta ejecución), `\"max_steps\"` "
                        "(steps = `self.max_steps`). `usage` suma todas las respuestas; `tool_calls` cuenta las llamadas ejecutadas. "
                        "El historial debe seguir siendo válido en todos los casos: cada id de `tool_call` recibe un mensaje `tool`.",
            "steps": [
                "Crea un `Counter` para usage, un `Counter` para los pares `(name, arguments)` y un contador de llamadas.",
                "`for step in range(1, self.max_steps + 1)`: primero, si `self.cancel.is_set()`, devuelve el "
                "resultado `\"interrupted\"`.",
                "Stream: `self.llm.stream(messages, tools=self.tools.schemas() or None)`; reenvía cada `TextDelta` "
                "a `self.events.on_text` y quédate con la respuesta del `Done`.",
                "Suma su usage, `messages.append(resp.to_message())`, llama a `self.events.on_assistant(resp)`.",
                "Sin `resp.tool_calls` → devuelve `\"final\"`.",
                "Detección de bucles: cuenta cada `(c.name, c.arguments)`; si alguno supera `self.max_repeats`, añade un "
                "`ToolResult(cc.id, cc.name, False, \"Not executed: loop detected.\").to_message()` fallido para CADA llamada de "
                "esta respuesta y devuelve `\"loop\"`.",
                "Si no, `results = self._run_calls(resp.tool_calls)`, actualiza el contador y extiende `messages` con "
                "`r.to_message()` de cada resultado. Tras el `for`, devuelve `\"max_steps\"`.",
            ],
            "gotchas": [
                "`test_final_answer` espera `steps == 1` y que el último mensaje sea el del assistant.",
                "`test_streaming_events` comprueba que `on_text` recibió MÁS DE UN trozo: reenvía cada `TextDelta`, no "
                "emitas el texto completo al final.",
                "Usa `resp.to_message()`: un `{\"role\": \"assistant\", \"content\": …}` hecho a mano sin `tool_calls` "
                "rompe el emparejamiento y los backends reales responden HTTP 400.",
                "`test_max_steps_and_loop` recorre el historial tras una parada `\"loop\"` y comprueba que no queda ningún id de tool_call "
                "abierto → cierra todas las llamadas pendientes antes de retornar.",
                "Pasa `tools=None` cuando no haya esquemas: algunos servidores rechazan `tools=[]`.",
            ],
            "hints": [
                "Escribe primero la versión de diez líneas (stream → añadir → ¿sin herramientas? retornar → ejecutar llamadas → añadir → repetir), "
                "y después añade la cancelación, la detección de bucles y los contadores.",
                "`Counter.update(dict)` suma los valores clave a clave — perfecto para `resp.usage`.",
                "Esqueleto:\n```python\nusage, seen, n_calls = Counter(), Counter(), 0\nfor step in range(1, self.max_steps + 1):\n"
                "    if self.cancel.is_set(): return AgentResult(...)\n    resp = None\n    for ev in self.llm.stream(...):\n"
                "        ...  # TextDelta -> on_text, Done -> resp\n    ...  # usage, append, on_assistant, final?\n"
                "    ...  # loop detection (close pending calls!)\n    ...  # run calls, append tool messages\n"
                "return AgentResult(..., \"max_steps\", self.max_steps, ...)\n```",
            ],
            "test": "python -m pytest tests/test_l03_agent.py -k \"final or streaming or cancel or max_steps\" -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 03` → `6 passed`.",
        "`forja --cwd playground` y pregunta `explain how an invoice total is calculated`. Deberías VER líneas azules "
        "por cada tool call, p. ej. `⏺ grep {\"pattern\": \"def total\", …}` seguidas de un `⎿ invoices/invoice.py:…` atenuado "
        "(args en JSON crudo hasta que el lab 05 los ponga bonitos), y después una respuesta en streaming con referencias `path:line` y "
        "`(N steps · M tools)`.",
        "Pregunta `read amounts.py and dates.py and summarise both`: si el modelo pide las dos lecturas en una sola respuesta, "
        "se ejecutan en paralelo (las dos líneas `⏺` aparecen antes que los resultados).",
        "Pídele que cambie algo, p. ej. `add a docstring to total_with_vat`. Hasta el lab 04/05 obtienes un prompt "
        "rudimentario `Allow edit_file {…}? [y/N]` — responde `n` y observa cómo reacciona el modelo a `DENIED by the user`.",
        "Pulsa Ctrl+C mientras trabaja: `interrupting…`, y el turno se detiene en el siguiente paso con "
        "`(interrupted by the user)`.",
    ],
    "troubleshooting": [
        ["`test_parallel_reads_keep_order` falla por tiempo (≈0.6 s o más)",
         "Las lecturas se ejecutan secuencialmente → revisa la agrupación con `_is_read` y que usas el pool para bloques > 1."],
        ["`test_parallel_reads_keep_order` falla por orden (`['r2', 'r1', …]`)",
         "Resultados añadidos según terminan los hilos → escribe en `results[i]`."],
        ["`AssertionError: assert not open_ids` en `test_max_steps_and_loop`",
         "En `\"loop\"` has retornado sin responder a los tool_calls pendientes → añade un mensaje tool fallido para cada uno."],
        ["Backend real: `400 … tool_call_id … not found` / `messages with role 'tool' must be a response…`",
         "Historial roto: mensaje del assistant construido a mano, o mensajes tool ausentes/desordenados → usa los "
         "helpers `to_message()` y respeta el orden."],
        ["La CLI llama a herramientas pero `bash` responde `ERROR in 'bash': NotImplementedError: TODO 04.2`",
         "Es lo esperado: la herramienta bash es el lab 04. Normalmente el modelo lo reintentará con herramientas de lectura."],
        ["El modelo responde sin llamar a ninguna herramienta, o escribe `<tool_call>{…}` como texto",
         "Modelo pequeño o herramientas no enviadas → comprueba `tools=self.tools.schemas() or None`; prueba `forja doctor`; "
         "`qwen3:8b` a veces necesita un prompt explícito como `use grep to find…`."],
        ["El agente repite el mismo `read_file` una y otra vez",
         "Para eso está la detección de bucles → debería parar con `I stopped: I repeated read_file…` tras "
         "`max_repeats` (3)."],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 03` → los 6 tests en verde.",
        "[ ] En `forja --cwd playground` el agente explora con glob/grep/read_file y responde con referencias `path:line`.",
        "[ ] Sabes explicar por qué cada `tool_call` necesita un mensaje `tool`, incluso cuando el bucle se detiene.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 04 · Bash y permisos
# ---------------------------------------------------------------------------------------------
GUIDE["04"] = {
    "before": [
        "Abre `forja/shell.py` (04.1–04.2), `forja/permissions.py` (04.3–04.5), `forja/config.py` "
        "(`DEFAULT_DENY`, `Settings.allow/deny`) y `tests/test_l04_bash_permissions.py`.",
        "Stdlib: `subprocess.run(..., shell=True, cwd=…, capture_output=True, text=True, timeout=…, env=…, "
        "stdin=subprocess.DEVNULL)` y `subprocess.TimeoutExpired`; `fnmatch.fnmatchcase(name, pattern)` "
        "(`*` coincide con cualquier cosa, incluidos espacios y `/`); `shlex.split(cmd)` (divide como una shell POSIX).",
        "Ya hechos: `clean_env()` (entorno sin `*KEY*`, `*TOKEN*`, `*SECRET*`…), `parse_rule(\"bash(git *)\")` → "
        "`(\"bash\", \"git *\")` (patrón `None` para un `\"edit_file\"` a secas), `split_commands(cmd)` (divide por `&&`, "
        "`||`, `;`, `|`), `Tool.subject(args)` (el comando para bash, la ruta para las herramientas de ficheros) y `tool.risk` "
        "(`\"read\"`, `\"edit\"`, `\"exec\"`).",
        "Shell: con `shell=True` el comando se ejecuta en `/bin/sh` en macOS/Linux y en **cmd.exe en Windows** "
        "(`ls`, `cat`, `rm -rf` no existen ahí; `dir`, `type` sí). La descripción de la herramienta le dice al modelo qué shell tiene.",
        "Cómo encaja: el gate del harness llama a `decide(tool, args, mode, settings.allow, settings.deny)`: "
        "`\"deny\"` → error al modelo, `\"ask\"` → prompt de aprobación, `\"allow\"` → ejecutar. Cuando el usuario responde "
        "*always*, `suggest_rule` genera la regla que se añade a `settings.allow` durante la sesión.",
    ],
    "order": "04.1 `head_tail` (pura, 5 minutos) → 04.2 `bash` (la usa) → 04.3 `rule_matches` → 04.4 `decide` "
             "(usa `rule_matches`) → 04.5 `suggest_rule` (independiente). Shell y permisos son ficheros separados: "
             "si trabajáis en pareja, uno puede empezar 04.3 mientras el otro hace 04.1–04.2.",
    "todos": {
        "04.1": {
            "where": "`forja/shell.py` · `head_tail(text, limit=MAX_SHELL_OUTPUT)`",
            "contract": "`head_tail(text: str, limit: int = 20_000) -> str`. Si `len(text) <= limit`, devuélvelo sin cambios. "
                        "Si no, devuelve los primeros `limit // 4` caracteres, una nota en MEDIO indicando cuántos "
                        "caracteres se han omitido (debe contener la palabra `omitted`) y los últimos `limit * 3 // 4` "
                        "caracteres. `test_head_tail_and_env`: con 1000 `A` + 1000 `B` y límite 400, la salida empieza por "
                        "`A`, termina en `B` y contiene `omitted`.",
            "steps": [
                "Retorna pronto si el texto cabe.",
                "Corta la cabeza (un cuarto del límite) y la cola (tres cuartos, desde el final).",
                "Construye `head + note + tail`, con el número de omitidos `len(text) - limit` en la nota.",
            ],
            "gotchas": [
                "La cola es más grande a propósito: los fallos de tests y los tracebacks están al FINAL de la salida.",
                "La nota debe ir en medio; si la añades al final, `endswith(\"B\")` falla.",
                "Slicing negativo: `text[-n:]` son los últimos `n` caracteres.",
            ],
            "hints": [
                "Un `if` y un f-string.",
                "`text[: limit // 4]` y `text[-(limit * 3 // 4):]`.",
                "Esqueleto:\n```python\nif len(text) <= limit:\n    return text\nhead, tail = ..., ...\n"
                "return f\"{head}\\n…[{...} characters omitted]…\\n{tail}\"\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k head_tail -v",
        },
        "04.2": {
            "where": "`forja/shell.py` · `make_shell_tool` → `bash(command, timeout=default_timeout)` interna",
            "contract": "Devuelve `ToolOutput(\"exit_code=N\\n<output>\", {\"exit_code\": N})` donde output es stdout más, "
                        "si lo hay, `\"\\n[stderr]\\n\" + stderr`, sin espacios en los extremos y pasado por `head_tail` (o `\"(no output)\"`). "
                        "Se ejecuta en `ws.root` con `shell=True`, `env=clean_env()`, `stdin=subprocess.DEVNULL`, `text=True`, "
                        "salida capturada y el timeout acotado a 1..600 s. Ante `subprocess.TimeoutExpired` DEVUELVE "
                        "`ToolOutput(\"TIMEOUT after Ns.\\n…\", {\"exit_code\": None})` — no lanza excepción. Un código de salida "
                        "distinto de cero es un resultado normal (`ok=True`): el modelo debe ver los tests que fallan.",
            "steps": [
                "Acota el timeout: `max(1, min(int(timeout), 600))`.",
                "Dentro de un `try`, llama a `subprocess.run` con los argumentos del contrato.",
                "Ante `TimeoutExpired`, devuelve el `ToolOutput` de TIMEOUT (puedes incluir la salida parcial si `e.stdout` es un str).",
                "Combina stdout y stderr (stderr bajo un marcador `[stderr]`), quita espacios de los extremos y aplica `head_tail`.",
                "Devuelve `ToolOutput(f\"exit_code={p.returncode}\\n…\", {\"exit_code\": p.returncode})`.",
            ],
            "gotchas": [
                "`test_bash_runs_in_root_with_exit_code` ejecuta `python -m pytest -q tests/test_invoice.py`: solo funciona "
                "si `cwd=ws.root` (la copia del playground) — y la salida debe EMPEZAR por `exit_code=0`.",
                "`test_bash_timeout` espera `\"TIMEOUT\"` en la salida: si dejas escapar la excepción, `execute` "
                "imprime `TimeoutExpired`, que no contiene `TIMEOUT` en mayúsculas.",
                "Sin `stdin=subprocess.DEVNULL`, un comando que espera entrada (un editor, una pregunta `y/n`) cuelga al agente.",
                "Usa `env=clean_env()`: el agente nunca debe ver `OPENROUTER_API_KEY` y compañía.",
                "Windows: el timeout mata `cmd.exe` pero su proceso hijo puede seguir ejecutándose hasta que termine, así que "
                "`test_bash_timeout` puede tardar ~5 s ahí. Aun así pasa.",
            ],
            "hints": [
                "`subprocess.run` con `capture_output=True, text=True` te da `p.stdout`, `p.stderr`, `p.returncode`.",
                "`except subprocess.TimeoutExpired as e:` — retorna, no lances.",
                "Esqueleto:\n```python\ntimeout = max(1, min(int(timeout), 600))\ntry:\n    p = subprocess.run(command, shell=True, cwd=ws.root, ...)\n"
                "except subprocess.TimeoutExpired as e:\n    return ToolOutput(f\"TIMEOUT after {timeout}s.\\n...\", {\"exit_code\": None})\n"
                "out = ...  # stdout + optional [stderr] block\nreturn ToolOutput(f\"exit_code={p.returncode}\\n...\", {...})\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k test_bash -v",
        },
        "04.3": {
            "where": "`forja/permissions.py` · `rule_matches(rule, tool, args)`",
            "contract": "`rule_matches(rule: str, tool: Tool, args: dict) -> bool`. `name, pattern = parse_rule(rule)`. El "
                        "nombre de la herramienta debe coincidir con `name` mediante `fnmatchcase` (así `\"mcp__issues__*\"` coincide con "
                        "`mcp__issues__get`). Sin patrón → `True`. Con patrón: `fnmatchcase(subject, pattern)` "
                        "donde `subject = tool.subject(args)`; para bash, normaliza antes los espacios "
                        "(`\" \".join(subject.split())`). Compara la cadena entera; las cadenas de comandos son cosa de `decide`.",
            "steps": [
                "Parsea la regla en nombre y patrón.",
                "Si el nombre de la herramienta no coincide con el patrón de nombre, devuelve `False`.",
                "Si no hay patrón, devuelve `True`.",
                "Obtén el subject; si la herramienta es `bash`, colapsa las secuencias de espacios.",
                "Devuelve si el subject coincide con el patrón.",
            ],
            "gotchas": [
                "`test_rule_matching`: `\"git   status --short\"` (tres espacios) debe coincidir con `bash(git status*)`.",
                "`bash(git status*)` NO debe coincidir con `git push`.",
                "El test de MCP construye `Tool(\"mcp__issues__get\", \"\", None, None, \"exec\")` sin modelo de args: usa solo "
                "`tool.name` y `tool.subject(args)`.",
                "Usa `fnmatchcase`, no `fnmatch`: `fnmatch` no distingue mayúsculas en Windows y se comportaría distinto "
                "según el sistema.",
            ],
            "hints": [
                "Las reglas son solo patrones glob aplicados dos veces: una al nombre de la herramienta y otra al subject.",
                "`fnmatch.fnmatchcase(tool.name, name)`, y luego `fnmatch.fnmatchcase(subject, pattern)`.",
                "Esqueleto:\n```python\nname, pattern = parse_rule(rule)\nif not ...: return False\nif pattern is None: return True\n"
                "subject = tool.subject(args)\nif tool.name == \"bash\": subject = ...\nreturn ...\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k rule_matching -v",
        },
        "04.4": {
            "where": "`forja/permissions.py` · `decide(tool, args, mode, allow, deny)`",
            "contract": "Devuelve `(decision, reason)` con decision en `\"allow\" | \"ask\" | \"deny\"`. Orden: "
                        "(1) alguna regla deny coincide con la llamada — para bash TAMBIÉN cada subcomando de `split_commands` — → "
                        "`\"deny\"`; (2) `mode == \"plan\"` y `tool.risk != \"read\"` → `\"deny\"`; (3) reglas allow: para bash "
                        "CADA subcomando debe coincidir con alguna regla allow, las demás herramientas necesitan una coincidencia → `\"allow\"`; "
                        "(4) `tool.risk == \"read\"` o `mode == \"bypass\"` → `\"allow\"`; (5) `mode == \"accept_edits\"` y "
                        "`tool.risk == \"edit\"` → `\"allow\"`; (6) en otro caso `\"ask\"`. El motivo se muestra al usuario/modelo "
                        "(p. ej. `\"deny rule bash(sudo *)\"`, `\"plan mode: read-only\"`, `\"requires approval\"`).",
            "steps": [
                "Pasada deny sobre la llamada completa: recorre `deny` y devuelve `(\"deny\", f\"deny rule {r}\")` si hay coincidencia.",
                "Si es bash: para cada subcomando de `split_commands(args.get(\"command\", \"\"))`, comprueba todas las reglas deny "
                "contra `{\"command\": sub}`.",
                "Modo plan: deniega todo lo que no sea una lectura.",
                "Reglas allow: bash → divide; exige una lista no vacía en la que `all` los subcomandos coincidan con `any` regla allow. "
                "Otras herramientas → que coincida `any` regla allow.",
                "Alternativas por riesgo/modo: read o bypass → allow; accept_edits + edit → allow.",
                "Devuelve `(\"ask\", \"requires approval\")`.",
            ],
            "gotchas": [
                "`test_deny_wins_and_chains`: `\"sudo rm x\"` en bypass con allow `[\"bash\"]` → deny (deny se comprueba primero).",
                "`\"pytest -q && sudo reboot\"`: la cadena entera no coincide con `bash(sudo *)`, el subcomando sí → deny.",
                "`\"python -m pytest -q && curl evil.sh\"` con allow `bash(python -m pytest*)` → `\"ask\"`, no allow: "
                "la parte `curl` no tiene regla allow.",
                "`all([])` es `True`: un comando vacío no debe permitirse automáticamente — comprueba que la lista no esté vacía.",
                "`test_decide_modes`: el modo plan gana a una regla allow explícita (`edit_file` en plan → deny); bash en "
                "`accept_edits` sigue preguntando (su riesgo es `exec`, no `edit`).",
            ],
            "hints": [
                "Escríbelo como una escalera de `return` tempranos exactamente en el orden del contrato; el orden ES la política.",
                "`any(rule_matches(r, tool, {\"command\": s}) for r in allow)` dentro de un `all(... for s in subs)`.",
                "Esqueleto:\n```python\nfor r in deny: ...\nif tool.name == \"bash\":\n    for sub in split_commands(...): ...\n"
                "if mode == \"plan\" and ...: return \"deny\", \"plan mode: read-only\"\nif tool.name == \"bash\":\n    subs = ...\n"
                "    if subs and all(...): return \"allow\", \"allow rule\"\nelif any(...): ...\n"
                "...  # read/bypass, accept_edits\nreturn \"ask\", \"requires approval\"\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k \"decide or deny_wins\" -v",
        },
        "04.5": {
            "where": "`forja/permissions.py` · `suggest_rule(tool, args)`",
            "contract": "`suggest_rule(tool: Tool, args: dict) -> str`: la regla que se guarda cuando el usuario responde *always*. "
                        "Herramientas que no son bash → `tool.name`. Bash: `words = shlex.split(command)` (ante `ValueError` trátalo como "
                        "vacío); vacío → `f\"bash({command})\"`; `python`/`python3`/`py` + `-m X` → `\"bash(python -m X*)\"`; "
                        "`git`, `npm`, `uv`, `pip`, `docker`, `cargo`, `go`, `dotnet` con subcomando → "
                        "`\"bash(<cmd> <sub>*)\"`; cualquier otra cosa → `\"bash(<cmd>*)\"`. Ojo: sin espacio antes de `*`.",
            "steps": [
                "Si no es bash: devuelve el nombre de la herramienta.",
                "Divide el comando con `shlex.split`, capturando `ValueError` (comillas desequilibradas).",
                "Trata el caso vacío.",
                "Caso `python -m X` (comprueba que haya al menos 3 palabras y que la segunda sea `-m`).",
                "Caso de herramientas con subcomandos (al menos 2 palabras).",
                "Por defecto: primera palabra + `*`.",
            ],
            "gotchas": [
                "`test_suggest_rule` espera exactamente `bash(python -m pytest*)`, `bash(git status*)`, `bash(ls*)` y "
                "`edit_file` — sin espacio antes de `*`.",
                "Demasiado amplia es peligrosa: `bash(git*)` también permitiría `git push`; `bash(python*)` permitiría cualquier script.",
                "Demasiado estrecha es inútil: el comando literal `bash(python -m pytest -q tests/x.py)` volvería a preguntar "
                "la próxima vez con otros flags.",
            ],
            "hints": [
                "Decide la forma solo a partir de la primera o las dos primeras palabras.",
                "`shlex.split(\"python -m pytest -q\")` → `['python', '-m', 'pytest', '-q']`.",
                "Esqueleto:\n```python\nif tool.name != \"bash\": return tool.name\ntry: words = shlex.split(...)\nexcept ValueError: words = []\n"
                "if not words: return ...\nif words[0] in (\"python\", \"python3\", \"py\") and ...: return ...\n"
                "if words[0] in (\"git\", \"npm\", ...) and len(words) > 1: return ...\nreturn f\"bash({words[0]}*)\"\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k suggest_rule -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 04` → `8 passed`.",
        "`forja --cwd playground` y pregunta `run the tests and tell me which ones fail`. Deberías VER "
        "`⏺ bash {\"command\": \"python -m pytest -q\"}` y un prompt de aprobación (hasta el lab 05 es el mínimo "
        "`Allow bash {'command': 'python -m pytest -q'}? [y/N]`). Responde `y`: `⎿ exit_code=1 (+N lines)` y una respuesta "
        "que nombra `test_round_half_up`, `test_total_with_vat_cent` y `test_due_date_sunday_moves_to_monday`.",
        "Pide `run sudo ls` (o `run rm -rf /`): en rojo `⎿ DENIED (deny rule bash(sudo *)). Don't retry it…` sin "
        "ningún prompt — ha decidido la política.",
        "Preaprueba los tests: crea `playground/.forja/settings.json` con "
        "`{\"permissions\": {\"allow\": [\"bash(python -m pytest*)\"]}}`, reinicia `forja --cwd playground` y vuelve a preguntar: "
        "esta vez sin prompt. Borra el fichero después.",
        "Comprueba la regla *always*: `python -c \"from forja.shell import make_shell_tool; from forja.fs_tools import "
        "Workspace; from forja.permissions import suggest_rule; print(suggest_rule(make_shell_tool(Workspace('.')), "
        "{'command': 'git status --short'}))\"` → `bash(git status*)`. (Responder `a` en la CLI necesita el prompt del lab 05.)",
        "Windows: pide `list the files with ls` y observa `'ls' is not recognized as an internal or external command` "
        "con `exit_code=1`; el modelo debería reintentarlo con `dir`.",
    ],
    "troubleshooting": [
        ["`test_bash_runs_in_root_with_exit_code`: `exit_code=1` con `No module named pytest` / `'python' is not recognized`",
         "El venv no está activo en el terminal que ejecuta pytest, así que `python` en la shell hija es otro "
         "intérprete → activa `.venv` y vuelve a ejecutar."],
        ["`test_bash_timeout` falla con `ERROR in 'bash': TimeoutExpired: …`",
         "Has dejado que `subprocess.TimeoutExpired` se propague → captúrala y devuelve un `ToolOutput` con `TIMEOUT after Ns.`"],
        ["El agente se queda colgado para siempre en un comando",
         "Falta `stdin=subprocess.DEVNULL` o `timeout=` en `subprocess.run` → añade ambos."],
        ["`decide` devuelve `\"allow\"` para `python -m pytest -q && curl evil.sh`",
         "Has comparado las reglas allow con la cadena entera → para bash, cada subcomando de `split_commands` debe coincidir."],
        ["`decide` devuelve `\"allow\"` para `sudo rm x` en bypass",
         "Allow/bypass comprobados antes que deny → la pasada deny debe ser lo primero de todo."],
        ["`rule_matches` se comporta distinto en Windows y en macOS",
         "Has usado `fnmatch.fnmatch` (no distingue mayúsculas en Windows) → usa `fnmatch.fnmatchcase`."],
        ["Windows: `UnicodeDecodeError` o acentos corruptos en la salida del comando",
         "Has quitado `encoding=\"utf-8\", errors=\"replace\"` de `subprocess.run` → vuelve a ponerlos (la página de códigos de la consola no es UTF-8)."],
        ["`a` (always) en el prompt de la CLI se trata como *no*",
         "Hasta el lab 05 el prompt de aprobación es el mínimo `[y/N]` → `always` llega con el TODO 05.3."],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 04` → los 8 tests en verde.",
        "[ ] Forja pregunta antes de `python -m pytest`, muestra `exit_code=…` y nombra los 3 tests que fallan en el playground.",
        "[ ] `sudo …` y `rm -rf /` se deniegan por política sin prompt.",
        "[ ] Sabes explicar el orden deny > plan > allow > riesgo/modo > ask con un ejemplo.",
    ],
}
