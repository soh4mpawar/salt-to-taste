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
