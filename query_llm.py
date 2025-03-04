import json
import streamlit as st
from openai import OpenAI
from prompt_engineering import get_system_prompt, get_user_prompt
import json_to_pdf_converter

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
        return resume
    except Exception as e:
        print("Error loading resume data:", e)
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
            # Optionally set temperature and max_tokens
            # temperature=0.7,
            # max_tokens=10000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return ""

def process_resume(job_description, additional_instructions, company, position):
    """Enhance the resume using the LLM and generate a tailored PDF."""
    resume = load_resume()
    if resume is None:
        print("Failed to load resume.")
        return None

    # Load action verbs from local file
    try:
        with open("action_verbs.json", "r") as f:
            action_verbs = json.load(f)
    except Exception as e:
        print("Error loading action_verbs.json:", e)
        return None

    full_job_description = job_description
    if additional_instructions.strip():
        full_job_description += "\nAdditional Instructions: " + additional_instructions.strip()

    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(full_job_description, resume, action_verbs)

    print("Calling API to enhance the resume...")
    llm_response = call_openai_api(system_prompt, user_prompt)

    try:
        cleaned_response = llm_response.replace("```", "").replace("```json", "")
        enhanced_resume = json.loads(cleaned_response)
        with open("enhanced_resume.json", "w") as f:
            json.dump(enhanced_resume, f, indent=2)
        print("Enhanced resume saved to 'enhanced_resume.json'")
    except json.JSONDecodeError as e:
        print("Error: The API response is not valid JSON.")
        print("Response:", llm_response)
        print("Error details:", e)
        return None

    output_pdf_filename = f"praneeth_ravuri_resume_{company}_{position}.pdf"
    json_to_pdf_converter.generate_pdf(output_pdf_filename)
    return output_pdf_filename

if __name__ == "__main__":
    # For testing purposes
    process_resume("Sample job description", "Some additional instructions", "SampleCompany", "SamplePosition")
