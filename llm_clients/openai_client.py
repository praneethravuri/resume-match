from openai import OpenAI
import asyncio

def call_openai_api(messages):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=16000
    )
    return completion.choices[0].message.content.strip()

async def async_call_openai_api(messages):
    return await asyncio.to_thread(call_openai_api, messages)
