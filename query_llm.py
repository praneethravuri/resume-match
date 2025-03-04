import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from prompt_engineering import get_system_prompt, get_user_prompt
import json_to_pdf_converter

# Load environment variables from .env (do not expose this file publicly)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize the OpenAI client (using your chosen API and base URL)
openai_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Configuration parameters
model_name = "gpt-4o"  # or your chosen model
temperature = 0.7
max_tokens = 10000

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
            # temperature=temperature,
            # max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling OpenAI API:", e)
        return ""

def process_resume(job_description, additional_instructions, company, position):
    """
    Tailors the resume using the provided job description (and additional instructions if any),
    then converts the enhanced resume into a PDF that is renamed based on company and position.
    """
    # Load resume data from JSON file
    try:
        with open("resume.json", "r") as f:
            resume = json.load(f)
    except Exception as e:
        print("Error loading resume.json:", e)
        return None
    
    # Load action verbs from JSON file
    try:
        with open("action_verbs.json", "r") as f:
            action_verbs = json.load(f)
    except Exception as e:
        print("Error loading action_verbs.json:", e)
        return None

    # Incorporate additional instructions if provided
    full_job_description = job_description
    if additional_instructions.strip():
        full_job_description += "\nAdditional Instructions: " + additional_instructions.strip()
    
    # Build the system and user prompts using your prompt engineering module
    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(full_job_description, resume, action_verbs)
    
    print("Calling API to enhance the resume...")
    llm_response = call_openai_api(system_prompt, user_prompt)
    
    # Parse the response as JSON and save the enhanced resume
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
    
    # Generate PDF from the enhanced resume and rename it accordingly
    output_pdf_filename = f"praneeth_ravuri_resume_{company}_{position}.pdf"
    json_to_pdf_converter.generate_pdf(output_pdf_filename)
    
    return output_pdf_filename

if __name__ == "__main__":
    # For testing purposes
    process_resume("Sample job description", "Some additional instructions", "SampleCompany", "SamplePosition")
