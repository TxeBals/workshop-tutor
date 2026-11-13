"""Step-by-step student guidance (English) for labs 05, 06, 07 and 08.

Schema: see scripts/guides/__init__.py users. All strings are Markdown.
"""
from __future__ import annotations

GUIDE: dict[str, dict] = {
    # ------------------------------------------------------------------ LAB 05
    "05": {
        "before": [
            "Open `forja/cli.py`. Almost everything in it is provided UI plumbing (`RichEvents`, `repl`, `main`, `doctor`). "
            "You only write four small functions: `summarize_call`, `diff_styles`, `ask_approval` and `handle_slash`. "
            "Read `RichEvents.on_tool_start` / `on_tool_end` first: they show exactly where your functions are called.",
            "The UI calls your functions through `_safe(...)`, which only swallows `NotImplementedError`. Any other exception "
            "(e.g. a `KeyError` because the model omitted an argument) would crash the turn, so be defensive with `dict.get`.",
            "Libraries used: `rich` (`console.print`, `Panel`, `Text`), already imported. You do not need to learn rich in depth: "
            "`console.print(Panel(Text(\"...\"), title=\"...\", border_style=\"yellow\"))` is all 05.3 needs.",
            "How it connects to the harness: `Forja.gate` (in `forja/harness.py`) calls `self.approver(tool, args, why)` when "
            "permissions answer `ask`; `build_app` passes your `ask_approval` as that approver. `handle_slash` receives the `Forja` "
            "object, so read the attributes it uses: `app.mode`, `app.set_mode()`, `app.registry.tools`, `app.todos`, "
            "`app.context_tokens()`, `app.compact_now()`, `app.usage`, `app.undo()`, `app.transcript.folder`, `app.history`, "
            "`app.settings.context_window`.",
            "This lab ends with the **day-1 milestone** (see the milestone section): your own agent fixes the 3 failing tests in "
            "`playground/`. Keep 15 minutes for it.",
        ],
        "order": (
            "Do 05.2 first (5 minutes, pure string logic, builds confidence), then 05.1 (string formatting with many cases, "
            "and 05.3 reuses it), then 05.3 (tiny once 05.1 exists), and finish with 05.4, which is the longest and needs a "
            "quick read of `Forja` in `forja/harness.py`. Run each TODO's test as you go; then run the whole lab with "
            "`python scripts/tasks.py test 05` and go to the milestone."
        ),
        "todos": {
            "05.1": {
                "where": "`forja/cli.py` · `summarize_call(name, args, width=100) -> str`",
                "contract": (
                    "Receives the tool name and the (raw, possibly incomplete) argument dict the model sent. Returns ONE line, "
                    "at most `width` characters. Exact formats checked by `test_summarize_call`:\n"
                    "- `read_file` -> `Read a.py`; with `offset` different from 1 -> `Read a.py (from line 50)`\n"
                    "- `write_file` -> `Write n.md (2 lines)` (number of lines of `content`)\n"
                    "- `edit_file` -> `Edit path`\n"
                    "- `bash` -> `$ pytest -q` (the command, whitespace collapsed)\n"
                    "- `grep` -> `Grep 'def x' in src (*.py)` (path defaults to `.`; ` (include)` only if include is set)\n"
                    "- `glob` -> `Glob pattern`\n"
                    "- `task` -> `Task[explore] find VAT` (`subagent_type` defaults to `explore`)\n"
                    "- `todo_write` -> `Todos (N)` (number of items)\n"
                    "- anything else -> `name(k=v, k2=v2)`, e.g. `mcp__x__y(id=3)`\n"
                    "All runs of whitespace (spaces, newlines) become a single space. If the line is longer than `width`, cut it "
                    "so the result is exactly `width` characters long, ending in `…`."
                ),
                "steps": [
                    "Branch on `name` with an `if/elif` chain and build a string `s` for each known tool, reading arguments with `args.get(key, default)`.",
                    "For `read_file`, start with `Read <path>` and append ` (from line N)` only when `args.get(\"offset\", 1) != 1`.",
                    "For `write_file`, count lines with `str(content).splitlines()`; for `grep`, add the ` (<include>)` suffix only when include is truthy.",
                    "For the fallback, join `f\"{k}={v}\"` pairs with `\", \"` inside `name(...)` (optionally trim long values to ~30 chars each).",
                    "Collapse whitespace on the final string: `\" \".join(s.split())`.",
                    "Truncate last: if `len(s) > width`, keep the first `width - 1` characters and add `…`.",
                ],
                "gotchas": [
                    "Collapse whitespace BEFORE truncating, otherwise the length check uses the wrong string (`test_summarize_call` checks `len(...) == 50` with `width=50`).",
                    "The cut must give exactly `width` characters including the `…` (one character), not `width + 1` and not `...` (three dots).",
                    "`args` comes straight from the model's JSON (not validated): keys may be missing. Use `.get()` everywhere; a `KeyError` here crashes the turn.",
                    "`bash` with `\"pytest  -q\\n\"` must become `$ pytest -q`: double spaces and the trailing newline disappear.",
                ],
                "hints": [
                    "Think of it as a lookup of 9 formats plus two post-processing steps (collapse, truncate) applied to whatever you built.",
                    "The default values matter for the expected strings: grep path `'.'`, task type `'explore'`, read offset `1`, todos `[]`.",
                    "Skeleton:\n```python\nif name == \"read_file\":\n    s = f\"Read {args.get('path')}\"\n    # if offset != 1: append \" (from line N)\"\nelif name == \"bash\":\n    s = ...\n# elif ... write_file / edit_file / grep / glob / task / todo_write\nelse:\n    s = f\"{name}(...)\"   # k=v pairs\ns = ...                  # collapse whitespace\nreturn ...               # truncate to width with '…'\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k summarize -v",
            },
            "05.2": {
                "where": "`forja/cli.py` · `diff_styles(diff: str) -> list[tuple[str, str]]`",
                "contract": (
                    "Receives a unified diff as one string (the `diff` that `write_file`/`edit_file` put in `ToolResult.meta`). "
                    "Returns one `(line, style)` tuple per line, in order, with the line text unchanged (no newline). Styles: "
                    "`'+++'` or `'---'` -> `'bold'`; `'@@'` -> `'cyan'`; `'+'` -> `'green'`; `'-'` -> `'red'`; everything else -> `'dim'`. "
                    "`test_diff_styles` expects `[\"bold\", \"bold\", \"cyan\", \"red\", \"green\", \"dim\"]` for a 6-line diff."
                ),
                "steps": [
                    "Split the diff into lines with `str.splitlines()`.",
                    "For each line, test the prefixes from most specific to least specific: headers (`+++`, `---`), then hunk (`@@`), then `+`, then `-`.",
                    "Append `(line, style)` to the output list; default style is `dim`.",
                    "Return the list (an empty diff gives `[]`).",
                ],
                "gotchas": [
                    "Order matters: `'--- a/x'` also starts with `'-'`. If you test `'-'` first, headers come out red and the test fails.",
                    "`str.startswith` accepts a tuple: `line.startswith((\"+++\", \"---\"))`.",
                    "Do not strip lines: a context line starts with a space, and the UI prints it as-is.",
                ],
                "hints": [
                    "It is a loop with an `if/elif` chain over prefixes.",
                    "Check the 3-character prefixes before the 1-character ones.",
                    "Skeleton:\n```python\nout = []\nfor line in diff.splitlines():\n    if line.startswith((\"+++\", \"---\")):\n        style = \"bold\"\n    # elif '@@' ... elif '+' ... elif '-' ...\n    else:\n        style = \"dim\"\n    out.append(...)\nreturn out\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k diff_styles -v",
            },
            "05.3": {
                "where": "`forja/cli.py` · `ask_approval(tool, args, reason, read=input) -> Approval`",
                "contract": (
                    "Called by `Forja.gate` when the permission decision is `ask`. Shows the user what is about to run "
                    "(a `Panel` with `summarize_call(tool.name, args, ...)`) and why it is being asked (`reason`, e.g. "
                    "`requires approval`). Reads ONE answer by calling `read(prompt_text)`. Returns the literal string "
                    "`\"yes\"` for `y`/`yes`, `\"always\"` for `a`/`always`, and `\"no\"` for anything else, including an empty "
                    "answer. `test_ask_approval` passes `read=lambda _: \"y\"`, `\"a\"` and `\"\"`. With `always`, the harness "
                    "(not you) adds a rule via `permissions.suggest_rule`."
                ),
                "steps": [
                    "Build the summary with `summarize_call(tool.name, args, width=...)`; use a large width (e.g. 400) so the user sees the full command before approving it.",
                    "Print it with `console.print(Panel(Text(summary), title=..., border_style=\"yellow\"))`; put `tool.name` and `reason` in the title.",
                    "Call `read(\"  [y]es / [n]o / [a]lways this session > \")` and normalise the answer with `str(...).strip().lower()`.",
                    "Map the answer to `\"yes\"`, `\"always\"` or `\"no\"` and return it.",
                ],
                "gotchas": [
                    "Use the `read` parameter, never `input()` or `console.input()` directly: the tests inject `read`, and under pytest a real `input()` fails because stdin is captured.",
                    "Return exactly `\"yes\"` / `\"no\"` / `\"always\"` (the `Approval` literal), not booleans and not `\"y\"`.",
                    "Default is NO: an empty answer (just Enter), `nope` or anything unknown -> `\"no\"`. Safe by default. Normalise first, so ` Y ` still counts as yes.",
                    "Wrap the summary in `Text(...)`: if you pass a raw string, rich interprets `[brackets]` in commands as markup.",
                ],
                "hints": [
                    "Two parts: print something, then translate one answer into one of three strings.",
                    "Membership tests are enough: `ans in (\"y\", \"yes\")`, `ans in (\"a\", \"always\")`.",
                    "Skeleton:\n```python\nsummary = summarize_call(tool.name, args, width=400)\nconsole.print(Panel(Text(summary), title=f\"Allow {tool.name}? (...)\", border_style=\"yellow\"))\nans = ...  # read(...) normalised\nif ...:\n    return \"yes\"\n# always?\nreturn \"no\"\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k approval -v",
            },
            "05.4": {
                "where": "`forja/cli.py` · `handle_slash(app: Forja, line: str) -> str | None`",
                "contract": (
                    "Receives the raw line typed in the REPL (starts with `/`). Returns the text to print, or `None` for `/exit`. "
                    "It acts on the harness directly, never calls the model. Checked by `test_slash_commands`:\n"
                    "- `/exit` -> `None`; `/help` -> `HELP` (contains `/mode`)\n"
                    "- `/mode` alone -> current mode and the list `MODES`; `/mode plan` -> exactly `mode -> plan` and `app.mode == \"plan\"` "
                    "(use `app.set_mode`, which raises `ValueError` for unknown modes; the REPL catches it and prints `error: ...`)\n"
                    "- `/tools` -> one line per tool with its risk in brackets, e.g. `bash   [exec]`\n"
                    "- `/todos` -> `app.todos.render()` (contains `▶ a` for an in-progress item)\n"
                    "- `/context` -> text containing `tokens` (use `app.context_tokens()`, optionally `app.settings.context_window` and `len(app.history)`)\n"
                    "- `/compact` -> `app.compact_now(force=True)` (or a fallback text if it returns empty)\n"
                    "- `/cost` -> text containing `input` (from `app.usage['prompt_tokens']` and `['completion_tokens']`)\n"
                    "- `/undo` -> `app.undo()` returns a list of `Path`; show them relative (`app.ws.rel(p)`) or say nothing to undo\n"
                    "- `/sessions` -> `Transcript.list_sessions(app.transcript.folder)` gives `[(id, first_message)]`\n"
                    "- `/clear` -> empties `app.history` (and the todo list) and returns exactly `new conversation`\n"
                    "- anything else -> a message containing `unknown`"
                ),
                "steps": [
                    "Split the line into command and argument: `line.strip().split(maxsplit=1)`; the argument is the rest (or `\"\"`).",
                    "Handle `/exit` and `/help` first (trivial returns).",
                    "`/mode`: without argument describe the current mode; with argument call `app.set_mode(arg)` and return `f\"mode -> {app.mode}\"`.",
                    "Read-only commands: `/tools` (iterate `app.registry.tools.values()`, each `Tool` has `.name` and `.risk`), `/todos`, `/context`, `/cost`, `/sessions`; build a string for each.",
                    "Commands with effects: `/compact`, `/undo`, `/clear` (assign `app.history = []` and `app.todos.items = []`).",
                    "End with the fallback for unknown commands, suggesting `/help`.",
                ],
                "gotchas": [
                    "`/mode plan` must return exactly `mode -> plan` (ASCII `->`, one space each side).",
                    "`/clear` must return exactly `new conversation` and leave `app.history == []` (assign a new list).",
                    "Do not catch the `ValueError` of `set_mode` yourself and return `None`: `None` means exit and would close the REPL. Let it propagate or return an error text.",
                    "`app.compact_now(force=True)` may return `\"\"` (nothing to compact); return a readable fallback instead of an empty line.",
                    "`/undo` and `/compact` depend on labs 11 and 07: until then the harness falls back quietly (empty list / nothing compacted). That is fine.",
                ],
                "hints": [
                    "A flat sequence of `if cmd == \"/...\": return ...` reads better than a dict of lambdas here.",
                    "Everything you need is already on `app`: `app.registry.tools`, `app.todos.render()`, `app.context_tokens()`, `app.usage`, `app.transcript.folder`.",
                    "Skeleton:\n```python\ncmd, *rest = line.strip().split(maxsplit=1)\narg = rest[0].strip() if rest else \"\"\nif cmd == \"/exit\":\n    return None\nif cmd == \"/mode\":\n    if not arg:\n        return ...            # current mode + MODES\n    app.set_mode(arg)\n    return f\"mode -> {app.mode}\"\n# /help /tools /todos /context /compact /cost /undo /sessions /clear\nreturn f\"unknown command: {cmd} (/help)\"\n```",
                ],
                "test": "python -m pytest tests/test_l05_cli.py -k slash -v",
            },
        },
        "try_it": [
            "Check the model first: `forja doctor`. Expected: `backend=ollama url=... model=...`, `answered in N.Ns`, then `✔ the model calls tools (ping)`.",
            "Start the REPL on the playground: `forja --cwd playground --mode accept_edits`. You see a cyan panel `Forja <version> · <model> · mode accept_edits` and the prompt `accept_edits ›`.",
            "Type `/tools`: one line per tool, e.g. `read_file   [read]`, `edit_file   [edit]`, `bash   [exec]`. Then `/mode`: `current mode: accept_edits (available: default, accept_edits, plan, bypass)`.",
            "Ask: `fix the amount rounding bug and check with the tests`. You should see one blue line per action (`⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`), a framed green/red diff after every edit, and a yellow `Allow bash? (requires approval)` panel before each command. Answer `a` once: a dim note `rule added for this session: allow bash(python -m pytest*)` appears and later pytest runs no longer ask.",
            "After the turn: `(N steps · M tools)` in grey. Type `/cost` (`input ... · output ... tokens`) and `/context` (`~N tokens of 32768 (M messages)`).",
            "Press Ctrl+C during a long answer: `interrupting…` and the agent stops at the next step boundary. Then `/exit`.",
        ],
        "troubleshooting": [
            ["`test_ask_approval` hangs or fails with `OSError: pytest: reading from stdin while output is captured`",
             "You called `input()`/`console.input()` instead of the `read` parameter → call `read(prompt)`."],
            ["`test_summarize_call` fails on the length assertion (51 != 50) or on `$ pytest  -q`",
             "Truncation adds `…` without removing a character, or you truncate before collapsing whitespace → collapse first, then `s[:width - 1] + \"…\"`."],
            ["`test_diff_styles` gives `['red', 'green', ...]` for the headers",
             "You test `-`/`+` before `---`/`+++` → check the 3-character prefixes first."],
            ["The REPL closes when you type `/mode foo`",
             "`handle_slash` returned `None` for an error → only `/exit` returns `None`; let `set_mode`'s `ValueError` propagate (the REPL prints `error: unknown mode: foo`)."],
            ["`KeyError` / crash on `⏺` lines when the model sends odd arguments",
             "`summarize_call` uses `args['x']` → use `args.get('x', default)`; arguments come unvalidated from the model."],
            ["`forja` is not recognised (Windows) / `command not found` (macOS/Linux)",
             "The venv is not active or setup was not run → PowerShell `.venv\\Scripts\\Activate.ps1` (if blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`), macOS/Linux `source .venv/bin/activate`, then `python scripts/tasks.py setup`. `python -m forja ...` also works."],
            ["Windows: the agent runs `ls`, `cat` or `python3` and gets errors",
             "The bash tool uses `cmd.exe` on Windows → normal; the model should adapt after the error. Tell it: `use python -m pytest -q; this is Windows cmd`."],
            ["Colours or `⏺` show as garbage in old Windows consoles",
             "Use Windows Terminal (or VS Code's terminal) instead of the legacy `cmd.exe` window; `chcp 65001` helps for UTF-8."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 05` → 4 passed.",
            "[ ] In the REPL you see one-line summaries, coloured diffs and the y/n/a approval panel; `/tools`, `/mode`, `/cost`, `/context` work.",
            "[ ] Day-1 milestone: your agent made the 3 failing playground tests pass, and you recorded model, success, steps and time.",
        ],
        "milestone": [
            "**Goal (15:15):** with YOUR Forja and YOUR local model, the 3 failing tests in `playground/` pass. Then compare results with a pair using a different model.",
            "**1. Reset the playground.** From the repo root: `python scripts/tasks.py reset` (same command on Windows and macOS/Linux). "
            "Check the starting point: `cd playground` then `python -m pytest -q`, then `cd ..`. Expected summary: `3 failed, 4 passed` "
            "(`test_round_half_up`, `test_total_with_vat_cent`, `test_due_date_sunday_moves_to_monday`).",
            "**2. Check the model.** `forja doctor` must end with `✔ the model calls tools`. If it prints `! the model answered without calling the tool`, switch model "
            "(`FORJA_MODEL` in `.env`) or use the classroom server before you go on.",
            "**3. Start the agent.** `forja --cwd playground --mode accept_edits` (edits are auto-approved, commands ask). Start a stopwatch when you press Enter on the prompt.",
            "**4. Prompt to use** (paste it as one line). Lab 06 is not done yet, so the agent does NOT see `playground/AGENTS.md`: the prompt carries the project rules itself:\n"
            "> Run the tests with `python -m pytest -q`, find why 3 tests fail and fix the code in `invoices/` (never change the tests). "
            "Amounts have 2 decimals with half-up rounding using `decimal`, never `round()` on floats. Due dates falling on Saturday or Sunday move to the next Monday. "
            "When you finish, run the tests again and show me the result.",
            "**5. Approvals.** When the yellow `Allow bash?` panel shows `$ python -m pytest -q`, answer `a` (always): only pytest gets a session rule. "
            "Answer `n` to anything you would not run on your own machine (installing packages, deleting files).",
            "**6. What a GOOD run looks like:** `⏺ $ python -m pytest -q` (3 failures) → `⏺ Read invoices/amounts.py` / `⏺ Read invoices/dates.py` → "
            "`⏺ Edit invoices/amounts.py` with a diff that rounds through `Decimal(str(value))` + `ROUND_HALF_UP` → `⏺ Edit invoices/dates.py` with a diff that also handles Sunday "
            "→ `⏺ $ python -m pytest -q` showing `7 passed` → a short summary citing the files. Typically 6–15 steps, one turn, no edits under `tests/`.",
            "**7. What a BAD run looks like** (record it, it is data, not failure): the model edits `tests/` to make them pass; uses `Decimal(value)` on the float "
            "(2.675 stays 2.67) or adds `+ 0.0001` hacks; claims `all tests pass` without running pytest again; repeats the same failing `edit_file` until the loop detector stops it; "
            "rewrites a whole file with `write_file` and drops functions; answers with a code block instead of calling tools; reaches `max_steps`. "
            "Give at most two corrective follow-up prompts (e.g. `the tests still fail, run them and read the error`) and count them.",
            "**8. Verify outside the agent.** `/exit`, then `cd playground` and `python -m pytest -q` → `7 passed`. Check that only `invoices/` changed: `git status playground` "
            "(or `git diff --stat playground`). If a test file changed, the run does not count as a success.",
            "**9. Record your result** (in your workbook or the shared sheet): **model** (exact tag, e.g. `qwen3:8b`, plus backend: local Ollama / classroom server / OpenRouter), "
            "**success** (yes/no and tests passing out of 7; note if you needed follow-up prompts), **steps** (the grey `(N steps · M tools)` line; add them up if there were several turns), "
            "**time** (stopwatch from Enter to the final answer; optionally `/cost` tokens). Then compare with a neighbour who used another model: who needed fewer steps, who broke a rule?",
            "**10. Optional: a reproducible headless run.** `python scripts/tasks.py reset`, then time it: PowerShell `Measure-Command { forja --cwd playground --mode bypass -p \"<same prompt>\" }`, "
            "macOS/Linux `time forja --cwd playground --mode bypass -p \"<same prompt>\"`. Headless has no user: in `accept_edits` every command would be DENIED, hence `bypass` "
            "(deny rules still apply). Exit code 0 means the agent finished with a final answer, not that tests pass: run pytest yourself.",
        ],
    },
    # ------------------------------------------------------------------ LAB 06
    "06": {
        "before": [
            "Open `forja/context.py`. Read the provided parts first: `BASE_PROMPT`, `MODE_REMINDERS` (a dict mode -> text), "
            "`INSTRUCTION_FILES = (\"AGENTS.md\", \"FORJA.md\")`, `MENTION_RE` and `git_info(root)`. You write three functions.",
            "Look at `Forja.system_prompt()` and `Forja.turn()` in `forja/harness.py`: the harness calls `build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos])` "
            "EVERY step, and `expand_mentions(text, self.ws)` on every user message. Until this lab is done it uses the one-line `FALLBACK_PROMPT`, so your agent has never seen `AGENTS.md`.",
            "Stdlib you need: `pathlib.Path` (`/`, `.is_file()`, `.resolve()`, `.parent`, `.read_text(encoding=\"utf-8\")`, `.is_relative_to()`), "
            "`re.Pattern.findall`, `dict.fromkeys(...)` (order-preserving de-duplication), `platform.system()`, `datetime.date.today().isoformat()`.",
            "From lab 02 you reuse the `Workspace` (`forja/fs_tools.py`): `ws.root`, `ws.resolve(path)` (raises `PermissionError` outside the sandbox), "
            "`ws.rel(p)` and `ws.mark_read(p)` (records the file in `ws.read_state` so a later `edit_file` does not complain that it was not read).",
        ],
        "order": (
            "06.1 first: 06.2 calls it to get the instruction files. Then 06.2, the layered prompt, which is what turns AGENTS.md on in your CLI. "
            "06.3 is independent; leave it for last. After 06.2 passes, lab 08's `test_plan_mode_flow` also depends on it (it checks `PLAN mode` and the task list in the system prompt)."
        ),
        "todos": {
            "06.1": {
                "where": "`forja/context.py` · `find_instruction_files(cwd, home=None, stop=None) -> list[Path]`",
                "contract": (
                    "Returns the instruction files that apply to `cwd`, in the order they must appear in the prompt: first the user's global "
                    "`home/.forja/AGENTS.md` (only if `home` is given and the file exists), then every `AGENTS.md`/`FORJA.md` found walking UP from `cwd`, "
                    "returned from the HIGHEST folder down to `cwd` (most specific last). The walk stops after checking `stop` (inclusive) or at the filesystem root. "
                    "`test_find_instruction_files_order` builds `home/.forja/AGENTS.md`, `repo/AGENTS.md`, `repo/pkg/AGENTS.md` and expects the contents `[\"global\", \"root\", \"package\"]` "
                    "when called with `cwd=repo/pkg, stop=tmp_path`."
                ),
                "steps": [
                    "Start a `found` list with the global file if `home` is set and `home / \".forja\" / \"AGENTS.md\"` is a file.",
                    "Set `d = cwd.resolve()` and loop: for each name in `INSTRUCTION_FILES`, if `d / name` is a file, add it to a `chain` list.",
                    "Stop the loop when `d` equals the resolved `stop`, or when `d.parent == d` (you are at the root); otherwise move to `d.parent`.",
                    "`chain` is now lowest-first; reverse it so the highest folder comes first.",
                    "Return `found + reversed chain`.",
                ],
                "gotchas": [
                    "Resolve BOTH `cwd` and `stop` before comparing. On macOS `tmp_path` lives under `/var`, which is a symlink to `/private/var`: comparing a resolved and an unresolved path never matches, and you walk to `/`.",
                    "Root detection: `d.parent == d` works on Windows too (`C:\\` is its own parent). Do not compare with `Path(\"/\")`.",
                    "Check `stop` AFTER collecting files in that folder: `stop` is inclusive.",
                    "The global file goes first, before the reversed chain, not mixed into it.",
                ],
                "hints": [
                    "It is a `while True` walk from `cwd` up to the root, collecting files, then a reverse.",
                    "Collect bottom-up (natural for a walk upwards) and reverse once at the end, instead of inserting at index 0.",
                    "Skeleton:\n```python\nfound = []\nif home and (home / \".forja\" / \"AGENTS.md\").is_file():\n    found.append(...)\nchain, d = [], cwd.resolve()\nwhile True:\n    # collect INSTRUCTION_FILES present in d\n    if ... or d.parent == d:   # reached stop (resolved) or root\n        break\n    d = d.parent\nreturn found + ...\n```",
                ],
                "test": "python -m pytest tests/test_l06_context.py -k find_instruction -v",
            },
            "06.2": {
                "where": "`forja/context.py` · `build_system_prompt(ws, mode, model, home=None, skills_catalog=\"\", extra=None) -> str`",
                "contract": (
                    "Returns the full system prompt: non-empty layers joined with a blank line (`\"\\n\\n\"`), in this order: `BASE_PROMPT`; "
                    "`MODE_REMINDERS[mode]`; one block per file from `find_instruction_files(ws.root, home=home)`, each with a `## ... instructions` heading followed by the file content; "
                    "`skills_catalog` if non-empty; each non-empty string in `extra` (the harness passes the task list here); and finally a `## Environment` block with the working directory "
                    "(`ws.root`), `git_info(ws.root)`, OS (`platform.system()`), date (`date.today().isoformat()`) and `model`. "
                    "`test_system_prompt_layers` checks that `You are Forja`, `PLAN mode`, `half-up` (from `playground/AGENTS.md`), `## Skills`, `## Extra`, the model name and `str(project)` are present, "
                    "and that `PLAN mode` comes before `half-up`, which comes before `## Environment`."
                ),
                "steps": [
                    "Start a `layers` list with `BASE_PROMPT` and the reminder for `mode` (`MODE_REMINDERS.get(mode, \"\")` is safe).",
                    "For each file from `find_instruction_files(ws.root, home=home)`, add `\"## <label>\\n<content>\"`. A useful label: `User global instructions` for the file under `home/.forja`, `Project instructions (<relative path>)` for the others.",
                    "Append `skills_catalog` if not empty, then each non-empty element of `extra or []`.",
                    "Append the `## Environment` block (directory, `git_info(ws.root)`, OS, date, model) as one multi-line string.",
                    "Return `\"\\n\\n\".join(...)` over the non-empty layers.",
                ],
                "gotchas": [
                    "Read files with `read_text(encoding=\"utf-8\")`. On Windows the default encoding is cp1252 and AGENTS.md files with accents or `—` raise `UnicodeDecodeError` or come out garbled.",
                    "`extra` may be `None` and may contain `\"\"` (the test passes `[\"## Extra\", \"\"]`, the harness passes `[\"\"]` when there are no todos): filter empty strings so you do not get stray blank sections.",
                    "Call `find_instruction_files` with `ws.root`, not `Path.cwd()`: with `forja --cwd playground` the process cwd is the repo root.",
                    "`f.relative_to(ws.root)` raises `ValueError` for files above the workspace or in home: guard with `f.is_relative_to(ws.root)`.",
                    "The test needs `str(project)` in the prompt: print `ws.root` itself (absolute), not `.`.",
                ],
                "hints": [
                    "Build a list of strings in order and join it once; do not concatenate with `+=` and forget separators.",
                    "The harness already gives you everything: `ws.root`, `mode`, `model`, `skills_catalog`, `extra`. You only add the files and the environment.",
                    "Skeleton:\n```python\nlayers = [BASE_PROMPT, MODE_REMINDERS.get(mode, \"\")]\nfor f in find_instruction_files(ws.root, home=home):\n    label = ...   # global vs project (relative path)\n    layers.append(f\"## {label}\\n{...}\")\n# skills_catalog, extra (non-empty only)\nlayers.append(f\"## Environment\\nWorking directory: {ws.root}\\n{git_info(ws.root)}\\n...\")\nreturn \"\\n\\n\".join(x for x in layers if x)\n```",
                ],
                "test": "python -m pytest tests/test_l06_context.py -k system_prompt -v",
            },
            "06.3": {
                "where": "`forja/context.py` · `expand_mentions(text, ws, max_chars=20_000) -> str`",
                "contract": (
                    "Finds `@path` mentions with `MENTION_RE` (it already ignores e-mail addresses like `joe@mail.com`). For each UNIQUE mention that resolves inside the "
                    "workspace to an existing FILE: read it (at most `max_chars` characters), call `ws.mark_read(p)`, and append a block "
                    "`<file path=\"<relative path>\">\\n<content>\\n</file>` at the END of the original text (the text itself is not modified). "
                    "Mentions outside the sandbox (`@../../etc/passwd` -> `PermissionError`), missing files (`@nobody`) and folders are skipped silently. "
                    "With no valid mention, return `text` unchanged (`expand_mentions(\"no mentions\", ws) == \"no mentions\"`). "
                    "`test_expand_mentions` expects exactly one `<file` block with `path=\"invoices/dates.py\"`, the file content (`def due_date`) and the path in `ws.read_state`."
                ),
                "steps": [
                    "Get the mentions with `MENTION_RE.findall(text)` and de-duplicate keeping order (`dict.fromkeys(...)`).",
                    "Strip trailing punctuation from each mention: the regex stops at `,` but it allows `.`, so `look at @src/app.py.` captures `src/app.py.`. Use `ref.rstrip(\".,;:\")`.",
                    "Resolve with `ws.resolve(ref)` inside `try/except PermissionError: continue`; skip if `not p.is_file()`.",
                    "Read with `read_text(encoding=\"utf-8\", errors=\"replace\")`, cut to `max_chars` (add a `…[truncated]` marker), `ws.mark_read(p)`, and build the `<file path=...>` block.",
                    "If you have blocks, return `text + \"\\n\\n\" + \"\\n\\n\".join(blocks)`; otherwise return `text`.",
                ],
                "gotchas": [
                    "A mention at the end of a sentence (`look at @src/app.py.`) captures the final dot: strip trailing `.,;:` or the file is not found.",
                    "Use `ws.rel(p)` for the `path` attribute: it already returns a POSIX path (`invoices/dates.py`) on Windows too, which is what the test looks for.",
                    "Call `ws.mark_read(p)` for every included file: the test checks `ws.read_state`, and in the CLI it lets the model `edit_file` right away without a `read_file` round-trip.",
                    "Do not replace the mention inside the text: keep the user's sentence intact and append blocks after it.",
                    "Do not let one bad mention abort the others: `continue`, never `return` inside the loop.",
                ],
                "hints": [
                    "Loop over mentions, filter the valid ones, build a list of blocks, append them at the end.",
                    "The sandbox is already done (lab 02): `ws.resolve` raising `PermissionError` is your filter for `../` paths.",
                    "Skeleton:\n```python\nblocks = []\nfor ref in dict.fromkeys(MENTION_RE.findall(text)):\n    try:\n        p = ws.resolve(ref.rstrip(\".,;:\"))\n    except PermissionError:\n        continue\n    # skip non-files; read (cap max_chars); ws.mark_read(p)\n    blocks.append(f'<file path=\"{...}\">\\n{...}\\n</file>')\nreturn ...  # text unchanged if no blocks\n```",
                ],
                "test": "python -m pytest tests/test_l06_context.py -k mentions -v",
            },
        },
        "try_it": [
            "Reset first: `python scripts/tasks.py reset`. Start `forja --cwd playground`. The dim note `context: lab 06 pending ...` should NO LONGER appear.",
            "Ask: `review @invoices/amounts.py and tell me whether it follows AGENTS.md`. Expected: NO `⏺ Read invoices/amounts.py` line (the file came with the message) and an answer that quotes the rules: half-up rounding with `decimal`, not `round()` on floats, don't change tests.",
            "Ask without mentioning the rules: `what are the rules of this project?`. The agent answers from `AGENTS.md` without calling any tool.",
            "Type `/context` before and after a message with a big `@` mention: the token count grows by roughly the file size / 4.",
            "Optional: create `~/.forja/AGENTS.md` (Windows: `%USERPROFILE%\\.forja\\AGENTS.md`) with `Always answer in Spanish.`; restart Forja and say hello. The answer language changes: the global layer works.",
        ],
        "troubleshooting": [
            ["`test_find_instruction_files_order` returns `['global', 'package', 'root']`",
             "You did not reverse the walk (or reversed the global file too) → collect bottom-up, reverse only the chain, then prepend the global file."],
            ["`test_find_instruction_files_order` finds extra files or never stops (macOS)",
             "Comparing resolved `cwd` with unresolved `stop` (`/var` vs `/private/var`) → resolve `stop` too."],
            ["`test_system_prompt_layers` fails on `half-up` in sp",
             "The playground AGENTS.md was not included → call `find_instruction_files(ws.root, home=home)` and append the file CONTENT, not just its path."],
            ["`UnicodeDecodeError: 'charmap' codec can't decode` (Windows)",
             "`read_text()` without encoding → `read_text(encoding=\"utf-8\")` (and `errors=\"replace\"` for mentioned files)."],
            ["`test_expand_mentions`: `out.count(\"<file\") == 2` or a crash on `@../../etc/passwd`",
             "Missing `except PermissionError` or missing `is_file()` check → skip invalid mentions with `continue`."],
            ["In the CLI the agent still ignores AGENTS.md",
             "You ran Forja from another folder, or the AGENTS.md is not under `--cwd` → start with `forja --cwd playground`; small models may also need the rule repeated in the prompt (less is more: keep AGENTS.md short)."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 06` → 3 passed.",
            "[ ] In the CLI the agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.",
            "[ ] An `@file` mention is answered without an extra `⏺ Read` line.",
        ],
    },
    # ------------------------------------------------------------------ LAB 07
    "07": {
        "before": [
            "Open `forja/compaction.py`. Provided: `SUMMARY_PROMPT`, `CLEARED = \"[old tool result cleared]\"`, `estimate_tokens(messages)` (~4 chars per token), "
            "`user_turn_starts(history)` (indices of the `user` messages) and `should_compact(...)` (true above 80% of the window). You write `microcompact` and `compact`.",
            "Know the history format (OpenAI chat): `{\"role\": \"user\", \"content\": ...}`, `{\"role\": \"assistant\", \"content\": ..., \"tool_calls\": [{\"id\", \"type\", \"function\": {\"name\", \"arguments\"}}]}`, "
            "`{\"role\": \"tool\", \"tool_call_id\": ..., \"name\": ..., \"content\": ...}`. An assistant message with `tool_calls` MUST be followed by one `tool` message per call: breaking that pair makes the API reject the request.",
            "A \"turn\" starts at a `user` message. Cutting only at `user_turn_starts(...)` indices is what guarantees you never separate a `tool_calls` message from its results.",
            "How it connects: `Forja.compact_now()` in `forja/harness.py` runs before every turn: if `should_compact` → `microcompact(self.history)` (free); if still too big → `compact(self.history, self.llm)` (one LLM call). "
            "`/compact` calls `compact_now(force=True)`. The LLM call is `llm.chat(messages, temperature=0)` and returns a `ChatResponse` whose `.content` is the text (in tests, `FakeLLM` records it in `llm.calls`).",
        ],
        "order": (
            "07.1 first: it is a pure in-place loop, no LLM, and it teaches you the cut point (`starts[-keep_recent_turns]`) that 07.2 reuses. "
            "Then 07.2. `test_harness_autocompacts` (run with 07.2) exercises both through the harness with a tiny window, so it only passes when both are right."
        ),
        "todos": {
            "07.1": {
                "where": "`forja/compaction.py` · `microcompact(history, keep_recent_turns=2, min_chars=500) -> int`",
                "contract": (
                    "Mutates `history` IN PLACE: every `tool` message located BEFORE the start of the last `keep_recent_turns` turns, whose content has at least "
                    "`min_chars` characters and is not already `CLEARED`, gets `content = CLEARED`. Returns how many messages were cleared. If there are "
                    "`keep_recent_turns` turns or fewer, does nothing and returns 0. Messages are never removed or reordered, so pairs stay valid. "
                    "`test_microcompact` (4 turns, tool outputs of 2000 chars) expects 2 cleared (turns 0 and 1), the last two untouched, tokens below 60% of before, "
                    "and a second call returning 0."
                ),
                "steps": [
                    "Compute `starts = user_turn_starts(history)`; if `len(starts) <= keep_recent_turns`, return 0.",
                    "The protected zone starts at `limit = starts[-keep_recent_turns]`.",
                    "Loop over `history[:limit]` (the slice is a new list but holds the SAME dict objects, so mutating them changes `history`).",
                    "For each message with role `tool`, content length `>= min_chars` and content `!= CLEARED`: set it to `CLEARED` and count it.",
                    "Return the count.",
                ],
                "gotchas": [
                    "Mutate the dicts; do not build a new list and return it. The function returns an `int` and the harness relies on `self.history` being changed in place.",
                    "Only `tool` messages: never blank user or assistant content (that is the conversation itself).",
                    "`content` may be `None`: use `len(m.get(\"content\") or \"\")`.",
                    "`>= min_chars`, not `>`: an output of exactly 500 characters counts.",
                ],
                "hints": [
                    "Find the index where the recent part begins; everything before it is fair game.",
                    "`starts[-keep_recent_turns]` is the index of the first user message you want to keep intact.",
                    "Skeleton:\n```python\nstarts = user_turn_starts(history)\nif len(starts) <= keep_recent_turns:\n    return 0\nlimit = ...\nn = 0\nfor m in history[:limit]:\n    if m[\"role\"] == \"tool\" and ...:   # long enough, not yet CLEARED\n        ...\nreturn n\n```",
                ],
                "test": "python -m pytest tests/test_l07_compaction.py -k microcompact -v",
            },
            "07.2": {
                "where": "`forja/compaction.py` · `compact(history, llm, keep_recent_turns=2) -> tuple[list, bool]`",
                "contract": (
                    "If there are `keep_recent_turns` turns or fewer, return `(history, False)` without calling the LLM. Otherwise cut at `starts[-keep_recent_turns]`: "
                    "`old = history[:cut]`, `recent = history[cut:]`. Turn `old` into plain text (one line per message: role and content; for assistants also the tools called "
                    "with truncated arguments; for tool messages a truncated result), and call `llm.chat([{system: SUMMARY_PROMPT}, {user: that text}], temperature=0)`. "
                    "Return `([{\"role\": \"user\", \"content\": \"[Summary of the previous session]\\n\" + summary}, {\"role\": \"assistant\", \"content\": <short ack>}, *recent], True)`. "
                    "`test_compact_keeps_pairs_and_recent` checks: the first message starts with `[Summary` and contains the fake summary; `new[2:] == h[8:]` (the last 2 turns untouched); "
                    "pairs are valid; the text sent as `messages[1]` contains `question 0` but NOT `question 3` (recent turns are not summarised); `compact(history(1), llm)[1] is False`."
                ),
                "steps": [
                    "Compute `starts`; return `(history, False)` early when there is not enough to compact.",
                    "Split into `old` and `recent` at `cut = starts[-keep_recent_turns]`.",
                    "Build a list of text lines from `old`: for `tool` messages something like `[result of <name>] <first 1500 chars>`; for others `<role>: <content>` plus `[tools: name(args…)]` taken from `m.get(\"tool_calls\", [])` → `t[\"function\"][\"name\"]` / `[\"arguments\"]`.",
                    "Join the lines and cap the total (keep the END, e.g. the last 60,000 characters: the most recent old work matters most).",
                    "Call `llm.chat([...system SUMMARY_PROMPT..., ...user transcript...], temperature=0)` and take `.content or \"\"`.",
                    "Return the new history: summary as a `user` message, an `assistant` acknowledgement (e.g. `Understood. I'll continue from here.`), then `*recent`; and `True`.",
                ],
                "gotchas": [
                    "The new history must start with `user` then `assistant`: two consecutive `user` messages (summary + next turn) or an orphan `tool` message break some chat templates. The ack fixes the alternation.",
                    "Never summarise the recent turns: the test checks that `question 3` is not in the prompt sent to the model.",
                    "Keep `recent` as-is (`new[2:] == h[8:]`): do not copy, clean or re-truncate those messages.",
                    "`content` can be `None` (assistant messages with only tool calls): use `m.get(\"content\") or \"\"` when formatting.",
                    "The summary prompt goes as `messages[0]` with role `system` and the transcript as `messages[1]` with role `user`: the test reads `llm.calls[0][\"messages\"][1][\"content\"]`.",
                ],
                "hints": [
                    "Same cut point as 07.1, but instead of blanking you replace the whole old part with one summary.",
                    "The LLM never sees the raw message dicts: you flatten them to text first, which is also where you truncate big tool results.",
                    "Skeleton:\n```python\nstarts = user_turn_starts(history)\nif len(starts) <= keep_recent_turns:\n    return history, False\ncut = starts[-keep_recent_turns]\nold, recent = history[:cut], history[cut:]\nlines = []\nfor m in old:\n    ...  # tool -> truncated result; others -> role: content [tools: ...]\nsummary = llm.chat([...], temperature=0).content or \"\"\nreturn [ ...summary user msg..., ...assistant ack..., *recent ], True\n```",
                ],
                "test": "python -m pytest tests/test_l07_compaction.py -k \"keeps_pairs or autocompacts\" -v",
            },
        },
        "try_it": [
            "`python scripts/tasks.py reset`, then `forja --cwd playground`. Ask: `read every file in the project and summarise them` (approve with `y` if asked; reads should not ask).",
            "Type `/context`: something like `~6000 tokens of 32768 (N messages)`. Ask two more short questions (e.g. `which function computes VAT?`, `where is the due date logic?`) so you have at least 3 turns: compaction always keeps the last 2.",
            "Type `/compact`. Expected: `compacted: summary + recent turns (~N tokens)`. If you only had 1–2 turns you get `nothing to compact` (or `microcompaction: N old outputs cleared`): that is correct behaviour.",
            "Type `/context` again: the number drops clearly. Ask `what were we doing?`: the agent still knows the files and the goal (it reads them from the summary).",
            "Optional: create `playground/.forja/settings.json` with `{\"contextWindow\": 6000}`, restart and work for a few turns: a dim note `· microcompaction: ...` or `· compacted: ...` appears automatically before a turn. Delete the file afterwards.",
        ],
        "troubleshooting": [
            ["`test_microcompact`: `assert 4 == 2` (everything cleared)",
             "You loop over the whole history → only `history[:starts[-keep_recent_turns]]`."],
            ["`test_microcompact`: second call returns 2 instead of 0, or the count is right but contents unchanged",
             "Not checking `!= CLEARED`, or modifying a copy (`dict(m)`) → mutate the original dicts and skip already-cleared ones."],
            ["`test_compact_keeps_pairs_and_recent`: `question 3` found in the prompt",
             "You summarise the whole history → only `old = history[:cut]`."],
            ["`test_compact_keeps_pairs_and_recent`: `KeyError: 'tool_calls'` or `TypeError: can only concatenate str (not \"NoneType\")`",
             "Use `m.get(\"tool_calls\", [])` and `m.get(\"content\") or \"\"`."],
            ["`test_harness_autocompacts`: `assert any(\"compact\" in n for n in app.notes)` fails",
             "`compact` returns `(history, False)` too often, or 07.1 raises → check both functions with the 07.1 test first; the harness only adds the note when something was compacted."],
            ["Real model: after `/compact` the agent forgets which files it changed",
             "Compaction is lossy → make sure your transcript text includes tool names and arguments (paths!), not just contents; measure it later with evals (lab 12)."],
            ["Real model: `/compact` takes a long time",
             "It is one full LLM call over up to 60k characters → normal on a laptop; a smaller cap on the transcript makes it faster."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 07` → 3 passed.",
            "[ ] `/context` drops after `/compact` and the agent still knows what it was doing.",
        ],
    },
    # ------------------------------------------------------------------ LAB 08
    "08": {
        "before": [
            "Open `forja/planning.py`. Provided: `TodoItem` (pydantic model with `content: str` and `status: \"pending\" | \"in_progress\" | \"completed\"`, default `pending`), "
            "`ICON` and `TodoStore` with `.items` and `.render()` (one line `☐/▶/☑ content` per item, or `(empty list)`). You write the BODIES of two tools, inside factory functions.",
            "Both tools are created with `@tool(risk=\"read\")` from lab 02: the docstring and type hints become the JSON schema the model reads, so do not change them. "
            "Raising an exception inside a tool is the right way to reject bad input: `ToolRegistry.execute` turns it into `ERROR in '<tool>': ValueError: <message>` and the model can correct itself.",
            "Arguments reach your function AFTER pydantic validation and `model_dump()`, so `todos` normally arrives as a list of plain dicts; but code may also call the function with `TodoItem` objects. Accept both (`TodoItem.model_validate(d)`).",
            "How it connects: `Forja._build_registry` registers `make_todo_tool(self.todos)` and `make_exit_plan_tool(self._approve_plan, lambda: self.set_mode(\"default\"))`. "
            "The task list goes back into the system prompt every step via `extra` in `build_system_prompt` (lab 06). Plan mode is read-only because `permissions.decide` (lab 04) denies non-read tools in `plan`, not because the model behaves.",
        ],
        "order": (
            "08.1 first (validation logic, fully unit-tested by `test_todo_write_validation`), then 08.2 (short). `test_plan_mode_flow`, selected with 08.2, "
            "drives a whole plan-mode turn through the harness and needs 08.1, 08.2, lab 04 (plan-mode deny) and lab 06 (the prompt layers) all working."
        ),
        "todos": {
            "08.1": {
                "where": "`forja/planning.py` · `make_todo_tool(store)` → inner `todo_write(todos: list[TodoItem]) -> str`",
                "contract": (
                    "Replaces the WHOLE list in `store.items` with the given items, after validating: each item converted to `TodoItem`; more than one `in_progress` → `ValueError` "
                    "(its message must contain `one task`, e.g. `only one task can be in_progress at a time`); an item with empty/blank `content` → `ValueError`. "
                    "Validation happens BEFORE touching the store: on error the previous list stays. Returns `\"List updated (X/N completed):\\n\" + store.render()` "
                    "(X = completed, N = total). `test_todo_write_validation` expects `1/3` in the output, render lines `[\"☑ read\", \"▶ edit\", \"☐ tests\"]`, "
                    "and after the double-`in_progress` call: `ok` false, `one task` in the output and still 3 items in the store."
                ),
                "steps": [
                    "Convert: `items = [t if isinstance(t, TodoItem) else TodoItem.model_validate(t) for t in todos]`.",
                    "Count items with `status == \"in_progress\"`; if more than 1, raise `ValueError` with a message the model can act on.",
                    "If any item has `not t.content.strip()`, raise `ValueError`.",
                    "Only now assign `store.items = items`.",
                    "Count completed items and return the header line plus `store.render()`.",
                ],
                "gotchas": [
                    "Assign `store.items` only after all checks pass: the test checks that a rejected call leaves the old 3 items.",
                    "The error text must contain `one task` (the test does `\"one task\" in two.output`).",
                    "`content` of only spaces is also empty: use `.strip()`.",
                    "Raise, do not return an error string: a returned string counts as success (`ok=True`) and the test expects `not two.ok`.",
                    "Keep the factory shape: `todo_write` must stay an inner function that closes over `store` and is returned at the end.",
                ],
                "hints": [
                    "Three phases: normalise, validate, commit. Commit last.",
                    "`sum(t.status == \"in_progress\" for t in items)` counts booleans.",
                    "Skeleton:\n```python\nitems = [...]               # dict or TodoItem -> TodoItem\nif sum(...) > 1:\n    raise ValueError(\"only one task can be in_progress at a time\")\nif any(...):                # blank content\n    raise ValueError(...)\nstore.items = items\ndone = ...\nreturn f\"List updated ({done}/{len(items)} completed):\\n{store.render()}\"\n```",
                ],
                "test": "python -m pytest tests/test_l08_planning.py -k todo_write -v",
            },
            "08.2": {
                "where": "`forja/planning.py` · `make_exit_plan_tool(approve, on_approved)` → inner `exit_plan_mode(plan: str) -> str`",
                "contract": (
                    "Empty/blank `plan` → `ValueError`. Otherwise call `approve(plan)` exactly once (in the CLI it shows the plan as Markdown and asks `Approve the plan and start? [y/N]`; "
                    "headless or in tests it is a function returning `bool`). If approved: call `on_approved()` (the harness switches to `default` mode) and return a text containing `APPROVED` "
                    "that tells the model it is no longer in plan mode and must implement the plan step by step and verify. If rejected: do NOT call `on_approved`, and return a text containing "
                    "`REJECTED` saying it is still in plan mode and should ask what to change or propose an alternative. `test_exit_plan_tool` checks both branches and that the callback ran only on approval; "
                    "`test_plan_mode_flow` checks that after approval `app.mode == \"default\"`."
                ),
                "steps": [
                    "Validate `plan.strip()`; raise `ValueError` if empty.",
                    "Call `approve(plan)` once and keep the boolean.",
                    "If true: call `on_approved()`, then return the APPROVED instruction.",
                    "If false: return the REJECTED instruction.",
                ],
                "gotchas": [
                    "The words `APPROVED` and `REJECTED` must be uppercase in the text: the tests look for them, and uppercase also helps small models notice the state change.",
                    "Call `on_approved()` only in the approved branch, and only once.",
                    "The return text is an instruction for the MODEL, not for the user: say clearly what to do next (implement + verify, or ask/propose). A vague `ok` makes small models re-plan forever.",
                    "Do not change the mode yourself here: the tool does not know the harness; the `on_approved` callback does it.",
                ],
                "hints": [
                    "It is a guard clause plus an if/else around a callback.",
                    "The two callbacks are injected so the tool is testable without a UI or a harness.",
                    "Skeleton:\n```python\nif not plan.strip():\n    raise ValueError(...)\nif approve(plan):\n    ...                     # callback\n    return \"The user APPROVED the plan. ...\"\nreturn \"The user REJECTED the plan. ...\"\n```",
                ],
                "test": "python -m pytest tests/test_l08_planning.py -k \"exit_plan or plan_mode_flow\" -v",
            },
        },
        "try_it": [
            "`python scripts/tasks.py reset`, then `forja --cwd playground --mode plan`. The prompt reads `plan ›`.",
            "Ask: `add percentage discounts to invoices (before VAT) with tests`. Expected: only read actions (`⏺ Read ...`, `⏺ Grep ...`, `⏺ Glob ...`). If the model tries an edit you see a red `⎿ DENIED (plan mode: read-only) ...` and it goes back to investigating.",
            "A magenta `Proposed plan` panel appears with files to touch, changes and how to verify, followed by `Approve the plan and start? [y/N] >`. Answer `n` once: the model gets `REJECTED` and asks what to change. Tell it what to adjust and approve with `y` the next time.",
            "After `y`: the REPL mode becomes `default` (the next prompt shows `default ›`), edits now ask for approval, and you see `⏺ Todos (N)` lines as the agent ticks tasks off. Type `/todos` any time: `☑ ...`, `▶ ...`, `☐ ...`.",
            "At the end the agent runs the tests; check yourself with `cd playground` and `python -m pytest -q`. Then `python scripts/tasks.py reset` to clean up.",
        ],
        "troubleshooting": [
            ["`test_todo_write_validation`: `assert len(store.items) == 3` fails (it is 2)",
             "You assigned `store.items` before validating → validate first, commit last."],
            ["`test_todo_write_validation`: `not two.ok` fails",
             "You returned an error string instead of raising → `raise ValueError(...)`."],
            ["`AttributeError: 'dict' object has no attribute 'status'`",
             "The registry passes dicts → convert with `TodoItem.model_validate(d)` (keep `TodoItem` instances as they are)."],
            ["`test_plan_mode_flow`: `assert \"PLAN mode\" in llm.calls[0][\"messages\"][0][\"content\"]` fails",
             "Lab 06 is not done, so the harness uses `FALLBACK_PROMPT` → finish 06.2 (or run `python scripts/tasks.py catchup 07`)."],
            ["`test_plan_mode_flow`: the first tool result is not `DENIED`",
             "Lab 04's `decide` does not deny non-read tools in plan mode → check TODO 04.x; the message must contain `plan mode`."],
            ["Real model never calls `exit_plan_mode` and just writes the plan as text",
             "Small models do that → say it explicitly: `when you have the plan, present it with exit_plan_mode`; or try a stronger model."],
            ["Real model sets several tasks `in_progress` and loops on the error",
             "Make the `ValueError` message actionable (`only one task can be in_progress at a time`); the model reads it and retries with one."],
            ["Headless (`forja -p ... --mode plan`) always rejects the plan",
             "With no user, `plan_approver` is `None` → expected; plan mode is meant for interactive use."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 08` → 3 passed.",
            "[ ] In plan mode the agent investigates, presents a plan with `exit_plan_mode`, and after `y` executes it ticking off tasks (`/todos` shows progress).",
            "[ ] You saw at least one `DENIED (plan mode: read-only)` or one `REJECTED` and the agent recovered.",
        ],
    },
}
