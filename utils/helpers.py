import os
import logging
import re
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("helpers module loaded.")

def sanitize_filename(text):
    """Sanitize a string to be used in a filename by replacing spaces, hyphens, and commas with underscores."""
    sanitized = re.sub(r"[\s\-,]+", "_", text)
    logging.info("Sanitized filename: %s", sanitized)
    return sanitized

def generate_pdf_filename(company, title, job_id=""):
    """
    This function is retained for legacy reasons.
    PDF generation is no longer used; filenames are not required.
    """
    sanitized_company = sanitize_filename(company)
    sanitized_title = sanitize_filename(title)
    filename = f"praneeth_ravuri_resume_{sanitized_company}_{sanitized_title}"
    if job_id.strip():
        sanitized_job_id = sanitize_filename(job_id)
        filename += f"_{sanitized_job_id}"
    final_filename = filename + ".pdf"
    logging.info("Generated PDF filename: %s", final_filename)
    return final_filename

def generate_markdown_resume(enhanced_resume):
    """
    Generate Markdown for the resume in the following format:
    
    Company/Project Name:
    
    bullet point 1
    bullet point 2
    bullet point 3

    The company/project name is displayed separately from the bullet points so that when copying,
    only the bullet points are included.
    """
    logging.info("Generating markdown resume.")
    md_lines = []
    # Process experience entries
    for exp in enhanced_resume.get("experience", []):
        company = exp.get("company", "")
        md_lines.append(f"**{company}:**")
        bullet_points = "\n".join(exp.get("points", []))
        md_lines.append(bullet_points)
        md_lines.append("")
    # Process project entries
    for proj in enhanced_resume.get("projects", []):
        title = proj.get("title", "")
        md_lines.append(f"**{title}:**")
        bullet_points = "\n".join(proj.get("points", []))
        md_lines.append(bullet_points)
        md_lines.append("")
    markdown = "\n".join(md_lines)
    logging.info("Markdown resume generated.")
    return markdown

def cleanup_generated_files():
    """Clean up temporary files created during resume generation."""
    files_to_remove = ["data/enhanced_resume.json"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            logging.info("Removed file: %s", file)
