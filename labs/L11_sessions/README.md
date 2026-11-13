# Lab 11 · Sesiones y deshacer

🇬🇧 [English](README.en.md) · Día 2 · 14:20–14:55

**Objetivo:** Retomar sesiones y deshacer lo que hizo el agente sin depender de git.

## Conceptos
- **Transcript JSONL append-only:** un mensaje por línea en `.forja/sessions/`. Reanudar, auditar y depurar. Tras compactar, una marca con el nuevo estado.
- **Checkpoints:** antes de que una tool modifique un fichero, se guarda su contenido original (o que no existía) — solo la primera vez por turno.
- **/undo:** restaura los ficheros del último turno con cambios. Funciona en carpetas sin git y no toca tus commits.
- **Límite:** los efectos de `bash` (instalar paquetes, borrar con `rm`) no se deshacen. Por eso bash pasa por permisos.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (con marcas de compactación) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

## Antes de empezar
- Abre `forja/session.py`. Dos clases independientes: `Transcript` (11.1, 11.2: un fichero JSONL por sesión en `<project>/.forja/sessions/<id>.jsonl`) y `Checkpoints` (11.3, 11.4: una pila en memoria de turnos, cada uno `{Path: original bytes | None}`). `mark_compaction` y `list_sessions` ya están escritas: léelas, te dicen el formato de línea (`{"ts": ..., "message": m}` y `{"ts": ..., "compacted": [...]}`).
- Cómo las usa el harness: al final de `Forja.turn` llama a `self.transcript.append(*self.history[start:])` (solo los mensajes NUEVOS); `resume(id)` llama a `Transcript.load(folder, id)`. `Forja.turn` llama a `self.checkpoints.begin_turn()`, y `Workspace` llama a `checkpoints.before_write(path)` justo ANTES de que `write_file`/`edit_file` toquen un fichero (ver `forja/fs_tools.py`). `/undo` llama a `Checkpoints.undo()`.
- Stdlib: `json.dumps(obj, ensure_ascii=False)`, `json.loads(line)`, `Path.open("a", encoding="utf-8")` (modo append), `Path.read_bytes()` / `write_bytes()` (bytes, para que codificaciones y finales de línea se restauren exactamente), `Path.unlink(missing_ok=True)`, `Path.mkdir(parents=True, exist_ok=True)`.
- Límite a tener en cuenta: solo las herramientas de ficheros crean checkpoints. Lo que haga `bash` (`rm`, `pip install`, `sed -i`) no se puede deshacer.

## Paso a paso
11.1 y 11.2 juntos (un test de ida y vuelta: `test_transcript_roundtrip`), luego 11.3 y 11.4 juntos (`test_checkpoints`). Termina con `test_harness_resume_and_undo`, que lo ejercita todo a través del harness real (necesita los labs 02-04 para `edit_file` en `accept_edits`).

### TODO 11.1 · `forja/session.py` · `Transcript.append(self, *messages: dict) -> None`

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

### TODO 11.2 · `forja/session.py` · `Transcript.load(folder: Path, session_id: str) -> list[dict]` (staticmethod)

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

### TODO 11.3 · `forja/session.py` · `Checkpoints.before_write(self, path: Path) -> None`

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

### TODO 11.4 · `forja/session.py` · `Checkpoints.undo(self) -> list[Path]`

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

## Ejecuta
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> cambia el vencimiento por defecto a 60 días
/undo
/sessions
forja --cwd playground --resume <id>
```

## Pruébalo en tu agente
1. `forja --cwd playground --mode accept_edits` y escribe `change the default due-date period to 60 days`. Esperado: un `edit_file invoices/dates.py` con un panel de diff (`days: int = 30` → `60`), sin pedir aprobación (accept_edits).
2. `/undo` → `restored: invoices/dates.py`. Comprueba el fichero: vuelve a poner `30`. `/undo` otra vez → `nothing to undo`.
3. Haz una pregunta simple (`what does due_date do?`), haz otra edición, otra pregunta, y luego `/undo`: sigue revirtiendo el último turno CON cambios (los turnos vacíos se omiten).
4. `/sessions` → líneas como `20261103-143012-a1b2  change the default due-date period to 60 days`. Mira el fichero en bruto: macOS/Linux `cat playground/.forja/sessions/<id>.jsonl` · PowerShell `Get-Content playground\.forja\sessions\<id>.jsonl` — un objeto JSON por línea.
5. `/exit`, luego `forja --cwd playground --resume <id>` y pregunta `what did you change before?` → el agente responde a partir del historial restaurado.
6. Fíjate en lo que NO se deshace: pide al agente `create a file tmp.txt using bash` y `/undo` → `tmp.txt` sigue ahí (`/undo` dice `nothing to undo`, o revierte en su lugar un turno de edición ANTERIOR). Limpia con `python scripts/tasks.py reset` si hace falta.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `json.decoder.JSONDecodeError: Extra data` en `load` | Dos registros en la misma línea → añade `"\n"` tras cada `json.dumps` en `append`. |
| La ida y vuelta devuelve solo el último mensaje | Abriste el fichero con `"w"` → usa el modo append `"a"`. |
| `test_checkpoints`: `a.txt` se restaura a `v1` en vez de `original` | `before_write` sobrescribe el original guardado → guárdalo solo la primera vez que aparece la ruta en el turno. |
| `/undo` siempre dice `nothing to undo` tras una pregunta posterior | No se omiten los turnos vacíos de la cima de la pila → saca los turnos vacíos antes de sacar el real. |
| `test_harness_resume_and_undo`: falla `app2.history == app.history` | Los mensajes se modifican por el camino (p. ej. guardaste `str(m)` o solo `content`) → vuelca el dict entero como JSON y cárgalo de vuelta sin cambios. |
| `UnicodeEncodeError` / texto corrupto en `.jsonl` en Windows | La página de códigos por defecto no es UTF-8 → pasa `encoding="utf-8"` al abrir y al leer, y mantén `ensure_ascii=False`. |
| `--resume` dice que la sesión no existe | Las sesiones viven en `<project>/.forja/sessions/` → reanuda con el mismo `--cwd` que usaste al crearla, y copia el id de `/sessions`. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 11` → 3 passed.
- [ ] [ ] `/undo` restaura un fichero editado por el agente y borra un fichero que creó, sin git.
- [ ] [ ] `forja --cwd playground --resume <id>` continúa la conversación anterior.

## Checkpoint
`/undo` deja el fichero como estaba y `--resume` continúa la conversación anterior.

## Retos
1. `/undo N` para deshacer varios turnos.
2. `/rewind`: deshacer ficheros Y volver el historial al mismo punto.

**Tests:** `tests/test_l11_sessions.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 12`

---
[← anterior](../L10_extensions/README.md) · [siguiente →](../L12_evals/README.md)
