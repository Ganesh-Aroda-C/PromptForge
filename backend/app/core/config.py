import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    APP_NAME: str = "PromptForge AI"
    APP_ENV: str = "development"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "promptforge_ai"
    
    # Model Providers
    LLM_PROVIDER: str = "mock"  # "mock", "gemini", "openai", "huggingface"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    
    DIFFUSION_PROVIDER: str = "demo"  # "demo", "diffusers", "huggingface", "openai"
    DIFFUSION_MODEL: str = "stabilityai/stable-diffusion-xl-base-1.0"
    
    EVALUATION_PROVIDER: str = "heuristic"  # "heuristic", "blip", "clip", "api"
    
    # Paths
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    STORAGE_DIR: str = os.path.join(BASE_DIR, "backend/data/storage")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "backend/data/uploads")
    


settings = Settings()

# Ensure directories exist
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
