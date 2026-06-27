from langchain_ollama import ChatOllama
from app.core.config import settings

def get_parsing_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.PARSING_MODEL,
        temperature=0.1,
        format="json"
    )

def get_analysis_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.ANALYSIS_MODEL,
        temperature=0.1
    )

def get_vision_llm() -> ChatOllama:
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.VISION_MODEL,
        temperature=0.1,
        format="json"
    )
