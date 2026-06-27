from typing import TypedDict, Annotated, Optional
import operator

class RecipePipelineState(TypedDict):
    # Input
    raw_input: str                    # raw recipe text or URL
    input_type: str                   # "url", "text", or "image"
    user_id: str                      # UUID string

    # Parsing Agent outputs
    parsed_recipe: Optional[dict]     # structured recipe JSON
    recipe_title: Optional[str]
    ingredients: Optional[list]       # list of {name, amount, unit}
    steps: Optional[list]             # cooking steps as strings
    servings: Optional[int]
    parsing_error: Optional[str]
    image_bytes: Optional[bytes]          # raw uploaded image bytes
    extraction_method: Optional[str]      # "tesseract", "vision_llm", or "text"

    # Culinary Analyst outputs
    total_mass_grams: Optional[float]
    hidden_sodium_mg: Optional[float]
    baseline_salt_grams: Optional[float]
    dish_type: Optional[str]          # e.g. "roasted_vegetables", "seafood", "soup"
    cooking_method: Optional[str]     # e.g. "simmer", "roast", "raw"
    evaporation_factor: Optional[float]
    analysis_notes: Optional[str]
    analysis_error: Optional[str]

    # Personalization Engine outputs
    personalized_salt_grams: Optional[float]
    sodium_mg_per_serving: Optional[float]
    recommended_salt_type: Optional[str]
    recommendation_context: Optional[dict]
    personalization_error: Optional[str]

    # Pipeline metadata
    errors: Annotated[list[str], operator.add]
    pipeline_stage: str               # tracks current stage for debugging

    low_sodium_mode: Optional[bool]        # from user profile
    low_sodium_warning: Optional[str]      # populated by personalization node
    herb_suggestions: Optional[list[str]]  # populated if low_sodium_mode active
    user_sodium_limit_mg: Optional[int]    # user's personal limit, None = use AHA default
    sodium_limit_source: Optional[str]     # "user_custom" or "aha_default"
