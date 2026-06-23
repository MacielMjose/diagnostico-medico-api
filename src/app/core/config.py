from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    model_path: str = "./models"
    llm_api_key: str = ""
    llm_model: str = "gpt-4"
    log_level: str = "INFO"
    max_image_size_mb: int = 10
