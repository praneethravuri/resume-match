import streamlit as st
import logging
import json
from db.operations import get_all_applications, update_application_status, delete_application
from utils.helpers import generate_markdown_resume
from utils.format_resume_data import render_resume

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("Tracker page loaded.")
st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")

def main():
    logging.info("Starting main function in Tracker.")
    st.title("Job Application Tracker 📋")
    applications = get_all_applications()
    if not applications:
        st.info("No applications found. Start adding your job applications to track them.")
        logging.info("No applications found.")
        return

    # Initialize filtered_apps to the full applications list
    filtered_apps = applications.copy()

    # Sidebar filters with search functionality
    with st.sidebar:
        st.header("Filters")
        with st.form(key="filter_form"):
            status_options = ["not applied", "applied", "interview", "rejected", "selected", "sent cold emails"]
            status_filter = st.multiselect("Status", options=status_options, default=[])
            companies = sorted(list(set(app.get("company_name", "") for app in applications)))
            company_filter = st.multiselect("Company", options=companies, default=[])
            search_query = st.text_input("Search (Role or Company)")
            sort_options = ["Date (newest first)", "Date (oldest first)", "Company", "Status"]
            sort_by = st.selectbox("Sort by", options=sort_options, index=0)
            submitted = st.form_submit_button("Apply Filters")
            if submitted:
                logging.info("Filter form submitted with status: %s, company: %s, search: %s", status_filter, company_filter, search_query)

        if submitted:
            if status_filter:
                filtered_apps = [app for app in filtered_apps if app.get("status", "") in status_filter]
            if company_filter:
                filtered_apps = [app for app in filtered_apps if app.get("company_name", "") in company_filter]
            if search_query:
                query = search_query.lower()
                filtered_apps = [
                    app for app in filtered_apps
                    if query in app.get("company_name", "").lower() or query in app.get("title", "").lower()
                ]
            logging.info("Filtered applications count: %d", len(filtered_apps))

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
                    logging.info("Application ID %s status changed from %s to %s", doc["_id"], current_status, new_status)
                    st.rerun()
            with col2:
                if st.button("Show Markdown", key=f"gen_{doc['_id']}"):
                    st.markdown("### Resume Points")
                    render_resume(doc.get("resume_content"))
            with col3:
                if st.button("Delete", key=f"delete_{doc['_id']}"):
                    delete_application(doc["_id"])
                    st.success("Application deleted!")
                    logging.info("Deleted application ID %s", doc["_id"])
                    st.rerun()
            with st.expander("Job Description"):
                st.write(doc.get('job_description', 'No description available.'))
            if i < len(filtered_apps) - 1:
                st.divider()

if __name__ == "__main__":
    main()
