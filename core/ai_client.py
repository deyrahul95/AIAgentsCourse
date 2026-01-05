from openai import OpenAI

from core.setting import get_settings


class AIClient:
    def __init__(self) -> None:
        self.openai_client = OpenAI(
            base_url=get_settings().OPENROUTER_API_URL,
            api_key=get_settings().OPENROUTER_API_KEY,
        )

    def get_openai_client(self) -> OpenAI:
        return self.openai_client
