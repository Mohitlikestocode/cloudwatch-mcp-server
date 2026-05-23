import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any

from tools import logs as logs_tool
from tools import summaries as summaries_tool


def format_logs(logs: List[dict], title: str = None) -> str:
    lines = []
    if title:
        lines.append(f"=== {title} ===")
    for l in logs:
        ts = l.get("timestamp")
        try:
            tsf = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            tsf = ts
        lines.append(f"[{tsf}]")
        lines.append(f"SERVICE: {l.get('service')}")
        lines.append(f"LEVEL: {l.get('level')}")
        lines.append(f"MESSAGE: {l.get('message')}")
        lines.append("")
    return "\n".join(lines) if lines else "(no logs)"


# legacy keyword intent detection removed — LLM now selects tools dynamically


def call_groq(user_input: str) -> str:
    """Call Groq's OpenAI-compatible chat completions endpoint via HTTP.

    Uses `GROQ_API_KEY` and optional `GROQ_BASE_URL` environment variables.
    """
    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "(No LLM available - set GROQ_API_KEY to enable)"

    base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.environ.get("GROQ_MODEL", os.environ.get("OPENAI_MODEL", "llama-3.3-70b-versatile"))
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an observability assistant. Keep answers concise."},
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 512,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # OpenAI-compatible response shape
        return data.get("choices", [])[0].get("message", {}).get("content")
    except Exception as e:
        return f"(LLM error: {e})"


# Tool registry: names -> {fn, description, args}
TOOLS: Dict[str, Dict[str, Any]] = {
    "get_error_logs": {
        "fn": logs_tool.get_error_logs,
        "description": "Return all ERROR and CRITICAL logs",
        "args": {}
    },
    "get_logs_by_service": {
        "fn": logs_tool.get_logs_by_service,
        "description": "Return logs for a specific service by name",
        "args": {"service_name": "string"}
    },
    "summarize_errors": {
        "fn": summaries_tool.summarize_errors,
        "description": "Return a short structured summary of recent errors",
        "args": {}
    },
    "list_services": {
        "fn": logs_tool.list_services,
        "description": "List available services in the logs",
        "args": {}
    },
    "get_logs_by_level": {
        "fn": logs_tool.get_logs_by_level,
        "description": "Return logs for a given severity level (INFO, WARN, ERROR, CRITICAL)",
        "args": {"level": "string"}
    }
}


def is_raw_request(text: str) -> bool:
    t = text.lower()
    raw_tokens = ("raw", "json", "structured output", "show raw logs", "show json")
    return any(tok in t for tok in raw_tokens)


def extract_json(text: str) -> Any:
    """Try to extract a JSON object from text and parse it."""
    try:
        return json.loads(text)
    except Exception:
        # try to find first { ... }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            snippet = text[start:end+1]
            try:
                return json.loads(snippet)
            except Exception:
                return None
        return None


def ask_tool_selector(user_input: str) -> Dict[str, Any]:
    """Ask the LLM which tool to call and with what arguments. Returns dict with tool and arguments."""
    # Build tools description
    tools_list = []
    for name, meta in TOOLS.items():
        tools_list.append({"name": name, "description": meta["description"], "args": meta["args"]})

    prompt = {
        "system": (
            "You are a tool selector. Given a user request and a list of available tools (name, description, and argument schema), "
            "choose a single best tool to satisfy the request and return a JSON object with keys: 'tool' and 'arguments'. "
            "If no tool is needed, return {\"tool\": null, \"arguments\": {}}. ONLY return JSON."
        ),
        "user": f"User request:\n{user_input}\n\nAvailable tools:\n{json.dumps(tools_list, indent=2)}\n\nRespond with JSON: {{\"tool\": <tool_name_or_null>, \"arguments\": {{...}} }}"
    }

    # Combine into a single text prompt for call_groq
    text = prompt["system"] + "\n\n" + prompt["user"]
    resp = call_groq(text)
    parsed = extract_json(resp or "")
    if not parsed or "tool" not in parsed:
        return {"tool": None, "arguments": {}}
    return parsed


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    meta = TOOLS.get(tool_name)
    if not meta:
        return {"error": f"Unknown tool: {tool_name}"}
    fn = meta["fn"]
    try:
        # match arguments to function signature simply by passing dict
        if arguments is None:
            return fn()
        # normalize keys (some tools expect different names)
        return fn(**arguments) if isinstance(arguments, dict) else fn(arguments)
    except Exception as e:
        return {"error": str(e)}


def repl():
    # load .env if present
    load_dotenv()
    print("Observability assistant (type 'quit' to exit)")
    while True:
        user_input = input("\nYou: ")
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye")
            break

        raw_mode = is_raw_request(user_input)

        # 1) Ask the LLM which tool to call and with what arguments
        selection = ask_tool_selector(user_input)
        tool_name = selection.get("tool")
        arguments = selection.get("arguments") or {}

        if not tool_name:
            # No tool needed: let the LLM answer directly.
            resp = call_groq(user_input)
            print("\nAssistant:")
            print(resp)
            continue

        # 2) Execute the selected tool dynamically
        result = execute_tool(tool_name, arguments)

        # 3) If user requested raw/structured output, print formatted result
        if raw_mode:
            print("\nAssistant (raw output):")
            if isinstance(result, list) and result and isinstance(result[0], dict):
                print(format_logs(result, f"{tool_name} output"))
            else:
                try:
                    print(json.dumps(result, indent=2, default=str))
                except Exception:
                    print(str(result))
            continue

        # 4) Otherwise, send the tool result back to the LLM for a natural explanation
        tool_output_text = json.dumps(result, default=str, indent=2)
        second_prompt = (
            f"The user asked:\n{user_input}\n\n"
            f"You executed the tool: {tool_name} with arguments: {json.dumps(arguments)}\n\n"
            f"Tool output (structured JSON):\n{tool_output_text}\n\n"
            "Please explain the results naturally in a professional, human-readable paragraph. "
            "Do NOT return raw JSON unless the user requested it. Keep the explanation concise and actionable."
        )

        explanation = call_groq(second_prompt)
        print("\nAssistant:")
        print(explanation)


if __name__ == "__main__":
    repl()