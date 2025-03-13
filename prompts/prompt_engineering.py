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
- Accurately represent my authentic experience.
- Transform each bullet point implicitly using the STAR framework (Situation, Task, Action, Result).
- Incorporate relevant keywords from the job description into the bullet points. From the provided keyword list, only add non-skill keywords (e.g., "cross-functional", "end-to-end", "user-centric"). Additionally, identify any pertinent keywords missing from my original resume that can be added without exaggerating my experience.
- If any provided keywords are already present in my resume, subtly emphasize their importance using natural language—do so in a way that does not appear as if they were inserted merely to pass an ATS.
- Use the job description as a guide to emphasize the most relevant skills and experiences
- Use the provided action verbs dictionary to begin each bullet point uniquely.
- Ensure bullet points are concise, impactful, and tailored to the job requirements.
- Preserve all authentic skills, experiences, and personal details
- Tailor content to highlight experience most relevant to the job requirements
- Define acronyms on first use, then use the acronym consistently
- Return a valid, properly formatted JSON object with the same structure as the input
- Use professional, engaging language free of jargon, filler phrases (e.g., "Assisted with," "Helped," "Was responsible for", "Mentored"), and cliché buzzwords (e.g., "hard-working, team player, dynamic, results-driven, self-motivated, detail-oriented, go-getter, strong communication skills, adaptability")
- Organize the skills under clear categories (e.g., "Programming Languages," "Web Technologies")
- Prioritize skills that match the job description's key requirements
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
    cleaned_job_description = clean_text(job_description)
    cleaned_instructions = clean_text(additional_instructions) if additional_instructions else ""
    
    prompt = f"""
I will provide my current resume in JSON format, a job description, a list of action verbs, additional instructions, and a set of keywords extracted from the application. Your task is to transform my resume to align with the job description by following these rules:

1. Maintain authenticity and truthfulness.
2. Implicitly apply the STAR methodology to rephrase each bullet point.
3. Start each bullet point with a unique action verb from the provided list.
4. Integrate relevant keywords from the job description. From the provided keyword list, include only non-skill keywords (e.g., "cross-functional", "end-to-end", "IaC"). Additionally, identify and add any pertinent keywords missing from my original resume that enhance alignment without overstating my experience.
5. For keywords already present in my resume, subtly emphasize their importance through natural language—ensure they stand out without appearing to be inserted solely for ATS optimization.
6. Follow the resume structure: personal, education, experience, skills, and projects. Limit the experience section to 6 bullet points and the projects section to 3 bullet points.
7. Ensure that bullet points are concise, impactful, and free of filler language.

Return ONLY the updated JSON object with no additional commentary.

Resume (JSON):
{resume}

Action Verbs:
{action_verbs}

Additional Instructions:
{cleaned_instructions}

Keywords:
{keywords}

Job Description:
{cleaned_job_description}
"""
    logging.info("Generated revised user prompt with subtle keyword highlighting instructions.")
    return prompt

