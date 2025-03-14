import streamlit as st
from logic.query_llm import process_resume, load_resume, validate_keyword_usage
import asyncio
import json
from utils.format_resume_data import render_resume
import logging
from db.operations import insert_application, update_application_status
from utils.helpers import sanitize_filename
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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

with st.form(key="tailor_form"):
    company = st.text_input("Company Name*").strip()
    job_title = st.text_input("Job Title*").strip()
    job_id = st.text_input("Job ID").strip()
    job_description = st.text_area("Job Description*", height=200).strip()
    keywords = st.text_area("Keywords (comma/newline separated)*", 
                          help="Enter relevant keywords from job description",
                          height=300).strip()
    additional_instructions = st.text_area("Additional Instructions", height=100)
    api_choice = st.radio("AI Model", options=["Deepseek", "Open AI"], index=0)
    submitted = st.form_submit_button("Generate Tailored Resume")
    
    if submitted:
        if not all([company, job_title, job_description, keywords]):
            st.error("Please fill required fields (*)")
        else:
            with st.spinner("Optimizing resume..."):
                try:
                    job_keywords = format_keywords(keywords)
                    sanitized_name = sanitize_filename(company, job_title, job_id)
                    
                    st.write("###Filename:")
                    st.code(sanitize_filename, language="text")
                    # Process resume through LLM
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
                    
                    # Parse and validate response
                    
                    original_resume = load_resume()
                    
                    # Show keyword integration results
                    missing_kws = validate_keyword_usage(
                        original_resume, 
                        enhanced_resume,
                        job_keywords
                    )
                    
                    # Database operations
                    application_id = insert_application(
                        company, job_title, job_id,
                        enhanced_resume, job_description,
                        sanitized_name
                    )
                    
                    # Display results
                    st.success("Resume tailored successfully!")
                    render_resume(enhanced_resume)
                    
                    if missing_kws:
                        st.warning(
                            f"Couldn't integrate these keywords: {', '.join(missing_kws)}\n\n"
                            "**Action Required:**\n"
                            "1. Add manually if accurate\n"
                            "2. Provide more context for auto-integration\n"
                            "3. Verify skill authenticity"
                        )
                    
                except json.JSONDecodeError:
                    st.error("Failed to parse AI response. Please try again.")
                    logging.error("Invalid JSON response: %s", enhanced_resume)
                except Exception as e:
                    st.error("Critical error during processing. Check logs.")
                    logging.exception("Tailoring error: %s", str(e))
                    
if st.session_state.get("application_id"):
    if st.button("Applied"):
         from db.operations import update_application_status
         update_application_status(st.session_state.application_id, "applied")
         st.success("Application status updated to 'applied'!")
         logging.info("Application status updated to applied for ID: %s", st.session_state.application_id)

if st.button("Clear Session"):
    st.session_state.clear()
    st.rerun()