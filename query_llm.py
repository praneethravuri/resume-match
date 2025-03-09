import json
import logging
import streamlit as st
from prompt_engineering import get_system_prompt, get_user_prompt
import asyncio
from utils.helpers import generate_pdf_filename  # Note: This is no longer used for PDF generation
from utils.text_processing import compute_matching_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# Initialize the Deepseek client (used for the deepseek API option)
from openai import OpenAI
openai_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def load_resume():
    """Load resume data from st.secrets; fallback to local file if necessary."""
    try:
        if "resume" in st.secrets and "data" in st.secrets["resume"]:
            resume = json.loads(st.secrets["resume"]["data"])
        else:
            with open("resume.json", "r") as f:
                resume = json.load(f)
        logging.info("Resume data loaded successfully.")
        return resume
    except Exception as e:
        logging.exception("Error loading resume data")
        return None

async def process_resume(job_description, additional_instructions, company, position, api_choice="deepseek", job_id=""):
    """Enhance the resume using the selected LLM and generate a tailored Markdown resume."""
    resume = load_resume()
    if resume is None:
        logging.error("Failed to load resume.")
        return None

    try:
        with open("action_verbs.json", "r") as f:
            action_verbs = json.load(f)
    except Exception as e:
        logging.exception("Error loading action_verbs.json")
        return None

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(job_description, resume, action_verbs, additional_instructions)

    logging.info("Calling API to enhance the resume...")

    # Call the appropriate API function based on the api_choice
    if api_choice == "open ai":
        from llm_clients.openai_client import async_call_openai_api
        llm_response = await async_call_openai_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
    elif api_choice == "deepseek":
        from llm_clients.deepseek_client import async_call_deepseek_api
        llm_response = await async_call_deepseek_api(system_prompt, user_prompt, openai_client)
    elif api_choice == "local":
        logging.info("Local mode selected: returning original resume without enhancement.")
        llm_response = json.dumps(resume)
    else:
        logging.error("Unknown API choice. Defaulting to local mode.")
        llm_response = json.dumps(resume)

    try:
        cleaned_response = llm_response.replace("```", "").replace("```json", "")
        enhanced_resume = json.loads(cleaned_response)
        with open("enhanced_resume.json", "w") as f:
            json.dump(enhanced_resume, f, indent=2)
        logging.info("Enhanced resume saved to 'enhanced_resume.json'")
    except json.JSONDecodeError as e:
        logging.exception("Error: The API response is not valid JSON. Response: %s", llm_response)
        return None

    # Generate Markdown resume instead of PDF
    from utils.helpers import generate_markdown_resume
    markdown_resume = generate_markdown_resume(enhanced_resume)
    return markdown_resume

if __name__ == "__main__":
    # For testing purposes, run the process_resume function with dummy data
    asyncio.run(process_resume("Sample job description", "Some additional instructions", "SampleCompany", "SamplePosition", "deepseek", "JOB123"))
