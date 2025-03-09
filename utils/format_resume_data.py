import streamlit as st
import logging

def render_coursework(coursework):
    logging.info("Rendering coursework, total items: %d", len(coursework))
    n = len(coursework)
    st.write("## Coursework")
    
    st.write("### First Half")
    for i in range(n // 2):
        st.write(f"* {coursework[i]}")
        
    st.write("### Second Half")
    for i in range(n // 2, n):
        st.write(f"* {coursework[i]}")
    logging.info("Coursework rendered.")

def render_work_experience(experience):
    logging.info("Rendering work experience, total jobs: %d", len(experience))
    st.write("## Work Experience")
    for job in experience:
        st.write(f"### {job.get('company', 'Unknown Company')}")
        for point in job.get('points', []):
            st.write(f"* {point}")
    logging.info("Work experience rendered.")
            
def render_projects(projects):
    logging.info("Rendering projects, total projects: %d", len(projects))
    st.write("## Projects")
    for project in projects:
        st.write(f"### {project.get('title', 'Untitled Project')}")
        for point in project.get('points', []):
            st.write(f"* {point}")
    logging.info("Projects rendered.")
            
def render_skills(skills):
    logging.info("Rendering skills, total categories: %d", len(skills))
    st.write("## Skills")
    for category in skills:
        st.write(f"**{category.get('label', '')}**: {category.get('content', '')}")
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
