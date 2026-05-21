from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FieldTech RAG"
    debug: bool = True

    # OpenAI (optional — falls back to keyword search)
    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # Chroma
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "field_manuals"

    # S3 / MinIO
    s3_endpoint: str | None = "http://localhost:9000"
    s3_bucket: str = "fieldmanuals"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_region: str = "us-east-1"
    use_local_storage: bool = True
    local_storage_path: str = "./storage"

    # Cognito (dev mode uses mock JWT)
    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str | None = None
    cognito_app_client_id: str | None = None
    auth_dev_mode: bool = True

    database_url: str = "sqlite+aiosqlite:///./fieldtech.db"


settings = Settings()
