import json
import logging
import streamlit as st
from openai import OpenAI
from prompt_engineering import get_system_prompt, get_user_prompt
import json_to_pdf_converter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load API keys from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

# Initialize the OpenAI client (using DEEPSEEK_API_KEY in this example)
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

def call_openai_api(system_prompt, user_prompt):
    """Call the OpenAI API with the given prompts and return the response."""
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

        # Check if the expected attributes exist in the response
        if not response.choices or not response.choices[0].message:
            logging.error("Empty or unexpected response structure received from API: %s", response)
            return ""
        
        result = response.choices[0].message.content.strip()
        logging.info("API response content: %s", result if result else "Empty response content")
        return result
    except Exception as e:
        logging.exception("Error calling OpenAI API")
        return ""


def process_resume(job_description, additional_instructions, company, position):
    """Enhance the resume using the LLM and generate a tailored PDF."""
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

    full_job_description = job_description
    if additional_instructions.strip():
        full_job_description += "\nAdditional Instructions: " + additional_instructions.strip()

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(full_job_description, resume, action_verbs)

    logging.info("Calling API to enhance the resume...")
    llm_response = call_openai_api(system_prompt, user_prompt)

    try:
        cleaned_response = llm_response.replace("```", "").replace("```json", "")
        enhanced_resume = json.loads(cleaned_response)
        with open("enhanced_resume.json", "w") as f:
            json.dump(enhanced_resume, f, indent=2)
        logging.info("Enhanced resume saved to 'enhanced_resume.json'")
    except json.JSONDecodeError as e:
        logging.exception("Error: The API response is not valid JSON. Response: %s", llm_response)
        return None

    output_pdf_filename = f"praneeth_ravuri_resume_{company}_{position}.pdf"
    json_to_pdf_converter.generate_pdf(output_pdf_filename)
    return output_pdf_filename

if __name__ == "__main__":
    process_resume("Sample job description", "Some additional instructions", "SampleCompany", "SamplePosition")
