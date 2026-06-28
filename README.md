# 🧂 Salt to Taste

## 1. Project Overview
**Salt to Taste** is an intelligent, full-stack culinary application designed to help home cooks precisely scale, measure, and adjust the salt and sodium content in their recipes. 

Many recipes suffer from the "salt to taste" ambiguity problem—leaving cooks guessing how much salt to add, especially when scaling recipes up or down. Salt to Taste solves this by providing mathematically perfect, personalized salt measurements. 

**Key Differentiators:**
- **100% Local AI:** No cloud API costs or data privacy concerns. Powered entirely by local models via Ollama.
- **Personalized Machine Learning:** Uses contextual bandit algorithms to learn your unique palate over time, adjusting recommendations based on your feedback.
- **Holistic Sodium Tracking:** Identifies hidden sodium in ingredients (like soy sauce or parmesan) and tracks your daily intake against American Heart Association (AHA) guidelines.

## 2. Architecture Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│  Next.js (PWA)  │ ◄───► │  FastAPI (API)  │ ◄───► │   PostgreSQL    │
│  Frontend (UI)  │       │ Backend Server  │       │    Database     │
│                 │       │                 │       │                 │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │
         │                         ▼
         │               ┌───────────────────┐      ┌─────────────────┐
         │               │    LangGraph      │      │     Ollama      │
         │               │                   │◄────►│  (Local LLMs:   │
         │               │ 1. Parsing Agent  │      │  gemma3,        │
         │               │ 2. Culinary       │      │  deepseek-r1:8b,│
         │               │    Analyst        │      │  gemma4:e4b)    │
         │               │ 3. Personalization│      │                 │
         │               └─────────┬─────────┘      └─────────────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ User Rating     │       │ Vowpal Wabbit   │
│ (Too Salty,     │ ───►  │ Contextual      │ ───► Updates Palate Profile
│ Perfect, etc.)  │       │ Bandit Model    │      (Adjusts future salt)
└─────────────────┘       └─────────────────┘
```

## 3. Tech Stack

| Technology | Purpose |
|------------|---------|
| **Next.js 14** | Frontend framework (App Router) |
| **Tailwind CSS** | Styling and responsive design |
| **Zustand** | Client-side state management |
| **FastAPI** | High-performance Python backend |
| **SQLAlchemy + Alembic** | ORM and database migrations |
| **LangGraph** | AI agent orchestration and pipeline flow |
| **Ollama** | Local LLM execution engine |
| **gemma3 / deepseek-r1:8b / gemma4:e4b** | Local LLMs for text, analysis, and vision/OCR |
| **Vowpal Wabbit** | Contextual bandit ML for personalization |
| **PostgreSQL (Neon)** | Relational database |
| **Tesseract** | OCR fallback for legacy image processing |

## 4. Features List
- **Multi-modal recipe input**: Import by pasting text, a URL, or a cookbook photo.
- **Hidden sodium detection**: Checks against a database of 18 naturally salty ingredients.
- **Salt type converter**: Seamlessly convert between Diamond Crystal, Morton, Fine Sea Salt, Table Salt, and Maldon.
- **Salty Swap**: Mid-cook recalculation if you add a salty ingredient (e.g., parmesan or miso) to the pot.
- **Rescue Protocol**: Smart recovery strategies for over-salted dishes.
- **Sub-linear dynamic scaling**: Scales salt based on dish type (e.g., soups vs. breads) rather than naive multiplication.
- **Low-sodium mode**: Automatically suggests herb and spice substitutions.
- **Vowpal Wabbit contextual bandit**: Learns your per-user palate and adjusts salt recommendations dynamically.
- **Daily sodium tracking**: Tracks your rolling 24-hour sodium intake against AHA guidelines.
- **Per-ingredient sodium breakdown**: See exactly where the sodium in your dish is coming from.
- **PWA support**: Installable on your mobile home screen.

## 5. Project Structure

```text
salt-to-taste/
├── backend/
│   ├── app/
│   │   ├── agents/        # LangGraph agent nodes
│   │   ├── api/           # FastAPI route handlers
│   │   ├── core/          # Config, DB engine, Ollama factory
│   │   ├── graphs/        # LangGraph pipeline definitions
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # Business logic layer
│   │   └── utils/         # Image processing, OCR
│   ├── alembic/           # Database migrations
│   ├── models/            # Vowpal Wabbit .vw model files (gitignored)
│   └── tests/             # 63 pytest tests
└── frontend/
    └── src/
        ├── app/           # Next.js App Router pages
        ├── components/    # Reusable UI components
        ├── lib/           # API client, utilities, TypeScript types
        └── store/         # Zustand state stores
```

## 6. Prerequisites
Before setting up the project, ensure you have the following installed:
- Python 3.11+
- Node.js 20+
- Poetry
- Ollama (ollama.com)
- Tesseract OCR
- Poppler (for PDF support)
- PostgreSQL via Neon or Supabase (free tier)
- NVIDIA GPU recommended (CUDA for Ollama acceleration)

## 7. Installation & Setup

```bash
# 1. Clone and navigate
git clone <repo>
cd salt-to-taste

# 2. Pull AI models
ollama pull gemma3
ollama pull deepseek-r1:8b
ollama pull gemma4:e4b

# 3. Backend setup
cd backend
poetry install
cp .env.example .env
# Edit .env with your DATABASE_URL from Neon/Supabase

# 4. Run migrations
poetry run alembic upgrade head

# 5. Start backend
poetry run uvicorn app.main:app --port 8000 --reload

# 6. Frontend setup (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your user ID

# 7. Start frontend
npm run dev
```

## 8. Environment Variables

### Backend (`backend/.env`)
| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `SECRET_KEY` | Random secret for signing | `any random string` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `PARSING_MODEL` | Text parsing model | `gemma3` |
| `ANALYSIS_MODEL` | Culinary analysis model | `deepseek-r1:8b` |
| `VISION_MODEL` | Vision/OCR model | `gemma4:e4b` |

### Frontend (`frontend/.env.local`)
| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_DEFAULT_USER_ID` | User UUID for MVP | `14cc53c8-...` |

## 9. API Reference

- **Recipes:**
  - `POST /recipes` - Parse text/URL recipe
  - `POST /recipes/image-upload` - Parse image/PDF recipe
  - `GET /recipes/{id}` - Get parsed recipe details
  - `POST /recipes/{id}/scale` - Scale recipe servings
  - `GET /recipes/{id}/sodium-breakdown` - Get ingredient sodium breakdown
- **Salt:**
  - `GET /salt-types` - List available salt types
  - `POST /salt/convert` - Convert between salt types
  - `POST /salt/convert-all` - Convert an amount to all salt types
- **Recommendations:**
  - `POST /recommendations/salty-swap` - Recalculate salt for added ingredients
  - `POST /recommendations/rescue` - Rescue an over-salted dish
- **Feedback:**
  - `POST /feedback` - Submit palate rating for a recipe
- **Palate:**
  - `GET /palate/{user_id}` - Get current user palate profile
  - `GET /palate/{user_id}/history` - Get user feedback history
  - `DELETE /palate/{user_id}/reset` - Reset user palate profile
- **Health:**
  - `GET /health/sodium-report/{user_id}` - Get 24-hour sodium report
  - `GET /health/daily-log/{user_id}` - Get daily sodium log entries
  - `PATCH /health/sodium-limit/{user_id}` - Update daily sodium limit
- **Users:**
  - `POST /users` - Create a new user
  - `GET /users/{user_id}` - Get user details
  - `PATCH /users/{user_id}` - Update user preferences (e.g., low-sodium mode)

## 10. Running Tests

```bash
cd backend
poetry run pytest tests/ -v
# 63 tests — runs full LLM pipeline tests, expect ~3 minutes
```

## 11. How the ML Works

Salt to Taste uses a **Contextual Bandit** (powered by Vowpal Wabbit) to learn your palate. 

When a recipe is analyzed, the model evaluates the dish type and cooking method (the "context") and chooses one of three actions:
- **Decrease Salt (0.82x)**
- **Keep Baseline (1.0x)**
- **Increase Salt (1.18x)**

After you cook and eat the meal, you rate it (e.g., "Too Salty", "Perfect", "Needs More"). This rating is sent back to the model as a reward or penalty. The model uses an **epsilon-greedy exploration** strategy to balance learning and exploiting known preferences. New users have an epsilon of 0.2 (20% chance to test a random multiplier to learn faster), which decays to 0.1 for experienced users.

Model files are securely stored locally at `backend/models/{user_id}.vw`. The calculated palate weights are also mirrored to the PostgreSQL database for quick retrieval and UI display.

## 12. Roadmap
- 🔒 Auth (NextAuth.js with Google login)
- 🚀 Deployment (Vercel + Railway)
- ⚡ Streaming responses via Server-Sent Events
- 🔄 Parallel LangGraph node execution for faster pipeline
- 📱 Offline mode via service worker caching

## 13. License
MIT
