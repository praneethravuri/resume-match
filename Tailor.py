import streamlit as st
from logic.query_llm import process_resume, load_resume, validate_keyword_usage
import asyncio
import json
from utils.format_resume_data import render_resume
import logging
from db.operations import insert_application, update_application_status
from utils.helpers import sanitize_filename
import re

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(
    page_title="Resume Tailor",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Resume Tailor")
st.write("Generate ATS-optimized resumes with keyword integration")

def format_keywords(keywords):
    """Parse keywords with multiple delimiters"""
    if not keywords:
        return []
    split_pattern = r'[,\n;]'
    keywords = re.split(split_pattern, keywords)
    cleaned = [kw.strip().lower() for kw in keywords if kw.strip()]
    return list(set(cleaned))

# Main Form
with st.form(key="tailor_form"):
    st.subheader("Enter Job Details")

    # Columns for company, title, job_id, and AI model
    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("Company Name*", placeholder="e.g., Google").strip()
        job_title = st.text_input("Job Title*", placeholder="e.g., Software Engineer").strip()
    with col2:
        job_id = st.text_input("Job ID (optional)", placeholder="e.g., 12345").strip()
        api_choice = st.radio("AI Model", options=["Deepseek", "Open AI"], index=0)

    # Job description text area
    job_description = st.text_area(
        "Job Description*",
        height=150,
        placeholder="Paste the job description here..."
    ).strip()

    # Make a collapsible expander for keywords
    st.subheader("Keywords")
    st.caption("Enter relevant keywords from the job description or required skills. Separate them by commas, new lines, or semicolons.")
    with st.expander("Click to enter keywords (required)"):
        keywords_text = st.text_area(
            "",
            height=150,
            help="Long keyword lists are easier to see in this expander."
        ).strip()

    # Additional instructions
    additional_instructions = st.text_area(
        "Additional Instructions (optional)",
        height=100,
        placeholder="Any extra guidance for the AI? e.g., Focus on Python experience, mention open-source contributions..."
    )

    st.divider()
    submitted = st.form_submit_button("Generate Tailored Resume")

    if submitted:
        # Validate required fields
        if not all([company, job_title, job_description, keywords_text]):
            st.error("Please fill out the required fields (Company, Title, Job Description, Keywords).")
        else:
            with st.spinner("Optimizing resume..."):
                try:
                    job_keywords = format_keywords(keywords_text)
                    sanitized_name = sanitize_filename(company, job_title, job_id)

                    st.write("## Generated Filename")
                    st.code(sanitized_name, language="text")

                    # Process resume with LLM
                    enhanced_resume, missing_kws = asyncio.run(
                        process_resume(
                            job_description,
                            additional_instructions,
                            company,
                            job_title,
                            api_choice.lower(),
                            job_id,
                            job_keywords
                        )
                    )

                    # Load original resume
                    original_resume = load_resume()

                    # Validate keyword usage again (in case LLM missed any)
                    missing_kws = validate_keyword_usage(
                        original_resume,
                        enhanced_resume,
                        job_keywords
                    )

                    # Insert record into DB
                    application_id = insert_application(
                        company, job_title, job_id,
                        enhanced_resume, job_description,
                        sanitized_name
                    )
                    st.session_state.application_id = application_id

                    st.success("Resume tailored successfully!")
                    render_resume(enhanced_resume)

                    if missing_kws:
                        st.warning(
                            f"Couldn't integrate these keywords: {', '.join(missing_kws)}\n\n"
                            "**Action Required:**\n"
                            "1. Add them manually if accurate.\n"
                            "2. Provide more context for auto-integration.\n"
                            "3. Verify the skill authenticity."
                        )

                except json.JSONDecodeError:
                    st.error("Failed to parse the AI response. Please try again.")
                    logging.error("Invalid JSON response: %s", enhanced_resume)
                except Exception as e:
                    st.error("A critical error occurred. Check the logs for more details.")
                    logging.exception("Tailoring error: %s", str(e))

# Additional controls outside the form
if st.session_state.get("application_id"):
    # "Applied" button updates the application status
    if st.button("Mark as Applied"):
        from db.operations import update_application_status
        update_application_status(st.session_state.application_id, "applied")
        st.success("Application status updated to 'applied'!")
        logging.info("Application status updated to applied for ID: %s",
                     st.session_state.application_id)

st.divider()
if st.button("Clear Session"):
    st.session_state.clear()
    st.rerun()
