## Objective
Create an internal LLM agent module that accepts prompts from carta-cli commands and executes them via OpenRouter API, using file/system tools as needed to complete tasks.

## Context
Carta-cli commands need to delegate reasoning and execution to an LLM. This module provides a simple interface: pass a prompt, get a result. The agent handles model communication and tool execution internally.

## Assumptions
- Calling commands trust the agent to select appropriate tools
- OpenRouter API follows OpenAI-compatible formats
- The agent has a fixed set of built-in tools (file read, file write, shell exec)
- Single prompt → single result; callers orchestrate multi-step workflows
- Network connectivity available when invoked

## Constraints
- Authentication via `OPENROUTER_API_KEY` environment variable
- Synchronous only (no streaming)
- Maximum 3 retries with exponential backoff (429/5xx only)
- Stateless between calls

## Acceptance Criteria
- Commands can call agent with a prompt and receive structured result
- Commands can specify model and LLM parameters (temperature, max_tokens, etc.)
- Agent can read files to fulfill prompts
- Agent can write files to fulfill prompts
- Agent can execute shell commands to fulfill prompts
- Returns structured response: content, tokens used, model, cost estimate
- Retries transient failures automatically
- Raises clear error when API key missing
- Logs token usage and cost for observability

## Developer Scenarios

1. **Simple call**: `agent.run("Explain what this code does", context=file_content)` → Returns explanation

2. **Tool-using call**: `agent.run("List all TODO comments in src/")` → Agent executes shell/file tools, returns findings

3. **With parameters**: `agent.run(prompt, model="anthropic/claude-3", temperature=0.7)` → Uses specified settings

4. **Failure**: API unavailable → Agent retries 3x → Raises exception with details

## Edge Cases
- Tool execution fails (file not found, command error)
- Model requests unsupported tool
- Token limit reached mid-response
- Invalid model name
- Network timeout

## Dependencies
- OpenRouter API availability

## Out of Scope
- Streaming
- Session/conversation state
- User-facing CLI interface
- Multi-prompt orchestration
- Custom tool registration (fixed tool set)
