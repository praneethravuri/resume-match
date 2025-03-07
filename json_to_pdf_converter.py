import json
import subprocess
import os
import logging
import PyPDF2  # New dependency for counting PDF pages

from utils.helpers import generate_pdf_filename  # Import if needed in the file

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

latex_template = r"""
% Praneeth Ravuri Resume
% Converted from HTML to LaTeX - Condensed to fit on one page

\documentclass[10pt,a4paper]{{article}}

\usepackage{{anyfontsize}}
\renewcommand{{\normalsize}}{{\fontsize{{10.75pt}}{{12.6pt}}\selectfont}}

\usepackage[margin=0.25in]{{geometry}}
\usepackage{{enumitem}}
\usepackage{{hyperref}}
\usepackage{{fontawesome}}
\usepackage{{titlesec}}
\usepackage{{color}}
\usepackage{{xcolor}}

\definecolor{{linkcolor}}{{rgb}}{{0,0,1}}
\hypersetup{{
    colorlinks=true,
    urlcolor=linkcolor,
    linkcolor=linkcolor
}}

\setlength{{\parindent}}{{0em}}
\setlength{{\parskip}}{{0.3em}}

\titleformat{{\section}}
{{\normalfont\large\bfseries}}
{{}}
{{0em}}
{{}}[{{\titlerule}}]

\titlespacing*{{\section}}{{0pt}}{{5pt}}{{3pt}}

\newcommand{{\dateplace}}[2]{{\raggedleft #1 \\ #2 \par}}
\newcommand{{\role}}[2]{{\raggedright \textbf{{#1}} \\ #2 \par}}

\setlist[itemize]{{noitemsep, topsep=0pt, parsep=0pt, partopsep=0pt, leftmargin=*}}

\begin{{document}}

\begin{{center}}
    \textbf{{\Large {name}}}\\
    \vspace{{0.2em}}
    {contact} $|$
    \href{{mailto:{email}}}{{ {email} }} $|$
    \href{{{website_url}}}{{{website}}} $|$
    \href{{https://www.{linkedin}}}{{{linkedin}}} $|$
    \href{{https://www.{github}}}{{{github}}} $|$
    {location}
\end{{center}}
\vspace{{-0.3em}}

\section*{{Education}}
\vspace{{0.5em}}
{education_section}

\section*{{Experience}}
\vspace{{0.5em}}
{experience_section}

\section*{{Skills}}
\vspace{{0.5em}}
{skills_section}

\section*{{Projects}}
\vspace{{0.5em}}
{projects_section}

\end{{document}}
"""

def generate_education_section(education_list):
    sections = []
    for edu in education_list:
        edu_entry = r"""
\begin{{minipage}}[t]{{0.70\textwidth}}
    \role{{{institution}}}{{{degree}\\{coursework}}}
\end{{minipage}}
\begin{{minipage}}[t]{{0.29\textwidth}}
    \dateplace{{{location}}}{{{dates}}}
\end{{minipage}}
\vspace{{0.5em}}
""".format(
            institution=edu.get('institution', ''),
            degree=edu.get('degree', ''),
            coursework=edu.get('coursework', ''),
            location=edu.get('location', ''),
            dates=edu.get('dates', '').replace("&ndash;", "–")
        )
        sections.append(edu_entry)
    return "\n".join(sections)

def generate_experience_section(experience_list):
    sections = []
    for exp in experience_list:
        exp_entry = r"""
\begin{{minipage}}[t]{{0.70\textwidth}}
    \role{{{company}}}{{{position}}}
\end{{minipage}}
\begin{{minipage}}[t]{{0.29\textwidth}}
    \dateplace{{{location}}}{{{dates}}}
\end{{minipage}}
\vspace{{0em}}
\begin{{itemize}}
""".format(
            company=exp.get('company', ''),
            position=exp.get('position', ''),
            location=exp.get('location', ''),
            dates=exp.get('dates', '').replace("&ndash;", "–")
        )
        for point in exp.get('points', []):
            safe_point = point.replace("%", "\\%")
            exp_entry += "\n    \\item " + safe_point
        exp_entry += r"""
\end{itemize}
\vspace{0.5em}
"""
        sections.append(exp_entry)
    return "\n".join(sections)

def generate_skills_section(skills_list):
    skills_block = r"\begin{{itemize}}"
    for skill in skills_list:
        safe_content = skill.get('content', '').replace("%", "\\%")
        skills_block += "\n    \\item \\textbf{{{label}:}} {content}".format(
            label=skill.get('label', ''), content=safe_content
        )
    skills_block += "\n\\end{itemize}"
    return skills_block

def generate_projects_section(projects_list):
    sections = []
    for proj in projects_list:
        title = proj.get('title', '')
        project_link = proj.get('projectLink', '')
        if project_link:
            proj_entry = r"\href{{{link}}}{{\textbf{{{title}}}}}".format(link=project_link, title=title)
        else:
            proj_entry = r"\textbf{{{title}}}".format(title=title)
        proj_entry += "\n\\vspace{{0.5em}}\n\\begin{{itemize}}"
        for point in proj.get('points', []):
            safe_point = point.replace("%", "\\%")
            proj_entry += "\n    \\item " + safe_point
        proj_entry += "\n\\end{itemize}\n\\vspace{{0.5em}}"
        sections.append(proj_entry)
    return "\n".join(sections)

def create_latex_resume(enhanced_resume):
    personal = enhanced_resume.get('personal', {})
    education_section = generate_education_section(enhanced_resume.get('education', []))
    experience_section = generate_experience_section(enhanced_resume.get('experience', []))
    skills_section = generate_skills_section(enhanced_resume.get('skills', []))
    projects_section = generate_projects_section(enhanced_resume.get('projects', []))
    
    website_url = personal.get('website', '')
    if not website_url.startswith("http"):
        website_url = "https://" + website_url
    
    filled_template = latex_template.format(
        name=personal.get('name', ''),
        contact=personal.get('contact', ''),
        email=personal.get('email', ''),
        website=personal.get('website', ''),
        website_url=website_url,
        linkedin=personal.get('linkedin', ''),
        github=personal.get('github', ''),
        location=personal.get('location', ''),
        education_section=education_section,
        experience_section=experience_section,
        skills_section=skills_section,
        projects_section=projects_section
    )
    return filled_template

def count_pdf_pages(pdf_filename):
    """Return the number of pages in the PDF file using PyPDF2."""
    with open(pdf_filename, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)

def generate_pdf(output_pdf_filename):
    """Generates a PDF resume from 'enhanced_resume.json', then adjusts the last project until the PDF is one page."""
    # Load enhanced resume and create LaTeX file
    try:
        with open("enhanced_resume.json", "r") as f:
            enhanced_resume = json.load(f)
        logging.info("Loaded enhanced_resume.json successfully.")
    except Exception as e:
        logging.exception("Error loading enhanced_resume.json")
        return
    
    latex_resume = create_latex_resume(enhanced_resume)
    latex_resume = latex_resume.replace(r"{{itemize}}", r"{itemize}")
    latex_resume = latex_resume.replace(r"{{0.5em}}", r"{0.5em}")
    latex_resume = latex_resume.replace("&", "\\&")
    
    try:
        with open("resume.tex", "w") as f:
            f.write(latex_resume)
        logging.info("LaTeX resume generated as 'resume.tex'")
    except Exception as e:
        logging.exception("Error writing resume.tex")
        return
    
    try:
        proc = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        logging.info("PDF generation stdout: %s", proc.stdout.decode())
        logging.info("PDF generation stderr: %s", proc.stderr.decode())
    except subprocess.CalledProcessError as e:
        logging.exception("PDF generation failed with CalledProcessError")
        logging.error("STDERR output: %s", e.stderr.decode())
    
    if os.path.exists("resume.pdf"):
        try:
            os.rename("resume.pdf", output_pdf_filename)
            logging.info("PDF renamed to '%s'", output_pdf_filename)
        except Exception as e:
            logging.exception("Error renaming PDF file")
    else:
        logging.error("resume.pdf not found after pdflatex run.")
        return

    # Check number of pages in the generated PDF
    try:
        page_count = count_pdf_pages(output_pdf_filename)
        logging.info("Initial PDF page count: %d", page_count)
    except Exception as e:
        logging.exception("Error counting PDF pages")
        return

    # Iteratively remove points from the last project until PDF is exactly one page.
    while page_count > 1:
        logging.info("PDF has %d pages, adjusting projects...", page_count)
        try:
            with open("enhanced_resume.json", "r") as f:
                enhanced_resume = json.load(f)
        except Exception as e:
            logging.exception("Error loading enhanced_resume.json during adjustment")
            break

        # Check if there is at least one project
        if "projects" in enhanced_resume and enhanced_resume["projects"]:
            last_project = enhanced_resume["projects"][-1]
            if "points" in last_project and len(last_project["points"]) >= 2:
                removed_point = last_project["points"].pop()  # Remove the last bullet point
                logging.info("Removed a bullet point: %s", removed_point)
            else:
                logging.info("Removing entire project because it has fewer than 2 points.")
                enhanced_resume["projects"].pop()  # Remove the whole project
        else:
            logging.info("No projects left to adjust.")
            break

        # Save updated resume JSON
        with open("enhanced_resume.json", "w") as f:
            json.dump(enhanced_resume, f, indent=2)

        # Regenerate the LaTeX resume and PDF
        latex_resume = create_latex_resume(enhanced_resume)
        latex_resume = latex_resume.replace(r"{{itemize}}", r"{itemize}")
        latex_resume = latex_resume.replace(r"{{0.5em}}", r"{0.5em}")
        latex_resume = latex_resume.replace("&", "\\&")
        with open("resume.tex", "w") as f:
            f.write(latex_resume)
        logging.info("Regenerated resume.tex with updated projects.")

        try:
            proc = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logging.info("Regenerated PDF stdout: %s", proc.stdout.decode())
        except subprocess.CalledProcessError as e:
            logging.exception("PDF regeneration failed during adjustment")
            break

        if os.path.exists("resume.pdf"):
            try:
                os.rename("resume.pdf", output_pdf_filename)
            except Exception as e:
                logging.exception("Error renaming regenerated PDF")
        try:
            page_count = count_pdf_pages(output_pdf_filename)
            logging.info("New PDF page count: %d", page_count)
        except Exception as e:
            logging.exception("Error counting pages after regeneration")
            break

    logging.info("Final PDF page count: %d", page_count)
