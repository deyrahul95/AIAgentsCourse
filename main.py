from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv(override=True)


def main():
    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    response = client.chat.completions.create(
        model="qwen3:0.6b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Give response to the point. NO BS."},
            {"role": "user", "content": "What is the capital of India?"},
        ],
        max_completion_tokens=100,
        reasoning_effort="none", # to disable the model thinking
    )

    msg = response.choices[0].message.content
    print(f"Response => {msg}")
    print("=" * 10 + " Usages " + "=" * 10)
    print(response.usage) # print our the token usages data


if __name__ == "__main__":
    main()
