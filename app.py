import streamlit as st
import os
from query_llm import process_resume
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configure the Streamlit page
st.set_page_config(page_title="Resume Tailor & PDF Generator", layout="centered")
st.title("Resume Tailor & PDF Generator")
st.write("Enter the details below to generate a tailored resume PDF.")

# --- New API Selection using radio buttons (only one can be selected) ---
api_choice = st.radio("Select API", options=["Open AI", "Deepseek"], index=1).lower()



# Input fields for company, job title, job description, and additional instructions
company = st.text_input("Company Name")
job_title = st.text_input("Job Title")
# --- New Optional Job ID input ---
job_id = st.text_input("Job ID (Optional)")
job_description = st.text_area("Job Description", height=200)
additional_instructions = st.text_area("Additional Instructions", height=100)

# Define cleanup function to remove generated files
def cleanup_generated_files(pdf_path):
    files_to_remove = [
        pdf_path,
        "enhanced_resume.json",
        "resume.aux",
        "resume.tex",
        "resume.out",
        "resume.log"
    ]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            logging.info("Removed file: %s", file)

if st.button("Generate PDF") and company and job_title and job_description:
    try:
        with st.spinner("Processing your resume..."):
            # Pass the API selection and job_id to process_resume
            pdf_path = process_resume(job_description, additional_instructions, company, job_title, api_choice, job_id)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()
                # Determine download filename based on job_id
                if job_id.strip():
                    download_filename = f"praneeth_ravuri_resume_{company}_{job_title}_{job_id}.pdf"
                else:
                    download_filename = f"praneeth_ravuri_resume_{company}_{job_title}.pdf"
                
                # Download button with an on_click callback for cleanup
                def cleanup_callback():
                    cleanup_generated_files(pdf_path)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=download_filename,
                    mime="application/pdf",
                    on_click=cleanup_callback
                )
                st.success("PDF generated successfully!")
            else:
                st.error("There was an error generating the PDF.")
    except Exception as e:
        logging.exception("Error during PDF generation")
        st.error("An unexpected error occurred while generating the PDF.")
