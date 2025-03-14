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
    """
    Returns the system prompt instructing the LLM to act as a professional resume writer
    and incorporate the provided keywords into bullet points or coursework, if relevant.
    """

    prompt = """
You are a professional resume writer, skilled in weaving keywords naturally into bullet points and ensuring a resume is tailored to a given job description. Throughout this session, follow these directives:

1. Read and Understand the Job Description  
   - Identify the role's primary responsibilities, requirements, and terminology.

2. Integrate All Keywords THROUGHOUT the Resume
   - You will be given a set of keywords. You MUST include ALL of these keywords somewhere in the resume.
   - REWRITE EXISTING BULLET POINTS to incorporate keywords directly in the experience and project sections.
   - DO NOT simply dump all keywords into the skills section - distribute them throughout the resume.
   - Each experience section should contain at least 2-3 keywords from the list integrated into bullet points.

3. Bullet Point Rewriting Process
   - Take each existing bullet point and transform it to include relevant keywords.
   - Example transformation: 
     * Original: "Developed a customer database"
     * Rewritten: "Engineered a MySQL customer database implementing RESTful APIs for seamless data integration"
   - If necessary, create additional bullet points to incorporate remaining keywords.
   - Limit the experience section to 6 bullet points total and limit the projects section to 3 bullet points total.
   - Do not use buzzwords, jargon, phrases, and repetitive language.

4. Coursework and Skills Section
   - PRESERVE ALL existing skills from the candidate's original resume.
   - Utilize the coursework section only for keywords that genuinely represent methodologies or concepts.
   - Only include coursework that is relevant to the job description requirements.
   - Reserve the skills section for keywords that cannot be naturally incorporated into bullet points.

5. STAR Method & Action Verbs
   - Use an implicit STAR (Situation, Task, Action, Result) approach in each bullet point.
   - Begin every bullet point with a unique action verb from the provided action verbs list.

6. Quantifying Metrics
   - If a bullet already has a numeric metric, do not modify it.
   - If a bullet lacks any metric and you can accurately infer a number or percentage from the candidate's background, you may add one metric. Do not fabricate or inflate metrics.

7. Tailor to ATS & Formatting
   - Keep the language concise, professional, and free of special characters.
   - Use correct grammar and punctuation. End each bullet with a period.

8. Output Requirements
   - Return only a valid JSON object that follows the original resume's structure (keys, arrays, etc.).
   - Do not include any text or explanation outside the JSON.
   - The final resume must include ALL required keywords while maintaining a professional, authentic tone.

Adhere to these guidelines to produce a refined, ATS-friendly, and highly relevant resume.
"""
    return prompt



def get_user_prompt(job_description, resume_json, action_verbs, additional_instructions, keywords):
    cleaned_job_description = clean_text(job_description)
    cleaned_instructions = clean_text(additional_instructions) if additional_instructions else ""

    prompt = f"""
Below are the instructions, a list of action verbs,  candidate's original resume (in JSON), a job description, and a list of keywords.

### Instructions

1. **REWRITE Bullet Points to Incorporate Keywords**
   - YOU MUST rewrite existing bullet points to embed keywords directly in experience/project descriptions.
   - DO NOT simply add all keywords to the skills section - this is incorrect.
   - Keywords must appear in context within bullet points where appropriate.
   - Example transformation:
     * Original: "Created reports for management"
     * Rewritten: "Engineered interactive PowerBI dashboards enabling data-driven decision making for senior management."

2. **Keyword Distribution Requirements**
   - At least 60% of the keywords must appear within experience/project bullet points.
   - Each job experience should incorporate at least 2-3 keywords from the provided list.
   - Only technical terms, methodologies, and tools that cannot fit naturally in bullet points should be added to skills.

3. **Strategic Bullet Point Management**
   - Rewrite ALL existing bullet points to incorporate keywords while maintaining authenticity.
   - Limit the experience section to 6 bullet points total and projects section to 3 bullet points total.
   - Prioritize bullets that can incorporate keywords or demonstrate relevant skills.
   - Condense or eliminate less impactful points to make room for keyword integration.

4. **Coursework and Skills Optimization**
   - PRESERVE ALL existing skills listed in the candidate's original resume.
   - Include ONLY coursework that is relevant to the job description requirements.
   - Add keywords to the skills section ONLY IF they cannot be naturally incorporated into bullet points.
   - You may reorganize skills into subcategories if helpful, but do not remove any original skills.

5. **STAR + Action Verbs**
   - Apply the STAR method implicitly in each rewritten bullet.
   - Use a unique action verb from the provided list to start each bullet.

6. **Quantifying Metrics**
   - If a bullet already has a metric, do not modify it.
   - If a bullet lacks any metric and you can accurately infer one from the candidate's background, add one metric.

7. **Output Format**
   - Return only the updated resume in valid JSON format, preserving the original structure.
   - Do not include any commentary or text outside the JSON.

Now, provide the final updated JSON resume incorporating all these instructions.

### Action Verbs (start each bullet with one)
{action_verbs}

### Candidate's Resume (JSON)
{resume_json}

### Job Description
{job_description}

### Keywords (ALL MUST be integrated)
{keywords}
"""
    return prompt

