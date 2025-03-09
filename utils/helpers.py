import os
import logging
import re

def sanitize_filename(text):
    """Sanitize a string to be used in a filename by replacing spaces, hyphens, and commas with underscores."""
    sanitized = re.sub(r"[\s\-,]+", "_", text)
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
    return filename + ".pdf"

def generate_markdown_resume(enhanced_resume):
    """Generate a Markdown representation of the enhanced resume."""
    md = []

    # Personal Section
    personal = enhanced_resume.get("personal", {})
    md.append("# Personal")
    for key, value in personal.items():
        md.append(f"- **{key.capitalize()}**: {value}")
    md.append("")

    # Education Section
    education = enhanced_resume.get("education", [])
    md.append("# Education")
    for edu in education:
        md.append(f"- **Institution**: {edu.get('institution', '')}")
        md.append(f"  - **Degree**: {edu.get('degree', '')}")
        md.append(f"  - **Coursework**: {edu.get('coursework', '')}")
        md.append(f"  - **Location**: {edu.get('location', '')}")
        md.append(f"  - **Dates**: {edu.get('dates', '')}")
    md.append("")

    # Experience Section
    experience = enhanced_resume.get("experience", [])
    md.append("# Experience")
    for exp in experience:
        md.append(f"- **Company**: {exp.get('company', '')}")
        md.append(f"  - **Position**: {exp.get('position', '')}")
        md.append(f"  - **Location**: {exp.get('location', '')}")
        md.append(f"  - **Dates**: {exp.get('dates', '')}")
        points = exp.get("points", [])
        if points:
            md.append("  - **Points:**")
            for pt in points:
                md.append(f"    - {pt}")
    md.append("")

    # Skills Section
    skills = enhanced_resume.get("skills", [])
    md.append("# Skills")
    for skill in skills:
        label = skill.get("label", "")
        content = skill.get("content", "")
        md.append(f"- **{label}**: {content}")
    md.append("")

    # Projects Section
    projects = enhanced_resume.get("projects", [])
    md.append("# Projects")
    for proj in projects:
        md.append(f"- **Title**: {proj.get('title', '')}")
        if proj.get('projectLink', ''):
            md.append(f"  - **Link**: {proj.get('projectLink', '')}")
        points = proj.get("points", [])
        if points:
            md.append("  - **Points:**")
            for pt in points:
                md.append(f"    - {pt}")
    md.append("")

    return "\n".join(md)

def cleanup_generated_files():
    """Clean up temporary files created during resume generation."""
    files_to_remove = ["enhanced_resume.json"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            logging.info("Removed file: %s", file)
