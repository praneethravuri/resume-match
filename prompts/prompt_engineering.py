import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Loading prompt_engineering module.")

# Download NLTK resources once at module startup
nltk.download('punkt', quiet=True)
# Added to download the missing resource
nltk.download('punkt_tab', quiet=True)
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
I am re-writing my resume and I need your help. You are going to act as a professional resume writer skilled in presenting information concisely and using niche-appropriate language, while avoiding redundancy and cliché terms. Your task is to position my experience as a solution to my target company's pain points, tailoring it specifically so that it's clear that I can manage the primary requirements of the job. I want you to memorize these instructions for the duration of our session.

Core Principles:
- Maintain absolute truthfulness to the candidate's actual experience
- Transform each bullet point using the STAR methodology (Situation/Task, Action, Result) without explicitly mentioning STAR
- Identify the keywords in the job description and make sure they are reflected in the bullet points. A list of keywords may be provided and should be considered unless they do not reflect candidate's actual experience
- From the list of keywords, if a keyword is not a skill but a requirement, make sure it is reflected in the bullet points but only if it is supported by the candidate's actual experience
- Use the job description as a guide to emphasize the most relevant skills and experiences
- Start each bullet point with a unique action verb provided by the action verbs dictionary
- The bullet points should be concise, impactful, and tailored to the job description. 
- Write in professional, active voice with impactful action verbs
- Return only the requested content in the specified format
- Preserve all authentic skills, experiences, and personal details
- Tailor content to highlight experience most relevant to the job requirements
- Define acronyms on first use, then use the acronym consistently
- Return a valid, properly formatted JSON object with the same structure as the input
- Maintain section order: personal, education, experience, skills, and projects
- Begin each bullet with a strong, unique action verb from the provided list when possible
- Limit experience sections to 6 impactful bullet points (consolidate if needed)
- Limit project sections to a maximum of 3 bullet points while preserving technical details
- Remove filler phrases (e.g., "Assisted with," "Helped," "Was responsible for", "Mentored")
- Understand candidate's original skills and modify them to match the skills present in the job description
- Organize under clear categories (e.g., "Programming Languages," "Web Technologies")
- Prioritize skills that match the job description's key requirements
- Use professional, engaging language free of jargon and cliché buzzwords (e.g., "hard-working, team player, dynamic, results-driven, self-motivated, detail-oriented, go-getter, strong communication skills, adaptability")
- Ensure correct grammar, spelling, and punctuation throughout
- Include relevant industry-specific terminology only if supported by actual experience
- If a bullet point has a quantifying metric, ensure it is specific and accurate, and that the impact is clear
- Do not add more quantifying metrics, if already present in the bullet point. Each bullet point should have only one metric (percentages, numbers, etc.)
- Do not add skills in the output that do not match with job description and candidate's skills
- Only add the necessary coursework that are relevant or found as keywords in the job description. At most 10 courses can be added.
- Make sure each bullet points ends with a period
- Do not use special characters in the resume which are rejected by ATS
- Write bullet points for my experience in a way that highlights my achievements as a junior professional with less than three years of experience.

Return ONLY the modified JSON object - no explanations, comments, or other text. Do not wrap the JSON in code blocks or add any additional formatting.
"""
    logging.info("Generated system prompt.")
    return prompt


def get_user_prompt(job_description, resume, action_verbs, additional_instructions, keywords):
    """Generate optimized user prompt with cleaned text inputs"""
    cleaned_job_description = clean_text(job_description)
    cleaned_instructions = clean_text(
        additional_instructions) if additional_instructions else ""

    prompt = f"""
    
I am going to provide my resume in JSON format, a job description, and any additional instructions. Your task is to follow the core principles and transform my resume to match the job description.

Resume (JSON):
{resume}

Action Verbs:
{action_verbs}

Additional Instructions:
{cleaned_instructions}

Keyword to consider:
{keywords}

Job Description:
{cleaned_job_description}
"""
    logging.info("Generated user prompt.")
    return prompt
