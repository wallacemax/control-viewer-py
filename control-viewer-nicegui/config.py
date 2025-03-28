"""
Configuration module for the Control Viewer application
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "{SOME NAME}"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "A web application for viewing and manipulating instrument control charts"
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    DEBUG: bool = True
    
    # Database settings (for future implementation)
    DB_URL: str = os.getenv("DB_URL", "")
    
    # Security settings
    API_KEY: str = os.getenv("API_KEY", "")
    ENABLE_AUTH: bool = False
    
    # Logging settings
    LOG_LEVEL: str = "WARN"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()