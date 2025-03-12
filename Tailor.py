import streamlit as st
from logic.query_llm import process_resume
import asyncio
import json
from utils.format_resume_data import render_resume
import logging
from db.operations import insert_application, update_application_status
from utils.helpers import sanitize_filename

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Tailor page loaded.")

st.set_page_config(
    page_title="Resume Tailor and Application Tracker",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Resume Tailor")
st.write("Enter the details below to generate a tailored resume in Markdown format.")

def format_keywords(keywords):
    keywords = keywords.split("\n")
    keywords = [kw.strip().lower() for kw in keywords]
    keywords = list(set(keywords))
    return keywords

with st.form(key="resume_form"):
    company = st.text_input("Company Name").strip()
    job_title = st.text_input("Job Title").strip()
    job_id = st.text_input("Job ID (Optional)").strip()
    job_description = st.text_area("Job Description", height=200).strip()
    keywords = st.text_area("Keywords", height=200).strip()
    additional_instructions = st.text_area("Additional Instructions", height=100)
    api_choice = st.radio("Select API", options=["Open AI", "Deepseek"], index=1).lower()
    submit_button = st.form_submit_button(label="Generate Resume Points")
    
    if submit_button and company and job_title and job_description:
        logging.info("Form submitted in Tailor with company: %s, job_title: %s", company, job_title)
        try:
            sanitized_filename = sanitize_filename(company, job_title, job_id)
            st.write("## File Name")
            st.code(sanitized_filename)
            logging.info("Sanitized filename: %s", sanitized_filename)
            job_keywords = format_keywords(keywords)
            logger.info(f"Formatted keywords: {job_keywords}")
            with st.spinner("Processing your resume..."):
                resume_data = asyncio.run(
                    process_resume(job_description, additional_instructions, company, job_title, api_choice, job_id, job_keywords)
                )
            logging.info("Received resume data from process_resume.")
            

                
            resume_data_dict = json.loads(resume_data)
            
            application_id = insert_application(company, job_title, job_id, resume_data_dict, job_description, sanitized_filename)
            logging.info("Application inserted with ID: %s", application_id)
            
            st.session_state["application_id"] = application_id
            
            render_resume(resume_data_dict)
            logging.info("Rendered resume data successfully.")
        except Exception as e:
            logging.exception("Error generating resume points in Tailor")
            st.error("An unexpected error occurred while generating the resume points.")
            
        st.session_state["company"] = ""
        st.session_state["job_title"] = ""
        st.session_state["job_id"] = ""
        st.session_state["job_description"] = ""
        
if st.session_state.get("application_id"):
    if st.button("Applied"):
         from db.operations import update_application_status
         update_application_status(st.session_state.application_id, "applied")
         st.success("Application status updated to 'applied'!")
         logging.info("Application status updated to applied for ID: %s", st.session_state.application_id)

