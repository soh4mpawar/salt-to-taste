# Salt to Taste

This project is a Python/FastAPI backend connected to PostgreSQL. The backend will eventually integrate with LangGraph, Ollama (local LLM inference), and Vowpal Wabbit.

## Agent Guidelines & Codebase Rules

When working on this project, adhere to the following rules:

- **Python Code**: All Python code must reside in the `/backend` directory.
- **Database Migrations**: All database migrations are to be handled by Alembic.
- **Environment Variables**: Environment variables are stored in a `.env` file at the project root. This file must **never** be committed to version control.
- **Database Access**: The primary database is PostgreSQL. Access it via the SQLAlchemy async engine using the `asyncpg` driver.
- **Data Validation**: Always use Pydantic v2 for all data validation and schema definitions.

**Verification rule**: When asked to run a command and check the result, always paste raw terminal output into an Artifact before writing any analysis. Never describe what you expect the output to be. If a command fails, stop and report the error — do not attempt to fix it unless explicitly instructed.

## Phase 2 — Agent Pipeline
- Agent orchestration uses LangGraph with TypedDict state
- All agents live in `backend/app/agents/` folder
- LangGraph graph definitions live in `backend/app/graphs/`
- Agent state schemas live in `backend/app/agents/state.py`
- Ollama is accessed via langchain-ollama ChatOllama class
- Parsing Agent uses gemma3 model
- Culinary Analyst uses deepseek-r1:8b model
- Personalization Engine uses Vowpal Wabbit (vowpalwabbit library)
- All agent functions must be async
- Never hardcode model names — always read from app.core.config settings
- LangGraph nodes return dicts with only the keys they modify

## Phase 3 — Multimodal Input
- Vision model is gemma3:12b accessed via Ollama
- Vision model config key: VISION_MODEL in app/core/config.py
- Image processing utilities live in app/utils/image_processing.py
- OCR fallback utilities live in app/utils/ocr_fallback.py
- Multimodal agent node lives in app/agents/parsing_agent.py (extended, not a new file)
- Image uploads are handled by app/api/recipes.py via FastAPI UploadFile
- Supported input formats: JPEG, PNG, WEBP, PDF (single page)
- All images are preprocessed before LLM: resize to max 1568px, convert to JPEG, base64 encode
- Tesseract is used as fallback when vision model confidence is low
- Never store raw image bytes in the database — store only extracted text and metadata

## Phase 4 — ML Personalization Engine
- Vowpal Wabbit (VW) is the contextual bandit library
- VW binary model files are stored at backend/models/{user_id}.vw
- VW model files must NEVER be committed to git
- Palate weights are mirrored to PostgreSQL in the palate_profiles table after every feedback update
- The contextual bandit has 3 actions: 1=too_salty, 2=perfect, 3=needs_more
- Cost mapping: perfect=0.0 (best), too_salty=1.0, needs_more=1.0
- Exploration probability (epsilon): 0.2 for new users, 0.1 for users with >10 feedback entries
- Context features: dish_type, cooking_method, baseline_normalized (baseline_grams/servings)
- All VW operations must be wrapped in try/except — never crash the API on VW failure
- The personalization_engine.py in app/agents/ is the canonical location for all VW logic
- Feedback endpoint: POST /api/v1/feedback accepts FeedbackCreate schema
- After recording feedback, always update both the .vw file AND the palate_profiles DB row

## Phase 5 — Culinary Feature Layer
- All Phase 5 features are pure Python math — no LLM calls
- Salt conversion logic lives in app/services/salt_service.py
- Salty Swap logic lives in app/services/swap_service.py
- Rescue Protocol logic lives in app/services/rescue_service.py
- Scaling logic lives in app/services/scaling_service.py
- All services are stateless pure functions — no DB writes except where noted
- Salt type data comes from the salt_types DB table, not hardcoded
- Rescue Protocol uses a static knowledge base dict, not an LLM
- All endpoints replace existing Phase 1 stubs — do not create new route files
- Salty Swap updates the existing recommendation row in DB after recalculation
- Dynamic scaling does NOT create new DB rows — returns calculated values only

## Phase 6 — Health & Dietary Features
- User custom sodium limit lives in users.sodium_daily_limit_mg (nullable integer)
- Default AHA limit (2300mg) is used when sodium_daily_limit_mg is null
- Daily sodium tracking lives in app/services/sodium_tracking_service.py
- Sodium tracking is per user per calendar date (UTC)
- Ingredient sodium breakdown lives in app/services/sodium_breakdown_service.py
- Dietary compliance report endpoint: GET /health/sodium-report/{user_id}
- Daily sodium log endpoint: GET /health/daily-log/{user_id}
- All health endpoints are in app/api/health.py
- AHA_SODIUM_LIMIT_MG constant lives in personalization_engine.py — import from there, never redefine
- sodium_daily_limit_mg of 0 means "use AHA default" not "zero sodium"
