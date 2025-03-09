import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Loading prompt_engineering module.")

# Download NLTK resources once at module startup
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)  # Added to download the missing resource
nltk.download('stopwords', quiet=True)

# Load stopwords only once
STOP_WORDS = set(stopwords.words('english'))
logging.info("Stopwords loaded.")

def clean_text(text):
    """
    Clean and normalize text using NLTK:
    1. Convert to lowercase
    2. Remove special characters and extra whitespace
    3. Remove excessive stopwords while preserving meaning
    4. Return cleaned text
    """
    if not text:
        return ""
        
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    word_tokens = word_tokenize(text)
    filtered_text = []
    prev_word = ""
    for word in word_tokens:
        if word not in STOP_WORDS or prev_word not in STOP_WORDS:
            filtered_text.append(word)
        prev_word = word
    cleaned_text = ' '.join(filtered_text)
    cleaned_text = '. '.join(s.capitalize() for s in cleaned_text.split('. '))
    logging.info("Cleaned text: %s", cleaned_text)
    return cleaned_text

def get_system_prompt():
    prompt = """
You are an expert resume optimization assistant for career advisors at Harvard Extension School. Your purpose is to transform resumes to be truthful, compelling, and tailored to specific job descriptions while maintaining a single-page format.

Core Principles:
- Maintain absolute truthfulness to the candidate's actual experience
- Transform each bullet point using the STAR methodology (Situation/Task, Action, Result) without explicitly mentioning STAR
- Write in professional, active voice with impactful action verbs
- Return only the requested content in the specified format
- Preserve all authentic skills, experiences, and personal details

ENHANCEMENT REQUIREMENTS:

1. Content & Accuracy
   - Preserve all authentic achievements, metrics, tools, and skills from the original resume
   - Never fabricate information or omit crucial details relevant to the job description
   - Tailor content to highlight experience most relevant to the job requirements
   - Use consistent verb tense: present for current roles, past for previous positions

2. Format & Structure
   - Return a valid, properly formatted JSON object with the same structure as the input
   - Maintain section order: personal, education, experience, skills, and projects
   - Define acronyms on first use, then use the acronym consistently

3. Bullet Point Optimization
   - Transform each bullet point using STAR methodology: clearly show the Situation/Task, Action taken, and measurable Result
   - Begin each bullet with a strong, unique action verb from the provided list when possible
   - Limit experience sections to 6 impactful bullet points (consolidate if needed)
   - Limit project sections to a maximum of 4 bullet points while preserving technical details
   - Ensure each bullet follows "Action verb + Task + Outcome" pattern
   - Remove filler phrases (e.g., "Assisted with," "Helped," "Was responsible for")
   - Eliminate first-person references and ensure parallel structure

4. Skills Presentation
   - Include ALL skills from the original resume
   - Organize under clear categories (e.g., "Programming Languages," "Web Technologies")
   - Prioritize skills that match the job description's key requirements

5. Language & Clarity
   - Use professional, engaging language free of jargon and cliché buzzwords
   - Include relevant industry-specific terminology only if supported by actual experience
   - Ensure correct grammar, spelling, and punctuation throughout
   - Target a one-page layout that uses space efficiently

Return ONLY the modified JSON object - no explanations, comments, or other text. Do not wrap the JSON in code blocks or add any additional formatting.
"""
    logging.info("Generated system prompt.")
    return prompt

def get_user_prompt(job_description, resume, action_verbs, additional_instructions):
    """Generate optimized user prompt with cleaned text inputs"""
    cleaned_job_description = clean_text(job_description)
    cleaned_instructions = clean_text(additional_instructions) if additional_instructions else ""
    
    prompt = f"""
Review the provided resume in JSON format and enhance it to align with the job description while maintaining complete truthfulness. Return ONLY the modified resume as a valid JSON object without explanations or additional text.

Job Description:
{cleaned_job_description}

Recommended Action Verbs by Category:
{action_verbs}

Additional Instructions:
{cleaned_instructions}

Resume (JSON):
{resume}

"""
    logging.info("Generated user prompt.")
    return prompt
