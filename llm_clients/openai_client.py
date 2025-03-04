from openai import OpenAI

def call_openai_api(messages):
    client = OpenAI()  # Uses default configuration (ensure your OPENAI_API_KEY is set appropriately)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=16000
    )
    return completion.choices[0].message.content.strip()
