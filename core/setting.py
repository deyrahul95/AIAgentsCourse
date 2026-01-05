from functools import lru_cache
from dotenv import load_dotenv
import os

load_dotenv()


class Setting:
    OPENROUTER_API_KEY: str = os.getenv(key="OPENROUTER_API_KEY", default="")
    OPENROUTER_API_URL: str = os.getenv(
        key="OPENROUTER_API_URL", default="https://openrouter.ai/api/v1"
    )
    OPENROUTER_MODEL: str = os.getenv(
        key="OPENROUTER_MODEL", default="openai/gpt-oss-120b:free"
    )


@lru_cache()
def get_settings() -> Setting:
    return Setting()
