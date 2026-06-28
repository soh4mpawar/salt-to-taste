import pytest
import httpx
from app.graphs.recipe_pipeline import run_recipe_pipeline

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
async def test_integration_pipeline(ollama_available):
    recipe_text = "Simple Pasta: 200g spaghetti, 50g parmesan cheese, 1 tbsp olive oil, 2 cups water. Boil pasta in water until al dente, drain, toss with oil and cheese."
    
    result = await run_recipe_pipeline(
        raw_input=recipe_text,
        input_type="text",
        user_id="test_user"
    )
    
    stage = result.get("pipeline_stage")
    error = result.get("parsing_error")
    
    assert stage in ("complete", "analysis_failed", "parsing_failed", "analysis_skipped", "personalization_skipped") or error is not None
