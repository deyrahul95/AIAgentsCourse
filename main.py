from core.ai_client import AIClient


def main():
    client = AIClient().get_llama_client()

    response = client.chat.completions.create(
        model="openai/qwen2.5",
        messages=[
            {"role": "user", "content": "How many r's are in the word 'strawberry'?"}
        ],
        extra_body={"reasoning": {"enabled": False}},
    )

    msg = response.choices[0].message.content
    print(f"Response => {msg}")


if __name__ == "__main__":
    main()
