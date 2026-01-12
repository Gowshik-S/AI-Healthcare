"""
Application configuration using environment variables.
Loads settings from .env file - NO hardcoded defaults for sensitive values.
"""
import os
import logging
from typing import List
from functools import lru_cache

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )
    
    # CORS - parse comma-separated origins
    _cors_origins = os.getenv("CORS_ORIGINS", "")
    CORS_ORIGINS: List[str] = [
        origin.strip() 
        for origin in _cors_origins.split(",") 
        if origin.strip()
    ]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.DATABASE_URL.startswith("sqlite")
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.DATABASE_URL.startswith("postgresql")
    
    def validate(self) -> None:
        """
        Validate required settings.
        Raises ValueError if configuration is invalid.
        """
        errors = []
        
        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        
        if not self.SECRET_KEY:
            errors.append("SECRET_KEY is required")
        elif len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters")
        
        if self.is_production:
            if self.is_sqlite:
                logging.warning("⚠️  SQLite is not recommended for production")
            if self.DEBUG:
                logging.warning("⚠️  DEBUG mode is enabled in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    def log_config(self) -> None:
        """Log current configuration (without sensitive values)."""
        db_type = "PostgreSQL" if self.is_postgresql else "SQLite" if self.is_sqlite else "Unknown"
        logging.info(f"📦 Database: {db_type}")
        logging.info(f"🌍 Environment: {self.ENVIRONMENT}")
        logging.info(f"🔗 CORS Origins: {len(self.CORS_ORIGINS)} configured")
        logging.info(f"🖥️  Server: {self.HOST}:{self.PORT}")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate()
    return settings


# Global settings instance
settings = get_settings()
