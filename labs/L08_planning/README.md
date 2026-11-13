# Lab 08 · Planificar antes de actuar

🇬🇧 [English](README.en.md) · Día 2 · 10:25–11:10

**Objetivo:** Lista de tareas visible y modo plan: el agente investiga, propone y solo ejecuta cuando apruebas.

## Conceptos
- **todo_write:** el agente mantiene su lista (pending / in_progress / completed). Obliga a descomponer y mejora mucho la constancia de modelos pequeños en tareas largas. Una sola tarea en curso.
- **La lista vuelve al contexto** cada turno (capa del system prompt): el agente no se pierde.
- **Modo plan:** solo lectura por permisos, no por buena voluntad del modelo. Cuando tiene un plan, llama a `exit_plan_mode`; si lo apruebas, el harness cambia a modo default.
- **Cuándo usarlo:** cambios de varios ficheros, código que no conoces, cualquier cosa difícil de deshacer.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write con validación |
| 08.2 | `forja/planning.py` | exit_plan_mode con aprobación del usuario |

## Antes de empezar
- Abre `forja/planning.py`. Se dan hechos: `TodoItem` (modelo pydantic con `content: str` y `status: "pending" | "in_progress" | "completed"`, por defecto `pending`), `ICON` y `TodoStore` con `.items` y `.render()` (una línea `☐/▶/☑ content` por elemento, o `(empty list)`). Tú escribes los CUERPOS de dos herramientas, dentro de funciones factoría.
- Ambas herramientas se crean con `@tool(risk="read")` del lab 02: el docstring y las anotaciones de tipo se convierten en el JSON schema que lee el modelo, así que no los cambies. Lanzar una excepción dentro de una herramienta es la forma correcta de rechazar una entrada incorrecta: `ToolRegistry.execute` la convierte en `ERROR in '<tool>': ValueError: <message>` y el modelo puede corregirse.
- Los argumentos llegan a tu función DESPUÉS de la validación de pydantic y de `model_dump()`, así que `todos` normalmente llega como una lista de dicts simples; pero el código también puede llamar a la función con objetos `TodoItem`. Acepta ambos (`TodoItem.model_validate(d)`).
- Cómo se conecta: `Forja._build_registry` registra `make_todo_tool(self.todos)` y `make_exit_plan_tool(self._approve_plan, lambda: self.set_mode("default"))`. La lista de tareas vuelve al system prompt en cada paso mediante `extra` en `build_system_prompt` (lab 06). El modo plan es de solo lectura porque `permissions.decide` (lab 04) deniega las herramientas que no son de lectura en `plan`, no porque el modelo se porte bien.

## Paso a paso
Primero el 08.1 (lógica de validación, totalmente cubierta por `test_todo_write_validation`), luego el 08.2 (corto). `test_plan_mode_flow`, seleccionado con el 08.2, conduce un turno completo en modo plan a través del harness y necesita que el 08.1, el 08.2, el lab 04 (deny en modo plan) y el lab 06 (las capas del prompt) funcionen.

### TODO 08.1 · `forja/planning.py` · `make_todo_tool(store)` → interna `todo_write(todos: list[TodoItem]) -> str`

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

### TODO 08.2 · `forja/planning.py` · `make_exit_plan_tool(approve, on_approved)` → interna `exit_plan_mode(plan: str) -> str`

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

## Ejecuta
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> añade descuentos porcentuales a las facturas (antes del IVA) con tests
/todos
```

## Pruébalo en tu agente
1. `python scripts/tasks.py reset` y luego `forja --cwd playground --mode plan`. El prompt muestra `plan ›`.
2. Pide: `add percentage discounts to invoices (before VAT) with tests`. Esperado: solo acciones de lectura (`⏺ Read ...`, `⏺ Grep ...`, `⏺ Glob ...`). Si el modelo intenta una edición verás un `⎿ DENIED (plan mode: read-only) ...` en rojo y volverá a investigar.
3. Aparece un panel magenta `Proposed plan` con los ficheros a tocar, los cambios y cómo verificarlo, seguido de `Approve the plan and start? [y/N] >`. Responde `n` una vez: el modelo recibe `REJECTED` y pregunta qué cambiar. Dile qué ajustar y aprueba con `y` la siguiente vez.
4. Tras `y`: el modo del REPL pasa a `default` (el siguiente prompt muestra `default ›`), las ediciones ahora piden aprobación y ves líneas `⏺ Todos (N)` a medida que el agente marca tareas. Escribe `/todos` cuando quieras: `☑ ...`, `▶ ...`, `☐ ...`.
5. Al final el agente ejecuta los tests; compruébalo tú con `cd playground` y `python -m pytest -q`. Luego `python scripts/tasks.py reset` para limpiar.

## Si algo falla
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

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 08` → 3 passed.
- [ ] [ ] En modo plan el agente investiga, presenta un plan con `exit_plan_mode` y, tras `y`, lo ejecuta marcando tareas (`/todos` muestra el progreso).
- [ ] [ ] Viste al menos un `DENIED (plan mode: read-only)` o un `REJECTED` y el agente se recuperó.

## Checkpoint
En modo plan el agente investiga, presenta un plan y, al aprobarlo, lo ejecuta marcando tareas.

## Retos
1. Al aprobar, pasa a `accept_edits` en vez de `default`. ¿Cuándo es buena idea?
2. Muestra la lista de tareas en vivo bajo cada respuesta.

**Tests:** `tests/test_l08_planning.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 09`

---
[← anterior](../L07_compaction/README.md) · [siguiente →](../L09_subagents/README.md)
