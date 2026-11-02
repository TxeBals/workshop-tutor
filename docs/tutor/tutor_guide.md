# Tutor guide · Forja: build your own coding agent with local models

🇪🇸 [Español](guia_tutor.md) · Student material: [`docs/student/student_workbook.md`](../student/student_workbook.md) · Labs: [`labs/`](../../labs)

> The code, practice project and agent prompts are in Spanish; READMEs, workbooks and decks exist in both languages.

## 1. What attendees achieve

By the end, every attendee has **their own terminal coding agent** —the same kind of tool as Claude Code, Codex CLI or OpenCode— running on **local open models**, and can explain and modify every piece:

| Layer | Piece | Lab |
|---|---|---|
| Model | Streaming client for Ollama / vLLM / LM Studio / OpenRouter | 01 |
| Agent | File tools, loop, bash | 02, 03, 04 |
| Harness | Permissions and approval, CLI, context, compaction, plan, subagents, hooks, skills, MCP, sessions, undo | 04–11 |
| Quality | Evals with real tasks and hidden tests | 12 |

**Learning outcomes (what they must be able to explain):**
1. Why an agent is *model + tools + loop* and everything else is harness.
2. How tool calls arrive in streaming and why history has `tool_calls`/`tool` pairs that must never break.
3. Why `edit_file` is exact replacement and why reading before editing is enforced.
4. How a permission is decided (deny > plan > allow > mode > ask) and why bash rules are checked per subcommand.
5. What goes into the context each turn and how to compact without breaking history.
6. When to plan, when to delegate to a subagent, and when a policy must be a hook rather than an instruction.
7. How to measure an agent with evals and compare models with data.

## 2. Format

- **2 days**, 7 effective hours each. Day 1 = *an agent that works*; day 2 = *a professional harness*.
- **1-day version:** labs 00–05 in full + live demos (no practice) of 06, 08 and 10 with `python scripts/tasks.py demo`.
- **Each lab:** 10–15 min theory with the deck → 25–45 min practice with tests → 2 min checkpoint out loud.
- **Pairs recommended** (one types, one reads the workbook and tests), switching each lab.
- **No IDE AI assistants** during labs: the goal is understanding, and the tests give instant feedback.

### Agenda
| Day 1 | | Day 2 | |
|---|---|---|---|
| 09:00 | L00 Setup and tour | 09:00 | L06 Context |
| 09:30 | L01 Streaming client | 09:40 | L07 Compaction |
| 10:15 | L02 File tools | 10:25 | L08 Plan and todos |
| 11:15 | *Break* | 11:10 | *Break* |
| 11:30 | L03 Loop | 11:25 | L09 Subagents |
| 12:15 | L04 Bash and permissions | 12:10 | L10 Hooks, skills, MCP |
| 13:00 | *Lunch* | 13:20 | *Lunch* |
| 14:00 | L05 CLI | 14:20 | L11 Sessions and undo |
| 15:00 | *Break* | 14:55 | L12 Evals |
| 15:15 | **Milestone: your agent fixes the playground** | 16:00 | **Final project + demos** |
| 16:30 | Day retro | 17:00 | Close |

## 3. Preparation

| When | What | ✔ |
|---|---|---|
| T-14 | Check attendees' hardware against `docs/hardware.png` (or the checklist). Decide whether you need a **shared server** | ☐ |
| T-14 | If so: NVIDIA 24 GB+ GPU running vLLM with `Qwen/Qwen3-Coder-30B-A3B-Instruct` (or Ollama with `qwen3-coder:30b` and `OLLAMA_NUM_PARALLEL`) | ☐ |
| T-10 | Send `docs/setup_checklist.md`: download models beforehand (≈ 5–19 GB depending on tier) | ☐ |
| T-7 | Workshop OpenRouter key with a spend limit, open-weight models only (plan B) | ☐ |
| T-3 | Check the Ollama tags and OpenRouter ids in `.env.example` still exist | ☐ |
| T-2 | `python scripts/tasks.py starters` and `python scripts/tasks.py solutions` → all green | ☐ |
| T-2 | Full rehearsal with a real model: `python scripts/tasks.py demo` on `playground/` (fix the 3 tests, plan mode with discounts, subagent, hooks with `examples/project/.forja`) | ☐ |
| T-2 | `python scripts/tasks.py evals --repeat 3` with 2 models: your reference numbers (not shown; used to spot problems) | ☐ |
| T-1 | Student repo (`TxeBals/devopsday-workshop`, no solutions) published. Bring `forja-solutions.zip` (in your folder) on USB/Teams: `catchup` needs it at the student repo root or via `--from` | ☐ |
| T-1 | Repo on reachable git (or USB). Network plan B: wheelhouse (`pip download -r … -d wheels`) and models on USB (`~/.ollama/models`) | ☐ |
| T-0 | ES/EN decks open, large terminal font, clean `playground` (`python scripts/tasks.py reset`) | ☐ |

**Windows:** the `bash` tool uses `cmd.exe` (the agent knows from the tool description). The whole repo works with `python scripts/tasks.py …`, no `make` needed. To copy folders: `xcopy /E /I`.

## 4. Running the room

- **Traffic light:** at the start of practice each pair marks green (tests pass), amber (stuck <10 min) or red. At two-thirds of the time, anyone red runs `python scripts/tasks.py catchup NN+1` and moves on. **Never wait for the last person**: the progressive design lets everyone reach the milestone.
- **Different paces:** fast pairs do the lab's *challenges*; they don't run ahead (it breaks the debrief).
- **Slow models:** anyone under ~15 tok/s moves to the shared server (`FORJA_BACKEND=openai_compat`).
- **What teaches most:** project a student's CLI when the model does something odd and ask the room “which harness piece would fix this?”.

## 5. Lab by lab

For each lab: **key message**, **demo** (with the solution: `python scripts/tasks.py demo`), **where people get stuck**, **check questions** and **if there's time left**.

### L00 · Setup and tour (30 min)
- **Message:** “The model is a swappable part. Today we build the harness, which is what makes an agent useful.”
- **Demo (5 min):** `python scripts/tasks.py demo` → *“make the tests pass”*. Show diffs, permissions, green tests. “By tomorrow afternoon you'll have written this.”
- **Context worth giving:** projects such as OpenClaude (a fork of the leaked Claude Code source), OpenCode, Aider or Pi exist. We use none of them: we build our own from scratch with the same, publicly documented architecture. That way we understand every piece and avoid licence and trademark issues in a corporate setting.
- **Stuck:** Ollama not running; model without a tools template (`llama3`, `deepseek-r1:8b`); PowerShell blocking `activate` (`Set-ExecutionPolicy -Scope Process Bypass`).

### L01 · Streaming client (45 min)
- **Message:** “In streaming, tool calls arrive in pieces too. Assembling them correctly is the first serious piece.”
- **Demo:** `curl` with `"stream": true` against Ollama asking for a tool: show raw chunks with `index`, `id`, `arguments` fragments.
- **Stuck:** `ThinkFilter` with split tags (the parametrised test covers it: have them read the failing case); forgetting `flush()`.
- **Questions:** why not retry a 400? What does `data_collection: deny` do on OpenRouter?
- **Extra:** measure local vs OpenRouter time-to-first-token.

### L02 · File tools (60 min)
- **Message:** “The tool description is the prompt. And errors are data: a good error message saves a loop step.”
- **Demo:** show the generated JSON Schema (`/tools` in the demo) and an `edit_file` failing because of line numbers, with the hint message.
- **Stuck:** `edit_file`: count occurrences before replacing; `check_fresh` (mtime) — explain why (a human or a formatter touches the file). `Workspace.resolve`: `is_relative_to` after `resolve()` to cover symlinks.
- **Questions:** why not a diff format? Why number lines in `read_file` but forbid them in `old_string`?

### L03 · Loop (45 min)
- **Message:** “An agent fits in ten lines. Write them on the whiteboard before opening the file.”
- **Demo:** with the solution, a question that triggers parallel reads (*“summarise every file in invoices/”*): several `⏺ Read` lines in a row.
- **Stuck:** breaking the `tool_calls`/`tool` pair on loop detection (the test checks it); keeping result order in parallel.
- **Questions:** why parallelise only reads? What if the model calls the same thing twice?

### L04 · Bash and permissions (45 min)
- **Message:** “The tool executes; permissions decide. And an allow rule must never let a chained second command through.”
- **Demo:** in the solution, `/mode default` → *“run the tests”*, answer *a* (always) and look at the suggested rule; then ask *“delete the invoices folder with rm -rf”* in bypass mode with the deny rules from `examples/project`.
- **Stuck:** `decide` per subcommand; `suggest_rule` for `python -m pytest`.
- **Questions:** why `bypass` only in a sandbox? What can't `/undo` (lab 11) reverse?

### L05 · CLI (60 min) + Milestone (75 min)
- **Message:** “Experience is part of the product: see what it does, how the code changes, and be able to stop it.”
- **Milestone:** everyone's own Forja fixes the 3 failing `playground` tests. First: `python scripts/tasks.py reset`. On the whiteboard: model · success? · steps · time. That table introduces lab 12.
- **Stuck:** Ctrl+C on Windows inside `input()`; `handle_slash` with `/mode` and no argument.
- **Retro (16:30):** what failed more, the model or the harness? (Spoiler: almost always the harness: unclear errors, context, permissions.)

### L06 · Context (40 min)
- **Message:** “The system prompt is rebuilt every turn. If it isn't in context, it doesn't exist for the model.”
- **Demo:** print the solution's `app.system_prompt()` and point at each layer; delete the playground `AGENTS.md` and repeat the rounding question: the agent goes back to `round()`.
- **Stuck:** order of AGENTS.md files (most specific last); `@mentions` that aren't files (emails).

### L07 · Compaction (45 min)
- **Message:** “Microcompaction is free; summarising costs a call and loses information. And never cut between a tool call and its result.”
- **Demo:** `.forja/settings.json` with `"contextWindow": 6000`, work until the compaction note appears, `/context` before and after.
- **Questions:** what must the summary always keep? How would you check compaction doesn't make the agent worse? (→ lab 12).

### L08 · Plan and todos (45 min)
- **Message:** “With small models, a visible task list makes the difference on long tasks. Plan mode is read-only through permissions, not manners.”
- **Demo:** `--mode plan` → *“add discounts to invoices with tests”*: investigation, plan, approval and execution ticking off tasks.

### L09 · Subagents (45 min)
- **Message:** “Delegating buys context: the subagent spends 30k tokens and hands you back 300.”
- **Demo:** `/context` before and after an exploration via subagent versus doing it in the main agent.
- **Stuck:** the subagent can't see the conversation: the `task` prompt must be self-contained (show the tool description).

### L10 · Hooks, skills, MCP (70 min)
- **Message:** “AGENTS.md asks; a hook enforces. It's the same convention commercial agents use (JSON on stdin, exit 2 blocks).”
- **Demo:** copy `examples/project/.forja` into the playground: Stop hook that won't let it finish with red tests, commit skill and the issues MCP (*“fix issue #12 and comment on it”*).
- **Stuck:** exit 1 ≠ block (only exit 2); relative paths in hook commands (they run at the project root).

### L11 · Sessions and undo (35 min)
- **Message:** “Everything the agent does must be auditable and undoable. What can't be undone (bash) goes through permissions.”
- **Demo:** an edit, `/undo`, `/sessions`, `--resume`.

### L12 · Evals (65 min)
- **Message:** “Without measurement it's all opinion. And hidden tests stop the agent from cheating.”
- **Demo:** `python scripts/tasks.py evals --repeat 3` with two models (start it at the beginning of the lab: it takes a while).
- **Close:** bring back the day-1 milestone table and compare with the evals: does intuition match the data?

### Final project (60 min)
Rubric (out of 10): useful AGENTS.md (1) · own skill (2) · hook that guarantees something real (2) · specialised subagent (2) · own eval task with a 2-model report (3). 3-minute demos.

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Connection refused :11434` | Ollama stopped | `ollama serve` or open the app |
| `does not support tools` | model without tools template | `qwen3:8b`, `qwen3-coder:30b`, `devstral` |
| Model doesn't call tools / forgets them | short default context | `OLLAMA_CONTEXT_LENGTH=32768` and restart Ollama |
| Replies > 60 s | CPU or swap | smaller model or shared server |
| `NotImplementedError: TODO NN.x` | pending lab | expected; `catchup` if needed |
| “lab NN pending” notes in the CLI | progressive design | they disappear when the lab is done |
| HTTP 400 mentioning `tool_call_id` | broken history | check 03.2 (closing calls on loop detection) and 07.2 |
| `edit_file` keeps failing | the model copies line numbers or changes indentation | read the hint message; bigger models fail less |
| bash on Windows: `ls` not found | cmd.exe | the agent should use `dir`; or `powershell -Command` |
| PowerShell won't activate the venv | execution policy | `Set-ExecutionPolicy -Scope Process Bypass` |
| MCP won't start | relative command path | commands run from the directory where you launch `forja` |
| Hook doesn't block | returns exit 1 | only exit 2 blocks |

## 7. Tutor material

- `solutions/forja/`: complete reference implementation. `python scripts/tasks.py demo` runs it on the playground.
- `scripts/make_starters.py`: regenerates `forja/` (student) from the solution. If you change the solution: `python scripts/tasks.py starters`.
- `scripts/labs_content.py` + `scripts/build_docs.py`: single source of lab READMEs and workbooks. Edit content there and regenerate.
- Full speaker script (all notes): [speaker_script.md](speaker_script.md)
- Decks: [ES](https://claude.ai/artifact/GkGG788cUiMgA9Xs238Yag) · [EN](https://claude.ai/artifact/CV6PaTZE4j8D58Gtpw2nKt) — speaker notes on every slide with the message and the demo.

## 8. After the workshop
- Survey ([link]).
- 2-week challenge: use their Forja on a real repo with an AGENTS.md, a skill and a hook, and bring the evals report.
