from langgraph.graph import StateGraph, END
from app.agents.state import RecipePipelineState
from app.agents.parsing_agent import parsing_agent_node
from app.agents.culinary_analyst import culinary_analyst_node
from app.agents.personalization_engine import personalization_node

def should_run_analysis(state: RecipePipelineState) -> str:
    if state.get("parsing_error"):
        return "end"
    return "culinary_analyst"

def should_run_personalization(state: RecipePipelineState) -> str:
    if state.get("analysis_error"):
        return "end"
    return "personalization"

def build_recipe_pipeline():
    graph = StateGraph(RecipePipelineState)

    graph.add_node("parsing_agent", parsing_agent_node)
    graph.add_node("culinary_analyst", culinary_analyst_node)
    graph.add_node("personalization", personalization_node)

    graph.set_entry_point("parsing_agent")

    graph.add_conditional_edges(
        "parsing_agent",
        should_run_analysis,
        {"culinary_analyst": "culinary_analyst", "end": END}
    )
    graph.add_conditional_edges(
        "culinary_analyst",
        should_run_personalization,
        {"personalization": "personalization", "end": END}
    )
    graph.add_edge("personalization", END)

    return graph.compile()

recipe_pipeline = build_recipe_pipeline()

async def run_recipe_pipeline(
    raw_input: str,
    input_type: str,
    user_id: str,
    image_bytes: bytes = None
) -> RecipePipelineState:
    initial_state = {
        "raw_input": raw_input,
        "input_type": input_type,
        "user_id": user_id,
        "image_bytes": image_bytes,
        "errors": [],
        "pipeline_stage": "starting",
        "parsed_recipe": None,
        "recipe_title": None,
        "ingredients": None,
        "steps": None,
        "servings": None,
        "parsing_error": None,
        "total_mass_grams": None,
        "hidden_sodium_mg": None,
        "baseline_salt_grams": None,
        "dish_type": None,
        "cooking_method": None,
        "evaporation_factor": None,
        "analysis_notes": None,
        "analysis_error": None,
        "personalized_salt_grams": None,
        "sodium_mg_per_serving": None,
        "recommended_salt_type": None,
        "recommendation_context": None,
        "personalization_error": None,
    }
    result = await recipe_pipeline.ainvoke(initial_state)
    return result
