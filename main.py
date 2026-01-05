from core.ai_client import AIClient
from core.setting import get_settings


def main():
    client = AIClient().get_openai_client()

    response = client.chat.completions.create(
        model=get_settings().OPENROUTER_MODEL,
        messages=[
            {"role": "user", "content": "How many r's are in the word 'strawberry'?"}
        ],
        extra_body={"reasoning": {"enabled": False}},
    )

    msg = response.choices[0].message.content
    print(f"Response => {msg}")


if __name__ == "__main__":
    main()
