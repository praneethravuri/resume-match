import streamlit as st
import io

# Configure the Streamlit page
st.set_page_config(page_title="Resume Match", layout="centered")

# App title and description
st.title("Job Description PDF Generator")
st.write("Enter the details below to generate a PDF of your job description.")

# Input fields
company = st.text_input("Company Name")
job_title = st.text_input("Job Title")
job_description = st.text_area("Job Description", height=200)
additional_instructions = st.text_area("Additional Instructions", height=100)

# # Only create the PDF if required fields are filled
# if company and job_title and job_description:
#     # Create a PDF object
#     pdf = FPDF()
#     pdf.add_page()
    
#     # Set a title font for header information
#     pdf.set_font("Arial", "B", size=16)
#     pdf.cell(0, 10, f"Company: {company}", ln=1)
#     pdf.cell(0, 10, f"Job Title: {job_title}", ln=1)
#     pdf.ln(10)
    
#     # Set a regular font for the body text
#     pdf.set_font("Arial", size=12)
#     pdf.multi_cell(0, 10, f"Job Description:\n{job_description}")
#     pdf.ln(5)
#     pdf.multi_cell(0, 10, f"Additional Instructions:\n{additional_instructions}")
    
#     # Save the PDF to a bytes buffer
#     pdf_buffer = io.BytesIO()
#     pdf.output(pdf_buffer)
#     pdf_buffer.seek(0)
    
#     # Download button to download the generated PDF
#     st.download_button(
#          label="Download PDF",
#          data=pdf_buffer,
#          file_name="job_description.pdf",
#          mime="application/pdf"
#     )

st.download_button(
    label = "Download resume",
    data = "ssf"
)
