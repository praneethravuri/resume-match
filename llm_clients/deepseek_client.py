import logging

def call_deepseek_api(system_prompt, user_prompt, openai_client):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        response = openai_client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
        )
        logging.info("API call successful. Full response: %s", response)
        if not response.choices or not response.choices[0].message:
            logging.error("Empty or unexpected response structure received from API: %s", response)
            return ""
        result = response.choices[0].message.content.strip()
        logging.info("API response content: %s", result if result else "Empty response content")
        return result
    except Exception as e:
        logging.exception("Error calling OpenAI API")
        return ""
