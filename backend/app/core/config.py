from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Learning & Study Assistant"
    api_prefix: str = "/api"
    database_url: str = Field(default="sqlite:///./study_assistant.db", alias="DATABASE_URL")
    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")
    frontend_origin_alt: str = Field(default="http://127.0.0.1:5173", alias="FRONTEND_ORIGIN_ALT")
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    llm_api_key: str | None = Field(default=None, alias="LLM_API_KEY")
    llm_model: str = Field(default="tinyllama:latest", alias="LLM_MODEL")
    llm_base_url: str = Field(default="https://api.openai.com/v1", alias="LLM_BASE_URL")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", alias="OLLAMA_BASE_URL")
    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="nomic-embed-text", alias="EMBEDDING_MODEL")
    jwt_secret_key: str = Field(default="change_this_secret", alias="JWT_SECRET_KEY")
    chroma_persist_directory: str = Field(default="./vector_db", alias="CHROMA_PERSIST_DIRECTORY")
    upload_directory: str = Field(default="./uploads", alias="UPLOAD_DIRECTORY")
    demo_user_id: str = "demo-user"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
