# Resume Tailoring and Application Tracking

This project provides a streamlined way to tailor a resume for a specific job description using AI (LLM) and track the application lifecycle. It allows you to:

1. **Tailor Your Resume** for a job by integrating relevant keywords and rewriting bullet points.
2. **Store Application Details** (company name, job ID, position name) in a MongoDB database.
3. **Track All Applications** in a Streamlit-based dashboard.
4. **Filter Applications** by status, company, or whether a cold email or LinkedIn message was sent.

---

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Usage](#usage)
  - [1. Tailor the Resume](#1-tailor-the-resume)
  - [2. Track Job Applications](#2-track-job-applications)
- [How It Works](#how-it-works)
  - [Resume Tailoring Flow](#resume-tailoring-flow)
  - [Application Tracking Flow](#application-tracking-flow)
- [Contributing](#contributing)
- [License](#license)

---

## Key Features

1. **Resume Tailoring with Keywords**  
   - AI-driven rewriting of existing resume content to include a list of user-defined keywords.
   - Follows a set of style guides (STAR method, action verbs, limited bullet points, etc.) to improve clarity and ATS-friendliness.

2. **AI Integration**  
   - Option to use either Deepseek or OpenAI for generating the tailored resume text.
   - Ensures that all keywords are woven organically into bullet points or skill sections.

3. **Application Database**  
   - Stores application info (company name, job ID, position title, job description) in MongoDB.
   - Saves the tailored resume to the database, so you can retrieve or modify it later.

4. **Dashboard for Tracking**  
   - A Streamlit-based interface to manage your applications.
   - Filter by status (not applied, applied, interview, rejected, selected), company, or whether you've sent a cold email or LinkedIn message.
   - Paginated list of all applications with the ability to update status or mark favorites.

5. **LinkedIn Message Generator**  
   - Quickly draft a short LinkedIn message to recruiters or hiring managers based on the company, role, and job ID.

---

## Tech Stack

- **Python** for the core logic.
- **Streamlit** for the web interface.
- **MongoDB** for the application data storage.
- **NLTK** and **scikit-learn** for text processing and keyword matching.
- **OpenAI API** or **Deepseek API** for LLM-based text generation.

---

## Project Structure

```
├── .devcontainer/
│   └── devcontainer.json
├── data/
│   ├── action_verbs.json
│   └── resume.json            # (Example or placeholder resume data)
├── db/
│   ├── mongodb_client.py      # MongoDB connection setup
│   └── operations.py          # CRUD operations on the "applications" collection
├── llm/
│   ├── deepseek_client.py     # Integration with Deepseek LLM
│   └── openai_client.py       # Integration with OpenAI LLM
├── logic/
│   └── query_llm.py           # Core function to call the LLM and process results
├── pages/
│   └── Tracker.py             # Streamlit page for tracking applications
├── prompts/
│   └── prompt_engineering.py  # Prompt templates and cleaning for job descriptions
├── utils/
│   ├── format_resume_data.py  # Render resume data in a Streamlit-friendly format
│   ├── helpers.py             # Helper functions (e.g., filename sanitizing)
│   ├── linkedin_message_generator.py
│   └── text_processing.py     # Preprocessing (tokenizing, lemmatizing) and matching
├── Tailor.py                  # Main Streamlit page for tailoring resumes
├── requirements.txt
└── README.md                  # (This file)
```

---

## Installation and Setup

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/praneethravuri/resume-match.git
   cd resume-tailor
   ```

2. **Create a Virtual Environment (Optional but Recommended)**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # or .\venv\Scripts\activate on Windows
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Configure .devcontainer**  
   - If using VSCode DevContainers, you can open the project in a container to have all dependencies automatically installed.

---

## Configuration

The application uses **Streamlit Secrets** for storing sensitive information such as:

- `OPENAI_API_KEY` (if using OpenAI)
- `DEEPSEEK_API_KEY` (if using Deepseek)
- `MONGODB_URI` (MongoDB connection string)
- `DATABASE_NAME`
- `COLLECTION_NAME`
- (Optional) `resume` object inside Streamlit secrets if you want to store your resume JSON there.

Create a `secrets.toml` file in a hidden `.streamlit` folder:
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-key"
DEEPSEEK_API_KEY = "your-deepseek-key"
MONGODB_URI = "mongodb+srv://username:password@cluster-url/test"
DATABASE_NAME = "myDatabase"
COLLECTION_NAME = "applications"

# Optional if storing resume JSON in secrets
[resume]
data = """
{
  "coursework": [],
  "experience": [],
  "skills": [],
  "projects": []
}
"""
```

> **Note**: If you do not store the resume in Streamlit secrets, you can place a `resume.json` file under `data/` folder and the application will load from there.

---

## Usage

### 1. Tailor the Resume

- **Launch Streamlit**:

  ```bash
  streamlit run Tailor.py
  ```
  
- **Fill out the Form**:
  1. **Company Name** and **Job Title** (required).
  2. **Job Description** (required) – paste the job description text.
  3. **Keywords** (required) – a comma-, newline-, or semicolon-separated list of keywords you want to ensure appear in the resume.
  4. **Additional Instructions** (optional) – any extra direction for the AI.

- **Generate Tailored Resume**:
  1. The system calls the AI (OpenAI or Deepseek) to rewrite resume bullet points to include keywords.
  2. The newly tailored resume is displayed on the page.
  3. The system stores the new resume along with the company, job title, and job description in the database.

### 2. Track Job Applications

- **Open the Tracker Page**:
  - From Streamlit’s main menu or URL, navigate to `pages/Tracker.py`, or run:
    ```bash
    streamlit run pages/Tracker.py
    ```

- **View and Filter**:
  1. Filter applications by **Status** (`not applied`, `applied`, `interview`, etc.).
  2. Filter by **Company** name.
  3. Search by a text query (for partial matches on company/title).
  4. Filter for applications missing a **Cold Email** or **LinkedIn** message.

- **Actions**:
  1. **Mark status changes** (e.g., to “applied,” “interview,” “selected,” etc.).
  2. **Toggle** favorite/cold email/linkedin flags.
  3. **Delete** an application record.
  4. **Show Resume Data** – see the tailored resume stored for that application.
  5. **Generate LinkedIn Message** – get a short message for connecting with recruiters.

---

## How It Works

### Resume Tailoring Flow
1. **Input**: Job Description, Keywords, Resume JSON.
2. **Prompt Engineering**: The job description is cleaned and combined with the resume data and a set of instructions for the LLM.
3. **AI Generation**: The LLM rewrites bullet points, ensuring the keywords are distributed across the experience/projects sections.
4. **Validation**: Checks which keywords (if any) are missing. The final JSON is displayed and stored in the database.

### Application Tracking Flow
1. **Insert**: After the resume is tailored, an “application” entry is saved in MongoDB with:
   - Resume content
   - Company, Title, Job ID
   - Status (default “not applied”)
2. **Update**: The user can later update the status (e.g., “applied,” “interview,” etc.).
3. **Search & Filter**: The Tracker page queries all saved applications from MongoDB, applying user-selected filters.
4. **Metadata**: Additional flags like “favorite,” “sent_cold_email,” and “sent_linkedin_message” help you quickly see next steps.

---

## Contributing

1. **Fork the Repository**
2. **Create a Feature Branch**
3. **Make and Commit Changes**
4. **Push the Branch and Open a Pull Request**

All contributions (bug reports, pull requests, suggestions) are welcome!

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). Feel free to use, modify, and distribute as needed.