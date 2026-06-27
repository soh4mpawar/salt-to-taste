import os
from app.agents.state import RecipePipelineState

CB_ACTIONS = 3          # 1=too_salty, 2=perfect, 3=needs_more
EPSILON_NEW = 0.2       # exploration for new users
EPSILON_EXPERIENCED = 0.1  # exploration for users with >10 feedback

AHA_SODIUM_LIMIT_MG = 2300

HERB_SUGGESTIONS = {
    "soup": ["Fresh thyme", "Bay leaf", "Fresh parsley", "Lemon zest"],
    "meat": ["Smoked paprika", "Fresh rosemary", "Garlic powder", "Black pepper"],
    "roasted_vegetables": ["Za'atar", "Sumac", "Fresh lemon juice", "Nutritional yeast"],
    "pasta": ["Fresh basil", "Red pepper flakes", "Lemon zest", "Toasted pine nuts"],
    "salad": ["Fresh dill", "Lemon juice", "Dijon mustard", "Nutritional yeast"],
    "seafood": ["Fresh dill", "Capers (rinsed)", "Lemon zest", "White pepper"],
    "other": ["Lemon juice", "Fresh herbs", "Black pepper", "Garlic"],
}

def get_herb_suggestions(dish_type: str) -> list[str]:
    return HERB_SUGGESTIONS.get(dish_type, HERB_SUGGESTIONS["other"])
EPSILON_NEW = 0.2       # exploration for new users
EPSILON_EXPERIENCED = 0.1  # exploration for users with >10 feedback

ACTION_TO_MULTIPLIER = {
    1: 0.82,   # too_salty — reduce salt by 18%
    2: 1.0,    # perfect — no adjustment
    3: 1.18,   # needs_more — increase salt by 18%
}

RATING_TO_ACTION = {
    "too_salty": 1,
    "perfect": 2,
    "needs_more": 3,
}


class PalateModelManager:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

    def get_model_path(self, user_id: str) -> str:
        # Sanitize user_id to prevent path traversal
        safe_id = user_id.replace("/", "").replace("..", "").replace("\\", "")
        return os.path.join(self.model_dir, f"{safe_id}.vw")

    def model_exists(self, user_id: str) -> bool:
        return os.path.exists(self.get_model_path(user_id))

    def get_feedback_count(self, user_id: str) -> int:
        # Read from a companion .count file alongside the .vw file
        count_path = self.get_model_path(user_id) + ".count"
        if not os.path.exists(count_path):
            return 0
        try:
            with open(count_path, "r") as f:
                return int(f.read().strip())
        except:
            return 0

    def increment_feedback_count(self, user_id: str) -> int:
        count = self.get_feedback_count(user_id) + 1
        count_path = self.get_model_path(user_id) + ".count"
        with open(count_path, "w") as f:
            f.write(str(count))
        return count

    def get_epsilon(self, user_id: str) -> float:
        count = self.get_feedback_count(user_id)
        return EPSILON_EXPERIENCED if count > 10 else EPSILON_NEW

def build_vw_features(
    dish_type: str,
    cooking_method: str,
    baseline_grams: float,
    servings: int
) -> str:
    servings = max(servings or 1, 1)
    baseline_normalized = round(baseline_grams / servings, 4)
    # VW format: |namespace feature=value feature2=value2
    return (
        f"|dish dish_type={dish_type.replace(' ', '_')} "
        f"|method cooking_method={cooking_method.replace(' ', '_')} "
        f"|quantity baseline_norm={baseline_normalized}"
    )

async def get_palate_adjustment(
    user_id: str,
    dish_type: str,
    cooking_method: str,
    baseline_grams: float,
    servings: int,
    model_manager: PalateModelManager
) -> tuple[float, int]:
    """Returns (multiplier, chosen_action)"""
    if not model_manager.model_exists(user_id):
        return 1.0, 2  # no model yet — assume perfect

    features = build_vw_features(dish_type, cooking_method, baseline_grams, servings)
    model_path = model_manager.get_model_path(user_id)

    try:
        import vowpalwabbit
        # Load existing model for prediction only (-i = input model, no saving)
        vw = vowpalwabbit.Workspace(
            f"--cb {CB_ACTIONS} --quiet -i {model_path}",
            enable_logging=False
        )
        # VW CB predict format: "| features"
        prediction = vw.predict(f"| {features}")
        print(f"VW PREDICTION TYPE: {type(prediction)}, VALUE: {prediction}")
        vw.finish()

        chosen_action = int(prediction) if prediction in [1, 2, 3] else 2
        multiplier = ACTION_TO_MULTIPLIER.get(chosen_action, 1.0)
        return multiplier, chosen_action

    except Exception as e:
        import logging
        logging.warning(f"VW prediction failed for user {user_id}: {e}")
        return 1.0, 2  # safe fallback

async def record_feedback(
    user_id: str,
    dish_type: str,
    cooking_method: str,
    baseline_grams: float,
    servings: int,
    rating: str,
    model_manager: PalateModelManager
) -> tuple[bool, int]:
    """Returns (success, new_feedback_count)"""
    action = RATING_TO_ACTION.get(rating, 2)
    features = build_vw_features(dish_type, cooking_method, baseline_grams, servings)
    model_path = model_manager.get_model_path(user_id)

    try:
        import vowpalwabbit
        epsilon = model_manager.get_epsilon(user_id)

        if model_manager.model_exists(user_id):
            # Continue training existing model
            vw = vowpalwabbit.Workspace(
                f"--cb {CB_ACTIONS} --epsilon {epsilon} --quiet "
                f"-i {model_path} -f {model_path}",
                enable_logging=False
            )
        else:
            # Initialize new model for this user
            vw = vowpalwabbit.Workspace(
                f"--cb {CB_ACTIONS} --epsilon {epsilon} --quiet "
                f"-f {model_path}",
                enable_logging=False
            )
            # Initialize intercept so actions default to cost > 0
            init_prob = round(1.0 / CB_ACTIONS, 4)  # = 0.3333
            for a in range(1, CB_ACTIONS + 1):
                vw.learn(f"{a}:1.0:{init_prob} |")

        # The action IS what should have been done — train it with cost 0.0
        probability = 1.0 / CB_ACTIONS  # uniform exploration

        # Cost 0.0 = this was the right action to take
        cb_example = f"{action}:0.0:{probability} | {features}"
        vw.learn(cb_example)
        vw.finish()

        new_count = model_manager.increment_feedback_count(user_id)
        return True, new_count

    except Exception as e:
        import logging
        logging.error(f"VW training failed for user {user_id}: {e}")
        return False, model_manager.get_feedback_count(user_id)

async def personalization_node(state: RecipePipelineState) -> dict:
    if state.get("analysis_error"):
        return {"pipeline_stage": "personalization_skipped"}

    model_manager = PalateModelManager(model_dir="models")
    baseline = state.get("baseline_salt_grams") or 0.5
    user_id = state.get("user_id", "anonymous")
    dish_type = state.get("dish_type") or "other"
    cooking_method = state.get("cooking_method") or "raw"
    servings = state.get("servings") or 1

    multiplier, chosen_action = await get_palate_adjustment(
        user_id, dish_type, cooking_method, baseline, servings, model_manager
    )

    personalized_grams = round(baseline * multiplier, 2)
    personalized_grams = max(personalized_grams, 0.5)  # clamp minimum

    sodium_mg = (personalized_grams * 1000 * 0.393) / max(servings, 1)

    # Check if user has low_sodium_mode enabled (passed via state)
    low_sodium_mode = state.get("low_sodium_mode", False)
    sodium_mg_total = sodium_mg * max(servings, 1)

    low_sodium_warning = None
    herb_suggestions = []

    # Get effective sodium limit for this user
    effective_limit = state.get("user_sodium_limit_mg") or AHA_SODIUM_LIMIT_MG
    limit_source = "user_custom" if state.get("user_sodium_limit_mg") else "aha_default"

    if sodium_mg > effective_limit * 0.30:  # >30% of daily limit in one serving
        low_sodium_warning = f"This serving contains {round(sodium_mg, 0)}mg sodium ({round(sodium_mg/(effective_limit/100), 1)}% of daily limit)"

    if low_sodium_mode:
        # Scale down to hit 25% of effective limit per serving max
        target_sodium_per_serving = effective_limit * 0.25  # 575mg default
        if sodium_mg > target_sodium_per_serving:
            reduction_factor = target_sodium_per_serving / sodium_mg
            personalized_grams = round(personalized_grams * reduction_factor, 2)
            sodium_mg = target_sodium_per_serving
            herb_suggestions = get_herb_suggestions(dish_type)

    return {
        "personalized_salt_grams": personalized_grams,
        "sodium_mg_per_serving": round(sodium_mg, 1),
        "recommended_salt_type": "Diamond Crystal Kosher",
        "low_sodium_warning": low_sodium_warning,
        "herb_suggestions": herb_suggestions,
        "recommendation_context": {
            "dish_type": dish_type,
            "cooking_method": cooking_method,
            "hidden_sodium_mg": state.get("hidden_sodium_mg") or 0.0,
            "adjustment_multiplier": multiplier,
            "chosen_action": chosen_action,
            "feedback_count": model_manager.get_feedback_count(user_id),
        },
        "pipeline_stage": "complete"
    }
