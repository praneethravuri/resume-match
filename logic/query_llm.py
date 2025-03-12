import re
import json
import logging
import streamlit as st
from prompts.prompt_engineering import get_system_prompt, get_user_prompt
import asyncio
from utils.text_processing import compute_matching_score

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# Initialize the Deepseek client (used for the deepseek API option)
from openai import OpenAI
openai_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def load_resume():
    """Load resume data from st.secrets; fallback to local file if necessary."""
    logging.info("Loading resume data.")
    try:
        if "resume" in st.secrets and "data" in st.secrets["resume"]:
            resume = json.loads(st.secrets["resume"]["data"])
            logging.info("Resume data loaded from st.secrets.")
        else:
            with open("data/resume.json", "r") as f:
                resume = json.load(f)
            logging.info("Resume data loaded from local file.")
        return resume
    except Exception as e:
        logging.exception("Error loading resume data")
        return None

async def process_resume(job_description, additional_instructions, company, position, api_choice="deepseek", job_id="", keywords=""):
    """
    Enhance the resume by processing only the bullet points for work experience and projects.
    Merge the enhanced bullet points back into the original resume structure.
    Return the final tailored JSON resume.
    """
    logging.info("Starting process_resume with company: %s, position: %s", company, position)
    original_resume = load_resume()
    if original_resume is None:
        logging.error("Failed to load resume.")
        return None

    try:
        with open("data/action_verbs.json", "r") as f:
            action_verbs = json.load(f)
        logging.info("Action verbs loaded successfully.")
    except Exception as e:
        logging.exception("Error loading action_verbs.json")
        return None

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(job_description, original_resume, action_verbs, additional_instructions, keywords)
    logging.info("System prompt and user prompt generated.")

    logging.info("Calling API to enhance the bullet points in experience and projects...")
    # Call the appropriate API function based on the api_choice
    if api_choice == "open ai":
        from llm.openai_client import async_call_openai_api
        llm_response = await async_call_openai_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        logging.info("Received response from OpenAI API.")
    elif api_choice == "deepseek":
        from llm.deepseek_client import async_call_deepseek_api
        llm_response = await async_call_deepseek_api(system_prompt, user_prompt, openai_client)
        logging.info("Received response from Deepseek API.")
    else:
        logging.error("Invalid API choice provided: %s", api_choice)
        return None

    pattern = re.compile(r"```(?:json)?\s*([\s\S]+?)\s*```")
    match = pattern.search(llm_response)
    if match:
        llm_response = match.group(1).strip()
        logging.info("Extracted JSON from API response using regex.")
    else:
        llm_response = llm_response.strip()
        logging.info("No markdown formatting found; using raw API response.")

    logging.info("process_resume completed.")
    return llm_response
