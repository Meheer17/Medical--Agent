from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    """Application configuration from environment variables"""
    
    # Database (MongoDB)
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "cliniq_db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, v):
        # Some environments set DEBUG=release (string). Treat release/prod as False.
        if isinstance(v, bool) or v is None:
            return v
        if isinstance(v, str):
            s = v.strip().lower()
            if s in {"1", "true", "t", "yes", "y", "on", "debug", "dev", "development"}:
                return True
            if s in {"0", "false", "f", "no", "n", "off", "release", "prod", "production"}:
                return False
        raise ValueError(f"Invalid DEBUG value: {v!r}")
    
    # AI/LLM Configuration
    # Google AI API Key for Genkit integration
    GOOGLE_AI_API_KEY: str = ""
    GENAI_API_KEY: str = ""  # Alternative env var
    
    # PDF Processing
    PDF_MAX_SIZE: int = 52428800  # 50MB default
    PDF_EXTRACTION_TIMEOUT: int = 30  # 30 seconds

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
