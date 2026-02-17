from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+mysql-connector-python://root:password@localhost:3306/nithin_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Server
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # AI/LLM Configuration
    # Google AI API Key for Genkit integration
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GENAI_API_KEY: str = os.getenv("GENAI_API_KEY", "")  # Alternative env var
    
    # COMMENTED OUT - Ollama configuration (uncomment to use Ollama instead)
    # OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # PDF Processing
    PDF_MAX_SIZE: int = int(os.getenv("PDF_MAX_SIZE", 52428800))  # 50MB default
    PDF_EXTRACTION_TIMEOUT: int = int(os.getenv("PDF_EXTRACTION_TIMEOUT", 30))  # 30 seconds
    
    class Config:
        env_file = ".env"

settings = Settings()
