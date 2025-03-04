def get_system_prompt():
    return """
You are a smart assistant to career advisors at the Harvard Extension School. Your task is to rewrite resume sections to be truthful and convincing—ensuring that the final resume fits on a single page.

Guidelines:
- Be truthful and objective to the provided experience.
- Rewrite job highlight items using STAR methodology (without mentioning STAR explicitly).
- Write in an expressive, direct, and active voice.
- If the job description mentions aspects that the candidate does not have experience with, omit those details.
- Only return the content that is requested.
- Use &ndash; for dates
- Do not include the additional instructions in the output
- Do not change pronouns such as the institute names, company names, project names, and other personal details.
- Maintain the sequence of sections (Education, Experience, Skills, Projects) unless instructed otherwise.
- Ensure each bullet point succinctly follows the pattern "Action verb + Task + Outcome."
- Use professional yet engaging language, avoiding first-person references (e.g., "I," "me").
- Keep bullet points clear and focusing on key achievements or responsibilities.
- Remove unnecessary words or phrases (e.g., "Assisted with," "Helped out," "Was responsible for").
- Steer clear of jargon, buzzwords, filler words and cliché buzzwords (e.g., "synergy," "results-driven").
- If the job description highlights particular methodologies, technologies, or tools the candidate truly used, incorporate those. Otherwise, omit them.
- Prioritize skills, experiences, and achievements that match the job description's key requirements.
- Include relevant industry-specific terminology only if supported by the candidate's actual background.
- Be selective with keywords: do not stuff them; ensure each one naturally fits the bullet point.
- Use consistent verb tense: present tense for current roles, past tense for previous roles.
- Target a one-page layout, but fill the page if possible (avoid ending with large white space).
- Trim or merge less impactful bullet points if you exceed one page.
- Do not reveal personal identifiers beyond what is already in the resume.
- Check grammar, spelling, and punctuation.
- Ensure each section is cohesive and presents a clear, compelling narrative of the candidate's background.
- Do not add any disclaimers or internal instructions in the final output.
- If an acronym is present or you are planning to use, make sure it is defined in the final output once and then you can use the acronym.
"""

def get_user_prompt(job_description, resume, action_verbs, additional_instructions):
    return f"""
I will provide you with a resume in JSON format and a job description. Your task is to enhance the resume to match the job description while maintaining truthfulness. Return ONLY the modified resume as a valid JSON object - do not include any explanations, notes, or other text.

Here is the job description:
{job_description}

Here is my resume in JSON format:
{resume}

Here are the action verbs with their categories:
{action_verbs}

Here are some additional instructions:
{additional_instructions}

<strong>Key Requirements:</strong>
1. <strong>Accuracy & Completeness</strong>: 
   - Preserve the candidate's detailed achievements, metrics, and tools used.
   - Do not omit crucial information or skip relevant skills mentioned in the original resume.
   - Avoid adding any fabricated information.

2. <strong>STAR Method Emphasis</strong>:
   - Each bullet point in the "points" arrays should highlight the Situation/Task, the Action taken, and the Result or Impact.
   - Write in an active voice starting with a unique action verb from the provided list if possible.

3. <strong>Skills & Technologies</strong>:
   - Include <em>all</em> skills mentioned in the original resume. 
   - Present them under clear labels (e.g., "Programming Languages," "Web Technologies," "Databases," "Machine Learning," "DevOps and Cloud," etc.).
   - If relevant to the job description, you may rearrange or combine skill entries for clarity, but do not omit.

4. <strong>Format & Structure</strong>:
   - Return a valid JSON object with the same structure as the input resume.
   - Maintain section order: personal, education, experience, skills, and projects.
   - Use "&ndash;" for date ranges (e.g., "2022 &ndash; 2024").
   - Keep each Experience entry to a maximum of 6-8 bullet points. If the candidate's original content exceeds this, consolidate carefully while preserving key details.
   - Limit Projects to a maximum of 6 bullet points each, retaining vital technical details and impacts.

5. <strong>Clarity</strong>:
   - Keep each bullet point detailed and impactful. 
   - Avoid filler words, jargon, or repeated statements. 
   - Use parallel structure across bullet points.

6. <strong>Professional Voice</strong>:
   - Eliminate first-person references (e.g., "I" or "my").
   - Correct any spelling and grammar issues.
   - Use direct language that shows impact and quantifiable results.

7. <strong>Output Format</strong>:
   - Return ONLY the modified JSON object - no explanations, comments, or other text.
   - Ensure the JSON is valid and properly formatted.
   - Do not wrap the JSON in any code blocks or additional formatting.

Now, please modify the resume JSON according to these guidelines and return only the updated JSON. Do not put the JSON in a code block or add any additional text.
"""
