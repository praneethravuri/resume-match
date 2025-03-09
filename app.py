import streamlit as st
import os
import logging
from query_llm import process_resume  # async version
from db.operations import insert_application, update_application_status
from session import init_session_state
import asyncio

# Initialize shared session state
init_session_state()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="Resume Tailor & Markdown Generator", layout="centered")
st.title("Resume Tailor & Markdown Generator")
st.write("Enter the details below to generate a tailored resume in Markdown format.")

# Use a form for inputs
with st.form(key="resume_form"):
    company = st.text_input("Company Name")
    job_title = st.text_input("Job Title")
    job_id = st.text_input("Job ID (Optional)")
    job_description = st.text_area("Job Description", height=200)
    additional_instructions = st.text_area("Additional Instructions", height=100)
    api_choice = st.radio("Select API", options=["Open AI", "Deepseek", "Local"], index=1).lower()
    submit_button = st.form_submit_button(label="Generate Markdown")

if submit_button and company and job_title and job_description:
    try:
        with st.spinner("Processing your resume..."):
            markdown_resume = asyncio.run(process_resume(job_description, additional_instructions, company, job_title, api_choice, job_id))
            st.session_state.markdown_resume = markdown_resume

        if markdown_resume:
            st.markdown("### Tailored Resume Markdown")
            st.code(markdown_resume, language="markdown")
            # Insert a new application record with status "not applied" and save the markdown content
            inserted_id = insert_application(company, job_title, job_id, markdown_resume, job_description, status="not applied")
            st.session_state.application_id = inserted_id
            st.success("Markdown resume generated successfully! Application record saved with status 'not applied'.")
        else:
            st.error("There was an error generating the markdown resume.")
    except Exception as e:
        logging.exception("Error during markdown resume generation")
        st.error("An unexpected error occurred while generating the markdown resume.")

# Button to update the application status to 'applied'
if st.session_state.get("application_id"):
    if st.button("Applied"):
         update_application_status(st.session_state.application_id, "applied")
         st.success("Application status updated to 'applied'!")
