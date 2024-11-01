from pydantic_settings import BaseSettings

class NeMoConfig(BaseSettings):
    NEMO_MODEL_PATH: str = "nvidia/nemo-multimodal-large"
    NEMO_CACHE_DIR: str = "./cache"
    MAX_INPUT_LENGTH: int = 1024
    MAX_OUTPUT_LENGTH: int = 512
    BATCH_SIZE: int = 1
    TEMPERATURE: float = 0.7
    TOP_K: int = 50
    TOP_P: float = 0.9
    
    class Config:
        env_prefix = "NEMO_"