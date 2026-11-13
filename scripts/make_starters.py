"""Generates forja/ (student version) from solutions/forja/ by emptying the TODOs.

Usage (instructor):  python scripts/make_starters.py
"""
from __future__ import annotations

import ast
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC, DST = ROOT / "solutions" / "forja", ROOT / "forja"

STUBS: dict[str, list[tuple[str, str, str]]] = {
    "llm.py": [
        ("ToolCallAccumulator.add", "01.1", "For each delta: slot = self._parts.setdefault(d.index, {'id': '', 'name': '', 'arguments': ''}). If d.id, store it. If d.function: CONCATENATE name and arguments (they arrive in pieces)."),
        ("ToolCallAccumulator.finish", "01.1", "Walk the indices in order; skip those without a name; build ToolCall(id or a generated one, name, arguments or '{}')."),
        ("ThinkFilter.feed", "01.2", "Append the text to self.buf. Outside <think>: emit up to the opening tag (and hold back at the end a possible start of '<think>', e.g. '<thi'). Inside: discard up to '</think>' (holding back a possible split closing tag). Return the visible text."),
        ("LLMClient.stream", "01.3", "params = self._params(...). Create the stream with retries (RETRYABLE, backoff 1, 2, 4 s; not for 4xx). For each chunk: usage if present; delta.content -> ThinkFilter -> yield TextDelta; delta.tool_calls -> accumulator. At the end: flush, if there are no tool calls try rescue_text_tool_calls, and yield Done(ChatResponse(...))."),
    ],
    "tools.py": [
        ("Tool.schema", "02.1", "self.args_model.model_json_schema(); remove 'title' from the root and from every property; additionalProperties=False. Return {'type':'function','function':{name, description, parameters}}."),
        ("ToolRegistry.execute", "02.2", "NEVER raises. t, args, err = self.parse_args(call); if err -> ToolResult(ok=False, err). Run t.fn(**args) catching any exception as 'ERROR in ...'. If it returns ToolOutput use .text and .meta; otherwise str or JSON. Use _truncate and measure duration_ms."),
    ],
    "fs_tools.py": [
        ("Workspace.resolve", "02.3", "Relative path -> self.root / path; absolute is kept. .resolve() (follows symlinks). If it is neither self.root nor inside it (is_relative_to) -> PermissionError('path outside the workspace: …')."),
        ("make_fs_tools.write_file", "02.4", "p = ws.resolve(path). If it exists: ws.check_fresh(p) and keep the previous content. Call every cb in ws.before_write(p). Create folders, write, ws.mark_read(p). Return ToolOutput(short text, {'path': ws.rel(p), 'diff': unified_diff(before, after, path)})."),
        ("make_fs_tools.edit_file", "02.5", "Must exist; ws.check_fresh(p); old != new. n = text.count(old_string): 0 -> ValueError with a hint (line numbers ' 12→'? whitespace?); n>1 without replace_all -> ValueError 'appears N times'. Replace (1 or all), before_write, write, mark_read. ToolOutput with the line of the change and the diff."),
        ("make_fs_tools.grep", "02.6", "re.compile(pattern, re.I if ignore_case). If path is a file, only that one; otherwise ws.walk(base). Filter by include (fnmatch on the name). Read as UTF-8 (skip binaries). show_content: 'path:n: line'; otherwise paths only. Stop at 300 results. Nothing found: '(no matches)'."),
    ],
    "agent.py": [
        ("Agent._run_calls", "03.1", "results = [None]*len(calls). Group CONSECUTIVE reads (self._is_read) and run them with ThreadPoolExecutor; the rest in order. For each one: events.on_tool_start, execute (self.execute or self.tools.execute), events.on_tool_end. Return the results in the original order."),
        ("Agent.run", "03.2", "For step 1..max_steps: if self.cancel is set -> 'interrupted'. Consume self.llm.stream(messages, tools=schemas or None): TextDelta -> events.on_text; Done -> resp. Accumulate usage, append resp.to_message(), events.on_assistant. No tool_calls -> 'final'. Loop detection (same tool+args > max_repeats): close the pending tool_calls with an error ToolResult and return 'loop'. Otherwise _run_calls and append the tool messages. At the end: 'max_steps'."),
    ],
    "shell.py": [
        ("head_tail", "04.1", "If it fits, unchanged. Otherwise: 1/4 of the limit from the start + 3/4 from the end, with a note saying how many characters are omitted in the middle."),
        ("make_shell_tool.bash", "04.2", "subprocess.run(command, shell=True, cwd=ws.root, capture_output, text, encoding='utf-8', errors='replace', timeout (1..600), env=clean_env(), stdin=DEVNULL). TimeoutExpired -> 'TIMEOUT after Ns'. Return ToolOutput('exit_code=N\\n' + head_tail(stdout + [stderr]), {'exit_code': N})."),
    ],
    "permissions.py": [
        ("rule_matches", "04.3", "name, pattern = parse_rule(rule). The tool name is matched with fnmatchcase (allows 'mcp__issues__*'). No pattern: match. With a pattern: fnmatchcase(tool.subject(args), pattern); for bash normalise whitespace (' '.join(split()))."),
        ("decide", "04.4", "1) deny (also for each bash subcommand via split_commands) -> 'deny'. 2) plan and risk != read -> 'deny'. 3) allow: for bash ALL subcommands must match some rule; for the rest, some rule. 4) read risk or bypass mode -> allow. 5) accept_edits and edit risk -> allow. 6) 'ask'. Return (decision, reason)."),
        ("suggest_rule", "04.5", "bash: shlex.split; 'python -m X' -> bash(python -m X*); git/npm/uv/pip/docker… -> bash(<cmd> <subcmd>*); others -> bash(<cmd>*). Other tools: their name."),
    ],
    "cli.py": [
        ("summarize_call", "05.1", "One readable line per tool: 'Read path' (+ ' (from line N)' if offset != 1), 'Write path (N lines)', 'Edit path', '$ command', \"Grep 'pattern' in path (include)\", 'Glob pattern', 'Task[type] description', 'Todos (N)', others 'name(k=v, …)'. Collapse whitespace and cut to `width` with '…'."),
        ("diff_styles", "05.2", "Per line: '+++'/'---' -> 'bold'; '@@' -> 'cyan'; '+' -> 'green'; '-' -> 'red'; the rest -> 'dim'. Return [(line, style)]."),
        ("ask_approval", "05.3", "Draw a Panel with summarize_call and the reason. Read the answer with read(...): y/yes -> 'yes'; a/always -> 'always'; anything else (including empty) -> 'no'."),
        ("handle_slash", "05.4", "Split command and argument. /exit -> None. /help -> HELP. /mode [m] (app.set_mode). /tools (name [risk]). /todos (app.todos.render()). /context (app.context_tokens()). /compact (app.compact_now(force=True)). /cost (app.usage). /undo (app.undo()). /sessions (Transcript.list_sessions). /clear. Unknown -> message."),
    ],
    "context.py": [
        ("find_instruction_files", "06.1", "First home/.forja/AGENTS.md if it exists. Then walk up from cwd to `stop` or the filesystem root collecting AGENTS.md/FORJA.md, and return them from the HIGHEST folder to the lowest (most specific last)."),
        ("build_system_prompt", "06.2", "Layers joined with '\\n\\n': BASE_PROMPT, MODE_REMINDERS[mode], each instruction file under a '## … instructions' heading, skills_catalog, extra (non-empty) and '## Environment' with directory, git_info(ws.root), OS, date and model."),
        ("expand_mentions", "06.3", "For each unique @path (MENTION_RE): ws.resolve (ignore PermissionError), only if it is a file; read it (max max_chars), ws.mark_read and append <file path=\"…\">content</file> to the end of the text. Without valid mentions, the text unchanged."),
    ],
    "compaction.py": [
        ("microcompact", "07.1", "starts = user_turn_starts(history). If there are <= keep_recent_turns turns, 0. Otherwise, for the messages BEFORE starts[-keep_recent_turns]: 'tool' messages with content >= min_chars not yet cleared -> content = CLEARED. Return how many."),
        ("compact", "07.2", "Cut ONLY at the start of a user turn, keeping keep_recent_turns turns. Turn the old part into text (role, content, tools called, truncated results), ask for the summary with SUMMARY_PROMPT (temperature=0) and return ([user: '[Summary of the previous session]\\n…', assistant: ack, *recent], True)."),
    ],
    "planning.py": [
        ("make_todo_tool.todo_write", "08.1", "Convert each item to TodoItem (dicts may arrive). More than one in_progress -> ValueError. Empty content -> ValueError. store.items = items. Return 'List updated (X/N completed):' + store.render()."),
        ("make_exit_plan_tool.exit_plan_mode", "08.2", "Empty plan -> ValueError. If approve(plan): on_approved() and return a text saying the user APPROVED and it should implement it. Otherwise: that they REJECTED it and it is still in plan mode."),
    ],
    "subagents.py": [
        ("load_profiles", "09.1", "Start with dict(BUILTIN). For each *.md in the folder (if it exists): FRONTMATTER.match; yaml.safe_load the frontmatter; require name and description; tools may be a list or 'a, b'; max_steps optional. The body is the system prompt."),
        ("make_task_tool.task", "09.2", "Look up the profile (ValueError if missing). sub_tools = parent_tools.subset(the profile's tools, without 'task'). Wrap execute so a call to a tool NOT in sub_tools returns ToolResult(ok=False, 'ERROR: tool ... is not available to subagent ...') instead of running. Agent(llm, sub_tools, execute=<wrapper>, max_steps, events=events_factory(name) or Events()). NEW messages: [profile system, user prompt]. Return '[subagent …] ' + the answer."),
    ],
    "hooks.py": [
        ("HookRunner.matching", "10.1", "From self.config[event]: no matcher -> always; with a matcher -> only if there is a tool_name and re.fullmatch(matcher, tool_name)."),
        ("HookRunner.run", "10.2", "Serialise {'hook_event_name', 'cwd', **payload} to JSON. For each matching hook: subprocess.run(command, shell=True, cwd, input=json, capture_output, text, timeout). Exit 2 -> block=True and accumulate stderr (or stdout) in message. Exit 0 -> stdout to context. Other -> errors. TimeoutExpired -> errors."),
    ],
    "skills.py": [
        ("discover_skills", "10.3", "For each existing folder: */SKILL.md sorted; FRONTMATTER + yaml; require name and description (normalise whitespace). Later folders override earlier ones."),
        ("make_skill_tool.skill", "10.4", "Unknown skill -> ValueError listing the available ones. Return '# Skill: name', the folder and the BODY without frontmatter."),
    ],
    "mcp_tools.py": [
        ("mcp_tool_name", "10.5", "'mcp__' + server + '__' + tool, replacing any character outside [a-zA-Z0-9_] with '_' (NAME_RE)."),
    ],
    "session.py": [
        ("Transcript.append", "11.1", "Create the folder; open self.path in 'a' mode and write one JSON line per message: {'ts': ..., 'message': m} (ensure_ascii=False)."),
        ("Transcript.load", "11.2", "FileNotFoundError if it doesn't exist. Walk the lines: 'compacted' -> replaces the whole history; 'message' -> append."),
        ("Checkpoints.before_write", "11.3", "If there is no turn, begin_turn(). Only the FIRST time a path is touched in the turn: store path.read_bytes() or None if it didn't exist."),
        ("Checkpoints.undo", "11.4", "Drop empty turns from the end. Pop the last one: restore each file (write_bytes, creating folders) or delete it if it was None. Return the sorted paths; [] if there is nothing."),
    ],
    "evals.py": [
        ("grade", "12.1", "In order: forbid_changes (different snapshot -> fail); answer_contains (compare with norm(), list what is missing); copy the hidden files into the workdir; run command in the workdir (timeout -> fail; exit != 0 -> fail with the last 3 lines). If all good: (True, 'ok')."),
        ("summarize", "12.2", "Group by id. Return model, runs, pass_rate (3 decimals), per_task (2 decimals), avg_steps and avg_seconds (1 decimal), total_tokens and results (asdict)."),
    ],
}


def stub(src: str, qualname: str, label: str, hint: str) -> str:
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    parts = qualname.split(".")
    nodes = tree.body
    target = None
    for i, name in enumerate(parts):
        for n in nodes:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name:
                target = n
                nodes = n.body
                break
        else:
            raise SystemExit(f"not found: {qualname}")
    body = target.body
    first = body[0]
    keep_doc = isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) and isinstance(first.value.value, str)
    def top(n: ast.AST) -> int:  # includes decorators
        decs = getattr(n, "decorator_list", None) or []
        return min([n.lineno, *(d.lineno for d in decs)])

    start = top(body[1] if keep_doc and len(body) > 1 else first) - 1
    if keep_doc and len(body) == 1:
        start = first.end_lineno
    end = body[-1].end_lineno
    indent = " " * (body[0].col_offset)
    hint_lines = [f"{indent}# TODO {label}: {hint}\n", f'{indent}raise NotImplementedError("TODO {label}")\n']
    return "".join(lines[:start] + hint_lines + lines[end:])


def main() -> None:
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("__pycache__"))
    for fname, items in STUBS.items():
        p = DST / fname
        src = p.read_text(encoding="utf-8")
        # Bottom-up so line numbers don't shift
        for q, label, hint in sorted(items, key=lambda it: -_lineno(src, it[0])):
            src = stub(src, q, label, hint)
        src = src.replace("(starter)", "")
        p.write_text(src, encoding="utf-8")
    print(f"starters generated in {DST}")


def _lineno(src: str, qualname: str) -> int:
    nodes = ast.parse(src).body
    n = None
    for name in qualname.split("."):
        n = next(x for x in nodes if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and x.name == name)
        nodes = n.body
    return n.lineno


if __name__ == "__main__":
    main()
