# Forja · Construye tu propio agente de código con modelos locales

🇬🇧 [English](README.en.md)

> 🔒 **Repo privado del tutor.** Contiene la solución (`solutions/`), el material del tutor (`docs/tutor/`) y los generadores.
> El repo de los alumnos (`TxeBals/devopsday-workshop`, solo inglés, sin soluciones) se genera desde aquí:
> ```
> python scripts/export_student.py ../devopsday-workshop --zip   # regenera el repo del alumno y ../forja-solutions.zip
> ```
> Si cambias la solución: `python scripts/tasks.py starters` → `python scripts/tasks.py solutions` → `export_student.py`.
> Guion completo: [guion_ponente.md](docs/tutor/guion_ponente.md) · Reparte `forja-solutions.zip` solo a quien necesite `catchup`.


Workshop práctico de 2 días (o 1 día comprimido) en el que cada asistente construye **Forja**, un agente de código de terminal —del tipo de Claude Code, Codex CLI u OpenCode— desde cero, en Python y con **modelos abiertos en local** (Ollama, vLLM, LM Studio) u OpenRouter con modelos open-weight. No se usan modelos de Anthropic ni OpenAI: el código los bloquea.

Cada lab rellena una pieza; el harness es **progresivo**: la CLI funciona desde el lab 01 y gana capacidades a medida que completas labs.

## Por dónde empiezo
| Soy… | Lee |
|---|---|
| **Tutor** | [Guía del tutor](docs/tutor/guia_tutor.md) → [checklist de setup](docs/checklist_setup.md) → decks [ES](https://claude.ai/artifact/GkGG788cUiMgA9Xs238Yag) · [EN](https://claude.ai/artifact/CV6PaTZE4j8D58Gtpw2nKt) |
| **Alumno** | [Checklist de setup](docs/checklist_setup.md) (antes del día) → [Cuaderno del alumno](docs/alumno/cuaderno_alumno.md) → labs en orden |

## Labs
| Lab | Día · hora | Tema |
|---|---|---|
| [L00](labs/L00_setup/README.md) | 1 · 09:00–09:30 | Setup y primer contacto |
| [L01](labs/L01_llm_streaming/README.md) | 1 · 09:30–10:15 | Cliente LLM con streaming |
| [L02](labs/L02_file_tools/README.md) | 1 · 10:15–11:15 | Tools de ficheros |
| [L03](labs/L03_loop/README.md) | 1 · 11:30–12:15 | El bucle del agente |
| [L04](labs/L04_bash_permissions/README.md) | 1 · 12:15–13:00 | Bash y permisos |
| [L05](labs/L05_cli/README.md) | 1 · 14:00–15:00 | La CLI: tu agente de terminal |
| [L06](labs/L06_context/README.md) | 2 · 09:00–09:40 | Ingeniería de contexto |
| [L07](labs/L07_compaction/README.md) | 2 · 09:40–10:25 | Gestión de contexto y compactación |
| [L08](labs/L08_planning/README.md) | 2 · 10:25–11:10 | Planificar antes de actuar |
| [L09](labs/L09_subagents/README.md) | 2 · 11:25–12:10 | Subagentes |
| [L10](labs/L10_extensions/README.md) | 2 · 12:10–13:20 | Extensibilidad: hooks, skills y MCP |
| [L11](labs/L11_sessions/README.md) | 2 · 14:20–14:55 | Sesiones y deshacer |
| [L12](labs/L12_evals/README.md) | 2 · 14:55–16:00 | Evals: medir tu agente |
| — | 2 · 16:00 | Proyecto final (ver cuaderno) |

## Comandos (Windows, macOS y Linux)
```bash
python scripts/tasks.py setup          # instalar y crear .env
python scripts/tasks.py test 03        # tests del lab 03 contra tu código
python scripts/tasks.py catchup 05     # ponerte al día: resuelve los labs 01–04
forja                                  # tu agente, sobre el directorio actual
python scripts/tasks.py demo           # (tutor) la solución sobre playground/
python scripts/tasks.py evals          # evals con tu agente
```

## Estructura
```
forja-workshop/
├── docs/
│   ├── tutor/          guia_tutor.md · tutor_guide.md        ← tutor / tutor
│   ├── alumno/         cuaderno_alumno.md                    ← alumno (ES)
│   ├── student/        student_workbook.md                   ← student (EN)
│   ├── checklist_setup.md · setup_checklist.md · hardware.png
├── labs/L00…L12/       README.md (ES) · README.en.md (EN)
├── forja/              código del alumno con TODOs  / student code with TODOs
├── solutions/forja/    implementación de referencia / reference implementation
├── tests/              test_lNN_*.py  (offline, FakeLLM)
├── playground/         proyecto con bugs para el agente / buggy practice project
├── examples/           settings, hooks, skills, subagente, servidor MCP
├── evals/              tasks.yaml · hidden/ · run_evals.py
└── scripts/            tasks.py · catchup.py · make_starters.py · build_docs.py
```

## Notas
- Datos y proyecto de práctica sintéticos.
- No se basa en OpenClaude (fork del código filtrado de Claude Code): Forja es una implementación propia con la misma arquitectura, documentada públicamente.
- Los tests no necesitan modelo ni GPU (FakeLLM). Los tags de modelos cambian: verifícalos antes del workshop.
