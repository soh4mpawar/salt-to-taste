# Salt to Taste

Salt to Taste is an intelligent, full-stack culinary application designed to help home cooks precisely scale, measure, and adjust the salt and sodium content in their recipes. Using a powerful combination of LLM-based parsing, personalized palate profiling, and sub-linear scaling algorithms, it ensures your food is perfectly seasoned and tailored to your dietary needs.

## Features

- **Multi-Modal Recipe Input**: Import recipes by pasting a URL, uploading a photo/screenshot (powered by OCR and Vision LLMs), or pasting plain text.
- **Intelligent Parsing & Analysis**: Powered by LangGraph agents (Llama 3 via Ollama) that break down the recipe, identify hidden sodium sources (like soy sauce or parmesan), and estimate the total mass and dish type.
- **Personalized Salt Recommendations**: Uses a Vowpal Wabbit contextual bandit model to learn your salt preferences over time, adapting to how you rate past meals (e.g., "too salty" or "perfect").
- **Sub-Linear Scaling**: Going from 2 servings to 8? Salt shouldn't scale linearly. The app uses specialized exponents based on the dish type (soups vs. breads vs. roasted vegetables) to recommend the mathematically perfect amount of salt.
- **Salty Swap & Rescue**: Added extra salty ingredients mid-cook? Or accidentally over-salted the dish? The app recalculates and offers recovery strategies on the fly.
- **Sodium Health Tracking**: Provides an AHA-compliant dashboard tracking your rolling 24-hour sodium intake to help you stay within healthy limits.

## Tech Stack

### Frontend
- **Framework**: Next.js 14 App Router (React)
- **Styling**: Tailwind CSS
- **State Management**: Zustand & React Query
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **AI/LLM**: LangGraph, LangChain, Ollama (Llama 3 8B), Tesseract OCR
- **Database**: PostgreSQL (SQLAlchemy) with async asyncpg
- **Machine Learning**: Vowpal Wabbit for reinforcement learning and palate profiling

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.12+)
- PostgreSQL database
- Ollama with the `llama3` model installed locally

### Backend Setup
1. Navigate to the `backend` directory.
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Copy `.env.example` to `.env` and configure your PostgreSQL database URL.
4. Run the development server:
   ```bash
   poetry run uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Next.js development server:
   ```bash
   npm run dev
   ```

## Architecture

For a detailed breakdown of the AI pipelines, the contextual bandit personalization, and the data schema, see [ARCHITECTURE.md](ARCHITECTURE.md).

## License

MIT License
