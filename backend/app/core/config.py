import os
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine the path to the .env file at the project root
env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    PARSING_MODEL: str = "gemma3"
    ANALYSIS_MODEL: str = "deepseek-r1:8b"
    VISION_MODEL: str = "gemma4:e4b"
    VW_MODEL_PATH: str = "models/palate.vw"
    MAX_IMAGE_DIMENSION: int = 1568
    IMAGE_QUALITY: int = 85
    TESSERACT_CONFIDENCE_THRESHOLD: float = 60.0
    MAX_UPLOAD_SIZE_MB: int = 10
    
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8", extra="ignore")

settings = Settings()
