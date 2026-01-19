import httpx
import json
import os
from typing import Any, Callable


class AgentError(Exception):
    """Base exception for Agent failures"""

    pass


class Agent:
    def __init__(
        self,
        root_path: str = ".",
        http_client: Any = None,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: int = 5000,
    ):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")

        if not self.api_key:
            raise AgentError("OPENROUTER_API_KEY is not set")

        self._root_path = root_path
        self._http_client = http_client or httpx
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._max_iterations = 100
        self._tools = [
            {
                "type": "function",
                "function": {
                    "name": "file_read",
                    "description": "Read a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the file to read",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The path to the directory to list files from",
                            },
                        },
                        "required": ["path"],
                    },
                },
            },
        ]

    def _resolve_path(self, path: str) -> str:
        """Resolve a path relative to root_path"""
        return os.path.join(self._root_path, path)

    def _execute_read_file(self, path: str) -> str:
        """Read a file"""

        full_path = self._resolve_path(path)

        if os.path.isdir(full_path):
            return f"Error: '{path}' is a directory. Use list_files to see its contents."

        if not os.path.exists(full_path):
            return f"Error: '{path}' does not exist."

        with open(full_path, "r") as f:
            return f.read()

    def _execute_list_files(self, path: str = ".") -> str:
        """List files in a directory, with trailing / for subdirectories"""
        full_path = self._resolve_path(path)

        if not os.path.exists(full_path):
            return f"Error: '{path}' does not exist."

        if not os.path.isdir(full_path):
            return f"Error: '{path}' is not a directory."

        entries = []

        for name in os.listdir(full_path):
            entry_path = os.path.join(full_path, name)

            if os.path.isdir(entry_path):
                entries.append(f"{name}/")
            else:
                entries.append(name)

        return json.dumps(entries)

    def _execute_tool(self, tool_call: dict) -> str:
        """Execute a tool call from OpenRouter API response"""
        tools: dict[str, Callable[..., str]] = {
            "file_read": self._execute_read_file,
            "list_files": self._execute_list_files,
        }

        func = tool_call["function"]
        name = func["name"]

        if name not in tools:
            return f"Error: Unknown tool '{name}'. Available tools: {', '.join(tools.keys())}"

        try:
            parameters = json.loads(func["arguments"])
            return tools[name](**parameters)
        except (KeyError, json.JSONDecodeError) as e:
            return f"Error: Malformed arguments for '{name}': {e}"
        except Exception as e:
            return f"Error: Tool '{name}' failed: {e}"

    def _call_model(self, messages: list[dict]) -> dict:
        try:
            response = self._http_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": self._model,
                    "temperature": self._temperature,
                    "max_tokens": self._max_tokens,
                    "messages": messages,
                    "tools": self._tools,
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        except Exception as e:
            raise AgentError(f"Request failed: {e}")

        if response.status_code >= 400:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            raise AgentError(f"API error ({response.status_code}): {error_msg}")

        data = response.json()

        return {
            "id": data["id"],
            "model": data["model"],
            "finish_reason": data["choices"][0]["finish_reason"],
            "message": data["choices"][0]["message"],
            "total_tokens": data["usage"]["total_tokens"],
        }

    def _wrap_up(self, messages: list[dict]) -> dict:
        messages = messages + [
            {
                "role": "user",
                "content": "You've reached the maximum number of tool calls. Please provide your best answer with the information gathered so far.",
            }
        ]
        data = self._call_model(messages)
        data["truncated"] = True
        return data

    def _prompt(self, messages: list[dict], _depth: int = 0) -> dict:
        """Internal: handle the agentic loop"""
        data = self._call_model(messages)

        finish_reason = data["finish_reason"]
        assistant_message = data["message"]

        # Approaching limit - ask model to wrap up instead of cutting off
        if _depth >= self._max_iterations - 1:
            return self._wrap_up(messages + [assistant_message])

        if finish_reason != "tool_calls":
            return data

        messages = messages + [assistant_message]

        for tool_call in assistant_message["tool_calls"]:
            tool_result = self._execute_tool(tool_call)

            messages = messages + [
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": str(tool_result),
                }
            ]

        return self._prompt(messages, _depth + 1)

    def run(self, prompt: str) -> dict:
        """Run the agent with a prompt string."""
        messages = [{"role": "user", "content": prompt}]
        return self._prompt(messages)
