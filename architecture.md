# Architecture

This document explains the high-level architecture of the project.

1. MCP Server
- `server.py` uses `FastMCP` to register a set of tools that operate on the mock logs dataset. These tools are exposed over the MCP protocol and can be inspected with `mcp dev server.py`.

2. Tool Flow
- `tools/logs.py` provides log-loading and filtering functions: `get_error_logs`, `get_logs_by_level`, `get_logs_by_service`, and `list_services`.
- `tools/summaries.py` provides lightweight summarization helpers such as `summarize_errors`.
- `server.py` wires those functions into MCP tools using the `@mcp.tool()` decorator.

3. Chatbot Flow
- `chatbot.py` is a CLI that performs simple intent detection and routes queries to the local tools when possible (e.g., "show critical logs", "list services").
- When the query doesn't match a local intent, the chatbot falls back to an LLM (if `OPENAI_API_KEY` is available).

4. Mock CloudWatch
- Logs are stored in `data/logs.json` and structured to mimic CloudWatch events: timestamps, level, service, and message. This allows realistic demos without external dependencies.

Design Goals
- Beginner-friendly: minimal dependencies and clear function boundaries
- Demo-ready: human-readable outputs and simple CLI for live demos
- Extendable: add more tools or richer analysis without changing the MCP plumbing
