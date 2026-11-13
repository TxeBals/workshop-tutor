"""Step-by-step student guidance (English) for labs 09-12 and the final project.

Schema: see the other guide modules. All strings are Markdown.
"""
from __future__ import annotations

GUIDE: dict[str, dict] = {
    # =====================================================================================
    "09": {
        "before": [
            "Open `forja/subagents.py` (your TODOs) and keep `forja/agent.py` (lab 03) and `forja/harness.py` "
            "(`_build_registry`) open next to it. The harness already calls `subagents.load_profiles(root / \".forja\" / \"agents\")` "
            "and registers `subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events)`: "
            "you only fill in the two functions.",
            "What you reuse: `Agent(llm, tools, execute=..., events=..., max_steps=...)` and its `run(messages) -> AgentResult` "
            "(fields `answer`, `stop_reason`, `steps`, `tool_calls`, `usage`). `ToolRegistry.subset(names)` builds a registry "
            "with only the names that exist (unknown names are silently skipped).",
            "Stdlib / libs used: `Path.glob(\"*.md\")`, `Path.read_text(encoding=\"utf-8\")`, the precompiled regex "
            "`FRONTMATTER` (group 1 = YAML between the `---` lines, group 2 = body) and `yaml.safe_load` (returns a dict, or "
            "`None` for empty YAML). `tools: read_file, grep` in YAML is a *string*; `tools: [read_file, grep]` is a *list*.",
            "Key idea: the subagent starts from a NEW `messages` list (system + user prompt). It never sees the main history; "
            "the main agent only gets back the string your `task` tool returns. Every subagent tool call still goes through "
            "`execute` = the harness gate (hooks, permissions, approvals, checkpoints).",
            "Look at `examples/project/.forja/agents/reviewer.md` for a real profile (it has `tools` and `max_steps`).",
        ],
        "order": "Do 09.1 first: it is pure parsing, has its own isolated test (`test_load_profiles`) and the harness needs it to "
                 "build the list of subagents that appears in the `task` tool description. Then 09.2, whose tests "
                 "(`test_task_isolated_context`, `test_unknown_subagent`) run through the full harness, so labs 02-04 must already pass.",
        "todos": {
            "09.1": {
                "where": "`forja/subagents.py` · `load_profiles(folder: Path) -> dict[str, AgentProfile]`",
                "contract": "Receives the agents folder (it may not exist). Returns a dict `name -> AgentProfile` that ALWAYS contains "
                            "the built-in `explore` profile (start from a copy of `BUILTIN`, never mutate `BUILTIN` itself). For each "
                            "`*.md` file with valid frontmatter that has both `name` and `description`, add "
                            "`AgentProfile(name, description, system=<body stripped>, tools=<list[str]>, max_steps=<int, default 25>)`. "
                            "Files without frontmatter or missing `name`/`description` are skipped silently. The test checks: "
                            "`set(p) == {\"explore\", \"reviewer\"}`, `tools == [\"read_file\", \"grep\"]` (from the string `read_file, grep`), "
                            "`max_steps == 5`, `system == \"You are a reviewer.\"`, and that a missing folder returns exactly `BUILTIN`.",
                "steps": [
                    "Create `profiles = dict(BUILTIN)`; if the folder is not a directory, return it right away.",
                    "Loop over the `*.md` files in a stable order (`sorted`). Read each one as UTF-8 and apply `FRONTMATTER.match`.",
                    "No match → skip. Match → `yaml.safe_load(group 1)`, and treat `None` as `{}`.",
                    "Skip if `name` or `description` is missing or empty.",
                    "Normalise `tools`: default `[\"read_file\", \"grep\", \"glob\"]`; if it is a string, split on commas and strip each "
                    "item, dropping empties; if it is already a list, keep it.",
                    "Build the profile: the body (group 2) `.strip()`ped is the system prompt; `max_steps` via `int(...)` with default 25. "
                    "Store it under its `name` (a file can override `explore` if it uses that name).",
                ],
                "gotchas": [
                    "Returning `BUILTIN` itself and then adding to it mutates the module constant: the next test (`load_profiles(missing) == BUILTIN`) "
                    "or the next harness instance will see stale profiles. Copy it.",
                    "`tools: read_file, grep` is the string `'read_file, grep'`. Forgetting to split gives `['r','e','a',...]` if you iterate it, "
                    "or a single unknown tool name — and `subset()` silently drops unknown names, so the subagent ends up with NO tools.",
                    "`system` must be the body *without* the frontmatter and stripped: the test compares it exactly.",
                    "`yaml.safe_load` on a frontmatter that only contains comments returns `None`: `.get` on it raises `AttributeError`.",
                ],
                "hints": [
                    "It is the same \"frontmatter + body\" parsing you will do again for skills in lab 10. The regex is already compiled for you.",
                    "`m = FRONTMATTER.match(text)`; `meta = yaml.safe_load(m.group(1)) or {}`; `m.group(2).strip()` is the system prompt. "
                    "`isinstance(tools, str)` tells you when to split.",
                    "```python\nprofiles = dict(BUILTIN)\nif not folder.is_dir(): return profiles\nfor f in sorted(folder.glob(\"*.md\")):\n"
                    "    m = ...            # FRONTMATTER.match on the file text\n    if not m: continue\n    meta = ...         # yaml, never None\n"
                    "    if <missing name or description>: continue\n    tools = ...        # default list; split 'a, b' strings\n"
                    "    profiles[meta[\"name\"]] = AgentProfile(...)\nreturn profiles\n```",
                ],
                "test": "python -m pytest tests/test_l09_subagents.py -k load_profiles -v",
            },
            "09.2": {
                "where": "`forja/subagents.py` · `make_task_tool(...)` → inner tool `task(description, prompt, subagent_type=\"explore\") -> str`",
                "contract": "`make_task_tool` is already written except the body of `task`. Inside `task`: look up `profiles[subagent_type]`; "
                            "if it does not exist raise `ValueError` whose message contains `unknown` and lists the available names (the registry turns "
                            "it into a failed tool result; `test_unknown_subagent` checks `\"unknown\"` is in it). Build the subagent's registry with "
                            "`parent_tools.subset(...)` using the profile's tools MINUS `\"task\"`. Create an `Agent` with the same `llm`, that sub-registry, "
                            "`execute=execute`, `max_steps=prof.max_steps` and `events=events_factory(prof.name)` if a factory was given, else `Events()`. "
                            "Run it on a BRAND-NEW list `[{\"role\": \"system\", \"content\": prof.system}, {\"role\": \"user\", \"content\": prompt}]`. "
                            "Return a header that contains `subagent <name>` (the test looks for `\"subagent explore\"`), e.g. "
                            "`[subagent explore · <description> · N steps · M tools · <stop_reason>]`, then a newline and `res.answer`. "
                            "The test also checks that the subagent's first LLM call had exactly 2 messages starting with the explore system prompt, "
                            "that it was offered exactly `{read_file, grep, glob}`, and that the main history only contains ONE tool message (`task`).",
                "steps": [
                    "Look up the profile; if missing, `raise ValueError(f\"unknown subagent: ... Available: ...\")`.",
                    "Compute the allowed tool names: the profile's `tools` without `\"task\"` (no recursion).",
                    "`sub_tools = parent_tools.subset(those names)`.",
                    "Pick the events object: `events_factory(prof.name)` when the factory is not `None`, otherwise `Events()`. "
                    "In the CLI this factory prints the subagent's tool calls with the `[explore]` prefix.",
                    "Wrap `execute` in a small `sub_execute(call)`: if `call.name` is not in `sub_tools.tools`, return "
                    "`ToolResult(call.id, call.name, False, \"ERROR: tool '...' is not available to subagent '...'\")`; otherwise delegate to "
                    "`execute` (or `sub_tools.execute` when `execute` is `None`). The schema list only *offers* tools; the model can still call others.",
                    "Create the `Agent` (same `llm`, `execute=sub_execute`, `max_steps=prof.max_steps`) and call `run` with a NEW two-message list.",
                    "Format and return the header line + the subagent's `answer` (use `res.steps`, `res.tool_calls`, `res.stop_reason`).",
                ],
                "gotchas": [
                    "Reusing or copying the parent's history: the subagent must start clean (`len(messages) == 2` on its first call).",
                    "Passing `parent_tools` instead of the subset: the subagent would get `write_file`, `bash`, `task`… and "
                    "`test_task_isolated_context` fails on the tool set.",
                    "Forgetting to route through `execute`: the subagent would bypass the gate (no permissions, no hooks, no checkpoints).",
                    "Trusting the offered tool list: `test_subagent_cannot_use_tools_outside_its_profile` makes the model call `write_file` "
                    "from `explore`; your wrapper must refuse it and the file must not exist.",
                    "The same `FakeLLM` serves main agent and subagent in call order: if your `task` makes an extra LLM call (or none), "
                    "every scripted reply shifts and the assertions fail in confusing ways.",
                    "Do not touch `task.description`: it is set after the function and includes the catalogue the model reads to choose a subagent.",
                ],
                "hints": [
                    "The whole subagent is just lab 03's `Agent` with a smaller registry and a fresh message list.",
                    "`parent_tools.subset([t for t in prof.tools if t != \"task\"])`; `Agent(llm, sub_tools, execute=sub_execute, max_steps=..., events=...)`; "
                    "`res = agent.run(messages)`.",
                    "```python\nprof = profiles.get(subagent_type)\nif prof is None: raise ValueError(...)  # 'unknown', list names\n"
                    "sub_tools = ...                 # subset, never 'task'\ndef sub_execute(call): ...     # refuse names not in sub_tools.tools\nevents = ...                    # factory(name) or Events()\n"
                    "agent = Agent(...)\nres = agent.run([...])         # system + user ONLY\nreturn f\"[subagent {prof.name} · ...]\\n{res.answer}\"\n```",
                ],
                "test": "python -m pytest tests/test_l09_subagents.py -k \"task_isolated or unknown_subagent or outside_its_profile\" -v",
            },
        },
        "try_it": [
            "Copy the example project config into the playground. macOS/Linux: `cp -r examples/project/.forja playground/` · "
            "PowerShell: `Copy-Item -Recurse examples\\project\\.forja playground\\.forja` · cmd: `xcopy /E /I examples\\project\\.forja playground\\.forja`.",
            "`forja --cwd playground`, then `/tools`: you should see `task [read]` at the end of the list, and no "
            "`subagents: lab 09 pending` note at startup.",
            "Type `use a subagent to find every place where amounts are rounded`. Expected: `⏺ task …`, then indented lines "
            "`  [explore] ⏺ grep …` / `  [explore] ⏺ read_file …` (the subagent's calls; its text is not streamed), and finally the "
            "main agent's answer listing `path:line` locations.",
            "Run `/context` before and after: the main context grows by a few hundred tokens, not by the size of every file the subagent read.",
            "Edit something in `playground/invoices/` by hand, then: `ask the reviewer subagent to review my uncommitted changes`. "
            "You should see `  [reviewer] ⏺ bash git diff …` (allowed by `bash(git diff*)` in settings) and a review with numbered sections.",
        ],
        "troubleshooting": [
            ["`test_task_isolated_context` fails with `StopIteration` / FakeLLM 'no more responses'",
             "Your `task` calls the LLM a different number of times (e.g. you ran `agent.run` twice, or the main loop from lab 03 is broken) → one `Agent.run` per task call; run `tests/test_l03_agent.py` first."],
            ["Assertion on `{t['function']['name'] ...} == {'read_file','grep','glob'}`",
             "You passed the whole parent registry, or included `task` → use `parent_tools.subset(...)` with `task` filtered out."],
            ["Subagent has no tools / answers without reading anything",
             "In 09.1 `tools` was not split (string `'read_file, grep'`), so `subset()` dropped every name → split on commas and strip."],
            ["`reviewer` does not appear in the `task` description / 'unknown subagent: reviewer'",
             "The profile file has no `---` frontmatter on the very first line, or lacks `description` → fix the file; profiles are read from `<project>/.forja/agents/`, so check you copied `.forja` into `playground/`."],
            ["No `[explore]` prefix in the CLI, subagent calls look like main calls",
             "You ignored `events_factory` and always used `Events()` (then you see nothing) or passed the main events → use `events_factory(prof.name)` when it is not `None`."],
            ["The small model never delegates",
             "8B models often prefer doing it themselves → ask explicitly ('use a subagent…'); the `task` description is all it reads to decide."],
            ["Windows: `cp -r` fails in cmd.exe",
             "`cp` only exists in PowerShell (as an alias) → use `xcopy /E /I examples\\project\\.forja playground\\.forja` in cmd."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 09` → 3 passed.",
            "[ ] In the CLI you see `[explore]`-prefixed tool calls and `/context` barely grows after a delegated search.",
            "[ ] The `reviewer` profile from `.forja/agents/` is listed in the `task` tool description and can be invoked by name.",
        ],
    },
    # =====================================================================================
    "10": {
        "before": [
            "Three small files, three ideas: `forja/hooks.py` (10.1, 10.2), `forja/skills.py` (10.3, 10.4) and `forja/mcp_tools.py` (10.5). "
            "The harness (`forja/harness.py`) already calls them: `self.hooks.run(\"PreToolUse\", {...}, tool.name)` in `gate`, "
            "`\"PostToolUse\"` after executing, `\"UserPromptSubmit\"` and `\"Stop\"` in `turn`; `skills.discover_skills(home/.forja/skills, root/.forja/skills)` "
            "at startup; `mcp_tool_name` inside `connect_servers`.",
            "Hooks API: `subprocess.run(cmd, shell=True, cwd=..., input=<json str>, capture_output=True, text=True, timeout=...)` returns a "
            "`CompletedProcess` with `returncode`, `stdout`, `stderr`; it raises `subprocess.TimeoutExpired` on timeout. `re.fullmatch(pattern, s)` "
            "matches the WHOLE string (so `edit_file|write_file` works as an alternation). With `shell=True` the shell is cmd.exe on Windows and "
            "`/bin/sh` on macOS/Linux.",
            "Exit-code convention (same as commercial agents): `0` = OK (stdout may be useful context), `2` = BLOCK (stderr, or stdout if empty, is the "
            "message for the model), anything else = hook error (recorded, never blocks). `HookOutcome` has `block`, `message`, `context`, `errors`.",
            "Skills reuse the frontmatter parsing you wrote in 09.1 (`FRONTMATTER` + `yaml.safe_load`). `catalog()` is already written: it only needs "
            "`Skill.name` and `Skill.description`.",
            "Look at `examples/project/.forja/settings.json` and `examples/project/.forja/hooks/*.py`: a real PreToolUse hook reads the event with "
            "`json.load(sys.stdin)` and exits 2 with a message on stderr.",
        ],
        "order": "10.1 → 10.2 (one test covers both: `test_hook_matching_and_exit_codes`; then `test_hooks_in_harness` checks the integration), "
                 "then 10.5 (one line, quick win), then 10.3 → 10.4 (both checked by `test_skills`). Leave `test_mcp_end_to_end` for last: it "
                 "starts a real MCP server subprocess and needs labs 02-04 working.",
        "todos": {
            "10.1": {
                "where": "`forja/hooks.py` · `HookRunner.matching(event: str, tool_name: str | None = None) -> list[dict]`",
                "contract": "Returns, in config order, the hook dicts from `self.config.get(event, [])` that apply. A hook WITHOUT `matcher` always applies. "
                            "A hook WITH `matcher` applies only if `tool_name` is not `None` and `re.fullmatch(matcher, tool_name)` matches. Unknown event → `[]`. "
                            "Test: `[h.get(\"matcher\") for h in runner.matching(\"PreToolUse\", \"bash\")] == [\"bash\", None]`, "
                            "`len(matching(\"PreToolUse\", \"write_file\")) == 2`, `matching(\"Stop\") == []`.",
                "steps": [
                    "Get the list for the event with `.get(event, [])` (missing events are normal).",
                    "For each hook read `h.get(\"matcher\")`.",
                    "No matcher → keep it.",
                    "Matcher but no `tool_name` (events like `Stop`/`UserPromptSubmit`) → skip it.",
                    "Matcher and `tool_name` → keep it only if `re.fullmatch` succeeds. Preserve the original order.",
                ],
                "gotchas": [
                    "`re.match`/`re.search` instead of `fullmatch`: `bash` would also match `bash_tool`, and `edit_file|write_file` with `re.match` "
                    "accepts prefixes. The test expects exactly 2 hooks for `write_file`.",
                    "`self.config[event]` raises `KeyError` for events nobody configured — `matching(\"Stop\")` must return `[]`.",
                    "Matchers are REGEX, not globs: in settings write `mcp__issues__.*`, not `mcp__issues__*` (that is the syntax of permission rules).",
                ],
                "hints": [
                    "Three cases per hook: no matcher, matcher without tool name, matcher with tool name.",
                    "`re.fullmatch(matcher, tool_name)` returns a match object or `None`.",
                    "```python\nout = []\nfor h in self.config.get(event, []):\n    matcher = h.get(\"matcher\")\n"
                    "    if matcher and <no tool_name or no fullmatch>:\n        continue\n    out.append(h)\nreturn out\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k hook_matching -v",
            },
            "10.2": {
                "where": "`forja/hooks.py` · `HookRunner.run(event: str, payload: dict, tool_name: str | None = None) -> HookOutcome`",
                "contract": "Serialises `{\"hook_event_name\": event, \"cwd\": str(self.cwd), **payload}` to JSON (`ensure_ascii=False, default=str`) and sends it on "
                            "stdin to EVERY matching hook (they all run, even after a block). Per hook: exit 2 → `block=True` and append `stderr` (or `stdout`, or "
                            "a default text) stripped + newline to `message`; exit 0 → append non-empty `stdout` stripped to `context`; other codes → append a "
                            "description to `errors`; `TimeoutExpired` → append to `errors` and continue. Use `h.get(\"timeout\", self.timeout)`. At the end strip "
                            "`message` and `context`. Tests: PreToolUse with hooks exiting 2 / 0 / 1 → `block` and `message == \"no\"` and `len(errors) == 1`; "
                            "UserPromptSubmit printing `ctx:` + prompt → `context == \"ctx:hello\"`, not blocked, 1 error. In the harness "
                            "(`test_hooks_in_harness`): `BLOCKED by hook` in the tool result and the Stop hook forces one more round.",
                "steps": [
                    "Create an empty `HookOutcome()` and build the JSON string once.",
                    "For each hook in `self.matching(event, tool_name)` call `subprocess.run` with `h[\"command\"]`, `shell=True`, `cwd=self.cwd`, "
                    "the JSON as `input`, `capture_output=True`, `text=True` and the timeout.",
                    "Wrap the call in `try/except subprocess.TimeoutExpired` → record an error, `continue`.",
                    "Branch on `returncode`: 2 → block + message; 0 → context if stdout has text; else → errors (include the code and a slice of stderr).",
                    "After the loop, `.strip()` `message` and `context` so trailing newlines don't break the exact comparisons.",
                ],
                "gotchas": [
                    "Stopping at the first blocking hook: the test config has a third hook (exit 1) that must still run, giving `len(errors) == 1`.",
                    "Forgetting `text=True`: `input` must then be bytes and `stdout` comes back as bytes → `TypeError` or `b'no'` != `'no'`.",
                    "Not stripping: `message` would be `'no\\n'`; the test compares with `== \"no\"`.",
                    "Without `cwd=self.cwd` relative hook commands (`python .forja/hooks/x.py`) and the test's Stop hook (`pathlib.Path('DONE')`) look in the wrong folder.",
                    "Windows: the test builds commands as `\"C:/path/python.exe\" -c \"...\"`; that only works with `shell=True` (cmd.exe parses the quotes).",
                ],
                "hints": [
                    "Run each command once with the event on stdin and look only at `returncode`, `stdout`, `stderr`.",
                    "`p = subprocess.run(h[\"command\"], shell=True, cwd=self.cwd, input=data, capture_output=True, text=True, timeout=h.get(\"timeout\", self.timeout))`.",
                    "```python\noutcome = HookOutcome()\ndata = json.dumps({...}, ensure_ascii=False, default=str)\nfor h in self.matching(event, tool_name):\n"
                    "    try: p = subprocess.run(...)\n    except subprocess.TimeoutExpired: outcome.errors.append(...); continue\n"
                    "    if p.returncode == 2: ...          # block, message += stderr or stdout\n    elif p.returncode == 0: ...        # context += stdout\n"
                    "    else: ...                          # errors\n# strip message and context\nreturn outcome\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k hook -v",
            },
            "10.3": {
                "where": "`forja/skills.py` · `discover_skills(*folders: Path) -> dict[str, Skill]`",
                "contract": "For each folder that exists, look at `<folder>/*/SKILL.md` (sorted). Parse frontmatter; keep only files with `name` and `description`. "
                            "Store `Skill(name, description_normalised, path_to_SKILL.md)` under `name`; later folders overwrite earlier ones (the harness passes user "
                            "folder first, project folder second, so project wins). Normalise the description's whitespace: the test's YAML description spans two lines "
                            "and must become exactly `\"How to make commits here.\"`. A `SKILL.md` without frontmatter is skipped (`list(sk) == [\"commits\"]`).",
                "steps": [
                    "Start with an empty dict; loop over the folders in the order given and skip non-directories.",
                    "`sorted(folder.glob(\"*/SKILL.md\"))` — one level of subfolders, exactly that file name.",
                    "Match `FRONTMATTER`; no match → skip. Load the YAML (guard against `None`).",
                    "Require `name` and `description`; collapse all whitespace in the description into single spaces.",
                    "Store `Skill(...)` with the path of the `SKILL.md` file itself (10.4 reads it again).",
                ],
                "gotchas": [
                    "A multi-line YAML value (`description: How to make\\n  commits here.`) is folded by YAML, but be explicit: `\" \".join(str(d).split())` "
                    "guarantees single spaces and no newline, which `catalog()` needs to produce `- commits: How to make commits here.`.",
                    "Returning early when the first folder is missing: the user folder (`~/.forja/skills`) usually doesn't exist — skip it and keep going.",
                    "Storing the folder instead of the `SKILL.md` path: 10.4 then fails to read the body.",
                ],
                "hints": [
                    "This is 09.1 again with a different glob and a different dataclass.",
                    "`folder.glob(\"*/SKILL.md\")`, `FRONTMATTER.match(f.read_text(encoding=\"utf-8\"))`, `\" \".join(str(meta[\"description\"]).split())`.",
                    "```python\nout = {}\nfor folder in folders:\n    if not folder.is_dir(): continue\n    for f in sorted(folder.glob(...)):\n"
                    "        m = ...; meta = ...            # None-safe\n        if <valid>:\n            out[meta[\"name\"]] = Skill(..., ..., f)\nreturn out\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k skills -v",
            },
            "10.4": {
                "where": "`forja/skills.py` · `make_skill_tool(skills)` → inner tool `skill(name: str) -> str`",
                "contract": "Unknown name → `ValueError` listing the available skills (or `none`). Known name → re-read `skill.path`, strip the frontmatter, and return "
                            "`# Skill: <name>`, a line with the folder (`(folder: <path.parent>)`, so the model can find scripts/templates next to `SKILL.md`), a blank "
                            "line and the stripped BODY. The test checks the result contains `Use conventional commits.` and does NOT contain `---`. Do not change "
                            "the docstring: it becomes the tool description and the `Args:` section documents `name`.",
                "steps": [
                    "Look up `skills.get(name)`; if missing, raise `ValueError` with the list of names.",
                    "Read the file again (the body is not cached: that is progressive disclosure).",
                    "Apply `FRONTMATTER.match` and keep group 2 stripped; if somehow it doesn't match, fall back to the whole text.",
                    "Return the header, the folder line and the body.",
                ],
                "gotchas": [
                    "Returning the whole file: the frontmatter `---` lines leak into the result and the test fails on `\"---\" not in out`.",
                    "Returning an error string instead of raising: it still \"works\", but the tool result is marked ok and the model can't tell it failed.",
                    "If `test_skills` fails on `\"commits\" in llm.calls[0][\"messages\"][0][\"content\"]`, the catalogue is not reaching the system prompt: that needs lab 06's "
                    "`build_system_prompt` to include `skills_catalog`.",
                ],
                "hints": [
                    "The catalogue (descriptions only) is already in the prompt; this tool returns the part that was left out.",
                    "`m = FRONTMATTER.match(s.path.read_text(encoding=\"utf-8\"))`; `m.group(2).strip()`.",
                    "```python\ns = skills.get(name)\nif s is None:\n    raise ValueError(f\"unknown skill: {name}. Available: ...\")\n"
                    "body = ...    # text without frontmatter\nreturn f\"# Skill: {s.name}\\n(folder: ...)\\n\\n{body}\"\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k skills -v",
            },
            "10.5": {
                "where": "`forja/mcp_tools.py` · `mcp_tool_name(server: str, tool: str) -> str`",
                "contract": "Returns `mcp__<server>__<tool>` where every character outside `[a-zA-Z0-9_]` in server AND tool is replaced with `_` (use the precompiled "
                            "`NAME_RE`). Tests: `(\"issues\", \"get_issue\") -> \"mcp__issues__get_issue\"`, `(\"my-wiki\", \"search.docs\") -> \"mcp__my_wiki__search_docs\"`. "
                            "`connect_servers` (already written) uses it to rename every MCP tool; MCP tools get risk `exec`, so they go through permissions.",
                "steps": [
                    "Sanitise the server name with `NAME_RE.sub(\"_\", ...)`.",
                    "Sanitise the tool name the same way.",
                    "Join with the `mcp__` prefix and a double underscore between them.",
                ],
                "gotchas": [
                    "Single underscores (`mcp_issues_get_issue`): permission rules like `mcp__issues__*` in `settings.json` then never match.",
                    "Sanitising only the tool name: a server called `my-wiki` produces an invalid tool name that some models/servers reject.",
                ],
                "hints": [
                    "One line with an f-string.",
                    "`NAME_RE.sub(\"_\", server)` replaces every forbidden character.",
                    "```python\nreturn f\"mcp__{...}__{...}\"\n```",
                ],
                "test": "python -m pytest tests/test_l10_extensions.py -k mcp -v",
            },
        },
        "try_it": [
            "Make sure `playground/.forja/` exists (copied in lab 09). The MCP server path in `settings.json` (`../examples/mcp/issues_server.py`) "
            "is resolved from the project root (`playground/`), so `forja --cwd playground` from the repo root works. If the server fails you get "
            "a startup note `· MCP 'issues': …` and no MCP tools.",
            "`/tools` → you should see `mcp__issues__list_issues`, `mcp__issues__get_issue`, `mcp__issues__comment_issue` with `[exec]`, and `skill [read]`.",
            "`list the open issues, fix #12 and comment on the issue what you changed`. Expected: `⏺ mcp__issues__list_issues` (no approval prompt: `mcp__issues__*` is "
            "in `allow`), reads/edits in `invoices/amounts.py`, a PostToolUse compile check after each edit, and finally `mcp__issues__comment_issue`.",
            "Watch the Stop hook (`.forja/hooks/stop_tests.py`): it only runs when there are uncommitted changes in the project (git), so plain questions are not affected. "
            "If the agent edited files and says it is done while tests are red, you will see it keep working (a `[Stop hook] You are not done yet…` user message is injected "
            "with the pytest tail). It gives up after 3 extra rounds.",
            "`commit following the repo's convention` → the first call should be `⏺ skill conventional-commits`, then `git status`/`git diff`, then a commit "
            "message like `fix(amounts): …`. (You will be asked to approve `git commit`: it is not in `allow`.)",
            "Try the PreToolUse hook: `run cat .env` → the result shows `BLOCKED by hook: Command blocked by policy: it may expose secrets…`.",
        ],
        "troubleshooting": [
            ["`test_hook_matching_and_exit_codes`: `assert out.message == 'no'` fails with `'no\\n'`",
             "You didn't strip → `.strip()` the accumulated `message`/`context` at the end."],
            ["`len(out.errors) == 1` fails (0 errors)",
             "You `break` after the blocking hook, so the exit-1 hook never runs → run every matching hook."],
            ["`TypeError: a bytes-like object is required` in `subprocess.run`",
             "Missing `text=True` → add it (input/stdout/stderr become `str`)."],
            ["Windows: hook test fails with `'C:/…/python.exe' is not recognized` or quoting errors",
             "Run without `shell=True` and cmd.exe never parses the quoted command → keep `shell=True` and pass the command as a single string."],
            ["Answers end with `[Stop hook] You are not done yet…` although you only asked a question",
             "`stop_tests.py` runs the tests whenever there are uncommitted changes under `playground/` (e.g. a half-finished fix from an earlier lab) → finish the fix, or `python scripts/tasks.py reset`. Outside git it always runs."],
            ["No `mcp__issues__*` tools; startup note `· MCP 'issues': …`",
             "The server failed to start → check the path is relative to the project root (`playground/`), that `mcp` is installed (`pip show mcp`), and run the server by hand: `python examples/mcp/issues_server.py`."],
            ["PostToolUse/PreToolUse hook never fires for MCP tools",
             "The matcher is a regex with `fullmatch` → use `mcp__issues__.*`, not the glob `mcp__issues__*`."],
            ["The model never calls `skill`",
             "Small models ignore catalogues → make the skill description say WHEN to load it ('Load it before running git commit') and mention it in the prompt."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 10` → 5 passed (including `test_mcp_end_to_end`).",
            "[ ] In the CLI: `cat .env` is blocked by the PreToolUse hook, and the Stop hook makes the agent continue while tests are red.",
            "[ ] `/tools` lists `skill` and the `mcp__issues__*` tools, and the agent loads `conventional-commits` before committing.",
        ],
    },
    # =====================================================================================
    "11": {
        "before": [
            "Open `forja/session.py`. Two independent classes: `Transcript` (11.1, 11.2: a JSONL file per session in `<project>/.forja/sessions/<id>.jsonl`) and "
            "`Checkpoints` (11.3, 11.4: an in-memory stack of turns, each `{Path: original bytes | None}`). `mark_compaction` and `list_sessions` are already written: "
            "read them, they tell you the line format (`{\"ts\": ..., \"message\": m}` and `{\"ts\": ..., \"compacted\": [...]}`).",
            "How the harness uses them: at the end of `Forja.turn` it calls `self.transcript.append(*self.history[start:])` (only the NEW messages); `resume(id)` "
            "calls `Transcript.load(folder, id)`. `Forja.turn` calls `self.checkpoints.begin_turn()`, and `Workspace` calls `checkpoints.before_write(path)` right "
            "BEFORE `write_file`/`edit_file` touch a file (see `forja/fs_tools.py`). `/undo` calls `Checkpoints.undo()`.",
            "Stdlib: `json.dumps(obj, ensure_ascii=False)`, `json.loads(line)`, `Path.open(\"a\", encoding=\"utf-8\")` (append mode), `Path.read_bytes()` / "
            "`write_bytes()` (bytes, so encodings and line endings are restored exactly), `Path.unlink(missing_ok=True)`, `Path.mkdir(parents=True, exist_ok=True)`.",
            "Limit to keep in mind: only file tools create checkpoints. Whatever `bash` does (`rm`, `pip install`, `sed -i`) cannot be undone.",
        ],
        "order": "11.1 and 11.2 together (one round-trip test: `test_transcript_roundtrip`), then 11.3 and 11.4 together (`test_checkpoints`). Finish with "
                 "`test_harness_resume_and_undo`, which exercises everything through the real harness (needs labs 02-04 for `edit_file` in `accept_edits`).",
        "todos": {
            "11.1": {
                "where": "`forja/session.py` · `Transcript.append(self, *messages: dict) -> None`",
                "contract": "Creates `self.folder` if needed, opens `self.path` in APPEND mode (UTF-8) and writes one line per message: "
                            "`json.dumps({\"ts\": <time.time() rounded>, \"message\": m}, ensure_ascii=False) + \"\\n\"`. Never rewrites earlier lines. "
                            "Called several times on the same file (the test appends 2 messages, then 1 more, then a compaction marker, then 1 more).",
                "steps": [
                    "`self.folder.mkdir(parents=True, exist_ok=True)`.",
                    "Open `self.path` with mode `\"a\"` and `encoding=\"utf-8\"` in a `with` block.",
                    "For each message write one JSON object per line with keys `ts` and `message`.",
                ],
                "gotchas": [
                    "Mode `\"w\"` truncates the file: after the second `append` only the last message survives and the round-trip fails.",
                    "Forgetting the trailing `\"\\n\"`: two records on one line → `json.JSONDecodeError: Extra data` in `load`.",
                    "Windows: without `encoding=\"utf-8\"` the default codepage (cp1252) breaks on `€`, `→` or accented text in messages.",
                    "Use the key `message` exactly: `list_sessions` (already written) reads `.get(\"message\")`.",
                ],
                "hints": [
                    "JSON Lines = one complete JSON document per line, only ever appended.",
                    "`with self.path.open(\"a\", encoding=\"utf-8\") as f:` then `f.write(json.dumps({...}, ensure_ascii=False) + \"\\n\")`.",
                    "```python\nself.folder.mkdir(...)\nwith self.path.open(...) as f:\n    for m in messages:\n        f.write(...)   # {'ts': ..., 'message': m} + newline\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k transcript -v",
            },
            "11.2": {
                "where": "`forja/session.py` · `Transcript.load(folder: Path, session_id: str) -> list[dict]` (staticmethod)",
                "contract": "Reads `<folder>/<session_id>.jsonl`; if it doesn't exist raise `FileNotFoundError`. Rebuilds the history line by line: a record with "
                            "`compacted` REPLACES the whole history with that list; a record with `message` is appended. Skip blank lines. Test: after "
                            "`[hello, how are you, second]` + compaction `[[Summary] x]` + `continuing`, the result is `[\"[Summary] x\", \"continuing\"]`. "
                            "The harness test checks `app2.history == app.history` after `resume`, so messages must come back unchanged (including `tool_calls`).",
                "steps": [
                    "Build the path `folder / f\"{session_id}.jsonl\"`; raise `FileNotFoundError` if it is not a file.",
                    "Start with an empty list and read the file as UTF-8, line by line.",
                    "Skip empty lines; `json.loads` the rest.",
                    "If the record has `compacted` → replace the history with a copy of that list; otherwise append `record[\"message\"]`.",
                    "Return the history.",
                ],
                "gotchas": [
                    "Appending the compacted list instead of replacing: you get `hello, how are you, second, [Summary] x, continuing`.",
                    "Checking `if \"message\" in rec` first and ignoring the rest silently drops compaction markers — check `compacted` first.",
                    "A trailing empty line makes `json.loads(\"\")` raise — skip blank lines.",
                ],
                "hints": [
                    "The file is an event log; replay it to rebuild the state.",
                    "`for line in p.read_text(encoding=\"utf-8\").splitlines():` and `rec = json.loads(line)`; branch on `\"compacted\" in rec`.",
                    "```python\np = folder / f\"{session_id}.jsonl\"\nif not p.is_file(): raise FileNotFoundError(...)\nhistory = []\nfor line in ...:\n"
                    "    if not line.strip(): continue\n    rec = ...\n    if \"compacted\" in rec: history = ...\n    else: history.append(...)\nreturn history\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k transcript -v",
            },
            "11.3": {
                "where": "`forja/session.py` · `Checkpoints.before_write(self, path: Path) -> None`",
                "contract": "Records the ORIGINAL state of `path` in the current (last) turn of `self.stack`: `path.read_bytes()` if it exists, `None` if it doesn't. "
                            "Only the FIRST time a given path is seen in that turn (later writes in the same turn must not overwrite the original). If there is no "
                            "turn yet (`self.stack` empty), call `self.begin_turn()` first. Test: `a.txt` written twice in one turn must undo to `\"original\"`; "
                            "`new.txt` created in the turn must be deleted on undo.",
                "steps": [
                    "If `self.stack` is empty, `self.begin_turn()`.",
                    "Take the current turn dict: `self.stack[-1]`.",
                    "If `path` is already a key, do nothing.",
                    "Otherwise store `path.read_bytes()` if `path.exists()`, else `None`.",
                ],
                "gotchas": [
                    "Overwriting the stored value on every call: after `v1` → `v2` the undo would restore `v1`, not `original`.",
                    "Storing text (`read_text`) instead of bytes: CRLF line endings on Windows and non-UTF-8 files don't round-trip exactly.",
                    "Calling `begin_turn()` unconditionally here: every write would open a new turn and `/undo` would only revert the last write.",
                ],
                "hints": [
                    "`None` means \"this file did not exist before\" — undo will delete it.",
                    "`turn = self.stack[-1]`; `if path not in turn: turn[path] = ...`.",
                    "```python\nif not self.stack: ...\nturn = self.stack[-1]\nif path not in turn:\n    turn[path] = ...  # bytes or None\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k checkpoints -v",
            },
            "11.4": {
                "where": "`forja/session.py` · `Checkpoints.undo(self) -> list[Path]`",
                "contract": "Discards EMPTY turns from the top of the stack (turns where nothing was written), then pops the last non-empty turn and restores every "
                            "file in it: original bytes → write them back (creating parent folders); `None` → delete the file (no error if already gone). Returns "
                            "the restored paths SORTED. Nothing to undo → `[]`. Test: an empty turn on top is skipped, both files are restored, and a second "
                            "`undo()` returns `[]`. The CLI's `/undo` prints `restored: <paths>` or `nothing to undo`.",
                "steps": [
                    "While the stack is not empty and its last turn is empty, pop it.",
                    "If the stack is now empty, return `[]`.",
                    "Pop the last turn.",
                    "For each `(path, original)`: if `original is None` → `unlink(missing_ok=True)`; else `mkdir` the parent and `write_bytes(original)`.",
                    "Return `sorted(...)` of the turn's paths.",
                ],
                "gotchas": [
                    "Not skipping empty turns: the harness calls `begin_turn()` on EVERY turn, so a question after an edit would make `/undo` say 'nothing to undo'.",
                    "Peeking (`self.stack[-1]`) instead of popping: a second `undo()` would restore the same turn again instead of returning `[]`.",
                    "Writing back a file whose folder was deleted meanwhile → `FileNotFoundError`; create parents first.",
                ],
                "hints": [
                    "Think of the stack as a list of snapshots of only the files each turn touched.",
                    "`while self.stack and not self.stack[-1]: self.stack.pop()`.",
                    "```python\n# drop empty turns from the end\nif not self.stack: return []\nturn = self.stack.pop()\nfor path, original in turn.items():\n"
                    "    if original is None: ...   # delete\n    else: ...                  # mkdir parent + write bytes\nreturn sorted(turn)\n```",
                ],
                "test": "python -m pytest tests/test_l11_sessions.py -k \"checkpoints or resume_and_undo\" -v",
            },
        },
        "try_it": [
            "`forja --cwd playground --mode accept_edits` and type `change the default due-date period to 60 days`. Expected: an `edit_file invoices/dates.py` with a diff "
            "panel (`days: int = 30` → `60`), no approval prompt (accept_edits).",
            "`/undo` → `restored: invoices/dates.py`. Check the file: it says `30` again. `/undo` once more → `nothing to undo`.",
            "Ask a plain question (`what does due_date do?`), make another edit, ask another question, then `/undo`: it still reverts the last turn WITH changes (empty turns are skipped).",
            "`/sessions` → lines like `20261103-143012-a1b2  change the default due-date period to 60 days`. Look at the raw file: macOS/Linux "
            "`cat playground/.forja/sessions/<id>.jsonl` · PowerShell `Get-Content playground\\.forja\\sessions\\<id>.jsonl` — one JSON object per line.",
            "`/exit`, then `forja --cwd playground --resume <id>` and ask `what did you change before?` → the agent answers from the restored history.",
            "Note what is NOT undone: ask the agent to `create a file tmp.txt using bash` and `/undo` → `tmp.txt` is still there (`/undo` says `nothing to undo`, or reverts an OLDER edit turn instead). Clean up with `python scripts/tasks.py reset` if needed.",
        ],
        "troubleshooting": [
            ["`json.decoder.JSONDecodeError: Extra data` in `load`",
             "Two records on the same line → add `\"\\n\"` after each `json.dumps` in `append`."],
            ["Round-trip returns only the last message",
             "You opened the file with `\"w\"` → use append mode `\"a\"`."],
            ["`test_checkpoints`: `a.txt` restores to `v1` instead of `original`",
             "`before_write` overwrites the stored original → only store it the first time the path appears in the turn."],
            ["`/undo` always says `nothing to undo` after a follow-up question",
             "Empty turns on top of the stack are not skipped → pop empty turns before popping the real one."],
            ["`test_harness_resume_and_undo`: `app2.history == app.history` fails",
             "Messages are being changed on the way (e.g. you saved `str(m)` or only `content`) → dump the whole dict as JSON and load it back unchanged."],
            ["`UnicodeEncodeError` / garbled text in `.jsonl` on Windows",
             "Default codepage is not UTF-8 → pass `encoding=\"utf-8\"` when opening and reading, keep `ensure_ascii=False`."],
            ["`--resume` says the session does not exist",
             "Sessions live in `<project>/.forja/sessions/` → resume with the same `--cwd` you used when creating it, and copy the id from `/sessions`."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 11` → 3 passed.",
            "[ ] `/undo` restores a file edited by the agent and deletes a file it created, without git.",
            "[ ] `forja --cwd playground --resume <id>` continues the previous conversation.",
        ],
    },
    # =====================================================================================
    "12": {
        "before": [
            "Open `forja/evals.py` (your TODOs: `grade` and `summarize`) and `evals/tasks.yaml` (the tasks). Already written for you: `load_tasks`, `snapshot(root)` "
            "(dict `relative path -> sha1`, ignoring `.forja`, `.git`, `__pycache__`, `.pytest_cache`), `norm(s)` (lowercase + strip accents) and `run_task`, which copies "
            "`playground/` into a temp dir, runs ONE headless turn in `bypass` mode, then calls your `grade(task, work, answer, before, repo_root)`.",
            "The runner is `evals/run_evals.py` (via `python scripts/tasks.py evals ...`): flags `--model`, `--backend`, `--repeat N`, `--only <id>`, `--max-steps`, `--config <.forja folder>` (use your settings, hooks, skills and subagents in every task), `--mcp` and `--label <suffix>` for the report name. It prints one "
            "`PASS`/`FAIL` line per run, calls your `summarize` and writes `out/evals_<model>.json` (`/` and `:` in the model name become `_`).",
            "Stdlib: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, timeout=...)` and `subprocess.TimeoutExpired`; `shutil.copy(src, dst)`; "
            "`statistics.mean`; `dataclasses.asdict`. `TaskResult` fields: `id, passed, reason, steps, tool_calls, tokens, seconds, stop_reason, answer`.",
            "A task's `check` dict may contain: `command` (exit 0 = pass, optional `timeout`, default 120 s), `hidden` (`{repo-relative source: workdir-relative destination}`, "
            "copied AFTER the agent finished), `answer_contains` (list of strings), `forbid_changes` (bool).",
            "Evals use YOUR whole agent (labs 01-11). `test_run_task_pass_and_fail` drives `read_file`, `edit_file` and `bash` through the harness, so those labs must pass.",
        ],
        "order": "12.1 first (`test_grade_answer_and_forbid_changes`, `test_hidden_tests_copied_after`, then `test_run_task_pass_and_fail`), because `run_task` and the "
                 "runner depend on it. 12.2 is independent arithmetic (`test_summarize`). Then run real evals: start with `--only vat_question` (fast, read-only).",
        "todos": {
            "12.1": {
                "where": "`forja/evals.py` · `grade(task, workdir, answer, before, repo_root) -> tuple[bool, str]`",
                "contract": "Applies the checks in THIS order and returns at the first failure: (1) `forbid_changes` and `snapshot(workdir) != before` → `(False, <reason containing "
                            "'modified'>)`; (2) `answer_contains`: every string, compared with `norm()` on both sides, must be in the answer, else `(False, <reason listing the "
                            "missing ones>)`; (3) copy each `hidden` file from `repo_root / src` to `workdir / dst` (create parent folders); (4) if `command`: run it in `workdir` "
                            "with `shell=True`; timeout → `(False, ...)`; non-zero exit → `(False, <reason containing 'failed'> + the last 3 lines of stdout+stderr)`. "
                            "All good → exactly `(True, \"ok\")` (the test compares the tuple).",
                "steps": [
                    "Read `chk = task.check`.",
                    "If `chk.get(\"forbid_changes\")` and the current snapshot differs from `before`, fail with a 'modified files…' reason.",
                    "Collect the `answer_contains` strings whose `norm(str(s))` is not in `norm(answer)`; if any, fail and list them.",
                    "For each `(src, dst)` in `chk.get(\"hidden\") or {}`: create `(workdir / dst).parent` and `shutil.copy(repo_root / src, workdir / dst)`.",
                    "If there is a `command`, run it in `workdir` with `capture_output=True, text=True, timeout=chk.get(\"timeout\", 120)`; handle `TimeoutExpired`.",
                    "On non-zero exit, join the last 3 non-empty-trimmed lines of `stdout + stderr` into the reason (e.g. `\"check failed: \" + \" | \".join(tail)`).",
                    "Return `(True, \"ok\")`.",
                ],
                "gotchas": [
                    "Copying `hidden` files BEFORE the `forbid_changes` check: your own copy counts as a change. The order matters.",
                    "Not using `norm()`: `\"VAT\"` must match `\"the vat\"` in the test answer (case-insensitive; accents are stripped too).",
                    "Copying hidden tests only when the command passes: `test_hidden_tests_copied_after` checks the file exists even though the check fails.",
                    "Forgetting `cwd=workdir`: the command runs against the REAL playground (or the repo root) and the result is meaningless.",
                    "Windows: `command` strings like `python -m pytest -q` need `python` on PATH → activate the venv in the terminal where you run evals.",
                ],
                "hints": [
                    "Cheap checks first, then the side effects (copy files), then the expensive one (run the command).",
                    "`missing = [s for s in chk.get(\"answer_contains\", []) if norm(str(s)) not in norm(answer)]`; "
                    "`tail = (p.stdout + p.stderr).strip().splitlines()[-3:]`.",
                    "```python\nchk = task.check\nif chk.get(\"forbid_changes\") and ...: return False, \"modified files in a read-only task\"\n"
                    "missing = ...\nif missing: return False, f\"the answer is missing: {missing}\"\nfor src, dst in ...: ...   # mkdir + copy\n"
                    "if chk.get(\"command\"):\n    try: p = subprocess.run(...)\n    except subprocess.TimeoutExpired: return False, ...\n"
                    "    if p.returncode != 0: return False, \"check failed: \" + ...\nreturn True, \"ok\"\n```",
                ],
                "test": "python -m pytest tests/test_l12_evals.py -k \"grade or hidden or run_task\" -v",
            },
            "12.2": {
                "where": "`forja/evals.py` · `summarize(results: list[TaskResult], model: str) -> dict`",
                "contract": "Returns a dict with keys: `model`; `runs` = number of results; `pass_rate` = passed / runs rounded to 3 decimals; `per_task` = `{task id: pass rate "
                            "rounded to 2}` (grouping repetitions of the same id); `avg_steps` and `avg_seconds` = means rounded to 1 decimal (0 if there are no results); "
                            "`total_tokens` = sum of tokens; `results` = `[asdict(r) for r in results]`. Test: 3 results → `pass_rate == 0.667`, "
                            "`per_task == {\"a\": 0.5, \"b\": 1.0}`, `avg_steps == 4.0`, `total_tokens == 350`, `len(results) == 3`.",
                "steps": [
                    "Group the results by `r.id` into a dict of lists (`setdefault` is handy).",
                    "Compute the global pass rate; protect against division by zero for an empty list.",
                    "Compute the per-task pass rate from each group.",
                    "Compute the means of `steps` and `seconds` (guard empty input), and the token sum.",
                    "Assemble the dict with exactly the keys above; `results` via `asdict`.",
                ],
                "gotchas": [
                    "Rounding: `pass_rate` 3 decimals (`0.667`), `per_task` 2 decimals, averages 1 decimal. The test uses `==`.",
                    "`statistics.mean([])` raises `StatisticsError` → guard empty lists (the runner with a wrong `--only` gives zero results).",
                    "`sum(r.passed for r in ...)` works because `True == 1`; don't count `reason == \"ok\"` instead.",
                    "`run_evals.py` reads `rep[\"pass_rate\"]`, `rep[\"avg_steps\"]`, `rep[\"avg_seconds\"]`, `rep[\"total_tokens\"]`, `rep[\"per_task\"]`, `rep[\"model\"]` — "
                    "a typo in a key name crashes the runner after all the (slow) runs.",
                ],
                "hints": [
                    "Group, then aggregate. Everything is a sum, a count or a mean.",
                    "`by_task.setdefault(r.id, []).append(r)`; `round(statistics.mean(r.steps for r in results), 1)`.",
                    "```python\nby_task = {}\nfor r in results: ...\nn = len(results) or 1\nreturn {\n    \"model\": model, \"runs\": ...,\n"
                    "    \"pass_rate\": round(..., 3),\n    \"per_task\": {k: round(..., 2) for k, v in by_task.items()},\n"
                    "    \"avg_steps\": ..., \"avg_seconds\": ..., \"total_tokens\": ...,\n    \"results\": [asdict(r) for r in results],\n}\n```",
                ],
                "test": "python -m pytest tests/test_l12_evals.py -k summarize -v",
            },
        },
        "try_it": [
            "`python scripts/tasks.py evals --only vat_question` (read-only, fastest). Expected: `» …run_evals.py --only vat_question`, then a line like "
            "`PASS  vat_question           18.4s   4 steps` (or `FAIL … the answer is missing: ['calculate_vat']`), then the summary "
            "`qwen3:8b: pass_rate 100% · 4.0 steps · 18.4s/task · 9123 tokens`, `per task: {...}` and `-> out/evals_qwen3_8b.json`.",
            "`python scripts/tasks.py evals --only fix_rounding` → a FAIL line shows the last 3 lines of pytest output as the reason. Note that your real `playground/` is never modified.",
            "`python scripts/tasks.py evals --repeat 3` (all 5 tasks × 3; this takes a while on a laptop — start it and keep reading). Look at `per_task`: which tasks are flaky (0.33, 0.67)?",
            "If you have a second model: `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (or the classroom server via `--backend openai_compat`). "
            "Open both `out/evals_*.json` files and compare `pass_rate`, `avg_steps`, `avg_seconds`, `total_tokens`.",
            "Inspect a failure: in the JSON, `results[i].answer` (first 500 chars) and `stop_reason` (`max_steps`, `loop`, `error`…) usually tell you why.",
        ],
        "troubleshooting": [
            ["`grade(...) == (True, 'ok')` fails with `(False, 'modified files…')` in the forbid test",
             "You copied hidden files or ran the command before the `forbid_changes` check, or compared against a fresh snapshot → check `snapshot(workdir) != before` first."],
            ["`test_grade_answer_and_forbid_changes`: 'the answer is missing: [VAT]'",
             "Comparison is case-sensitive → apply `norm()` to both the expected string and the answer."],
            ["`test_hidden_tests_copied_after`: hidden file does not exist",
             "You return before copying, or only copy on success → copy hidden files before running the command, whatever the result."],
            ["`test_run_task_pass_and_fail`: `ok.passed` is False / `steps != 5`",
             "Earlier labs are broken in your harness (edit_file, bash, permissions in bypass) → run `python scripts/tasks.py test 03` and `test 04`; or `catchup 12` if you are short of time."],
            ["Every real eval FAILs with `EXCEPTION …` or `stop_reason: error`",
             "The backend is not reachable or the model is not pulled → `forja doctor`, `ollama list`, check `.env`."],
            ["Windows: `check failed: 'python' is not recognized…`",
             "The check command runs through cmd.exe and the venv isn't active in that terminal → `.venv\\Scripts\\activate` before running evals."],
            ["`StatisticsError: mean requires at least one data point`",
             "`--only` with an unknown id gives zero results → guard empty lists in `summarize` (and check the id spelling)."],
            ["Results vary a lot between runs",
             "Models are not deterministic → always compare with `--repeat 3` or more and look at `per_task`, not at a single run."],
        ],
        "done_when": [
            "[ ] `python scripts/tasks.py test 12` → 5 passed.",
            "[ ] You have at least one `out/evals_<model>.json` produced with `--repeat 3`.",
            "[ ] You can state, with numbers (pass rate, steps, seconds, tokens), which model you would use for which tasks.",
        ],
        # ---------------------------------------------------------------------------------
        "capstone": {
            "intro": "Final project (16:00–17:00): customise Forja for the way YOU work and prove it with numbers. Five deliverables, each small. Work in `playground/` "
                     "(or a real repo of yours for 1–4) and keep a short `NOTES` list of what you changed for the 3-minute demo. Budget: ~10 min per deliverable, 15 min for the evals.",
            "deliverables": {
                "1_agents_md": {
                    "title": "AGENTS.md: global preferences + one per repo",
                    "where": "Global: `~/.forja/AGENTS.md` (macOS/Linux) · `%USERPROFILE%\\.forja\\AGENTS.md` (Windows; in PowerShell `$HOME\\.forja\\AGENTS.md`). "
                             "Project: `AGENTS.md` (or `FORJA.md`) at the root of the repo; files are collected from the filesystem root down to `--cwd`, global first, "
                             "so the closest one is the most specific.",
                    "steps": [
                        "Create the folder: macOS/Linux `mkdir -p ~/.forja` · PowerShell `New-Item -ItemType Directory -Force $HOME\\.forja`.",
                        "Write 5–10 bullets of PERSONAL preferences (language, verbosity, test habits). Keep it short: it is sent on every turn.",
                        "In a real repo of yours, write `AGENTS.md` with: how to run tests, the build/lint command, conventions, and things that must never be done.",
                        "Verify it is loaded: start `forja --cwd <repo>` and ask `which instructions are you following?` — it should quote both layers "
                        "(the prompt contains `## User global instructions` and `## Project instructions (AGENTS.md)`).",
                    ],
                    "template": "```markdown\n# AGENTS.md — <project>\n\n- Stack: <language/version>, <framework>.\n- Tests: `<command>`. Run them after every code change.\n"
                                "- Lint/format: `<command>`.\n- Conventions: <naming, error handling, logging>.\n- Never: <edit generated files / touch migrations / change public APIs without asking>.\n"
                                "- When unsure, ask before large refactors.\n```",
                    "pitfall": "Evals run with a temporary home, so `~/.forja/AGENTS.md` is NOT used by `run_evals.py`; only `playground/AGENTS.md` (copied with the project) is. "
                               "If you want to measure an instruction change, put it in `playground/AGENTS.md`.",
                },
                "2_skill": {
                    "title": "A team skill",
                    "where": "`<project>/.forja/skills/<skill-name>/SKILL.md` (project) or `~/.forja/skills/<skill-name>/SKILL.md` (personal; project wins on name clash). "
                             "Extra files (scripts, templates) can live in the same folder: the `skill` tool tells the model the folder path.",
                    "steps": [
                        "Pick a procedure you explain repeatedly: release checklist, code-review rubric, how to add an endpoint, DB migration steps…",
                        "Write the frontmatter: `name` (kebab-case, = folder name) and a `description` that says WHAT it is and WHEN to load it.",
                        "Write the body as numbered steps with exact commands. Keep it under ~60 lines.",
                        "Check discovery: `/tools` shows `skill`, and a prompt that needs it produces `⏺ skill <name>` as an early call.",
                    ],
                    "template": "```markdown\n---\nname: add-endpoint\ndescription: How to add a REST endpoint in this repo (routing, validation, tests). Load it before creating or changing an endpoint.\n---\n"
                                "# Adding an endpoint\n\n1. Route in `<file>`; handler in `<folder>/<name>.py`.\n2. Validate input with <library>; return <error format> on failure.\n"
                                "3. Add a test in `tests/<...>` covering success and one error.\n4. Run `<test command>` before finishing.\n```",
                    "pitfall": "If the model never loads it, the description is too vague. Say when: 'Load it before …'. See `examples/project/.forja/skills/conventional-commits/SKILL.md`.",
                },
                "3_hook": {
                    "title": "A hook that guarantees something you now ask for politely",
                    "where": "Script in `<project>/.forja/hooks/<name>.py`; registration in `<project>/.forja/settings.json` under `hooks.<Event>` "
                             "(`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`). Commands run with `cwd` = project root through the shell (cmd.exe on Windows).",
                    "steps": [
                        "Choose the event: block something → `PreToolUse`; give feedback after an edit (lint, compile, format check) → `PostToolUse`; "
                        "'don't finish until X' → `Stop`; inject context or filter prompts → `UserPromptSubmit`.",
                        "Write the script: read the event with `json.load(sys.stdin)` (`tool_name`, `tool_input`, and `tool_response` for PostToolUse; `prompt` for UserPromptSubmit), "
                        "decide, print the reason to stderr and `sys.exit(2)` to block/feed back, `sys.exit(0)` otherwise.",
                        "Register it with a regex `matcher` (full match on the tool name, e.g. `edit_file|write_file`, `bash`, `mcp__issues__.*`); omit the matcher to apply to all.",
                        "Test the script alone first. macOS/Linux: `echo '{\"tool_name\":\"bash\",\"tool_input\":{\"command\":\"cat .env\"}}' | python .forja/hooks/<name>.py; echo $?` · "
                        "PowerShell: `'{\"tool_name\":\"bash\",\"tool_input\":{\"command\":\"cat .env\"}}' | python .forja\\hooks\\<name>.py; $LASTEXITCODE`.",
                        "Then trigger it from the CLI and check you see `BLOCKED by hook: …` (Pre) or `[hook PostToolUse] …` in the tool result (Post).",
                    ],
                    "template": "```python\n\"\"\"PostToolUse (edit_file|write_file): <what it guarantees>. Exit 2 = feedback to the model.\"\"\"\nimport json, subprocess, sys\n\n"
                                "event = json.load(sys.stdin)\npath = event.get(\"tool_input\", {}).get(\"path\", \"\")\nif not path.endswith(\".py\"):\n    sys.exit(0)\n"
                                "p = subprocess.run([\"ruff\", \"check\", \"--quiet\", path], capture_output=True, text=True)\nif p.returncode != 0:\n"
                                "    print(f\"Lint errors in {path}:\\n{p.stdout[-2000:]}\", file=sys.stderr)\n    sys.exit(2)\nsys.exit(0)\n```\n"
                                "```json\n\"hooks\": {\"PostToolUse\": [{\"matcher\": \"edit_file|write_file\", \"command\": \"python .forja/hooks/lint.py\", \"timeout\": 30}]}\n```",
                    "pitfall": "Exit 1 does NOT block (it is recorded as a hook error and ignored): use exit 2. A slow `Stop` hook runs on every final answer — keep it fast (`-x`, a subset of tests).",
                },
                "4_subagent": {
                    "title": "A specialised subagent profile",
                    "where": "`<project>/.forja/agents/<name>.md`. Frontmatter keys read by `load_profiles`: `name`, `description` (required), `tools` (list or `a, b` string; "
                             "default `read_file, grep, glob`), `max_steps` (default 25). Valid tool names: `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `bash`, `todo_write`, "
                             "`skill`, `mcp__<server>__<tool>` (`task` is always removed). The body is its system prompt.",
                    "steps": [
                        "Pick a narrow job where a clean context helps: test-failure triage, security review, docs writer, dependency auditor, `tester` that only runs pytest.",
                        "Give it the MINIMUM tools. Read-only roles: `read_file, grep, glob` (+ `bash` if it needs `git diff`/pytest, and add matching `allow` rules in settings).",
                        "Write the description from the main agent's point of view: what it does and when to delegate to it.",
                        "Write the body: role, method (numbered), and the exact output format you want back (it is all the main agent will see).",
                        "Check: the profile appears in the `task` tool description; ask `use the <name> subagent to …` and look for `[<name>]`-prefixed calls.",
                    ],
                    "template": "```markdown\n---\nname: tester\ndescription: Runs the test suite and explains failures with the likely cause and file:line. Use it after code changes or when tests fail.\n"
                                "tools: read_file, grep, glob, bash\nmax_steps: 15\n---\nYou are a test triage specialist. Only run `python -m pytest` commands with bash; never modify files.\n"
                                "1. Run the suite (`python -m pytest -q -x`).\n2. For each failure, read the test and the code under test.\n"
                                "Answer with: a one-line verdict, then per failure `test name — cause — path:line — suggested fix (1 sentence)`.\n```",
                    "pitfall": "Tool restriction is by tool NAME; a `bash` subagent can run any command your permissions allow. To restrict commands, rely on `allow`/`deny` rules "
                               "(e.g. `bash(python -m pytest*)`) and on approvals — subagent calls go through the same gate as the main agent.",
                },
                "5_eval": {
                    "title": "An eval task for your daily work + a 2-model report",
                    "where": "Append the task to `evals/tasks.yaml` (at the END: `test_tasks_file` expects `fix_rounding` and `fix_due_date` to stay first). Hidden tests go in "
                             "`evals/hidden/` and are referenced as `{\"evals/hidden/<file>.py\": \"tests/<dest>.py\"}`. Reports go to `out/evals_<model>.json`. "
                             "Tasks always run on a copy of `playground/`, so express your daily work against the invoices project.",
                    "steps": [
                        "Pick a task type you do every week: a small bug fix, a feature with tests, a refactor that must keep tests green, or a code question.",
                        "Write the prompt like a ticket (what, not how). Choose an OBJECTIVE check: `command` (tests), `hidden` (tests the agent can't see — best for features), "
                        "`answer_contains` (+ `forbid_changes: true` for questions).",
                        "For a `hidden` check, write the hidden test file in `evals/hidden/` and verify it FAILS on the untouched playground (otherwise the task measures nothing).",
                        "Run it alone: `python scripts/tasks.py evals --only <id> --repeat 3`. Iterate the prompt/check until a pass means 'done right'.",
                        "Run the same task (or the full suite) with two models: `python scripts/tasks.py evals --model qwen3:8b --repeat 3` and "
                        "`python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (or `--backend openai_compat` / `--backend openrouter --model <open-weight model>`).",
                        "Write the report: a table from the two JSON files (pass rate, per_task for your task, avg steps, avg seconds, total tokens) + 2–3 sentences of conclusion.",
                    ],
                    "template": "```yaml\n- id: my_overdue_flag\n  prompt: \"Add a method Invoice.is_overdue(today) that returns True when today is after the due date. Add a test.\"\n"
                                "  check: {command: \"python -m pytest -q tests/test_overdue_hidden.py\", hidden: {\"evals/hidden/test_overdue.py\": \"tests/test_overdue_hidden.py\"}}\n\n"
                                "- id: my_question\n  prompt: \"Without modifying anything: where is the due date computed and what happens on weekends?\"\n"
                                "  check: {answer_contains: [\"dates.py\", \"due_date\"], forbid_changes: true}\n```\n"
                                "Report skeleton (Markdown):\n```markdown\n| model | pass rate | my task | avg steps | avg s | tokens |\n|---|---|---|---|---|---|\n"
                                "| qwen3:8b | 0.60 | 0.33 | 9.1 | 41.0 | 120k |\n| qwen3-coder:30b | … | … | … | … | … |\n\nConclusion: <which model for which task, and why>.\n```\n"
                                "To print the numbers: `python -c \"import json,glob; [print(r['model'], r['pass_rate'], r['per_task'], r['avg_steps'], r['avg_seconds'], r['total_tokens']) "
                                "for r in map(lambda f: json.load(open(f, encoding='utf-8')), glob.glob('out/evals_*.json'))]\"`",
                    "pitfall": "By default `run_task` copies the playground WITHOUT `.forja/` (only `playground/AGENTS.md` counts). To measure your configuration run twice and compare: "
                               "`python scripts/tasks.py evals --repeat 3 --label base` and `python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config`. "
                               "`~/.forja/AGENTS.md` is never used (temp home). MCP paths in `settings.json` resolve from the temp copy, so use absolute paths with `--mcp`.",
                },
            },
            "demo": [
                "3 minutes per person/pair: 30 s what you added (show the files), 90 s one live prompt where a skill/hook/subagent visibly kicks in, 60 s the eval table and your conclusion.",
                "Bring numbers, not impressions: 'pass rate on my task went from 0.33 to 1.0 with qwen3-coder:30b at 2× the time'.",
            ],
            "done_when": [
                "[ ] Global and project `AGENTS.md` exist and the agent can quote them.",
                "[ ] One skill is loaded by the agent (`⏺ skill <name>`) when relevant.",
                "[ ] One hook visibly blocks or feeds back (`BLOCKED by hook` / `[hook PostToolUse]`).",
                "[ ] One subagent profile is listed in the `task` description and used (`[<name>]` calls).",
                "[ ] One new task in `evals/tasks.yaml`, `python scripts/tasks.py test 12` still passes, and two `out/evals_*.json` reports compared in a table.",
            ],
        },
    },
}
