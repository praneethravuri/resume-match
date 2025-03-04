import streamlit as st
import os
from query_llm import process_resume

# Configure the Streamlit page
st.set_page_config(page_title="Resume Match", layout="centered")
st.title("Resume Tailor & PDF Generator")
st.write("Enter the details below to generate a tailored resume PDF.")

# Input fields for company name, job title, job description, and additional instructions
company = st.text_input("Company Name")
job_title = st.text_input("Job Title")
job_description = st.text_area("Job Description", height=200)
additional_instructions = st.text_area("Additional Instructions", height=100)

# Process inputs and generate PDF when button is pressed
if st.button("Generate PDF") and company and job_title and job_description:
    with st.spinner("Processing your resume..."):
        pdf_path = process_resume(job_description, additional_instructions, company, job_title)
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            # The download file name is renamed according to company and position
            download_filename = f"praneeth_ravuri_resume_{company}_{job_title}.pdf"
            st.download_button(label="Download PDF", data=pdf_data, file_name=download_filename.lower(), mime="application/pdf")
            st.success("PDF generated successfully!")
        else:
            st.error("There was an error generating the PDF.")
