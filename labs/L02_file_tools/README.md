# Lab 02 · Tools de ficheros

🇬🇧 [English](README.en.md) · Día 1 · 10:15–11:15

**Objetivo:** Dar al agente ojos y manos sobre el proyecto: leer, buscar, crear y editar ficheros con seguridad.

## Conceptos
- **El schema es el prompt:** nombre, docstring y type hints generan el JSON Schema que lee el modelo. Una buena descripción vale más que cualquier instrucción en el system prompt.
- **Las tools nunca lanzan:** cualquier error vuelve al modelo como texto accionable ("aparece 3 veces: añade contexto") para que se corrija solo.
- **edit_file = sustitución exacta de un texto único.** Es el formato más robusto con modelos pequeños (los diffs los generan mal). Errores frecuentes del modelo: incluir los números de línea de `read_file` o cambiar la indentación.
- **Leer antes de editar** y detectar cambios externos (mtime): el agente no pisa lo que no ha visto ni lo que tú has cambiado.
- **Sandbox:** todas las rutas se resuelven dentro del workspace. `../` y rutas absolutas fuera, rechazadas.
- **Explorar sin cargar el repo:** `grep` y `glob` devuelven rutas y líneas; el agente solo lee lo relevante.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: JSON Schema en formato OpenAI |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: ejecutar sin lanzar nunca |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: sandbox de rutas |
| 02.4 | `forja/fs_tools.py` | write_file: crear / reescribir con «leer antes» |
| 02.5 | `forja/fs_tools.py` | edit_file: sustitución exacta y única con errores útiles |
| 02.6 | `forja/fs_tools.py` | grep: búsqueda por regex en el workspace |

## Antes de empezar
- Abre `forja/tools.py` (TODOs 02.1–02.2), `forja/fs_tools.py` (02.3–02.6) y `tests/test_l02_tools.py`. Lee primero las partes ya hechas: el decorador `@tool` construye un modelo pydantic a partir de los type hints + el docstring (`Tool.args_model`), `ToolRegistry.parse_args(call)` valida los argumentos JSON, y `read_file` / `glob` son ejemplos completos de herramientas.
- Stdlib/APIs que usarás: pydantic `Model.model_json_schema()`; `json.dumps`; `time.perf_counter()`; `pathlib.Path.resolve()`, `.is_absolute()`, `.is_relative_to()`; `str.count`, `str.replace(old, new, 1)`; `re.compile`, `fnmatch.fnmatch`.
- Helpers de `Workspace` ya hechos que debes usar: `ws.resolve(path)` (tu 02.3), `ws.rel(p)` (cadena relativa), `ws.mark_read(p)` (recuerda el mtime), `ws.check_fresh(p)` (lanza `PermissionError` si no se ha leído o ha cambiado en disco), `ws.walk(base)` (ficheros, saltándose `.git`, `.venv`, `__pycache__`…), `ws.before_write` (callbacks, que usan los checkpoints del lab 11) y `unified_diff(before, after, path)`.
- Idea clave: las herramientas **lanzan** excepciones normales de Python con mensajes útiles; `ToolRegistry.execute` (02.2) lo captura todo y devuelve el mensaje al modelo como `ToolResult(ok=False, …)`. Así que las aserciones de los tests como `"before modifying" in res.output` comprueban TU texto de error pasado a través de `execute`.
- Cómo encaja: `schemas()` es lo que el modelo ve como `tools=[…]`; el gate del harness llama a `execute` por cada llamada que hace el modelo.

## Paso a paso
Primero 02.1 → 02.2 → 02.3: todos los tests de herramientas de ficheros pasan por `registry.execute` y `ws.resolve`, así que nada más puede pasar antes. Luego 02.4 (`write_file`), 02.5 (`edit_file`, la más grande) y 02.6 (`grep`). Ten `read_file` abierto como modelo de cómo se escribe una herramienta.

### TODO 02.1 · `forja/tools.py` · `Tool.schema()`

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

### TODO 02.2 · `forja/tools.py` · `ToolRegistry.execute(call)`

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

### TODO 02.3 · `forja/fs_tools.py` · `Workspace.resolve(path)`

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

### TODO 02.4 · `forja/fs_tools.py` · `make_fs_tools` → `write_file(path, content)` interna

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

### TODO 02.5 · `forja/fs_tools.py` · `make_fs_tools` → `edit_file(path, old_string, new_string, replace_all=False)` interna

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

### TODO 02.6 · `forja/fs_tools.py` · `make_fs_tools` → `grep(pattern, path=".", include=None, ignore_case=False, show_content=True)` interna

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

## Ejecuta
```bash
python scripts/tasks.py test 02
forja --cwd playground
> ¿qué hace la función due_date?        (aún sin bucle: responde como un chat; las tools llegan en el lab 03)
```

## Pruébalo en tu agente
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

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| Todos los tests de herramientas de ficheros fallan con `NotImplementedError: TODO 02.2` o `TODO 02.3` | Todos los tests pasan por `registry.execute` y `ws.resolve` → termina primero 02.2 y 02.3. |
| `AttributeError: 'NoneType' object has no attribute 'name'` en `execute` | Herramienta desconocida → `t` es `None` → usa `call.name` al construir el resultado de error. |
| El test espera `"before modifying"` pero la salida dice `"old_string not found"` | Cuentas las apariciones antes de `ws.check_fresh(p)` → sube la comprobación de frescura. |
| `edit_file` funciona una vez y la siguiente edición dice `has changed since you read it` | Falta `ws.mark_read(p)` tras escribir → llámalo al final de write_file y de edit_file. |
| `AssertionError: 'line numbers' in …` en el test de edición | Tu regex de pista no coincide con `"     9→    return …"` → usa `^\s*\d+→` con `re.M`, y copia el carácter `→` del código de `read_file`. |
| `UnicodeDecodeError` / caracteres corruptos al escribir en Windows | Falta `encoding="utf-8"` en `write_text`/`read_text` → pásalo siempre. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 02` → los 8 tests en verde.
- [ ] [ ] Desde el REPL obtienes un `read_file` numerado, un `grep` con resultados `path:line:` y un error de sandbox para `../`.
- [ ] [ ] Los mensajes de error de tu `edit_file` le dicen al modelo cómo corregir su llamada.

## Checkpoint
Tests del lab 02 en verde. Con el lab 03 todavía pendiente, Forja sigue siendo un chat: el bucle llega a continuación.

## Retos
1. Añade una tool `list_dir` con árbol de 2 niveles. ¿Mejora o empeora la exploración del modelo?
2. Pide al modelo que edite algo y fíjate en sus errores de `old_string`: ¿qué pista añadirías al mensaje de error?

**Tests:** `tests/test_l02_tools.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 03`

---
[← anterior](../L01_llm_streaming/README.md) · [siguiente →](../L03_loop/README.md)
