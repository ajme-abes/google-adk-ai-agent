import pytest
from agent_try.agent import validate_query, get_agent_info
from agent_try.agent import ValidationError
import asyncio


def test_agent_validation():
    """Test input validation works."""
    # Test valid query
    validate_query("What is Python?")
    
    # Test empty query should raise error
    with pytest.raises(ValidationError):
        validate_query("")
    
    # Test very short query should raise error
    with pytest.raises(ValidationError):
        validate_query("a")
    
    # Test query with forbidden patterns
    with pytest.raises(ValidationError):
        validate_query("<script>alert('xss')</script>")


def test_agent_info():
    """Test agent information endpoint."""
    info = get_agent_info()
    assert "agent_name" in info
    assert "model" in info
    assert "available_tools" in info
    assert isinstance(info["available_tools"], list)
    assert info["agent_name"] == "professional_ai_agent"
    assert info["model"] == "gemini-2.5-flash-lite"


def test_agent_config():
    """Test agent configuration."""
    from agent_try.agent import config
    assert hasattr(config, 'model_name')
    assert hasattr(config, 'app_name')
    assert hasattr(config, 'max_retries')
    assert config.model_name == "gemini-2.5-flash-lite"
    assert config.app_name == "professional_search_agent"


def test_agent_response_type():
    """Test if the agent returns a string response."""
    from agent_try.agent import get_agent_response
    
    query = "Hello, who are you?"
    response = asyncio.run(get_agent_response(query))
    assert isinstance(response, str), "Agent response should be a string"
    assert len(response) > 0, "Agent response should not be empty"


def test_agent_non_empty_response():
    """Test if the agent returns a non-empty response."""
    from agent_try.agent import get_agent_response
    
    query = "Tell me a joke."
    response = asyncio.run(get_agent_response(query))
    assert response.strip() != "", "Agent response should not be empty"
    assert len(response) > 10, "Agent response should be meaningful"


def test_agent_with_different_queries():
    """Test agent with various query types."""
    from agent_try.agent import get_agent_response
    
    test_queries = [
        "What is Python?",
        "Explain artificial intelligence",
        "What's the weather like?",
    ]
    
    for query in test_queries:
        response = asyncio.run(get_agent_response(query))
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"Query: '{query}' -> Response length: {len(response)}")


def test_agent_error_handling():
    """Test agent error handling for invalid inputs."""
    from agent_try.agent import get_agent_response, ValidationError
    
    # Test empty query
    with pytest.raises(ValidationError):
        asyncio.run(get_agent_response(""))
    
    # Test very short query  
    with pytest.raises(ValidationError):
        asyncio.run(get_agent_response("a"))