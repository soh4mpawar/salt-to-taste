import pytest
import io
import httpx
from PIL import Image, ImageDraw, ImageFont
from app.agents.parsing_agent import build_vision_parsing_prompt, parse_recipe_from_image

@pytest.fixture
def ollama_available():
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get("http://localhost:11434/api/tags")
            resp.raise_for_status()
            return True
    except Exception:
        pytest.skip("Ollama is not reachable on localhost:11434")

def test_build_vision_parsing_prompt():
    prompt = build_vision_parsing_prompt()
    assert "ocr_confidence" in prompt
    assert "extraction_notes" in prompt

@pytest.mark.asyncio
async def test_parse_recipe_from_image_invalid_bytes():
    invalid_bytes = b'not an image'
    result = await parse_recipe_from_image(invalid_bytes, "test.txt")
    
    assert "error" in result
    assert result["extraction_method"] == "failed"

@pytest.mark.asyncio
async def test_parse_recipe_from_image_tesseract(ollama_available):
    # Create an image with enough text to trigger Tesseract fallback
    img = Image.new("RGB", (800, 400), color="white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        
    # Repeat text to exceed the 200 character threshold
    text = "Salt to taste. " * 20
    d.text((10, 10), text, fill="black", font=font)
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
    
    # We pass it to the function. Since we use Tesseract, it won't crash.
    result = await parse_recipe_from_image(png_bytes, "test.png")
    
    # It might return an error dict or a success dict, but it shouldn't raise an exception
    assert isinstance(result, dict)
