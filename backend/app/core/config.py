from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ArchAI"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password123"
    OPENAI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    GOOGLE_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    CLAUDE_API_KEY: str | None = None  # Alias for ANTHROPIC_API_KEY
    DATABASE_URL: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
