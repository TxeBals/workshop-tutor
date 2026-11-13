# Lab 07 · Gestión de contexto y compactación

🇬🇧 [English](README.en.md) · Día 2 · 09:40–10:25

**Objetivo:** Que una sesión larga quepa en la ventana de un modelo local sin romper el historial.

## Conceptos
- **El presupuesto:** modelos locales trabajan con 16–32k tokens efectivos. Un `pytest` verboso o un fichero grande se comen la ventana.
- **Nivel 1 — microcompactación (gratis):** vaciar salidas de tools antiguas. El modelo ya las usó; si las necesita, vuelve a leer.
- **Nivel 2 — compactación (1 llamada):** resumir los turnos antiguos (objetivo, ficheros, comandos, decisiones, pendientes) y conservar los recientes.
- **Invariante:** solo se corta antes de un mensaje `user`. Nunca entre un `tool_calls` y sus `tool`.
- **Es con pérdida:** mídelo con evals (lab 12) usando una ventana pequeña.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: vaciar salidas antiguas |
| 07.2 | `forja/compaction.py` | compact: resumen + turnos recientes, sin romper pares |

## Antes de empezar
- Abre `forja/compaction.py`. Se dan hechos: `SUMMARY_PROMPT`, `CLEARED = "[old tool result cleared]"`, `estimate_tokens(messages)` (~4 caracteres por token), `user_turn_starts(history)` (índices de los mensajes `user`) y `should_compact(...)` (verdadero por encima del 80% de la ventana). Tú escribes `microcompact` y `compact`.
- Conoce el formato del historial (chat de OpenAI): `{"role": "user", "content": ...}`, `{"role": "assistant", "content": ..., "tool_calls": [{"id", "type", "function": {"name", "arguments"}}]}`, `{"role": "tool", "tool_call_id": ..., "name": ..., "content": ...}`. Un mensaje assistant con `tool_calls` DEBE ir seguido de un mensaje `tool` por llamada: romper ese par hace que la API rechace la petición.
- Un "turno" empieza en un mensaje `user`. Cortar solo en los índices de `user_turn_starts(...)` es lo que garantiza que nunca separas un mensaje `tool_calls` de sus resultados.
- Cómo se conecta: `Forja.compact_now()` en `forja/harness.py` se ejecuta antes de cada turno: si `should_compact` → `microcompact(self.history)` (gratis); si sigue siendo demasiado grande → `compact(self.history, self.llm)` (una llamada al LLM). `/compact` llama a `compact_now(force=True)`. La llamada al LLM es `llm.chat(messages, temperature=0)` y devuelve un `ChatResponse` cuyo `.content` es el texto (en los tests, `FakeLLM` la registra en `llm.calls`).

## Paso a paso
Primero el 07.1: es un bucle puro que modifica en sitio, sin LLM, y te enseña el punto de corte (`starts[-keep_recent_turns]`) que reutiliza el 07.2. Luego el 07.2. `test_harness_autocompacts` (se ejecuta con el 07.2) ejercita ambos a través del harness con una ventana diminuta, así que solo pasa cuando los dos están bien.

### TODO 07.1 · `forja/compaction.py` · `microcompact(history, keep_recent_turns=2, min_chars=500) -> int`

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

### TODO 07.2 · `forja/compaction.py` · `compact(history, llm, keep_recent_turns=2) -> tuple[list, bool]`

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

## Ejecuta
```bash
python scripts/tasks.py test 07
forja --cwd playground
> lee todos los ficheros del proyecto y resúmelos
/context
/compact
/context
```

## Pruébalo en tu agente
1. `python scripts/tasks.py reset` y luego `forja --cwd playground`. Pide: `read every file in the project and summarise them` (aprueba con `y` si pregunta; las lecturas no deberían preguntar).
2. Escribe `/context`: algo como `~6000 tokens of 32768 (N messages)`. Haz dos preguntas cortas más (p. ej. `which function computes VAT?`, `where is the due date logic?`) para tener al menos 3 turnos: la compactación siempre conserva los 2 últimos.
3. Escribe `/compact`. Esperado: `compacted: summary + recent turns (~N tokens)`. Si solo tenías 1–2 turnos obtienes `nothing to compact` (o `microcompaction: N old outputs cleared`): es el comportamiento correcto.
4. Vuelve a escribir `/context`: el número baja claramente. Pregunta `what were we doing?`: el agente sigue conociendo los ficheros y el objetivo (los lee del resumen).
5. Opcional: crea `playground/.forja/settings.json` con `{"contextWindow": 6000}`, reinicia y trabaja unos cuantos turnos: aparece automáticamente una nota tenue `· microcompaction: ...` o `· compacted: ...` antes de un turno. Borra el fichero después.

## Si algo falla
| Síntoma | Causa → solución |
|---|---|
| `test_microcompact`: `assert 4 == 2` (se limpia todo) | Recorres el historial entero → solo `history[:starts[-keep_recent_turns]]`. |
| `test_microcompact`: la segunda llamada devuelve 2 en lugar de 0, o el contador es correcto pero los contenidos no cambian | No compruebas `!= CLEARED`, o modificas una copia (`dict(m)`) → muta los dicts originales y omite los ya limpiados. |
| `test_compact_keeps_pairs_and_recent`: se encuentra `question 3` en el prompt | Resumes el historial entero → solo `old = history[:cut]`. |
| `test_compact_keeps_pairs_and_recent`: `KeyError: 'tool_calls'` o `TypeError: can only concatenate str (not "NoneType")` | Usa `m.get("tool_calls", [])` y `m.get("content") or ""`. |
| `test_harness_autocompacts`: falla `assert any("compact" in n for n in app.notes)` | `compact` devuelve `(history, False)` demasiado a menudo, o el 07.1 lanza una excepción → comprueba primero ambas funciones con el test del 07.1; el harness solo añade la nota cuando se compactó algo. |
| Modelo real: tras `/compact` el agente olvida qué ficheros cambió | La compactación pierde información → asegúrate de que el texto de tu transcripción incluye los nombres de las herramientas y sus argumentos (¡las rutas!), no solo los contenidos; mídelo más adelante con evals (lab 12). |
| Modelo real: `/compact` tarda mucho | Es una llamada completa al LLM sobre hasta 60k caracteres → normal en un portátil; un límite menor en la transcripción lo hace más rápido. |

## Has terminado cuando
- [ ] [ ] `python scripts/tasks.py test 07` → 3 passed.
- [ ] [ ] `/context` baja tras `/compact` y el agente sigue sabiendo lo que estaba haciendo.

## Checkpoint
`/context` baja tras `/compact` y el agente sigue sabiendo qué estaba haciendo.

## Retos
1. Pon `"contextWindow": 6000` en `.forja/settings.json` y trabaja: ¿cuándo compacta?
2. Compacta con un modelo más pequeño que el principal.

**Tests:** `tests/test_l07_compaction.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 08`

---
[← anterior](../L06_context/README.md) · [siguiente →](../L08_planning/README.md)
