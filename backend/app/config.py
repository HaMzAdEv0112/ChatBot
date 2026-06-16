from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "ollama"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 4
    min_relevance_score: float = 0.35

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
