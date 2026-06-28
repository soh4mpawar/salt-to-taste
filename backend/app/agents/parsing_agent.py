import httpx
import json
from bs4 import BeautifulSoup
from app.agents.state import RecipePipelineState
from app.core.ollama import get_parsing_llm, get_vision_llm
from langchain_core.messages import HumanMessage
from app.utils.image_processing import validate_image_format, preprocess_image, image_to_base64, enhance_for_ocr
from app.utils.ocr_fallback import should_use_tesseract

async def fetch_url_content(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
            
            soup = BeautifulSoup(html, 'lxml')
            for element in soup(["script", "style", "nav", "footer"]):
                element.extract()
                
            text = soup.get_text(separator=' ', strip=True)
            return text[:8000]
    except Exception as e:
        return f"ERROR: Failed to fetch URL content - {str(e)}"

def build_parsing_prompt(raw_text: str) -> str:
    return f"""You are a recipe parser. Extract structured data from the following recipe text.
Return ONLY a valid JSON object with NO explanation, NO markdown, NO code blocks.

Required JSON structure:
{{
  "title": "recipe name",
  "servings": 4,
  "ingredients": [
    {{"name": "ingredient name", "amount": 1.5, "unit": "cups", "is_salty": false}}
  ],
  "steps": ["step 1 text", "step 2 text"],
  "cooking_method": "roast|simmer|fry|steam|raw|grill|bake",
  "dish_type": "soup|salad|roasted_vegetables|seafood|meat|pasta|bread|dessert|other",
  "estimated_servings_grams": 300
}}

For the is_salty field: mark true for ingredients that contain significant sodium
(soy sauce, fish sauce, miso, canned broths, cheese, cured meats, pickles, olives).

Recipe text:
{raw_text}

JSON only:"""

async def parsing_agent_node(state: RecipePipelineState) -> dict:
    raw_input = state.get("raw_input", "")
    input_type = state.get("input_type", "text")
    
    text_to_parse = raw_input
    extraction_method = "text"
    if input_type == "url":
        fetched = await fetch_url_content(raw_input)
        if fetched.startswith("ERROR:"):
            return {
                "parsing_error": fetched, 
                "pipeline_stage": "parsing_failed", 
                "errors": [fetched]
            }
        text_to_parse = fetched
    elif input_type == "image":
        image_bytes = state.get("image_bytes")
        if not image_bytes:
            return {"parsing_error": "No image data in state", "pipeline_stage": "parsing_failed", "errors": ["No image data"]}
        result = await parse_recipe_from_image(image_bytes, state.get("raw_input", "upload.jpg"))
        if "error" in result:
            return {"parsing_error": result["error"], "pipeline_stage": "parsing_failed", "errors": [result["error"]]}
        
        # Merge result natively since parse_recipe_from_image handles the full output dict
        result["pipeline_stage"] = "parsing_complete"
        return result
        
    prompt = build_parsing_prompt(text_to_parse)
    llm = get_parsing_llm()
    
    try:
        response = await llm.ainvoke(prompt)
        response_text = response.content.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        parsed_json = json.loads(response_text.strip())
        
        return {
            "parsed_recipe": parsed_json,
            "recipe_title": parsed_json.get("title"),
            "ingredients": parsed_json.get("ingredients", []),
            "steps": parsed_json.get("steps", []),
            "servings": parsed_json.get("servings"),
            "extraction_method": extraction_method,
            "pipeline_stage": "parsing_complete"
        }
    except Exception as e:
        error_msg = str(e)
        if 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
            error_msg = 'LLM timed out — Ollama may be loading the model. Please try again in 30 seconds.'
        return {
            "parsing_error": error_msg, 
            "pipeline_stage": "parsing_failed", 
            "errors": [error_msg]
        }

def build_vision_parsing_prompt() -> str:
    return """You are a recipe parser analyzing an image of a recipe — either a cookbook page, handwritten recipe, or screenshot.

Extract all recipe information visible in the image.
Return ONLY a valid JSON object with NO explanation, NO markdown, NO code blocks.

Required JSON structure:
{
  "title": "recipe name",
  "servings": 4,
  "ingredients": [
    {"name": "ingredient name", "amount": 1.5, "unit": "cups", "is_salty": false}
  ],
  "steps": ["step 1 text", "step 2 text"],
  "cooking_method": "roast|simmer|fry|steam|raw|grill|bake",
  "dish_type": "soup|salad|roasted_vegetables|seafood|meat|pasta|bread|dessert|other",
  "estimated_servings_grams": 300,
  "ocr_confidence": "high|medium|low",
  "extraction_notes": "any issues with image quality or partial visibility"
}

For the is_salty field: mark true for soy sauce, fish sauce, miso, canned broths, cheese, cured meats, pickles, olives.
If the image is unclear or a recipe cannot be found, still return valid JSON with empty arrays and ocr_confidence: "low".

JSON only:"""

async def parse_recipe_from_image(image_bytes: bytes, filename: str) -> dict:
    valid, reason = validate_image_format(image_bytes, filename)
    if not valid:
        return {"error": f"Unsupported format: {reason}", "extraction_method": "failed"}
        
    try:
        processed_bytes, metadata = preprocess_image(image_bytes, filename)
    except Exception as e:
        return {"error": f"Image preprocessing failed: {str(e)}", "extraction_method": "failed"}
        
    use_tess, tess_text, mean_conf = await should_use_tesseract(processed_bytes)
    if use_tess:
        # Re-use the text parsing logic natively
        llm = get_parsing_llm()
        prompt = build_parsing_prompt(tess_text)
        try:
            response = await llm.ainvoke(prompt)
            response_text = response.content.strip()
            if response_text.startswith("```json"): response_text = response_text[7:]
            if response_text.startswith("```"): response_text = response_text[3:]
            if response_text.endswith("```"): response_text = response_text[:-3]
            parsed_json = json.loads(response_text.strip())
            
            if metadata.get("pdf_pages_ignored"):
                parsed_json["extraction_notes"] = f"Warning: {metadata['pdf_pages_ignored']} extra PDF pages were ignored. " + parsed_json.get("extraction_notes", "")
                
            return {
                "parsed_recipe": parsed_json,
                "recipe_title": parsed_json.get("title"),
                "ingredients": parsed_json.get("ingredients", []),
                "steps": parsed_json.get("steps", []),
                "servings": parsed_json.get("servings"),
                "extraction_method": "tesseract"
            }
        except Exception as e:
            return {"error": f"Tesseract LLM fallback failed: {str(e)}", "extraction_method": "failed"}

    # Vision LLM path
    base64_image = image_to_base64(processed_bytes)
    llm = get_vision_llm()
    
    message = HumanMessage(
        content=build_vision_parsing_prompt(),
        additional_kwargs={"images": [base64_image]}
    )
    
    try:
        response = await llm.ainvoke([message])
        response_text = response.content.strip()
        if response_text.startswith("```json"): response_text = response_text[7:]
        if response_text.startswith("```"): response_text = response_text[3:]
        if response_text.endswith("```"): response_text = response_text[:-3]
        parsed_json = json.loads(response_text.strip())
        
        extraction_method = "vision_llm"
        
        if parsed_json.get("ocr_confidence") == "low" and not parsed_json.get("ingredients"):
            enhanced_bytes = enhance_for_ocr(processed_bytes)
            enhanced_base64 = image_to_base64(enhanced_bytes)
            
            retry_message = HumanMessage(
                content=build_vision_parsing_prompt(),
                additional_kwargs={"images": [enhanced_base64]}
            )
            retry_response = await llm.ainvoke([retry_message])
            retry_text = retry_response.content.strip()
            if retry_text.startswith("```json"): retry_text = retry_text[7:]
            if retry_text.startswith("```"): retry_text = retry_text[3:]
            if retry_text.endswith("```"): retry_text = retry_text[:-3]
            parsed_json = json.loads(retry_text.strip())
            
            if not parsed_json.get("ingredients"):
                return {"parsing_error": f"Vision LLM failed to extract ingredients. Model notes: {parsed_json.get('extraction_notes')}", "extraction_method": "vision_llm"}
                
        if metadata.get("pdf_pages_ignored"):
            parsed_json["extraction_notes"] = f"Warning: {metadata['pdf_pages_ignored']} extra PDF pages were ignored. " + parsed_json.get("extraction_notes", "")
        
        return {
            "parsed_recipe": parsed_json,
            "recipe_title": parsed_json.get("title"),
            "ingredients": parsed_json.get("ingredients", []),
            "steps": parsed_json.get("steps", []),
            "servings": parsed_json.get("servings"),
            "extraction_method": extraction_method
        }
    except Exception as e:
        return {"error": f"Vision parsing failed: {str(e)}", "extraction_method": "failed"}
