# Lab 06 · Ingeniería de contexto

🇬🇧 [English](README.en.md) · Día 2 · 09:00–09:40

**Objetivo:** Decidir qué ve el modelo en cada turno: prompt por capas, AGENTS.md, entorno y menciones @fichero.

## Conceptos
- **El system prompt se reconstruye cada turno** por capas: base del agente, recordatorio del modo, instrucciones del proyecto, skills, lista de tareas y entorno (git, SO, fecha, modelo).
- **AGENTS.md:** convención abierta para instrucciones de proyecto que leen varias herramientas. Global del usuario + desde la carpeta más alta hasta la actual: lo más específico, al final.
- **Entorno = verdad barata:** rama y cambios de git, directorio, fecha. Evita que el modelo adivine.
- **@menciones:** `@src/app.py` mete el fichero en el mensaje (y cuenta como leído). Ahorra una vuelta del bucle.
- **Menos es más con modelos locales:** cada token de prompt compite con el código. Instrucciones cortas y concretas.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: AGENTS.md del usuario y de la jerarquía |
| 06.2 | `forja/context.py` | build_system_prompt: capas en orden |
| 06.3 | `forja/context.py` | expand_mentions: @ruta → contenido |

## Antes de empezar
- Abre `forja/context.py`. Lee primero las partes que se dan hechas: `BASE_PROMPT`, `MODE_REMINDERS` (un dict modo -> texto), `INSTRUCTION_FILES = ("AGENTS.md", "FORJA.md")`, `MENTION_RE` y `git_info(root)`. Escribes tres funciones.
- Mira `Forja.system_prompt()` y `Forja.turn()` en `forja/harness.py`: el harness llama a `build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos])` en CADA paso, y a `expand_mentions(text, self.ws)` en cada mensaje del usuario. Hasta que termines este lab usa el `FALLBACK_PROMPT` de una línea, así que tu agente nunca ha visto `AGENTS.md`.
- Stdlib que necesitas: `pathlib.Path` (`/`, `.is_file()`, `.resolve()`, `.parent`, `.read_text(encoding="utf-8")`, `.is_relative_to()`), `re.Pattern.findall`, `dict.fromkeys(...)` (deduplicación que conserva el orden), `platform.system()`, `datetime.date.today().isoformat()`.
- Del lab 02 reutilizas el `Workspace` (`forja/fs_tools.py`): `ws.root`, `ws.resolve(path)` (lanza `PermissionError` fuera del sandbox), `ws.rel(p)` y `ws.mark_read(p)` (registra el fichero en `ws.read_state` para que un `edit_file` posterior no se queje de que no se ha leído).

## Paso a paso
Primero el 06.1: el 06.2 lo llama para obtener los ficheros de instrucciones. Luego el 06.2, el prompt por capas, que es lo que activa AGENTS.md en tu CLI. El 06.3 es independiente; déjalo para el final. Cuando el 06.2 pase, el `test_plan_mode_flow` del lab 08 también depende de él (comprueba `PLAN mode` y la lista de tareas en el system prompt).

### TODO 06.1 · `forja/context.py` · `find_instruction_files(cwd, home=None, stop=None) -> list[Path]`

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

### TODO 06.2 · `forja/context.py` · `build_system_prompt(ws, mode, model, home=None, skills_catalog="", extra=None) -> str`

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

### TODO 06.3 · `forja/context.py` · `expand_mentions(text, ws, max_chars=20_000) -> str`

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

## Ejecuta
```bash
python scripts/tasks.py test 06
forja --cwd playground
> revisa @invoices/amounts.py y dime si cumple lo que dice AGENTS.md
```

## Pruébalo en tu agente
1. Resetea primero: `python scripts/tasks.py reset`. Arranca `forja --cwd playground`. La nota tenue `context: lab 06 pending ...` YA NO debería aparecer.
2. Pide: `review @invoices/amounts.py and tell me whether it follows AGENTS.md`. Esperado: NINGUNA línea `⏺ Read invoices/amounts.py` (el fichero llegó con el mensaje) y una respuesta que cite las reglas: redondeo half-up con `decimal`, no `round()` sobre floats, no cambiar los tests.
3. Pregunta sin mencionar las reglas: `what are the rules of this project?`. El agente responde a partir de `AGENTS.md` sin llamar a ninguna herramienta.
4. Escribe `/context` antes y después de un mensaje con una mención `@` grande: el número de tokens crece aproximadamente el tamaño del fichero / 4.
5. Opcional: crea `~/.forja/AGENTS.md` (Windows: `%USERPROFILE%\.forja\AGENTS.md`) con `Always answer in Spanish.`; reinicia Forja y saluda. Cambia el idioma de la respuesta: la capa global funciona.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_find_instruction_files_order` devuelve `['global', 'package', 'root']` | No invertiste el recorrido (o invertiste también el fichero global) → recoge de abajo arriba, invierte solo la cadena y luego antepón el fichero global. |
| `test_find_instruction_files_order` encuentra ficheros de más o nunca se detiene (macOS) | Comparas `cwd` resuelto con `stop` sin resolver (`/var` frente a `/private/var`) → resuelve también `stop`. |
| `test_system_prompt_layers` falla en `half-up` in sp | No se incluyó el AGENTS.md del playground → llama a `find_instruction_files(ws.root, home=home)` y añade el CONTENIDO del fichero, no solo su ruta. |
| `UnicodeDecodeError: 'charmap' codec can't decode` (Windows) | `read_text()` sin encoding → `read_text(encoding="utf-8")` (y `errors="replace"` para los ficheros mencionados). |
| `test_expand_mentions`: `out.count("<file") == 2` o un fallo con `@../../etc/passwd` | Falta el `except PermissionError` o la comprobación `is_file()` → omite las menciones no válidas con `continue`. |
| En el CLI el agente sigue ignorando AGENTS.md | Ejecutaste Forja desde otra carpeta, o el AGENTS.md no está bajo `--cwd` → arranca con `forja --cwd playground`; los modelos pequeños también pueden necesitar que se repita la regla en el prompt (menos es más: mantén AGENTS.md corto). |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 06` → 3 passed.
- [ ] [ ] En el CLI el agente cita las reglas de `playground/AGENTS.md` (half-up, no tocar los tests) sin que se lo digas.
- [ ] [ ] Una mención `@file` se responde sin una línea `⏺ Read` adicional.

## Checkpoint
El agente cita reglas del `playground/AGENTS.md` (half-up, no tocar tests) sin que se las digas.

## Retos
1. Escribe tu `~/.forja/AGENTS.md` con tus preferencias (idioma, estilo).
2. Añade al entorno la versión de Python y los últimos 3 commits.

**Tests:** `tests/test_l06_context.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 07`

---
[← anterior](../L05_cli/README.md) · [siguiente →](../L07_compaction/README.md)
