## Technical Context

**Existing**: Python 3.11+, Click CLI, pytest, Black/Ruff/Mypy | **Detected**: No HTTP client, no API integrations yet | **Decisions**: httpx for HTTP, single module, allowlisted commands + directory restriction, plain dict responses, Python logging

## Decision Exploration

### HTTP Client
- **Options**: httpx (modern, async-ready) vs requests (ubiquitous)
- **Selected**: httpx
- **Rationale**: Greenfield project, better timeout handling, future-proof if async needed

### Module Structure
- **Options**: Package with multiple files vs single module
- **Selected**: Single module (`src/carta/agent.py`)
- **Rationale**: Matches existing patterns, can refactor later if complexity grows

### Tool Safety
- **Options**: Unrestricted vs allowlist vs directory-restricted
- **Selected**: Allowlist + working directory restriction (layered)
- **Rationale**: Defense in depth - only predefined commands, and they can only operate within project directory

### Response Format
- **Options**: Dataclass vs TypedDict vs plain dict
- **Selected**: Plain dict
- **Rationale**: Minimal dependencies, easy to serialize, keeps it simple

### Logging
- **Options**: Python logging vs click.echo vs callback
- **Selected**: Python logging module
- **Rationale**: Standard, configurable, production-grade observability

## Solution Architecture

The LLM agent will be a single module exposing a primary `run()` function that accepts prompts and optional parameters. Internally, it manages the OpenRouter API connection, tool execution loop, and retry logic.

When a command calls `agent.run(prompt)`, the agent sends the prompt to OpenRouter along with tool definitions. If the model requests a tool, the agent validates it against the allowlist and working directory constraints, executes it, and returns the result to the model. This loop continues until the model produces a final response.

The agent is stateless - each call is independent. Retry logic with exponential backoff handles transient 429/5xx errors. All token usage and costs are logged via Python's logging module for observability.

## Technology Decisions

- **HTTP Client**: `httpx` (synchronous mode)
- **API**: OpenRouter with OpenAI-compatible chat completions endpoint
- **Auth**: `OPENROUTER_API_KEY` environment variable
- **Retry**: Exponential backoff (1s, 2s, 4s) for 429/5xx, max 3 attempts
- **Tools**: file_read, file_write, shell_exec with allowlist
- **Logging**: Python `logging` module at INFO level for usage, DEBUG for details

## Component Modifications

1. **pyproject.toml**: Add `httpx` to dependencies

## New Components

1. **src/carta/agent.py**: LLM agent module with `run()` function, tool execution, retry logic
2. **tests/test_agent.py**: Unit tests for agent module

## Task Sequence

**Phase 1: Foundation**
1. Add httpx dependency to pyproject.toml
2. Create agent module skeleton with configuration (API key loading, logging setup)
3. Implement OpenRouter API client (chat completions request/response)
4. Add retry logic with exponential backoff

Dependencies: None

**Phase 2: Tool System**
5. Define tool schemas (file_read, file_write, shell_exec)
6. Implement tool execution with allowlist validation
7. Implement working directory restriction
8. Add tool execution loop (model requests tool → execute → return result)

Dependencies: Phase 1

**Phase 3: Integration & Polish**
9. Implement structured response (content, tokens, model, cost)
10. Add comprehensive error handling (missing API key, invalid model, network errors)
11. Write unit tests with mocked API responses
12. Integration test with real API (manual/CI)

Dependencies: Phase 2

## Integration Points

- **Commands**: Import `from carta.agent import run` and call with prompts
- **Environment**: Reads `OPENROUTER_API_KEY` at runtime
- **Filesystem**: Tools operate within working directory only

## Testing Strategy

**Unit**: Mock httpx responses, test retry logic, test tool validation, test allowlist enforcement
**Integration**: Test full prompt→response flow with mocked API
**Edge Cases**: Missing API key, invalid model, tool execution failure, network timeout, command not in allowlist, path traversal attempts

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Shell command injection | Allowlist + directory restriction + no shell expansion |
| Path traversal in file tools | Validate paths are within working directory |
| API costs spiral | Log all token usage, caller can set max_tokens |
| OpenRouter API changes | Pin to known working API version, integration tests |
