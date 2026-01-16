import pytest
from unittest.mock import Mock, MagicMock
from carta.agent import Agent


@pytest.fixture
def mock_httpx():
    mock = MagicMock()
    mock.post.return_value = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "id": "123",
                "model": "openai/gpt-4o-mini",
                "usage": {"total_tokens": 100},
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": "Hello, world!"},
                    }
                ],
            }
        ),
    )
    return mock


@pytest.fixture
def agent(mock_httpx):
    return Agent(
        http_client=mock_httpx,
        model="openai/gpt-4o-mini",
        temperature=0.0,
        max_tokens=5000,
    )


def test_agent_init(agent):
    """Test agent initialization."""
    assert agent._http_client is not None
    assert agent._model == "openai/gpt-4o-mini"
    assert agent._temperature == 0.0
    assert agent._max_tokens == 5000


def test_agent_run(agent):
    """Test agent run."""
    data = agent.run("Hello, world!")
    assert data is not None


def test_agent_run_with_tool(mock_httpx):
    """Test agent run with tool."""
    # First response: model wants to call a tool
    first_response = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "id": "123",
                "model": "openai/gpt-4o-mini",
                "usage": {"total_tokens": 100},
                "choices": [
                    {
                        "finish_reason": "tool_calls",
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_123",
                                    "type": "function",
                                    "function": {
                                        "name": "list_files",
                                        "arguments": '{"path": "."}',
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ),
    )

    # Second response: final answer after tool execution
    second_response = Mock(
        status_code=200,
        json=Mock(
            return_value={
                "id": "123",
                "model": "openai/gpt-4o-mini",
                "usage": {"total_tokens": 100},
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "role": "assistant",
                            "content": "The files in the current directory are: ['test_agent.py']",
                        },
                    }
                ],
            }
        ),
    )

    mock_httpx.post.side_effect = [first_response, second_response]

    agent = Agent(
        http_client=mock_httpx,
        model="openai/gpt-4o-mini",
        temperature=0.0,
        max_tokens=5000,
    )

    data = agent.run("Index the code in the current directory.")
    assert data is not None
    assert mock_httpx.post.call_count == 2
