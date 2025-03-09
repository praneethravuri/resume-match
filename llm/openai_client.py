from openai import OpenAI
import asyncio
import logging

def call_openai_api(messages):
    logging.info("Calling OpenAI API with messages: %s", messages)
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=16000
    )
    result = completion.choices[0].message.content.strip()
    logging.info("OpenAI API response: %s", result)
    return result

async def async_call_openai_api(messages):
    logging.info("Asynchronously calling OpenAI API.")
    return await asyncio.to_thread(call_openai_api, messages)
