import streamlit as st
import os
import logging
from query_llm import process_resume  # async version
from db.operations import insert_application, update_application_status
from utils.helpers import cleanup_generated_files, generate_pdf_filename
from session import init_session_state
import asyncio

# Initialize shared session state
init_session_state()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

st.set_page_config(page_title="Resume Tailor & PDF Generator", layout="centered")
st.title("Resume Tailor & PDF Generator")
st.write("Enter the details below to generate a tailored resume PDF.")

# Use a form for inputs
with st.form(key="resume_form"):
    company = st.text_input("Company Name")
    job_title = st.text_input("Job Title")
    job_id = st.text_input("Job ID (Optional)")
    job_description = st.text_area("Job Description", height=200)
    additional_instructions = st.text_area("Additional Instructions", height=100)
    api_choice = st.radio("Select API", options=["Open AI", "Deepseek", "Local"], index=1).lower()
    submit_button = st.form_submit_button(label="Generate PDF")

if submit_button and company and job_title and job_description:
    if st.session_state.pdf_path:
        cleanup_generated_files(st.session_state.pdf_path)
    try:
        with st.spinner("Processing your resume..."):
            # Use asyncio to call async process_resume
            pdf_path = asyncio.run(process_resume(job_description, additional_instructions, company, job_title, api_choice, job_id))
            st.session_state.pdf_path = pdf_path
            if os.path.exists("enhanced_resume.json"):
                with open("enhanced_resume.json", "r") as f:
                    st.session_state.resume_content = f.read()
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            st.session_state.pdf_data = pdf_data  # Store PDF data in session state
            download_filename = generate_pdf_filename(company, job_title, job_id)
            
            # Insert a new application record with status "not applied"
            inserted_id = insert_application(company, job_title, job_id, st.session_state.resume_content, job_description, status="not applied")
            st.session_state.application_id = inserted_id
            
            def download_callback():
                cleanup_generated_files(st.session_state.pdf_path)
                st.session_state.pdf_downloaded = True
            
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=download_filename,
                mime="application/pdf",
                on_click=download_callback
            )
            st.success("PDF generated successfully! Application record saved with status 'not applied'.")
        else:
            st.error("There was an error generating the PDF.")
    except Exception as e:
        logging.exception("Error during PDF generation")
        st.error("An unexpected error occurred while generating the PDF.")

# When the user clicks the Applied button, update the record to status "applied" and add the date.
if st.session_state.get("pdf_downloaded", False):
    if st.button("Applied"):
         if st.session_state.application_id:
             update_application_status(st.session_state.application_id, "applied")
             st.success("Application status updated to 'applied'!")
         else:
             st.error("No application record found to update.")
