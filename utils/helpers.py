import os
import logging
import re
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("helpers module loaded.")

def sanitize_filename(company, title, job_id):
    if title:
        temp_file_name = f"praneeth_ravuri_resume_{company}_{title}_{job_id}"
    else:
        temp_file_name = f"praneeth_ravuri_resume_{company}_{title}"
    
    # The regex below replaces spaces, commas, hyphens, and parentheses with underscores.
    sanitized_file_name = re.sub(r"[\s,\-\(\)]+", "_", temp_file_name)
    logging.info("Sanitized filename: %s", sanitized_file_name)
    return sanitized_file_name