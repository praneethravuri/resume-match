import re
import json
import logging
import streamlit as st
import asyncio
from prompts.prompt_engineering import get_system_prompt, get_user_prompt
from utils.text_processing import compute_matching_score
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize clients
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def format_action_verbs(action_verbs):
    action_verbs = ""
    for verb in action_verbs:
        action_verbs += f"- {verb}: {" ".join(action_verbs[verb])}\n"
    
    print(action_verbs)
    return action_verbs

def load_resume():
    """Load resume from secrets or file with enhanced error handling"""
    try:
        if "resume" in st.secrets and "data" in st.secrets["resume"]:
            return json.loads(st.secrets["resume"]["data"])
        with open("data/resume.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error("Resume loading failed: %s", str(e))
        return None

def validate_keyword_usage(original_resume, enhanced_resume, keywords):
    """
    Validate keyword integration and return missing keywords.
    Only flags keywords missing in both original and enhanced resumes.
    """
    if not keywords:
        return []
    
    original_text = json.dumps(original_resume).lower()
    enhanced_text = json.dumps(enhanced_resume).lower()
    
    missing = []
    for kw in keywords:
        kw_lower = kw.lower()
        # Check if keyword exists in either version
        in_original = kw_lower in original_text
        in_enhanced = kw_lower in enhanced_text
        
        if not in_original and not in_enhanced:
            missing.append(kw)
    
    return missing

async def process_resume(job_description, additional_instructions, company, position, 
                        api_choice="deepseek", job_id="", keywords=[]):
    """
    Main processing function with keyword validation and retry logic
    """
    logging.info("Starting resume processing for %s at %s", position, company)
    
    original_resume = load_resume()
    if not original_resume:
        st.error("Failed to load resume data")
        return None, []

    try:
        with open("data/action_verbs.json", "r") as f:
            action_verbs = json.load(f)
    except Exception as e:
        logging.error("Action verbs load failed: %s", str(e))
        return None, []

    # Generate prompts
    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(job_description, original_resume, 
                                 format_action_verbs(action_verbs), additional_instructions, keywords)

    # LLM API selection
    if api_choice == "openai":
        from llm.openai_client import async_call_openai_api
        llm_response = await async_call_openai_api([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
    else:
        from llm.deepseek_client import async_call_deepseek_api
        llm_response = await async_call_deepseek_api(system_prompt, user_prompt, deepseek_client)

    # Response cleaning
    try:
        if "```json" in llm_response:
            llm_response = re.search(r"```json(.*?)```", llm_response, re.DOTALL).group(1).strip()
        enhanced_resume = json.loads(llm_response)
    except json.JSONDecodeError:
        logging.error("JSON decode failed. Raw response: %s", llm_response)
        st.error("Failed to parse AI response. Please try again.")
        return None, []
    except Exception as e:
        logging.error("Response processing failed: %s", str(e))
        return None, []

    # Keyword validation
    missing_keywords = validate_keyword_usage(original_resume, enhanced_resume, keywords)
    
    return enhanced_resume, missing_keywords