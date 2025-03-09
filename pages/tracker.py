import streamlit as st
import os
import logging
from db.operations import get_all_applications, update_application_status, delete_application
from utils.helpers import generate_markdown_resume
import pandas as pd
from session import init_session_state
import json

# Initialize shared session state
init_session_state()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")

def main():
    st.title("Job Application Tracker 📋")
    applications = get_all_applications()
    if not applications:
        st.info("No applications found. Start adding your job applications to track them.")
        return

    # Sidebar filters with a modern form layout
    with st.sidebar:
        st.header("Filters")
        with st.form(key="filter_form"):
            status_options = ["not applied", "applied", "interview", "rejected", "selected", "sent cold emails"]
            status_filter = st.multiselect("Status", options=status_options, default=[])
            companies = sorted(list(set(app.get("company_name", "") for app in applications)))
            company_filter = st.multiselect("Company", options=companies, default=[])
            sort_options = ["Date (newest first)", "Date (oldest first)", "Company", "Status"]
            sort_by = st.selectbox("Sort by", options=sort_options, index=0)
            submitted = st.form_submit_button("Apply Filters")
    # Display metrics in a modern layout
    col1, col2, col3, col4 = st.columns(4)
    total = len(applications)
    not_applied = sum(1 for app in applications if app.get("status") == "not applied")
    applied = sum(1 for app in applications if app.get("status") == "applied")
    interview = sum(1 for app in applications if app.get("status") == "interview")
    selected = sum(1 for app in applications if app.get("status") == "selected")
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Not Applied", not_applied)
    with col3:
        st.metric("Interviews", interview)
    with col4:
        st.metric("Offers", selected)
        
    filtered_apps = applications
    if submitted:
        if status_filter:
            filtered_apps = [app for app in filtered_apps if app.get("status", "") in status_filter]
        if company_filter:
            filtered_apps = [app for app in filtered_apps if app.get("company_name", "") in company_filter]
        sort_key_map = {
            "Date (newest first)": lambda x: x.get("date_applied", ""),
            "Date (oldest first)": lambda x: x.get("date_applied", ""),
            "Company": lambda x: x.get("company_name", ""),
            "Status": lambda x: x.get("status", "")
        }
        reverse_sort = sort_by == "Date (newest first)"
        filtered_apps = sorted(filtered_apps, key=sort_key_map[sort_by], reverse=reverse_sort)
        st.caption(f"Showing {len(filtered_apps)} of {total} applications")
    
    for i, doc in enumerate(filtered_apps):
        company = doc.get('company_name', '')
        title = doc.get('title', '')
        job_id = doc.get('job_id', 'N/A')
        date_applied = doc.get('date_applied', 'N/A')
        current_status = doc.get("status", "not applied")
        status_colors = {
            "not applied": "🟠",
            "applied": "🟢",
            "interview": "🔵",
            "rejected": "🔴",
            "selected": "🟢",
            "sent cold emails": "🟣"
        }
        status_emoji = status_colors.get(current_status, "⚪")
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{company} - {title}")
                st.caption(f"Applied: {date_applied} | ID: {job_id}")
            with col2:
                st.write(f"**Status:** {status_emoji} {current_status.upper()}")
            col1, col2, col3 = st.columns(3)
            with col1:
                options = ["not applied", "applied", "interview", "rejected", "selected", "sent cold emails"]
                new_status = st.selectbox(
                    "Update Status", 
                    options=options, 
                    index=options.index(current_status), 
                    key=f"status_{doc['_id']}"
                )
                if new_status != current_status:
                    update_application_status(doc["_id"], new_status)
                    st.success("Updated!")
                    st.experimental_rerun()
            with col2:
                if st.button("Show Markdown", key=f"gen_{doc['_id']}"):
                    markdown_resume = generate_markdown_for_document(doc)
                    st.markdown("### Resume Markdown")
                    st.code(markdown_resume, language="markdown")
            with col3:
                if st.button("Delete", key=f"delete_{doc['_id']}"):
                    delete_application(doc["_id"])
                    st.success("Application deleted!")
                    st.experimental_rerun()
            with st.expander("Job Description"):
                st.write(doc.get('job_description', 'No description available.'))
            if i < len(filtered_apps) - 1:
                st.divider()

def generate_markdown_for_document(doc):
    # Write the stored resume markdown content to a temporary file and read it back
    with open("enhanced_resume.json", "w") as f:
        f.write(doc["resume_content"])
    with open("enhanced_resume.json", "r") as f:
        enhanced_resume = json.load(f)
    markdown_resume = generate_markdown_resume(enhanced_resume)
    return markdown_resume

if __name__ == "__main__":
    main()
