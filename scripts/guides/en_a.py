"""Step-by-step student guidance (English) for labs 00-04.

Schema: see scripts/guides/__init__.py consumers (GUIDE[lab_id] -> before / order / todos / try_it /
troubleshooting / done_when; labs without TODOs use steps_noTODO). All strings are Markdown.
"""
from __future__ import annotations

GUIDE: dict[str, dict] = {}

# ---------------------------------------------------------------------------------------------
# LAB 00 · Setup and first contact
# ---------------------------------------------------------------------------------------------
GUIDE["00"] = {
    "before": [
        "You need **Python 3.11+**, **git** and **Ollama** installed (or the address of the room's shared server). "
        "Check with `python --version` (macOS/Linux: `python3 --version`), `git --version` and `ollama --version`.",
        "Everything is run **from the repo root** through `python scripts/tasks.py …` so the same commands work on "
        "Windows (PowerShell/cmd) and macOS/Linux, without `make`.",
        "Map of the repo: `forja/` = YOUR code (stub functions raising `NotImplementedError(\"TODO NN.x\")` with a hint "
        "comment above), `tests/test_lNN_*.py` = offline tests per lab (they use `forja/fake_llm.py`, no model needed), "
        "`playground/` = small invoices project with 3 bugs that your agent will fix, `labs/LNN_*/` = lab sheets.",
        "Forja is **progressive**: `forja/harness.py` catches `NotImplementedError` and keeps running without the "
        "missing piece, printing a note like `· tools: lab 02 pending — running without this capability`. "
        "Every lab you finish lights up a capability in the CLI.",
    ],
    "order": "Do the steps in order: virtualenv → install → model → `forja doctor` → tests. "
             "The model download is the slow part (~5 GB for `qwen3:8b`), so start `ollama pull` as soon as Ollama "
             "is installed and do the Python steps while it downloads.",
    "todos": {},
    "steps_noTODO": [
        "**Open a terminal at the repo root** (the folder with `pyproject.toml`).\n"
        "  - Windows PowerShell: `cd C:\\path\\to\\forja-workshop`\n"
        "  - macOS/Linux: `cd ~/path/to/forja-workshop`\n"
        "  - Expected: `dir` / `ls` shows `forja`, `tests`, `playground`, `scripts`, `pyproject.toml`.",
        "**Create and activate a virtualenv.**\n"
        "  - Windows PowerShell: `python -m venv .venv` then `.venv\\Scripts\\Activate.ps1`\n"
        "    (if you get *\"running scripts is disabled on this system\"*: "
        "`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then activate again).\n"
        "  - Windows cmd.exe: `python -m venv .venv` then `.venv\\Scripts\\activate.bat`\n"
        "  - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`\n"
        "  - Expected: your prompt starts with `(.venv)` and `python --version` prints 3.11 or newer. "
        "From now on `python` (not `python3`) is the venv interpreter on every OS.",
        "**Install Forja and create `.env`:** `python scripts/tasks.py setup` (same on every OS).\n"
        "  - Expected: a first line `» …python -m pip install -e .[dev]`, pip output ending in "
        "`Successfully installed … forja-1.0.0 …`, and `created .env (review it)` the first time.\n"
        "  - Check: `forja --help` prints `usage: forja [-h] [-p PROMPT] [--mode …]`.",
        "**Choose your backend in `.env`** (open it with any editor).\n"
        "  - 16 GB laptop: `FORJA_BACKEND=ollama`, `FORJA_MODEL=qwen3:8b` (the default).\n"
        "  - 32 GB Mac / 24 GB GPU: `FORJA_MODEL=qwen3-coder:30b`.\n"
        "  - Shared room server: uncomment the `openai_compat` block and set `FORJA_BASE_URL` / `FORJA_MODEL` "
        "from the tutor.\n"
        "  - OpenRouter: open-weight models only — `anthropic/*`, `openai/*`, `gpt-oss`, `o3`… are blocked in "
        "`forja/config.py` (`ModelPolicyError`).",
        "**Download and try the model** (skip if you use the shared server).\n"
        "  - Every OS: `ollama pull qwen3:8b` → progress bars, then `success`.\n"
        "  - `ollama run qwen3:8b \"hello\"` → a short greeting (qwen3 may print a *Thinking…* section first).\n"
        "  - While it answers, in another terminal: `ollama ps` → a row with `qwen3:8b`, its SIZE and "
        "PROCESSOR (`100% GPU`, or a CPU/GPU split, which is slower).",
        "**Check that the model can call tools:** `forja doctor` (it talks to the backend with the `openai` SDK "
        "directly, so it works before lab 01).\n"
        "  - Expected:\n"
        "    ```\n"
        "    backend=ollama url=http://localhost:11434/v1 model=qwen3:8b\n"
        "    answered in 4.2s · ~35 tok/s (includes loading)\n"
        "    ✔ the model calls tools (ping)\n"
        "    ```\n"
        "  - `! the model answered without calling the tool` → the model doesn't do tool calling: pick another one. "
        "`✘ could not talk to the model` → Ollama isn't running or the URL in `.env` is wrong.",
        "**Run the workshop tests:** `python scripts/tasks.py test`.\n"
        "  - Expected: almost all red — around `58 failed, 7 passed`, each failure ending in "
        "`NotImplementedError: TODO NN.x`. That is correct: those are your TODOs.\n"
        "  - One lab only: `python scripts/tasks.py test 01` → `9 failed, 5 passed` "
        "(the 5 green ones test provided code).",
        "**Run the practice project's tests** (the work for your agent):\n"
        "  - Windows PowerShell: `cd playground; python -m pytest -q; cd ..`\n"
        "  - macOS/Linux: `cd playground && python -m pytest -q; cd ..`\n"
        "  - Expected: `3 failed, 4 passed` — `test_round_half_up`, `test_total_with_vat_cent` and "
        "`test_due_date_sunday_moves_to_monday`. Don't fix them by hand: Forja will.",
        "**Open the CLI once:** `forja --cwd playground`.\n"
        "  - Expected: a cyan banner `Forja 1.0.0 · qwen3:8b · mode default`, the path, and `/help for commands`.\n"
        "  - Type `hello` → `NotImplementedError: TODO 01.3` in red, plus dim `· … lab NN pending` notes. "
        "Correct for now: the streaming client is lab 01. Leave with `/exit` or Ctrl+D (Windows: Ctrl+Z, Enter).",
    ],
    "try_it": [
        "Watch the tutor run `python scripts/tasks.py demo`: the reference agent on `playground/`. "
        "That is your agent at the end of day 2.",
        "Run `ollama ps` while `ollama run qwen3:8b \"write a haiku\"` is answering: note GPU vs CPU and the memory used.",
        "Skim `forja/harness.py`, method `Forja.gate`: every tool call goes parse → PreToolUse hook → permissions "
        "→ approval → execute → PostToolUse hook. Each step is a lab.",
        "Open `forja/llm.py` and find the first `# TODO 01.1:` comment: this is what a starter stub looks like.",
    ],
    "troubleshooting": [
        ["PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled`",
         "Execution policy → `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, or use cmd.exe "
         "with `.venv\\Scripts\\activate.bat`."],
        ["`forja` is not recognized / `command not found: forja`",
         "The venv isn't active or `setup` failed → activate it and re-run `python scripts/tasks.py setup`. "
         "`python -m forja` works as a fallback."],
        ["`ERROR: Package 'forja' requires a different Python`",
         "Your Python is older than 3.11 → install 3.11+ and recreate `.venv` with it "
         "(Windows: `py -3.12 -m venv .venv`)."],
        ["`forja doctor` → `✘ could not talk to the model: APIConnectionError`",
         "Ollama is not running or `OLLAMA_BASE_URL` is wrong → start the Ollama app (or `ollama serve`) and "
         "check `http://localhost:11434` in a browser says *Ollama is running*."],
        ["`forja doctor` → `ModelPolicyError: model '…' blocked by policy`",
         "You chose a closed model id (anthropic/openai/gpt-oss/o3…) → use an open-weight model."],
        ["`forja doctor` is very slow the first time (30–90 s)",
         "The model is being loaded into memory → normal; the second call is fast. If it stays slow, `ollama ps` "
         "probably shows CPU: use a smaller model or the shared server."],
        ["macOS: `python: command not found`",
         "Outside the venv macOS only has `python3` → create the venv with `python3 -m venv .venv`; once it is "
         "active, `python` works."],
    ],
    "done_when": [
        "[ ] `ollama run <your model> \"hello\"` answers (or the shared server answers `forja doctor`).",
        "[ ] `forja doctor` prints `✔ the model calls tools`.",
        "[ ] `python scripts/tasks.py test` runs and shows red `NotImplementedError: TODO …` failures.",
        "[ ] `playground` tests show exactly 3 failures.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 01 · Streaming LLM client
# ---------------------------------------------------------------------------------------------
GUIDE["01"] = {
    "before": [
        "Open `forja/llm.py` (your three TODOs), `forja/types.py` (`ToolCall`, `ChatResponse`, `TextDelta`, `Done` — "
        "provided) and `tests/test_l01_llm.py`.",
        "The `openai` SDK is only an HTTP client here. With `stream=True`, "
        "`client.chat.completions.create(**params)` returns an iterator of *chunks*. Each chunk has `.model`, "
        "`.usage` (usually only on the LAST chunk, which has `choices == []`) and `.choices[0].delta` with "
        "`.content` (a text piece or `None`) and `.tool_calls` (a list of fragments or `None`). "
        "`.choices[0].finish_reason` is set on the last content chunk.",
        "A tool-call fragment has `.index` (which call), `.id` and `.function.name` (usually only in the first "
        "fragment) and `.function.arguments` (a *piece* of a JSON string). The test fakes them with class `D`.",
        "How it connects: `LLMClient.stream()` is the generator the agent loop (lab 03) consumes. It yields "
        "`TextDelta(text)` for the UI while streaming and ends with ONE `Done(ChatResponse(...))` with everything "
        "assembled. `chat()` (provided) just returns the `Done` response.",
        "Provided helpers you will reuse: `self._params(messages, tools, **kw)` (builds the request body, "
        "including `stream`, `stream_options`, `tools`, `tool_choice` and `extra_body`), `RETRYABLE` "
        "(the transient exception classes) and `rescue_text_tool_calls(text)`.",
    ],
    "order": "Do 01.1 (accumulator) first: it is small, pure and tested in isolation. Then 01.2 (think filter), "
             "also pure but trickier — draw the buffer states on paper. Finish with 01.3, which wires both into "
             "the real stream; its tests use an `httpx.MockTransport`, so you still need no model. "
             "Run each TODO's test command before moving on.",
    "todos": {
        "01.1": {
            "where": "`forja/llm.py` · `ToolCallAccumulator.add(deltas)` / `ToolCallAccumulator.finish()`",
            "contract": "`add(deltas: list | None) -> None` receives ONE chunk's `delta.tool_calls` (may be `None`) "
                        "and updates `self._parts: dict[int, dict[str, str]]`, one slot per `index` with keys "
                        "`'id'`, `'name'`, `'arguments'`. `finish() -> list[ToolCall]` returns the complete calls "
                        "ordered by index, skipping slots without a name; a missing id is replaced by a generated "
                        "non-empty one, and empty arguments become `'{}'`. `arguments` stays a raw JSON **string**.",
            "steps": [
                "In `add`, treat `None` as an empty list (the test calls `acc.add(None)`).",
                "For each fragment, get (or create) the slot for `d.index` with empty strings.",
                "If the fragment has an `id`, store it (don't overwrite a stored id with `None`).",
                "If `d.function` is not `None`: CONCATENATE `name` and `arguments` onto the slot when present.",
                "In `finish`, walk the indices in sorted order, skip slots whose name is empty, and build "
                "`ToolCall(id or generated, name, arguments or '{}')`.",
            ],
            "gotchas": [
                "Fragments of different calls arrive interleaved (`test_accumulator_interleaved`): index 0, then 1, "
                "then 0 and 1 again in the same list. Key by `index`, never by arrival order.",
                "`function.arguments` can be `''` or `None`; `'' + None` raises `TypeError` — check before adding.",
                "Don't `json.loads` the arguments here: `ToolCall.arguments` is the raw string; validation happens "
                "in lab 02.",
                "`test_accumulator_empty_args_and_missing_id` checks `c.arguments == \"{}\"` and that `c.id` is truthy "
                "(e.g. `f\"call_{uuid.uuid4().hex[:8]}\"` — `uuid` is already imported).",
            ],
            "hints": [
                "`dict.setdefault(key, default)` returns the existing value or inserts and returns the default — "
                "perfect for “get or create the slot”.",
                "Everything is string concatenation with `+=`. The only special cases are `None` values and "
                "the empty name in `finish`.",
                "Skeleton:\n```python\ndef add(self, deltas):\n    for d in deltas or []:\n        slot = ...  # setdefault by d.index\n"
                "        # id: store if present\n        # function: += name, += arguments (if present)\n\n"
                "def finish(self):\n    out = []\n    for i in sorted(self._parts):\n        ...  # skip nameless, build ToolCall\n    return out\n```",
            ],
            "test": "python -m pytest tests/test_l01_llm.py -k accumulator -v",
        },
        "01.2": {
            "where": "`forja/llm.py` · `ThinkFilter.feed(text)` (`flush()` is provided)",
            "contract": "`feed(text: str) -> str` returns the VISIBLE text that can be printed now. State lives in "
                        "`self.buf` (text not decided yet) and `self.in_think` (inside a `<think>` block). Text inside "
                        "`<think>…</think>` is dropped; anything that might be the start of a tag split across chunks "
                        "is held in `buf` until the next call. `flush()` (provided) returns what is left in `buf` "
                        "if we are not inside a think block. Tests: `\"\".join(feed(c) for c in chunks) + flush()` "
                        "with newlines removed must equal `\"Hello\"`, and `\"a < b\"` must pass through untouched.",
            "steps": [
                "Append the new text to `self.buf`, prepare an output list, and loop while `buf` is not empty.",
                "Outside a think block: look for `\"<think>\"` in `buf`. If found, emit everything before it, cut `buf` "
                "after the tag, set `in_think = True` and continue the loop.",
                "Outside and NOT found: check whether the END of `buf` is a prefix of `\"<think>\"` (`\"<\"`, `\"<t\"`, …, "
                "`\"<think\"`). If so, emit everything except that suffix, keep the suffix in `buf` and return. "
                "Otherwise emit all of `buf`, empty it.",
                "Inside a think block: look for `\"</think>\"`. If found, drop everything up to and including it "
                "(optionally strip leading `\\n`), set `in_think = False`, continue the loop.",
                "Inside and NOT found: discard the buffer but keep its last `len(\"</think>\") - 1` characters (a "
                "closing tag may be starting) and return what you have emitted.",
                "Return the joined output.",
            ],
            "gotchas": [
                "Case `[\"<thi\", \"nk>reasoning</th\", \"ink>Hel\", \"lo\"]`: both tags are split. If you emit `\"<thi\"` "
                "immediately, the test fails.",
                "Case `[\"Hel\", \"lo<\", \"think>x</think>\"]`: you must hold back only the `\"<\"`, still emitting `\"lo\"`.",
                "`test_think_filter_keeps_normal_lt`: `\"a < b\"` — the suffix `\"b\"` is not a tag prefix, so nothing "
                "is held. Only hold a suffix that `\"<think>\".startswith(...)`.",
                "One chunk may contain a whole block plus text after it: use a `while` loop, not a single `if`.",
                "Check the longest possible suffix first (6 chars down to 1), and never more than `len(buf)`.",
            ],
            "hints": [
                "Think of it as a two-state machine (outside / inside) with a buffer of undecided characters.",
                "`str.find` returns `-1` when not found. `\"<think>\".startswith(self.buf[-k:])` tells you whether the "
                "last `k` characters could be the start of the tag.",
                "Skeleton:\n```python\nself.buf += text\nout = []\nwhile self.buf:\n    if self.in_think:\n"
                "        end = self.buf.find(\"</think>\")\n        if end == -1:\n            ...  # keep last 7 chars, return\n"
                "        ...  # cut after the tag, in_think = False\n    else:\n        start = self.buf.find(\"<think>\")\n"
                "        if start == -1:\n            ...  # hold back a tag prefix at the end, or emit all\n"
                "        ...  # emit before tag, cut, in_think = True\nreturn \"\".join(out)\n```",
            ],
            "test": "python -m pytest tests/test_l01_llm.py -k think_filter -v",
        },
        "01.3": {
            "where": "`forja/llm.py` · `LLMClient.stream(messages, tools=None, **kw)`",
            "contract": "A **generator** yielding `StreamEvent`s: zero or more `TextDelta(text)` (visible text only, "
                        "after `ThinkFilter`) and exactly one final `Done(ChatResponse(content or None, tool_calls, "
                        "usage, model, finish_reason))`. Retries only exceptions in `RETRYABLE`, at most "
                        "`self.max_retries` extra attempts, waiting 1, 2, 4… seconds with `time.sleep`. "
                        "`usage` must be exactly `{\"prompt_tokens\": …, \"completion_tokens\": …}`. If no native tool "
                        "calls arrived, try `rescue_text_tool_calls(content)`. `finish_reason` is `\"tool_calls\"` when "
                        "there are calls, otherwise the last one seen.",
            "steps": [
                "Build `params = self._params(messages, tools, **kw)`.",
                "Retry loop: `for attempt in range(self.max_retries + 1)`, call "
                "`self._client.chat.completions.create(**params)`; on success `break`; on a `RETRYABLE` exception "
                "re-raise if it was the last attempt, else `time.sleep(delay)` and double `delay` (start at 1).",
                "Create a `ToolCallAccumulator`, a `ThinkFilter`, a list for the text, and defaults for usage, "
                "finish reason and model (`self.model`).",
                "For each chunk: read `usage` (if present) and `model` (if present) FIRST; then skip chunks without "
                "`choices`; then take `choices[0]`, remember `finish_reason`, pass `delta.content` through the think "
                "filter and `yield TextDelta(...)` if anything is visible; pass `delta.tool_calls` to the accumulator.",
                "After the loop: `flush()` the filter (yield its tail too), join the text, `finish()` the accumulator; "
                "if there are no calls, use `rescue_text_tool_calls`.",
                "`yield Done(ChatResponse(...))`.",
            ],
            "gotchas": [
                "The usage chunk has `choices == []`: if you `continue` before reading `usage`, "
                "`test_stream_text_and_tool_calls` fails on `r.usage`.",
                "Copy only `prompt_tokens` and `completion_tokens` (the server also sends `total_tokens`; the test "
                "compares the whole dict).",
                "Call `time.sleep(...)` through the module (`import time` is there). The tests monkeypatch "
                "`\"time.sleep\"`; `from time import sleep` would really sleep.",
                "`test_retries_on_503` expects exactly 3 requests with `max_retries=2`. `test_no_retry_on_400` expects "
                "exactly 1: a 400 raises `openai.BadRequestError`, which is NOT in `RETRYABLE`, so let it propagate. "
                "(With the stub it fails as `assert 0 == 1`: the exception is raised but no request was made.)",
                "Don't add your own retries in the SDK: the client is created with `max_retries=0` on purpose.",
            ],
            "hints": [
                "The function contains `yield`, so it is a generator: nothing runs (not even the request) until "
                "someone iterates it.",
                "`except RETRYABLE:` works because `RETRYABLE` is a tuple of exception classes. The text and the "
                "content of the final response are the same visible text (`\"Looking…\"` in the test).",
                "Skeleton:\n```python\nparams = self._params(messages, tools, **kw)\ndelay = 1.0\n"
                "for attempt in range(self.max_retries + 1):\n    try: chunks = ...; break\n"
                "    except RETRYABLE: ...  # raise on last attempt, else sleep and double\n"
                "acc, think = ToolCallAccumulator(), ThinkFilter()\nfor ch in chunks:\n    ...  # usage/model, skip no choices, text, tool calls\n"
                "...  # flush, finish, rescue\nyield Done(ChatResponse(...))\n```",
            ],
            "test": "python -m pytest tests/test_l01_llm.py -k \"stream or retr\" -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 01` → `14 passed`.",
        "`forja --cwd playground` and ask `explain in 3 lines what an invoice due date is`. You should SEE the "
        "answer appear progressively (token by token) and then a dim `(1 steps · 0 tools)`. No `<think>` text "
        "should be printed.",
        "Before the prompt you will see dim notes such as `· tools: lab 02 pending — running without this capability` "
        "and `· agent: lab 03 pending — chat mode without tools`: expected, it is a plain chat for now.",
        "Check the retries: point to a dead port and watch it wait 1+2+4 s before failing.\n"
        "  - PowerShell: `$env:OLLAMA_BASE_URL=\"http://localhost:9999/v1\"; forja --cwd playground` "
        "(then `Remove-Item Env:OLLAMA_BASE_URL`)\n"
        "  - macOS/Linux: `OLLAMA_BASE_URL=http://localhost:9999/v1 forja --cwd playground`\n"
        "  - Type `hi` → after ~7 s, red `APIConnectionError: Connection error.`",
        "`forja doctor` still prints `✔ the model calls tools` (it doesn't use your client, so it is your baseline "
        "when something looks wrong).",
    ],
    "troubleshooting": [
        ["`TypeError: can only concatenate str (not \"NoneType\") to str` in `add`",
         "A fragment has `name` or `arguments` = `None` → only concatenate when the value is truthy."],
        ["Think-filter test fails with output like `<thiHello` or `Hel<`",
         "You emitted a possible tag prefix instead of holding it in `self.buf` → hold back the longest suffix "
         "that `\"<think>\".startswith(...)`."],
        ["`test_think_filter_keeps_normal_lt` returns `\"a \"` or `\"\"`",
         "You hold back every `<` (or everything after it) → hold only a suffix that is a prefix of `<think>`; "
         "`flush()` returns the rest."],
        ["`test_retries_on_503` takes 3 seconds or more",
         "You imported `sleep` directly → call `time.sleep(...)` so the monkeypatch applies."],
        ["`test_no_retry_on_400` fails with `assert 2 == 1` or `3 == 1`",
         "You catch `Exception` (or `openai.APIStatusError`) in the retry loop → catch only `RETRYABLE`."],
        ["`AssertionError` on `r.usage == {...}`",
         "Usage read after the `if not ch.choices: continue`, or `total_tokens` copied → read usage first, copy two keys."],
        ["In the CLI the answer appears all at once at the end",
         "You collect the text and only yield `Done` → `yield TextDelta(visible)` inside the chunk loop."],
        ["In the CLI you see `<think>…` text",
         "The content is not passed through `ThinkFilter.feed`, or `flush()` is called while `in_think` and returns "
         "the buffer → check both. (Some Ollama versions send reasoning in a separate field: then nothing appears, "
         "which is also fine.)"],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 01` → all 14 tests green.",
        "[ ] `forja --cwd playground` answers in streaming without `<think>` text.",
        "[ ] You can explain why a 400 is not retried and a 503 is.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 02 · File tools
# ---------------------------------------------------------------------------------------------
GUIDE["02"] = {
    "before": [
        "Open `forja/tools.py` (TODOs 02.1–02.2), `forja/fs_tools.py` (02.3–02.6) and `tests/test_l02_tools.py`. "
        "Read the provided parts first: the `@tool` decorator builds a pydantic model from type hints + docstring "
        "(`Tool.args_model`), `ToolRegistry.parse_args(call)` validates JSON arguments, and `read_file` / `glob` "
        "are complete examples of tools.",
        "Stdlib/APIs you will use: pydantic `Model.model_json_schema()`; `json.dumps`; `time.perf_counter()`; "
        "`pathlib.Path.resolve()`, `.is_absolute()`, `.is_relative_to()`; `str.count`, `str.replace(old, new, 1)`; "
        "`re.compile`, `fnmatch.fnmatch`.",
        "Provided `Workspace` helpers you must use: `ws.resolve(path)` (your 02.3), `ws.rel(p)` (relative string), "
        "`ws.mark_read(p)` (remember mtime), `ws.check_fresh(p)` (raises `PermissionError` if not read or changed "
        "on disk), `ws.walk(base)` (files, skipping `.git`, `.venv`, `__pycache__`…), `ws.before_write` "
        "(callbacks, used by checkpoints in lab 11) and `unified_diff(before, after, path)`.",
        "Key idea: tools **raise** normal Python exceptions with helpful messages; `ToolRegistry.execute` (02.2) "
        "catches everything and returns the message to the model as `ToolResult(ok=False, …)`. So the test "
        "assertions like `\"before modifying\" in res.output` check YOUR error text passed through `execute`.",
        "How it connects: `schemas()` is what the model sees as `tools=[…]`; `execute` is called by the harness "
        "gate for every call the model makes.",
    ],
    "order": "02.1 → 02.2 → 02.3 first: every file-tool test goes through `registry.execute` and `ws.resolve`, so "
             "nothing else can pass before them. Then 02.4 (`write_file`), 02.5 (`edit_file`, the biggest one) "
             "and 02.6 (`grep`). Keep `read_file` open as your model of how a tool is written.",
    "todos": {
        "02.1": {
            "where": "`forja/tools.py` · `Tool.schema()`",
            "contract": "Returns `{\"type\": \"function\", \"function\": {\"name\": self.name, \"description\": "
                        "self.description, \"parameters\": params}}` where `params` is the pydantic JSON Schema of "
                        "`self.args_model` with: no `\"title\"` at the root, no `\"title\"` inside any property, "
                        "`\"additionalProperties\": False`, and a `\"properties\"` key even for tools without arguments. "
                        "`test_schema_from_type_hints` checks name, description `\"Does something.\"`, "
                        "`required == [\"path\"]`, `n` default `3`, `path` description `\"Path.\"`.",
            "steps": [
                "Get the schema dict from `self.args_model.model_json_schema()`.",
                "Remove the root `title` (use `pop` with a default so it never fails).",
                "Loop over the values of `params[\"properties\"]` (may be missing) and remove each `title`.",
                "Make sure `properties` exists and set `additionalProperties` to `False`.",
                "Wrap it in the OpenAI function format and return.",
            ],
            "gotchas": [
                "pydantic adds titles like `\"Path\"`, `\"N\"` to each property: small models get confused by them, "
                "and the test asserts there is no root title.",
                "A tool with no parameters has no `properties` key: some backends reject a schema without it.",
                "Descriptions and `required` are already produced by pydantic from the `@tool` decorator: don't "
                "rebuild them by hand.",
            ],
            "hints": [
                "Print it first: `python -c \"from forja.fs_tools import *; from pathlib import Path; "
                "print(make_fs_tools(Workspace(Path('.')))[0].args_model.model_json_schema())\"`.",
                "`dict.pop(\"title\", None)` and `dict.setdefault(\"properties\", {})` do most of the work.",
                "Skeleton:\n```python\nparams = self.args_model.model_json_schema()\n# drop root title\n"
                "for prop in params.get(\"properties\", {}).values():\n    ...\n# ensure properties, additionalProperties\n"
                "return {\"type\": \"function\", \"function\": {...}}\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k schema -v",
        },
        "02.2": {
            "where": "`forja/tools.py` · `ToolRegistry.execute(call)`",
            "contract": "`execute(call: ToolCall) -> ToolResult` and it **never raises**. Uses `self.parse_args(call)` → "
                        "`(tool, args, err)`; if `err`, return `ToolResult(call.id, call.name, False, err)`. Otherwise "
                        "call `tool.fn(**args)`; any `Exception` becomes `ok=False` with output "
                        "`\"ERROR in '<tool>': <ExceptionType>: <message>\"`. Success: a `ToolOutput` gives `.text` and "
                        "`.meta`; a `str` is used as is; anything else is `json.dumps(..., ensure_ascii=False, "
                        "default=str)`. Output always goes through `_truncate`; `duration_ms` is measured.",
            "steps": [
                "Take `t0 = time.perf_counter()` at the start.",
                "Call `self.parse_args(call)`; on error return a failed `ToolResult` with that message.",
                "In a `try`, call the tool function with the validated args; on `Exception` return a failed result "
                "with type name and message.",
                "Convert the return value to `(text, meta)` according to its type.",
                "Return `ToolResult(call.id, call.name, ok, _truncate(text), meta, duration_ms)`.",
            ],
            "gotchas": [
                "When the tool doesn't exist, `parse_args` returns `t = None`: use `call.name`, not `t.name`, in the "
                "result (`test_execute_never_raises` calls a tool named `nope`).",
                "Include the exception MESSAGE in the output: later tests look for `\"outside the workspace\"`, "
                "`\"before modifying\"`, `\"times\"`, `\"line numbers\"`, `\"has changed\"` in `res.output`.",
                "Catch `Exception`, not bare `except:` (you don't want to swallow Ctrl+C / `KeyboardInterrupt`).",
                "A small helper closure `done(ok, out, meta=None)` avoids repeating the `ToolResult(...)` construction.",
            ],
            "hints": [
                "The ordered field list of `ToolResult` is `call_id, name, ok, output, meta, duration_ms`.",
                "`isinstance(res, ToolOutput)` / `isinstance(res, str)`; the message format is "
                "`f\"ERROR in '{t.name}': {type(e).__name__}: {e}\"`.",
                "Skeleton:\n```python\nt0 = time.perf_counter()\nt, args, err = self.parse_args(call)\nif err:\n    return ...\n"
                "try:\n    res = t.fn(**args)\nexcept Exception as e:\n    return ...\n# ToolOutput? str? other -> json\n"
                "return ToolResult(..., _truncate(text), meta, int((time.perf_counter() - t0) * 1000))\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k execute_never_raises -v",
        },
        "02.3": {
            "where": "`forja/fs_tools.py` · `Workspace.resolve(path)`",
            "contract": "`resolve(path: str) -> Path`: a relative path is joined to `self.root`, an absolute one is kept; "
                        "the result is `.resolve()`d (removes `..`, follows symlinks). If it is neither `self.root` nor "
                        "inside it, raise `PermissionError(f\"path outside the workspace: {path}\")`. Returns the "
                        "absolute resolved `Path`. `self.root` is already resolved in `__post_init__`.",
            "steps": [
                "Wrap the string in a `Path`.",
                "Build the candidate: the path itself if absolute, otherwise `self.root / path`.",
                "Call `.resolve()` on the candidate.",
                "If it equals `self.root` or `is_relative_to(self.root)`, return it; otherwise raise the "
                "`PermissionError`.",
            ],
            "gotchas": [
                "Check AFTER resolving: `\"invoices/../../secret.txt\"` looks relative but escapes.",
                "Don't compare strings with `startswith`: `/home/me/proj2` starts with `/home/me/proj`. "
                "`Path.is_relative_to` compares path components.",
                "`test_sandbox` checks both `\"../secret.txt\"` and `\"/etc/passwd\"` and that the message contains "
                "`\"outside the workspace\"` (on Windows `/etc/passwd` becomes `C:\\etc\\passwd`: still outside).",
            ],
            "hints": [
                "Three lines of logic: build, resolve, check.",
                "`Path.is_absolute()`, `Path.resolve()`, `Path.is_relative_to(other)`.",
                "Skeleton:\n```python\np = Path(path)\ntarget = (...).resolve()\nif target != self.root and not ...:\n"
                "    raise PermissionError(...)\nreturn target\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k \"sandbox or read_numbered\" -v",
        },
        "02.4": {
            "where": "`forja/fs_tools.py` · `make_fs_tools` → inner `write_file(path, content)`",
            "contract": "Returns `ToolOutput(text, {\"path\": ws.rel(p), \"diff\": unified_diff(before, content, ws.rel(p))})`. "
                        "New file: creates parent folders and writes. Existing file: `ws.check_fresh(p)` first (raises "
                        "`\"read … with read_file before modifying it\"`), keep the old content as `before`. Call every "
                        "callback in `ws.before_write` with `p` before writing. After writing, `ws.mark_read(p)`. "
                        "Text like `\"docs/note.md created (1 lines)\"` / `\"… updated (N lines)\"`. Write UTF-8.",
            "steps": [
                "`p = ws.resolve(path)`; `before = \"\"`.",
                "If `p` exists: `ws.check_fresh(p)` and read the old text into `before`.",
                "Call each `cb(p)` in `ws.before_write`.",
                "Create `p.parent` (parents, exist_ok) and write `content` with `encoding=\"utf-8\"`.",
                "`ws.mark_read(p)` and return the `ToolOutput` with path and diff.",
            ],
            "gotchas": [
                "`test_write_new_and_overwrite_rules` writes to `docs/note.md` — the `docs` folder doesn't exist yet.",
                "Overwriting a file that was never read must fail with `\"before modifying\"` in the output: let "
                "`check_fresh` raise, don't catch it.",
                "Without `mark_read` after writing, the next `edit_file` on the same file fails with "
                "`\"has changed since you read it\"` (your own write changed the mtime).",
                "Always pass `encoding=\"utf-8\"`: on Windows the default encoding is not UTF-8.",
            ],
            "hints": [
                "Mirror the structure of the provided `read_file`: resolve first, then work with `p`.",
                "`p.parent.mkdir(parents=True, exist_ok=True)`, `p.write_text(content, encoding=\"utf-8\")`.",
                "Skeleton:\n```python\np = ws.resolve(path)\nbefore = \"\"\nif p.exists():\n    ...  # fresh check + old content\n"
                "for cb in ws.before_write:\n    ...\n...  # mkdir, write, mark_read\nreturn ToolOutput(f\"...\", {\"path\": ..., \"diff\": ...})\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k write_new -v",
        },
        "02.5": {
            "where": "`forja/fs_tools.py` · `make_fs_tools` → inner `edit_file(path, old_string, new_string, replace_all=False)`",
            "contract": "Returns `ToolOutput(\"<rel> edited (N replacement(s), from line L)\", {\"path\": ws.rel(p), \"diff\": …})`. "
                        "Raises (in this order): `FileNotFoundError` if it isn't a file (suggest `write_file`); "
                        "`check_fresh` errors; `ValueError` if `old_string == new_string`; `ValueError` "
                        "`\"old_string not found in <path>.\"` + a hint when the count is 0; `ValueError` "
                        "`\"old_string appears N times in <path>: …\"` when the count is >1 and not `replace_all`. "
                        "Replaces one occurrence (or all), calls `ws.before_write` callbacks, writes, `mark_read`.",
            "steps": [
                "Resolve the path; if it is not a file, raise `FileNotFoundError` mentioning `write_file`.",
                "`ws.check_fresh(p)`; reject identical old/new strings.",
                "Read the text and count `old_string` occurrences.",
                "Count 0: build a hint — if `old_string` has lines starting with digits + `→` (regex "
                "`r\"^\\s*\\d+→\"` with `re.M`), say it contains read_file **line numbers**; else if its stripped "
                "version exists in the text, say whitespace/indentation differ. Raise `ValueError`.",
                "Count >1 without `replace_all`: raise `ValueError` saying it appears N times and how to fix it.",
                "Replace (once with `str.replace(old, new, 1)` or all), call `before_write` callbacks, write UTF-8, "
                "`mark_read`.",
                "Compute the line of the first match (`text[:text.index(old_string)].count(\"\\n\") + 1`) and return "
                "the `ToolOutput` with the diff.",
            ],
            "gotchas": [
                "Order matters: `test_edit_requires_read_and_unique` first edits an UNREAD file and expects "
                "`\"before modifying\"` — `check_fresh` must run before counting.",
                "The duplicate test uses `old_string=\"return\"` and checks `\"times\"` in the output.",
                "The line-number test passes `\"     9→    return round(value, 2)\"` and checks `\"line numbers\"` in the "
                "output: the `→` is the character `read_file` prints.",
                "`test_edit_detects_external_change` touches the file after reading: just calling `check_fresh` gives "
                "`\"has changed\"`.",
                "The diff must contain the new line exactly once → replace only the first occurrence by default.",
            ],
            "hints": [
                "These error messages are prompts for the model: say what went wrong AND what to do next.",
                "`text.count(old_string)`, `text.replace(old, new, 1)`, `re.search(pattern, old_string, re.M)`.",
                "Skeleton:\n```python\np = ws.resolve(path)\nif not p.is_file(): raise FileNotFoundError(...)\n"
                "ws.check_fresh(p)\nif old_string == new_string: raise ValueError(...)\ntext = ...\nn = text.count(old_string)\n"
                "if n == 0: ...   # hint: line numbers? whitespace?\nif n > 1 and not replace_all: ...\n"
                "new_text = ...\n# before_write, write, mark_read, line, return ToolOutput\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k \"edit_requires or external_change\" -v",
        },
        "02.6": {
            "where": "`forja/fs_tools.py` · `make_fs_tools` → inner `grep(pattern, path=\".\", include=None, ignore_case=False, show_content=True)`",
            "contract": "Returns a `str`. With `show_content=True`: one line per match, `\"<rel>:<lineno>: <line stripped, "
                        "max 300 chars>\"`. With `show_content=False`: one line per matching file (its relative path). "
                        "`include` filters by file NAME with `fnmatch` (e.g. `*.py`). Searches a single file if `path` is "
                        "a file, otherwise `ws.walk(base)`. Skips files that are not UTF-8. Stops at 300 results with a "
                        "note. Nothing found: `\"(no matches)\"`.",
            "steps": [
                "Compile the regex with `re.I` when `ignore_case`.",
                "Resolve `path`; the file list is `[base]` if it is a file, else `ws.walk(base)`.",
                "For each file: skip it if `include` is given and the name doesn't match.",
                "Read it as UTF-8 inside `try/except (UnicodeDecodeError, OSError)` and skip on error.",
                "Enumerate lines from 1; on `rx.search(line)`: append the formatted line, or (paths-only mode) "
                "append the path once and stop reading that file.",
                "Stop with a note when you reach 300 results; return the joined lines or `\"(no matches)\"`.",
            ],
            "gotchas": [
                "Line numbers start at 1: `test_grep_and_glob` expects `\"invoices/amounts.py:7:\"` for "
                "`def round_amount`.",
                "Use `ws.rel(f)` for the path, not the absolute path.",
                "`include` is matched against `f.name`, not the full path.",
                "In paths-only mode each file must appear once even if many lines match.",
                "An invalid regex raises `re.error`; that's fine — `execute` turns it into an error message for the model.",
            ],
            "hints": [
                "Look at the provided `glob` tool right above: same walk, different filter.",
                "`enumerate(text.splitlines(), 1)`, `fnmatch.fnmatch(f.name, include)`, `rx.search(line)`.",
                "Skeleton:\n```python\nrx = re.compile(pattern, re.I if ignore_case else 0)\nbase = ws.resolve(path)\n"
                "files = [base] if base.is_file() else ws.walk(base)\nout = []\nfor f in files:\n"
                "    ...  # include filter, read (skip binaries), match lines\n    if len(out) >= 300: ...\n"
                "return \"\\n\".join(out) or \"(no matches)\"\n```",
            ],
            "test": "python -m pytest tests/test_l02_tools.py -k grep -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 02` → `8 passed`.",
        "Drive the tools by hand from a Python REPL at the repo root (`python`, then type):\n"
        "```python\nimport json; from pathlib import Path\nfrom forja.fs_tools import Workspace, make_fs_tools\n"
        "from forja.tools import ToolRegistry; from forja.types import ToolCall\n"
        "r = ToolRegistry().register(*make_fs_tools(Workspace(Path(\"playground\"))))\n"
        "x = lambda name, **a: print(r.execute(ToolCall(\"1\", name, json.dumps(a))).output)\n"
        "x(\"grep\", pattern=\"def \", include=\"*.py\")\n```\n"
        "You should SEE lines like `invoices/amounts.py:7: def round_amount(value: float) -> float:`.",
        "In the same REPL: `x(\"read_file\", path=\"../README.md\")` → `ERROR in 'read_file': PermissionError: path "
        "outside the workspace: ../README.md`; `x(\"edit_file\", path=\"invoices/dates.py\", old_string=\"a\", "
        "new_string=\"b\")` → `… read invoices/dates.py with read_file before modifying it`.",
        "See what the model will read: `print(json.dumps(r.schemas()[2], indent=2))` → the `edit_file` schema, with "
        "its long description, `required` and `\"additionalProperties\": false`, and no `title` keys.",
        "`forja --cwd playground`: the note `tools: lab 02 pending` is gone. It is still a chat (`agent: lab 03 "
        "pending — chat mode without tools`), so the model cannot call your tools yet — that's lab 03.",
    ],
    "troubleshooting": [
        ["Every file-tool test fails with `NotImplementedError: TODO 02.2` or `TODO 02.3`",
         "All tests go through `registry.execute` and `ws.resolve` → finish 02.2 and 02.3 first."],
        ["`AttributeError: 'NoneType' object has no attribute 'name'` in `execute`",
         "Unknown tool → `t` is `None` → use `call.name` when building the error result."],
        ["Test expects `\"before modifying\"` but output says `\"old_string not found\"`",
         "You count occurrences before `ws.check_fresh(p)` → move the freshness check up."],
        ["`edit_file` works once, then the next edit says `has changed since you read it`",
         "Missing `ws.mark_read(p)` after writing → call it at the end of write_file and edit_file."],
        ["`AssertionError: 'line numbers' in …` in the edit test",
         "Your hint regex doesn't match `\"     9→    return …\"` → use `^\\s*\\d+→` with `re.M`, and copy the `→` "
         "character from `read_file`'s code."],
        ["`UnicodeDecodeError` / mojibake when writing on Windows",
         "Missing `encoding=\"utf-8\"` in `write_text`/`read_text` → always pass it."],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 02` → all 8 tests green.",
        "[ ] From the REPL you get a numbered `read_file`, a `grep` with `path:line:` hits and a sandbox error for `../`.",
        "[ ] Your `edit_file` error messages tell the model how to fix its call.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 03 · The agent loop
# ---------------------------------------------------------------------------------------------
GUIDE["03"] = {
    "before": [
        "Open `forja/agent.py` (`Events`, `AgentResult`, `Agent` and your two TODOs), `forja/fake_llm.py` "
        "(`FakeLLM`, `say`, `call`, `calls`: the scripted model the tests use) and `tests/test_l03_agent.py`.",
        "Message protocol (Chat Completions): an assistant message with `tool_calls` must be followed by one "
        "`{\"role\": \"tool\", \"tool_call_id\": …}` message per call, before the next assistant message. "
        "`ChatResponse.to_message()` and `ToolResult.to_message()` (provided) build those dicts for you.",
        "`self.llm.stream(messages, tools=...)` yields `TextDelta` and a final `Done` (your lab 01, or `FakeLLM` "
        "in tests, which yields text in 8-character pieces). `self.tools.schemas()` (lab 02) is the `tools` list.",
        "Stdlib: `concurrent.futures.ThreadPoolExecutor` (`ex.map(fn, iterable)`), `collections.Counter`, "
        "`threading.Event.is_set()`.",
        "How it connects: the harness creates `Agent(llm, registry, execute=self.gate, events=RichEvents(), …)`. "
        "The loop never knows about permissions or UI — it only calls `execute` and `events`. The same class is "
        "reused for subagents (lab 09) and evals (lab 12).",
    ],
    "order": "Start with the no-tools path of 03.2 (stream, append the assistant message, return `\"final\"`, plus "
             "the cancel check): that makes `test_final_answer`, `test_streaming_events` and `test_cancel` green. "
             "Then write 03.1 `_run_calls`, then complete 03.2 with tool execution, `max_steps` and loop detection. "
             "All 03.1 tests run through `run`, so you need both.",
    "todos": {
        "03.1": {
            "where": "`forja/agent.py` · `Agent._run_calls(calls)`",
            "contract": "`_run_calls(calls: list[ToolCall]) -> list[ToolResult]`, results in the SAME order as `calls`. "
                        "Uses `self.execute` if set, otherwise `self.tools.execute`. For each call: "
                        "`self.events.on_tool_start(call)`, execute, `self.events.on_tool_end(call, result)`. "
                        "Runs of CONSECUTIVE read-risk calls (`self._is_read(call)`) run in parallel in a "
                        "`ThreadPoolExecutor` when `self.parallel_reads`; everything else runs sequentially in order.",
            "steps": [
                "Pick the executor function: `self.execute or self.tools.execute`.",
                "Pre-allocate `results = [None] * len(calls)` and write a small inner function `run(i)` that fires "
                "the start event, executes `calls[i]` into `results[i]` and fires the end event.",
                "Walk the calls with an index `i`. If `calls[i]` is a read, advance `j` while the calls are reads.",
                "If the block has more than one read, run indices `i..j-1` with a `ThreadPoolExecutor` (e.g. up to 8 "
                "workers); a single read just runs. Set `i = j`.",
                "Non-read calls: `run(i)` and `i += 1`.",
                "Return the results list.",
            ],
            "gotchas": [
                "`test_parallel_reads_keep_order`: three 0.2 s reads + one write must take < 0.5 s AND produce tool "
                "contents `[\"r1\", \"r2\", \"r3\", \"wa\"]` with ids in the original order. Store by index; "
                "`as_completed` order is random.",
                "Only CONSECUTIVE reads: `[read, write, read]` must not run the second read before the write.",
                "`test_custom_execute_gate` asserts your gate is used: calling `self.tools.execute` directly skips "
                "permissions in the real CLI.",
                "Consume `ex.map(...)` (e.g. `list(...)`) or exceptions in workers are silently lost; leaving the "
                "`with` block waits for all of them.",
            ],
            "hints": [
                "Index-based writing (`results[i] = …`) is what keeps the order, no matter which thread finishes first.",
                "`with ThreadPoolExecutor(max_workers=min(8, j - i)) as ex: list(ex.map(run, range(i, j)))`.",
                "Skeleton:\n```python\nexecute = self.execute or self.tools.execute\nresults = [None] * len(calls)\n"
                "def run(i): ...   # start event, execute, end event\ni = 0\nwhile i < len(calls):\n"
                "    if self.parallel_reads and self._is_read(calls[i]):\n        ...  # find j, pool or single\n"
                "    else:\n        ...\nreturn results\n```",
            ],
            "test": "python -m pytest tests/test_l03_agent.py -k \"parallel or gate\" -v",
        },
        "03.2": {
            "where": "`forja/agent.py` · `Agent.run(messages)`",
            "contract": "`run(messages: list[dict]) -> AgentResult(answer, stop_reason, steps, usage, tool_calls)`. "
                        "`messages` is MODIFIED IN PLACE (the harness reads it afterwards). Stop reasons: `\"final\"` "
                        "(no tool calls; answer = `resp.content or \"\"`, steps = current step), `\"interrupted\"` "
                        "(`self.cancel` set at the start of a step; steps = step - 1), `\"loop\"` (same tool name + same "
                        "arguments string requested more than `self.max_repeats` times in this run), `\"max_steps\"` "
                        "(steps = `self.max_steps`). `usage` sums all responses; `tool_calls` counts executed calls. "
                        "The history must stay valid in every case: every `tool_call` id gets a `tool` message.",
            "steps": [
                "Create a `Counter` for usage, a `Counter` for `(name, arguments)` pairs, and a call counter.",
                "`for step in range(1, self.max_steps + 1)`: first, if `self.cancel.is_set()`, return the "
                "`\"interrupted\"` result.",
                "Stream: `self.llm.stream(messages, tools=self.tools.schemas() or None)`; forward every `TextDelta` "
                "to `self.events.on_text`, keep the `Done` response.",
                "Add its usage, `messages.append(resp.to_message())`, call `self.events.on_assistant(resp)`.",
                "No `resp.tool_calls` → return `\"final\"`.",
                "Loop detection: count each `(c.name, c.arguments)`; if one exceeds `self.max_repeats`, append a failed "
                "`ToolResult(cc.id, cc.name, False, \"Not executed: loop detected.\").to_message()` for EVERY call of "
                "this response and return `\"loop\"`.",
                "Otherwise `results = self._run_calls(resp.tool_calls)`, update the counter, extend `messages` with "
                "`r.to_message()` for each result. After the `for`, return `\"max_steps\"`.",
            ],
            "gotchas": [
                "`test_final_answer` expects `steps == 1` and the last message to be the assistant's.",
                "`test_streaming_events` checks `on_text` got MORE THAN ONE piece: forward each `TextDelta`, don't "
                "emit the full text at the end.",
                "Use `resp.to_message()`: a hand-made `{\"role\": \"assistant\", \"content\": …}` without `tool_calls` "
                "breaks the pairing and real backends answer HTTP 400.",
                "`test_max_steps_and_loop` walks the history after a `\"loop\"` stop and asserts no tool_call id is left "
                "open → close all pending calls before returning.",
                "Pass `tools=None` when there are no schemas: some servers reject `tools=[]`.",
            ],
            "hints": [
                "Write the ten-line version first (stream → append → no tools? return → run calls → append → repeat), "
                "then add cancel, loop detection and counters.",
                "`Counter.update(dict)` adds values key by key — perfect for `resp.usage`.",
                "Skeleton:\n```python\nusage, seen, n_calls = Counter(), Counter(), 0\nfor step in range(1, self.max_steps + 1):\n"
                "    if self.cancel.is_set(): return AgentResult(...)\n    resp = None\n    for ev in self.llm.stream(...):\n"
                "        ...  # TextDelta -> on_text, Done -> resp\n    ...  # usage, append, on_assistant, final?\n"
                "    ...  # loop detection (close pending calls!)\n    ...  # run calls, append tool messages\n"
                "return AgentResult(..., \"max_steps\", self.max_steps, ...)\n```",
            ],
            "test": "python -m pytest tests/test_l03_agent.py -k \"final or streaming or cancel or max_steps\" -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 03` → `6 passed`.",
        "`forja --cwd playground` and ask `explain how an invoice total is calculated`. You should SEE blue lines "
        "per tool call, e.g. `⏺ grep {\"pattern\": \"def total\", …}` followed by dim `⎿ invoices/invoice.py:…` "
        "(raw JSON args until lab 05 makes them pretty), then a streamed answer with `path:line` references and "
        "`(N steps · M tools)`.",
        "Ask `read amounts.py and dates.py and summarise both`: if the model requests both reads in one response, "
        "they run in parallel (both `⏺` lines appear before the results).",
        "Ask it to change something, e.g. `add a docstring to total_with_vat`. Until lab 04/05 you get a crude "
        "prompt `Allow edit_file {…}? [y/N]` — answer `n` and see the model react to `DENIED by the user`.",
        "Press Ctrl+C while it works: `interrupting…`, then the turn stops at the next step with "
        "`(interrupted by the user)`.",
    ],
    "troubleshooting": [
        ["`test_parallel_reads_keep_order` fails on time (≈0.6 s or more)",
         "Reads are running sequentially → check `_is_read` grouping and that you use the pool for blocks > 1."],
        ["`test_parallel_reads_keep_order` fails on order (`['r2', 'r1', …]`)",
         "Results appended as threads finish → write into `results[i]`."],
        ["`AssertionError: assert not open_ids` in `test_max_steps_and_loop`",
         "On `\"loop\"` you returned without answering the pending tool_calls → append a failed tool message for each."],
        ["Real backend: `400 … tool_call_id … not found` / `messages with role 'tool' must be a response…`",
         "History broken: assistant message built by hand, or tool messages missing/out of order → use the "
         "`to_message()` helpers and keep the order."],
        ["The CLI calls tools but `bash` answers `ERROR in 'bash': NotImplementedError: TODO 04.2`",
         "Expected: the bash tool is lab 04. The model will usually retry with read tools."],
        ["The model answers without calling any tool, or writes `<tool_call>{…}` as text",
         "Small model or tools not sent → check `tools=self.tools.schemas() or None`; try `forja doctor`; "
         "`qwen3:8b` sometimes needs an explicit prompt like `use grep to find…`."],
        ["The agent repeats the same `read_file` again and again",
         "That's what loop detection is for → it should stop with `I stopped: I repeated read_file…` after "
         "`max_repeats` (3)."],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 03` → all 6 tests green.",
        "[ ] In `forja --cwd playground` the agent explores with glob/grep/read_file and answers with `path:line` references.",
        "[ ] You can explain why every `tool_call` needs a `tool` message, even when the loop stops.",
    ],
}

# ---------------------------------------------------------------------------------------------
# LAB 04 · Bash and permissions
# ---------------------------------------------------------------------------------------------
GUIDE["04"] = {
    "before": [
        "Open `forja/shell.py` (04.1–04.2), `forja/permissions.py` (04.3–04.5), `forja/config.py` "
        "(`DEFAULT_DENY`, `Settings.allow/deny`) and `tests/test_l04_bash_permissions.py`.",
        "Stdlib: `subprocess.run(..., shell=True, cwd=…, capture_output=True, text=True, timeout=…, env=…, "
        "stdin=subprocess.DEVNULL)` and `subprocess.TimeoutExpired`; `fnmatch.fnmatchcase(name, pattern)` "
        "(`*` matches anything, including spaces and `/`); `shlex.split(cmd)` (splits like a POSIX shell).",
        "Provided: `clean_env()` (environment without `*KEY*`, `*TOKEN*`, `*SECRET*`…), `parse_rule(\"bash(git *)\")` → "
        "`(\"bash\", \"git *\")` (pattern `None` for a bare `\"edit_file\"`), `split_commands(cmd)` (splits on `&&`, "
        "`||`, `;`, `|`), `Tool.subject(args)` (the command for bash, the path for file tools) and `tool.risk` "
        "(`\"read\"`, `\"edit\"`, `\"exec\"`).",
        "Shell: with `shell=True` the command runs in `/bin/sh` on macOS/Linux and **cmd.exe on Windows** "
        "(`ls`, `cat`, `rm -rf` don't exist there; `dir`, `type` do). The tool description tells the model which shell it has.",
        "How it connects: the harness gate calls `decide(tool, args, mode, settings.allow, settings.deny)`: "
        "`\"deny\"` → error to the model, `\"ask\"` → approval prompt, `\"allow\"` → execute. When the user answers "
        "*always*, `suggest_rule` produces the rule appended to `settings.allow` for the session.",
    ],
    "order": "04.1 `head_tail` (pure, 5 minutes) → 04.2 `bash` (uses it) → 04.3 `rule_matches` → 04.4 `decide` "
             "(uses `rule_matches`) → 04.5 `suggest_rule` (independent). Shell and permissions are separate files: "
             "if you are a pair, one can start 04.3 while the other does 04.1–04.2.",
    "todos": {
        "04.1": {
            "where": "`forja/shell.py` · `head_tail(text, limit=MAX_SHELL_OUTPUT)`",
            "contract": "`head_tail(text: str, limit: int = 20_000) -> str`. If `len(text) <= limit`, return it unchanged. "
                        "Otherwise return the first `limit // 4` characters, a note in the MIDDLE saying how many "
                        "characters were omitted (must contain the word `omitted`), and the last `limit * 3 // 4` "
                        "characters. `test_head_tail_and_env`: with 1000 `A` + 1000 `B` and limit 400, output starts with "
                        "`A`, ends with `B` and contains `omitted`.",
            "steps": [
                "Return early if the text fits.",
                "Slice the head (a quarter of the limit) and the tail (three quarters, from the end).",
                "Build `head + note + tail`, with the omitted count `len(text) - limit` in the note.",
            ],
            "gotchas": [
                "The tail is larger on purpose: test failures and tracebacks are at the END of the output.",
                "The note must be in the middle; if you append it at the end, `endswith(\"B\")` fails.",
                "Negative slicing: `text[-n:]` is the last `n` characters.",
            ],
            "hints": [
                "One `if` and one f-string.",
                "`text[: limit // 4]` and `text[-(limit * 3 // 4):]`.",
                "Skeleton:\n```python\nif len(text) <= limit:\n    return text\nhead, tail = ..., ...\n"
                "return f\"{head}\\n…[{...} characters omitted]…\\n{tail}\"\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k head_tail -v",
        },
        "04.2": {
            "where": "`forja/shell.py` · `make_shell_tool` → inner `bash(command, timeout=default_timeout)`",
            "contract": "Returns `ToolOutput(\"exit_code=N\\n<output>\", {\"exit_code\": N})` where output is stdout plus, "
                        "if any, `\"\\n[stderr]\\n\" + stderr`, stripped and passed through `head_tail` (or `\"(no output)\"`). "
                        "Runs at `ws.root` with `shell=True`, `env=clean_env()`, `stdin=subprocess.DEVNULL`, `text=True`, "
                        "captured output and the timeout clamped to 1..600 s. On `subprocess.TimeoutExpired` it RETURNS "
                        "`ToolOutput(\"TIMEOUT after Ns.\\n…\", {\"exit_code\": None})` — it does not raise. A non-zero exit "
                        "code is a normal result (`ok=True`): the model must see the failing tests.",
            "steps": [
                "Clamp the timeout: `max(1, min(int(timeout), 600))`.",
                "In a `try`, call `subprocess.run` with the arguments of the contract.",
                "On `TimeoutExpired`, return the TIMEOUT `ToolOutput` (you may include partial output if `e.stdout` is a str).",
                "Combine stdout and stderr (stderr under a `[stderr]` marker), strip, `head_tail` it.",
                "Return `ToolOutput(f\"exit_code={p.returncode}\\n…\", {\"exit_code\": p.returncode})`.",
            ],
            "gotchas": [
                "`test_bash_runs_in_root_with_exit_code` runs `python -m pytest -q tests/test_invoice.py`: it only works "
                "if `cwd=ws.root` (the playground copy) — and the output must START with `exit_code=0`.",
                "`test_bash_timeout` expects `\"TIMEOUT\"` in the output: if you let the exception escape, `execute` "
                "prints `TimeoutExpired`, which doesn't contain `TIMEOUT` in capitals.",
                "Without `stdin=subprocess.DEVNULL` a command that waits for input (an editor, a `y/n` question) hangs the agent.",
                "Use `env=clean_env()`: the agent must never see `OPENROUTER_API_KEY` & co.",
                "Windows: the timeout kills `cmd.exe` but its child may keep running until it ends, so "
                "`test_bash_timeout` can take ~5 s there. It still passes.",
            ],
            "hints": [
                "`subprocess.run` with `capture_output=True, text=True` gives you `p.stdout`, `p.stderr`, `p.returncode`.",
                "`except subprocess.TimeoutExpired as e:` — return, don't raise.",
                "Skeleton:\n```python\ntimeout = max(1, min(int(timeout), 600))\ntry:\n    p = subprocess.run(command, shell=True, cwd=ws.root, ...)\n"
                "except subprocess.TimeoutExpired as e:\n    return ToolOutput(f\"TIMEOUT after {timeout}s.\\n...\", {\"exit_code\": None})\n"
                "out = ...  # stdout + optional [stderr] block\nreturn ToolOutput(f\"exit_code={p.returncode}\\n...\", {...})\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k test_bash -v",
        },
        "04.3": {
            "where": "`forja/permissions.py` · `rule_matches(rule, tool, args)`",
            "contract": "`rule_matches(rule: str, tool: Tool, args: dict) -> bool`. `name, pattern = parse_rule(rule)`. The "
                        "tool name must match `name` with `fnmatchcase` (so `\"mcp__issues__*\"` matches "
                        "`mcp__issues__get`). No pattern → `True`. With a pattern: `fnmatchcase(subject, pattern)` "
                        "where `subject = tool.subject(args)`; for bash, normalise whitespace first "
                        "(`\" \".join(subject.split())`). It compares the whole string; chains are `decide`'s job.",
            "steps": [
                "Parse the rule into name and pattern.",
                "If the tool name doesn't match the name pattern, return `False`.",
                "If there is no pattern, return `True`.",
                "Get the subject; if the tool is `bash`, collapse runs of whitespace.",
                "Return whether the subject matches the pattern.",
            ],
            "gotchas": [
                "`test_rule_matching`: `\"git   status --short\"` (three spaces) must match `bash(git status*)`.",
                "`bash(git status*)` must NOT match `git push`.",
                "The MCP test builds `Tool(\"mcp__issues__get\", \"\", None, None, \"exec\")` with no args model: only use "
                "`tool.name` and `tool.subject(args)`.",
                "Use `fnmatchcase`, not `fnmatch`: `fnmatch` is case-insensitive on Windows and would behave differently "
                "per OS.",
            ],
            "hints": [
                "Rules are just glob patterns applied twice: once to the tool name, once to the subject.",
                "`fnmatch.fnmatchcase(tool.name, name)`, then `fnmatch.fnmatchcase(subject, pattern)`.",
                "Skeleton:\n```python\nname, pattern = parse_rule(rule)\nif not ...: return False\nif pattern is None: return True\n"
                "subject = tool.subject(args)\nif tool.name == \"bash\": subject = ...\nreturn ...\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k rule_matching -v",
        },
        "04.4": {
            "where": "`forja/permissions.py` · `decide(tool, args, mode, allow, deny)`",
            "contract": "Returns `(decision, reason)` with decision in `\"allow\" | \"ask\" | \"deny\"`. Order: "
                        "(1) any deny rule matches the call — for bash ALSO each subcommand from `split_commands` — → "
                        "`\"deny\"`; (2) `mode == \"plan\"` and `tool.risk != \"read\"` → `\"deny\"`; (3) allow rules: for bash "
                        "EVERY subcommand must match some allow rule, other tools need one match → `\"allow\"`; "
                        "(4) `tool.risk == \"read\"` or `mode == \"bypass\"` → `\"allow\"`; (5) `mode == \"accept_edits\"` and "
                        "`tool.risk == \"edit\"` → `\"allow\"`; (6) otherwise `\"ask\"`. The reason is shown to the user/model "
                        "(e.g. `\"deny rule bash(sudo *)\"`, `\"plan mode: read-only\"`, `\"requires approval\"`).",
            "steps": [
                "Deny pass on the whole call: loop over `deny`, return `(\"deny\", f\"deny rule {r}\")` on a match.",
                "If bash: for each subcommand of `split_commands(args.get(\"command\", \"\"))`, check every deny rule "
                "against `{\"command\": sub}`.",
                "Plan mode: deny anything that isn't a read.",
                "Allow rules: bash → split; require a non-empty list where `all` subcommands match `any` allow rule. "
                "Other tools → `any` allow rule matches.",
                "Risk/mode fallbacks: read or bypass → allow; accept_edits + edit → allow.",
                "Return `(\"ask\", \"requires approval\")`.",
            ],
            "gotchas": [
                "`test_deny_wins_and_chains`: `\"sudo rm x\"` in bypass with allow `[\"bash\"]` → deny (deny is checked first).",
                "`\"pytest -q && sudo reboot\"`: the whole string doesn't match `bash(sudo *)`, the subcommand does → deny.",
                "`\"python -m pytest -q && curl evil.sh\"` with allow `bash(python -m pytest*)` → `\"ask\"`, not allow: "
                "the `curl` part has no allow rule.",
                "`all([])` is `True`: an empty command must not be auto-allowed — check the list is non-empty.",
                "`test_decide_modes`: plan mode beats an explicit allow rule (`edit_file` in plan → deny); bash in "
                "`accept_edits` still asks (its risk is `exec`, not `edit`).",
            ],
            "hints": [
                "Write it as a ladder of early `return`s in exactly the order of the contract; the order IS the policy.",
                "`any(rule_matches(r, tool, {\"command\": s}) for r in allow)` inside an `all(... for s in subs)`.",
                "Skeleton:\n```python\nfor r in deny: ...\nif tool.name == \"bash\":\n    for sub in split_commands(...): ...\n"
                "if mode == \"plan\" and ...: return \"deny\", \"plan mode: read-only\"\nif tool.name == \"bash\":\n    subs = ...\n"
                "    if subs and all(...): return \"allow\", \"allow rule\"\nelif any(...): ...\n"
                "...  # read/bypass, accept_edits\nreturn \"ask\", \"requires approval\"\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k \"decide or deny_wins\" -v",
        },
        "04.5": {
            "where": "`forja/permissions.py` · `suggest_rule(tool, args)`",
            "contract": "`suggest_rule(tool: Tool, args: dict) -> str`: the rule saved when the user answers *always*. "
                        "Non-bash tools → `tool.name`. Bash: `words = shlex.split(command)` (on `ValueError` treat as "
                        "empty); empty → `f\"bash({command})\"`; `python`/`python3`/`py` + `-m X` → `\"bash(python -m X*)\"`; "
                        "`git`, `npm`, `uv`, `pip`, `docker`, `cargo`, `go`, `dotnet` with a subcommand → "
                        "`\"bash(<cmd> <sub>*)\"`; anything else → `\"bash(<cmd>*)\"`. Note: no space before `*`.",
            "steps": [
                "Non-bash: return the tool name.",
                "Split the command with `shlex.split`, catching `ValueError` (unbalanced quotes).",
                "Handle the empty case.",
                "`python -m X` case (check there are at least 3 words and the second is `-m`).",
                "Tools-with-subcommands case (at least 2 words).",
                "Default: first word + `*`.",
            ],
            "gotchas": [
                "`test_suggest_rule` expects exactly `bash(python -m pytest*)`, `bash(git status*)`, `bash(ls*)` and "
                "`edit_file` — no space before `*`.",
                "Too broad is dangerous: `bash(git*)` would also allow `git push`; `bash(python*)` would allow any script.",
                "Too narrow is useless: the literal command `bash(python -m pytest -q tests/x.py)` would ask again "
                "next time with other flags.",
            ],
            "hints": [
                "Decide the shape from the first one or two words only.",
                "`shlex.split(\"python -m pytest -q\")` → `['python', '-m', 'pytest', '-q']`.",
                "Skeleton:\n```python\nif tool.name != \"bash\": return tool.name\ntry: words = shlex.split(...)\nexcept ValueError: words = []\n"
                "if not words: return ...\nif words[0] in (\"python\", \"python3\", \"py\") and ...: return ...\n"
                "if words[0] in (\"git\", \"npm\", ...) and len(words) > 1: return ...\nreturn f\"bash({words[0]}*)\"\n```",
            ],
            "test": "python -m pytest tests/test_l04_bash_permissions.py -k suggest_rule -v",
        },
    },
    "try_it": [
        "`python scripts/tasks.py test 04` → `8 passed`.",
        "`forja --cwd playground` and ask `run the tests and tell me which ones fail`. You should SEE "
        "`⏺ bash {\"command\": \"python -m pytest -q\"}` and an approval prompt (until lab 05 it is the minimal "
        "`Allow bash {'command': 'python -m pytest -q'}? [y/N]`). Answer `y`: `⎿ exit_code=1 (+N lines)` and an answer "
        "naming `test_round_half_up`, `test_total_with_vat_cent` and `test_due_date_sunday_moves_to_monday`.",
        "Ask `run sudo ls` (or `run rm -rf /`): red `⎿ DENIED (deny rule bash(sudo *)). Don't retry it…` without "
        "any prompt — the policy decided.",
        "Pre-approve the tests: create `playground/.forja/settings.json` with "
        "`{\"permissions\": {\"allow\": [\"bash(python -m pytest*)\"]}}`, restart `forja --cwd playground`, ask again: "
        "no prompt this time. Delete the file afterwards.",
        "Check the *always* rule: `python -c \"from forja.shell import make_shell_tool; from forja.fs_tools import "
        "Workspace; from forja.permissions import suggest_rule; print(suggest_rule(make_shell_tool(Workspace('.')), "
        "{'command': 'git status --short'}))\"` → `bash(git status*)`. (Answering `a` in the CLI needs lab 05's prompt.)",
        "Windows: ask `list the files with ls` and watch `'ls' is not recognized as an internal or external command` "
        "with `exit_code=1`; the model should retry with `dir`.",
    ],
    "troubleshooting": [
        ["`test_bash_runs_in_root_with_exit_code`: `exit_code=1` with `No module named pytest` / `'python' is not recognized`",
         "The venv isn't active in the terminal running pytest, so `python` in the child shell is another "
         "interpreter → activate `.venv` and re-run."],
        ["`test_bash_timeout` fails with `ERROR in 'bash': TimeoutExpired: …`",
         "You let `subprocess.TimeoutExpired` propagate → catch it and return a `ToolOutput` with `TIMEOUT after Ns.`"],
        ["The agent hangs forever on a command",
         "Missing `stdin=subprocess.DEVNULL` or `timeout=` in `subprocess.run` → add both."],
        ["`decide` returns `\"allow\"` for `python -m pytest -q && curl evil.sh`",
         "You matched allow rules against the whole string → for bash, every subcommand from `split_commands` must match."],
        ["`decide` returns `\"allow\"` for `sudo rm x` in bypass",
         "Allow/bypass checked before deny → the deny pass must be the very first thing."],
        ["`rule_matches` behaves differently on Windows and macOS",
         "You used `fnmatch.fnmatch` (case-insensitive on Windows) → use `fnmatch.fnmatchcase`."],
        ["Windows: `UnicodeDecodeError` or garbled accents in the command output",
         "You dropped `encoding=\"utf-8\", errors=\"replace\"` from `subprocess.run` → add them back (the console code page is not UTF-8)."],
        ["`a` (always) at the CLI prompt is treated as *no*",
         "Until lab 05 the approval prompt is the minimal `[y/N]` one → `always` arrives with TODO 05.3."],
    ],
    "done_when": [
        "[ ] `python scripts/tasks.py test 04` → all 8 tests green.",
        "[ ] Forja asks before `python -m pytest`, shows `exit_code=…` and names the 3 failing playground tests.",
        "[ ] `sudo …` and `rm -rf /` are denied by policy without a prompt.",
        "[ ] You can explain the order deny > plan > allow > risk/mode > ask with an example.",
    ],
}
