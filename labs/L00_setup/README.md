# Lab 00 · Setup y primer contacto

🇬🇧 [English](README.en.md) · Día 1 · 09:00–09:30

**Objetivo:** Tener Ollama con un modelo que sepa usar tools, el repo instalado y los tests ejecutándose.

## Conceptos
- **Qué vamos a construir:** *Forja*, un agente de código de terminal como los comerciales: lee y edita tu proyecto, ejecuta comandos, pide permiso, planifica, delega en subagentes y se extiende con hooks, skills y MCP. Funciona con modelos abiertos en tu máquina.
- **Agente = modelo + tools + bucle. Harness = todo lo demás** (permisos, contexto, interfaz, sesiones…). El modelo es una pieza intercambiable: el harness es lo que construimos.
- **Cómo funcionan los labs:** cada lab tiene funciones con `TODO` en `forja/` y tests en `tests/`. Cuando los tests pasan, la capacidad se enciende sola en tu CLI. ¿Te quedas atrás? `python scripts/tasks.py catchup NN`.
- **Modelos:** `qwen3:8b` (portátil de 16 GB), `qwen3-coder:30b` (Mac de 32 GB o GPU de 24 GB), o el servidor compartido del aula. OpenRouter solo con modelos open-weight.

## Lo que implementas
Este lab no tiene TODOs.

## Antes de empezar
- Necesitas tener instalados **Python 3.11+**, **git** y **Ollama** (o la dirección del servidor compartido de la sala). Compruébalo con `python --version` (macOS/Linux: `python3 --version`), `git --version` y `ollama --version`.
- Todo se ejecuta **desde la raíz del repo** mediante `python scripts/tasks.py …`, así los mismos comandos funcionan en Windows (PowerShell/cmd) y en macOS/Linux, sin `make`.
- Mapa del repo: `forja/` = TU código (funciones stub que lanzan `NotImplementedError("TODO NN.x")` con un comentario de pista encima), `tests/test_lNN_*.py` = tests offline por lab (usan `forja/fake_llm.py`, no hace falta modelo), `playground/` = pequeño proyecto de facturas con 3 bugs que arreglará tu agente, `labs/LNN_*/` = enunciados de los labs.
- Forja es **progresivo**: `forja/harness.py` captura `NotImplementedError` y sigue funcionando sin la pieza que falta, mostrando una nota como `· tools: lab 02 pending — running without this capability`. Cada lab que terminas enciende una capacidad en la CLI.

## Setup paso a paso
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

## Ejecuta
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # instala y crea .env
ollama pull qwen3:8b               # o el modelo de tu nivel de hardware
python scripts/tasks.py test       # casi todo en rojo: es lo esperado
cd playground && python -m pytest -q   # 3 tests fallan: trabajo para tu agente
```

## Pruébalo en tu agente
1. Mira cómo el tutor ejecuta `python scripts/tasks.py demo`: el agente de referencia sobre `playground/`. Ese es tu agente al final del día 2.
2. Ejecuta `ollama ps` mientras `ollama run qwen3:8b "write a haiku"` está respondiendo: fíjate en GPU vs CPU y en la memoria usada.
3. Echa un vistazo a `forja/harness.py`, método `Forja.gate`: cada tool call pasa por parse → hook PreToolUse → permisos → aprobación → ejecución → hook PostToolUse. Cada paso es un lab.
4. Abre `forja/llm.py` y busca el primer comentario `# TODO 01.1:`: así es un stub de partida.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled` | Política de ejecución → `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, o usa cmd.exe con `.venv\Scripts\activate.bat`. |
| `forja` is not recognized / `command not found: forja` | El venv no está activo o `setup` falló → actívalo y vuelve a ejecutar `python scripts/tasks.py setup`. `python -m forja` funciona como alternativa. |
| `ERROR: Package 'forja' requires a different Python` | Tu Python es anterior a 3.11 → instala 3.11+ y vuelve a crear `.venv` con él (Windows: `py -3.12 -m venv .venv`). |
| `forja doctor` → `✘ could not talk to the model: APIConnectionError` | Ollama no está en marcha o `OLLAMA_BASE_URL` es incorrecta → arranca la app de Ollama (o `ollama serve`) y comprueba que `http://localhost:11434` en un navegador dice *Ollama is running*. |
| `forja doctor` → `ModelPolicyError: model '…' blocked by policy` | Has elegido un id de modelo cerrado (anthropic/openai/gpt-oss/o3…) → usa un modelo open-weight. |
| `forja doctor` va muy lento la primera vez (30–90 s) | El modelo se está cargando en memoria → normal; la segunda llamada es rápida. Si sigue lento, `ollama ps` probablemente muestra CPU: usa un modelo más pequeño o el servidor compartido. |
| macOS: `python: command not found` | Fuera del venv macOS solo tiene `python3` → crea el venv con `python3 -m venv .venv`; una vez activo, `python` funciona. |

## Has terminado cuando
- [ ] [ ] `ollama run <your model> "hello"` responde (o el servidor compartido responde a `forja doctor`).
- [ ] [ ] `forja doctor` muestra `✔ the model calls tools`.
- [ ] [ ] `python scripts/tasks.py test` se ejecuta y muestra fallos rojos `NotImplementedError: TODO …`.
- [ ] [ ] Los tests de `playground` muestran exactamente 3 fallos.

## Checkpoint
`ollama run qwen3:8b "hola"` responde y `python scripts/tasks.py test` se ejecuta (en rojo, como debe ser). El tutor enseña `python scripts/tasks.py demo`: así será tu agente al final del día 2.

## Retos
1. Ejecuta `ollama ps` mientras el modelo responde: ¿va en GPU o CPU? ¿Cuánta memoria usa?
2. Lee `forja/harness.py` por encima: localiza la «puerta» por la que pasa cada tool call.

---
[siguiente →](../L01_llm_streaming/README.md)
