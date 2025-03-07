# Import required libraries once at the module level
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Initialize NLTK resources once
def initialize_nltk():
    """Initialize NLTK resources needed for text processing"""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    # Return the stopwords set for reuse
    return set(stopwords.words('english'))

# Initialize once
STOP_WORDS = initialize_nltk()

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
        
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and normalize spacing
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Tokenize the text
    word_tokens = word_tokenize(text)
    
    # Remove excessive stopwords, but keep some to preserve readability
    filtered_text = []
    prev_word = ""
    for word in word_tokens:
        # Keep consecutive stopwords to a minimum (avoid removing all)
        if word not in STOP_WORDS or prev_word not in STOP_WORDS:
            filtered_text.append(word)
        prev_word = word
        
    # Join the filtered words back into a string
    cleaned_text = ' '.join(filtered_text)
    
    # Capitalize first letter of sentences
    cleaned_text = '. '.join(s.capitalize() for s in cleaned_text.split('. '))
    
    return cleaned_text

def get_system_prompt():
    return """
You are an expert resume optimization assistant for career advisors at Harvard Extension School. Your purpose is to transform resumes to be truthful, compelling, and tailored to specific job descriptions while maintaining a single-page format.

Core Principles:
- Maintain absolute truthfulness to the candidate's actual experience
- Transform each bullet point using the STAR methodology (Situation/Task, Action, Result) without explicitly mentioning STAR
- Write in professional, active voice with impactful action verbs
- Return only the requested content in the specified format
- Preserve all authentic skills, experiences, and personal details
"""



def get_user_prompt(job_description, resume, action_verbs, additional_instructions):
    """Generate optimized user prompt with cleaned text inputs"""
    # Clean the job description and additional instructions
    cleaned_job_description = clean_text(job_description)
    cleaned_instructions = clean_text(additional_instructions) if additional_instructions else ""
    
    return f"""
Review the provided resume in JSON format and enhance it to align with the job description while maintaining complete truthfulness. Return ONLY the modified resume as a valid JSON object without explanations or additional text.

Job Description:
{cleaned_job_description}

Resume (JSON):
{resume}

Recommended Action Verbs by Category:
{action_verbs}

Additional Instructions:
{cleaned_instructions}

ENHANCEMENT REQUIREMENTS:

1. Content & Accuracy
   - Preserve all authentic achievements, metrics, tools, and skills from the original resume
   - Never fabricate information or omit crucial details relevant to the job description
   - Tailor content to highlight experience most relevant to the job requirements
   - Use consistent verb tense: present for current roles, past for previous positions

2. Format & Structure
   - Return a valid, properly formatted JSON object with the same structure as the input
   - Maintain section order: personal, education, experience, skills, and projects
   - Use "&ndash;" for date ranges (e.g., "2022 &ndash; 2024")
   - Define acronyms on first use, then use the acronym consistently

3. Bullet Point Optimization
   - Transform each bullet point using STAR methodology: clearly show the Situation/Task, Action taken, and measurable Result
   - Begin each bullet with a strong, unique action verb from the provided list when possible
   - Limit experience sections to 6-8 impactful bullet points (consolidate if needed)
   - Limit project sections to a maximum of 6 bullet points while preserving technical details
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