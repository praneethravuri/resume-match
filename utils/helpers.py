import os
import logging
import re

def cleanup_generated_files(pdf_path):
    """Clean up temporary files created during PDF generation."""
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

def sanitize_filename(text):
    """Sanitize a string to be used in a filename by replacing spaces, hyphens, and commas with underscores."""
    # Replace spaces, hyphens, and commas with underscores
    sanitized = re.sub(r"[\s\-,]+", "_", text)
    return sanitized

def generate_pdf_filename(company, title, job_id=""):
    """Generate a standardized PDF filename using sanitized inputs."""
    sanitized_company = sanitize_filename(company)
    sanitized_title = sanitize_filename(title)
    filename = f"praneeth_ravuri_resume_{sanitized_company}_{sanitized_title}"
    if job_id.strip():
        sanitized_job_id = sanitize_filename(job_id)
        filename += f"_{sanitized_job_id}"
    return filename + ".pdf"
