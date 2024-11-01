from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # NeMo
    NEMO_MODEL_PATH: str
    NEMO_CACHE_DIR: str
    
    # Snowflake
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: str
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_WAREHOUSE: str
    SNOWFLAKE_DATABASE: str
    SNOWFLAKE_SCHEMA: str
    
    # Storage
    VECTOR_STORE_PATH: str = "./data/vector_store"
    
    class Config:
        env_file = ".env"