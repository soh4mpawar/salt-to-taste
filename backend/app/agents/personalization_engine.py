import os
import logging
from typing import Optional
from app.agents.state import RecipePipelineState
from app.core.config import settings

try:
    import vowpalwabbit
except ImportError:
    vowpalwabbit = None

logger = logging.getLogger(__name__)

class PalateModelManager:
    def __init__(self, model_dir: str):
        self.model_dir = model_dir
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)

    def get_model_path(self, user_id: str) -> str:
        return os.path.join(self.model_dir, f"{user_id}.vw")

    def model_exists(self, user_id: str) -> bool:
        return os.path.exists(self.get_model_path(user_id))

    def get_vw_args(self, user_id: str) -> list[str]:
        return ["--cb", "3", "--quiet", "-f", self.get_model_path(user_id)]

def build_vw_features(dish_type: str, cooking_method: str, baseline_grams: float, servings: int) -> str:
    normalized = round(baseline_grams / max(1, servings), 3)
    return f"|dish dish_type={dish_type} |method cooking_method={cooking_method} |quantity baseline_normalized={normalized}"

async def get_palate_adjustment(user_id: str, dish_type: str, cooking_method: str, baseline_grams: float, servings: int, model_manager: PalateModelManager) -> float:
    if not model_manager.model_exists(user_id) or not vowpalwabbit:
        return 1.0
        
    try:
        model_path = model_manager.get_model_path(user_id)
        vw = vowpalwabbit.Workspace(f"--quiet -i {model_path}")
        
        features = build_vw_features(dish_type, cooking_method, baseline_grams, servings)
        prediction = vw.predict(features)
        
        if isinstance(prediction, (list, tuple)):
            action = prediction[0][0] if isinstance(prediction[0], tuple) else prediction[0]
        else:
            action = prediction
            
        action_map = {1: 0.85, 2: 1.0, 3: 1.15}
        return action_map.get(int(action), 1.0)
    except Exception as e:
        logger.warning(f"VW Prediction error: {e}")
        return 1.0

async def record_feedback(user_id: str, dish_type: str, cooking_method: str, baseline_grams: float, servings: int, rating: str, model_manager: PalateModelManager) -> bool:
    if not vowpalwabbit:
        return False
        
    try:
        action_map = {"too_salty": 1, "perfect": 2, "needs_more": 3}
        cost_map = {"perfect": 0.0, "too_salty": 1.0, "needs_more": 1.0}
        
        action = action_map.get(rating, 2)
        cost = cost_map.get(rating, 0.0)
        
        features = build_vw_features(dish_type, cooking_method, baseline_grams, servings)
        cb_line = f"{action}:{cost}:0.33 {features}"
        
        args = model_manager.get_vw_args(user_id)
        if model_manager.model_exists(user_id):
            args.extend(["-i", model_manager.get_model_path(user_id)])
            
        vw = vowpalwabbit.Workspace(" ".join(args))
        vw.learn(cb_line)
        vw.finish()
        return True
    except Exception as e:
        logger.warning(f"VW Learn error: {e}")
        return False

async def personalization_node(state: RecipePipelineState) -> dict:
    if state.get("analysis_error") or state.get("parsing_error"):
        return {"pipeline_stage": "personalization_skipped"}
        
    baseline_grams = state.get("baseline_salt_grams", 0.0)
    dish_type = state.get("dish_type", "other")
    cooking_method = state.get("cooking_method", "simmer")
    servings = state.get("servings", 1) or 1
    user_id = state.get("user_id", "default")
    
    model_dir = os.path.dirname(settings.VW_MODEL_PATH) or "models"
    model_manager = PalateModelManager(model_dir=model_dir)
    
    adjustment = await get_palate_adjustment(user_id, dish_type, cooking_method, baseline_grams, servings, model_manager)
    
    personalized_grams = round(baseline_grams * adjustment, 2)
    
    sodium_mg = (personalized_grams * 1000 * 0.393) / servings
    
    context_dict = {
        "dish_type": dish_type,
        "cooking_method": cooking_method,
        "hidden_sodium_mg": state.get("hidden_sodium_mg", 0.0),
        "adjustment_multiplier": adjustment
    }
    
    return {
        "personalized_salt_grams": personalized_grams,
        "sodium_mg_per_serving": round(sodium_mg, 1),
        "recommended_salt_type": "Diamond Crystal Kosher",
        "recommendation_context": context_dict,
        "pipeline_stage": "complete"
    }
