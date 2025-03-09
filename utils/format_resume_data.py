import streamlit as st
import logging

def render_coursework(coursework):
    logging.info("Rendering coursework, total items: %d", len(coursework))
    n = len(coursework)
    # Aggregate first and second half of coursework into strings
    coursework_first = ", ".join(coursework[0:n//2])
    coursework_second = ", ".join(coursework[n//2:])
    
    st.write("## Coursework")
    st.code(f"Coursework: {coursework_first}", language="text")
    st.code(f"**Coursework**: {coursework_second}", language="text")

def render_work_experience(experience):
    logging.info("Rendering work experience, total jobs: %d", len(experience))
    st.write("## Work Experience")
    for job in experience:
        header = f"### {job.get('company', 'Unknown Company')}"
        st.write(header)
        # Aggregate bullet points into a single string with dashes
        points = "\n".join([f"{point}" for point in job.get('points', [])])
        st.code(points, language="text")
    logging.info("Work experience rendered.")
            
def render_projects(projects):
    logging.info("Rendering projects, total projects: %d", len(projects))
    st.write("## Projects")
    for project in projects:
        header = f"### {project.get('title', 'Untitled Project')}"
        st.write(header)
        points = "\n".join([f"{point}" for point in project.get('points', [])])
        st.code(points, language="text")
    logging.info("Projects rendered.")
            
def render_skills(skills):
    logging.info("Rendering skills, total categories: %d", len(skills))
    st.write("## Skills")
    for category in skills:
        # Display each skill category in a code block for copyability
        content = category.get('content', '')
        st.code(f"{category.get('label', '')}: {content}", language="text")
    logging.info("Skills rendered.")
        
def render_resume(resume_data):
    logging.info("Rendering full resume.")
    coursework = resume_data.get("coursework", [])
    experience = resume_data.get("experience", [])
    projects = resume_data.get("projects", [])
    skills = resume_data.get("skills", [])
    
    render_coursework(coursework)
    render_work_experience(experience)
    render_projects(projects)
    render_skills(skills)
    logging.info("Full resume rendered.")
