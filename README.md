<!-- prettier-ignore -->
# CloudWatch MCP Server

**AI Observability Copilot — MCP-backed prototype**
Welcome to a polished, recruiter-ready demo that shows how a small MCP server, a few focused tools, and a Groq-compatible LLM can form a modern AI observability workflow. This repository is purpose-built for demos, interviews, and quick mentor walkthroughs.

--
**Why this project matters**
- Realistic: Uses a mock CloudWatch-style log corpus and realistic service names so demos feel production-like.
- Modern: The LLM is the primary reasoning engine — it chooses which tool to call, runs the tool, and explains results in natural language.
- Inspectable: Tools are exposed via an MCP server so you can use the MCP inspector in demos.
**Highlights**
- LLM-driven tool selection and orchestration
- Tool registry with clear descriptions for the LLM
- Two-pass flow: tool execution → natural-language explanation
- Clean, readable CLI outputs for demo videos and walkthroughs
**Project structure**

```
cloudwatch-mcp-server/
├── data/
│   └── logs.json            # Mock CloudWatch-style logs
├── tools/
│   ├── logs.py              # Log loading + filters
│   └── summaries.py         # Summarization helpers
├── chatbot.py               # LLM-first CLI and tool orchestration
├── server.py                # MCP server registering tools for inspector
├── requirements.txt
├── README.md
├── architecture.md
├── .env.example             # Put your GROQ_API_KEY here (do NOT commit .env)
└── screenshots/             # Add demo screenshots here
```

**Quick demo — TL;DR**
1. Create venv and install:

```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS / Linux
# source venv/bin/activate
pip install -r requirements.txt
```

2. Configure your key (private):

```bash
cp .env.example .env
# Edit .env, set GROQ_API_KEY, save
```

3. (Optional) Start the MCP server for inspector demos:

```bash
python server.py
# in a separate terminal: mcp dev server.py
```

4. Start the chatbot and ask natural questions:

```bash
python chatbot.py
```

Try these natural prompts:
- "What issues are affecting payments?"
- "Summarize recent failures in paragraph form"
- "Are there any critical incidents right now?"
- "Which service is the most unstable?"
**UX & Flow (what makes it special)**
1. The user speaks naturally.  
2. The LLM reads available tools and decides which one to call (and with what args).  
3. The selected tool runs locally and returns structured results.  
4. The LLM turns that structured data into a crisp, human-friendly explanation.

```mermaid
flowchart LR
	A[User prompt] --> B[LLM (selects tool + args)]
	B --> C[Tool (local Python) runs]
	C --> D[LLM (explains results in natural language)]
	D --> E[User receives explanation]
```

**Tool registry (short)**
- `get_error_logs` — return ERROR/CRITICAL logs
- `get_logs_by_service(service_name)` — fetch logs for a service
- `get_logs_by_level(level)` — fetch logs by severity
- `list_services` — list all services found in logs
- `summarize_errors` — structured summary of recent errors

Each tool lives in `tools/` and is intentionally small and testable.

**MCP + Inspector**
- `server.py` exposes the same tools via MCP. Run `mcp dev server.py` to inspect tools in the MCP inspector during a live demo.

**Git safety — critical**
- This repo ignores `.env` by default. Do NOT commit `.env`.
- If you ever accidentally commit a secret, rotate it IMMEDIATELY and remove the file from the index:

```bash
git rm --cached .env
git commit -m "Remove .env from repo"
git push origin main
```

If the secret reached a remote history, use `git filter-repo` or the BFG Repo-Cleaner and then rotate keys.

**For maintainers & mentors**
- Keep tools small and deterministic — they should return structured objects for the LLM to consume.  
- Keep the LLM prompts clear and low-context for reliable selection.  
- Add unit tests around tools (they're pure functions over `data/logs.json`).

**Design ideas for demos**
- Start with a query like "What's wrong with payments?" then open the MCP inspector to show the tool invoked.  
- Switch to `show raw logs` to demonstrate structured output, then ask the LLM to explain the failure in plain English.

**Contributing**
Contributions are welcome. Keep changes small and focused: new tools, better summaries, or improved mock data are ideal first PRs.

--

Built for demo-ready interviews and mentor walkthroughs. If you want I can help craft a 90-second demo script and screenshots for the `screenshots/` folder.

# CloudWatch MCP Server — Observability Assistant Prototype

A polished, demo-ready prototype: an "AI observability copilot" that uses a small MCP server
and a mock CloudWatch-style logs dataset. The LLM (Groq-compatible) reasons about user intent
and calls lightweight local tools to fetch data; the LLM then explains results in natural language.

Why this project
- Beginner-friendly, real-world feel: lightweight tools + mock data provide a realistic demo
- MCP-first: tools are exposed via an MCP server for inspector-compatible workflows
- Clean separation: tool logic lives in `tools/`, the chat UI is a compact CLI, and docs guide the demo

Highlights
- LLM-driven tool selection: the model chooses which tool to run and supplies arguments
- Tool registry: clearly documented tools the LLM can call dynamically
- Human-friendly explanations: tool results are summarized by the LLM into concise, professional text
- Demo-ready visuals: formatted log output for readable CLI demos

Project structure

```
cloudwatch-mcp-server/
├── data/
│   └── logs.json            # Mock CloudWatch-style logs (realistic entries)
├── tools/
│   ├── logs.py              # Log loading + filters
│   └── summaries.py         # Summary helpers
├── chatbot.py               # LLM-driven CLI + tool orchestration
├── server.py                # MCP server registering tools
├── requirements.txt
├── README.md
├── architecture.md
├── .env.example
└── screenshots/             # Add demo screenshots here
```

Quick start

1. Create a virtualenv and install dependencies

```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS / Linux
# source venv/bin/activate
pip install -r requirements.txt
```

2. Configure your Groq key

```bash
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY (do NOT commit .env)
```

3. Run the MCP server (optional — inspector / tool debugging)

```bash
python server.py
# Inspect tools with: mcp dev server.py
```

4. Run the chatbot CLI

```bash
python chatbot.py
```

Example queries

- "What issues are affecting payments?"
- "Summarize recent failures in paragraph form"
- "Are there any critical incidents?"
- "Which service is the most unstable?"
- "Show raw logs for auth-service"

Demo tips
- Start `server.py` to show MCP inspector and the registered tools
- Use the CLI and try natural language prompts — the LLM chooses tools for you
- Use `show raw logs` when you want the unaltered structured output

Security

- Never commit `.env` or real keys. Rotate keys if they've been exposed.
- `.env.example` contains placeholders only.

Git safety (important)

- **.env is ignored**: The project includes a [/.gitignore](.gitignore) entry that prevents `.env` from being committed. Do not remove that line.
- **If you haven't committed `.env` yet**: simply copy `.env.example` to `.env` and keep working — it will be ignored by Git.

Commands to make sure `.env` is not tracked:

```bash
# Add .env to .gitignore (already present) and remove from the index if necessary
echo ".env" >> .gitignore
git rm --cached .env || true
git add .gitignore
git commit -m "Ensure .env is ignored"
```

If you accidentally committed a secret, rotate the secret immediately. To remove a file from history you can use tools like `git filter-repo` or the `BFG Repo-Cleaner` — these rewrite history and should be used carefully. A simple, less-invasive cleanup (removes file from latest commit only) is:

```bash
# Remove from index and commit (does not rewrite older history)
git rm --cached .env
git commit -m "Remove .env from repo"
# Push the change
git push origin main
```

If the secret was pushed to a remote and you need to purge it fully from history, consider these references:

- BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/
- git filter-repo (recommended over filter-branch): https://github.com/newren/git-filter-repo

Always rotate keys after any accidental leak — it's the fastest way to secure your project.

Future improvements

- Add a web UI for interactive demos
- Add role-based access controls in the MCP server
- Expand tools to include traces and metrics in addition to logs

