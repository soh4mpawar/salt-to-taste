import pytest
import httpx
from app.agents.state import RecipePipelineState
from app.agents.parsing_agent import parsing_agent_node

@pytest.fixture
def ollama_available():
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get("http://localhost:11434/api/tags")
            resp.raise_for_status()
            return True
    except Exception:
        pytest.skip("Ollama is not reachable on localhost:11434")

@pytest.mark.asyncio
async def test_parsing_agent_text_input(ollama_available):
    state: RecipePipelineState = {
        "raw_input": "Quick scrambled eggs: 2 eggs, 1 tbsp butter, salt to taste. Melt butter, whisk eggs, cook on low heat until fluffy.",
        "input_type": "text",
        "user_id": "test-uuid",
        "errors": []
    }
    
    result = await parsing_agent_node(state)
    
    assert result.get("parsing_error") is None
    assert result.get("pipeline_stage") == "parsing_complete"
    assert result.get("parsed_recipe") is not None
    ingredients = result.get("ingredients")
    assert ingredients is not None
    assert len(ingredients) > 0
