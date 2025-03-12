import streamlit as st
import logging
from datetime import datetime
from db.operations import (
    get_all_applications, 
    update_application_status, 
    update_application_toggle, 
    delete_application
)
from utils.format_resume_data import render_resume
from utils.linkedin_message_generator import generate_linkedin_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
st.set_page_config(page_title="Job Application Tracker", page_icon="📋", layout="wide")

# --- Helper Functions ---

def get_date(app):
    """Convert the date string to a datetime object; return datetime.min if invalid."""
    date_str = app.get("date_applied", "")
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return datetime.min

def sort_date_newest_key(app):
    """Key: descending date, then ascending company and title."""
    dt = get_date(app)
    try:
        ts = dt.timestamp()
    except Exception:
        ts = 0
    return (-ts, app.get("company_name", "").lower(), app.get("title", "").lower())

def sort_date_oldest_key(app):
    """Key: ascending date, then ascending company and title."""
    dt = get_date(app)
    try:
        ts = dt.timestamp()
    except Exception:
        ts = 0
    return (ts, app.get("company_name", "").lower(), app.get("title", "").lower())

# --- Initialize Session State ---
if "filters" not in st.session_state:
    st.session_state.filters = {}

# --- Main Application ---

def main():
    st.title("Job Application Tracker 📋")
    
    # Retrieve all applications from the database
    applications = get_all_applications()
    if not applications:
        st.info("No applications found. Start adding your job applications to track them.")
        logging.info("No applications found.")
        return
    
    # Sort applications by date_applied in descending order (latest first)
    applications.sort(key=lambda app: app.get("date_applied", ""), reverse=True)
    
    # Calculate primary/secondary status metrics
    metrics = {"applied": 0, "not applied": 0, "interview": 0, "rejected": 0, "selected": 0}
    for app in applications:
        primary = app.get("primary_status", app.get("status", "not applied"))
        secondary = app.get("secondary_status", "")
        if primary == "applied":
            metrics["applied"] += 1
        else:
            metrics["not applied"] += 1
        if secondary:
            metrics[secondary] += 1

    # Additional metrics for cold email and linkedin not sent
    cold_email_not_sent = sum(1 for app in applications if not app.get("sent_cold_email", False))
    linkedin_not_sent = sum(1 for app in applications if not app.get("sent_linkedin_message", False))
    
    st.subheader("Application Metrics")
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.metric("Applied", metrics["applied"])
    with col2:
        st.metric("Not Applied", metrics["not applied"])
    with col3:
        st.metric("Interview", metrics["interview"])
    with col4:
        st.metric("Rejected", metrics["rejected"])
    with col5:
        st.metric("Selected", metrics["selected"])
    with col6:
        st.metric("No Cold Email", cold_email_not_sent)
    with col7:
        st.metric("No LinkedIn Msg", linkedin_not_sent)

    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("Filters")
        with st.form(key="filter_form"):
            status_options = ["not applied", "applied", "interview", "rejected", "selected"]
            status_filter = st.multiselect(
                "Status", 
                options=status_options, 
                default=st.session_state.filters.get("status_filter", [])
            )
            companies = sorted(list(set(app.get("company_name", "") for app in applications)))
            company_filter = st.multiselect(
                "Company", 
                options=companies, 
                default=st.session_state.filters.get("company_filter", [])
            )
            search_query = st.text_input(
                "Search (Role or Company)", 
                value=st.session_state.filters.get("search_query", "")
            )
            favorite_filter = st.checkbox(
                "Favorites Only", 
                value=st.session_state.filters.get("favorite_filter", False)
            )
            cold_email_not_sent_filter = st.checkbox(
                "Jobs with NO Cold Email Sent", 
                value=st.session_state.filters.get("cold_email_not_sent_filter", False)
            )
            linkedin_not_sent_filter = st.checkbox(
                "Jobs with NO LinkedIn Message Sent", 
                value=st.session_state.filters.get("linkedin_not_sent_filter", False)
            )
            missing_both_filter = st.checkbox(
                "Jobs missing BOTH Cold Email & LinkedIn", 
                value=st.session_state.filters.get("missing_both_filter", False)
            )
            sort_options = ["Date (newest first)", "Date (oldest first)", "Company", "Status"]
            sort_by = st.selectbox(
                "Sort by", 
                options=sort_options, 
                index=sort_options.index(st.session_state.filters.get("sort_by", "Date (newest first)"))
            )
            submitted = st.form_submit_button("Apply Filters")
            if submitted:
                # Save the current filters into session state
                st.session_state.filters = {
                    "status_filter": status_filter,
                    "company_filter": company_filter,
                    "search_query": search_query,
                    "favorite_filter": favorite_filter,
                    "cold_email_not_sent_filter": cold_email_not_sent_filter,
                    "linkedin_not_sent_filter": linkedin_not_sent_filter,
                    "missing_both_filter": missing_both_filter,
                    "sort_by": sort_by
                }
                st.rerun()
    
    # --- Apply Filters ---
    filtered_apps = applications.copy()
    filters = st.session_state.filters
    if filters.get("status_filter"):
        filtered_apps = [
            app for app in filtered_apps 
            if (app.get("primary_status", app.get("status", "not applied")) in filters["status_filter"] 
                or app.get("secondary_status", "") in filters["status_filter"])
        ]
    if filters.get("company_filter"):
        filtered_apps = [app for app in filtered_apps if app.get("company_name", "") in filters["company_filter"]]
    if filters.get("search_query"):
        query = filters["search_query"].lower()
        filtered_apps = [
            app for app in filtered_apps 
            if query in app.get("company_name", "").lower() or query in app.get("title", "").lower()
        ]
    if filters.get("favorite_filter"):
        filtered_apps = [app for app in filtered_apps if app.get("favorite", False)]
    if filters.get("cold_email_not_sent_filter"):
        filtered_apps = [app for app in filtered_apps if not app.get("sent_cold_email", False)]
    if filters.get("linkedin_not_sent_filter"):
        filtered_apps = [app for app in filtered_apps if not app.get("sent_linkedin_message", False)]
    if filters.get("missing_both_filter"):
        filtered_apps = [
            app for app in filtered_apps 
            if not app.get("sent_cold_email", False) and not app.get("sent_linkedin_message", False)
        ]
    
    # --- Apply Sorting ---
    sort_by = filters.get("sort_by", "Date (newest first)")
    if sort_by == "Date (newest first)":
        filtered_apps.sort(key=sort_date_newest_key)
    elif sort_by == "Date (oldest first)":
        filtered_apps.sort(key=sort_date_oldest_key)
    elif sort_by == "Company":
        filtered_apps.sort(key=lambda app: (app.get("company_name", "").lower(), get_date(app)))
    elif sort_by == "Status":
        filtered_apps.sort(key=lambda app: app.get("primary_status", app.get("status", "not applied")))
    
    # --- Display All Filtered Applications ---
    for i, doc in enumerate(filtered_apps):
        company = doc.get('company_name', '')
        title = doc.get('title', '')
        job_id = doc.get('job_id', 'N/A')
        date_applied = doc.get('date_applied', 'N/A')
        primary_status = doc.get("primary_status", doc.get("status", "not applied"))
        secondary_status = doc.get("secondary_status", "")
        effective_status = secondary_status if secondary_status else primary_status
        
        status_emojis = {
            "not applied": "🟠",
            "applied": "🟢",
            "interview": "🔵",
            "rejected": "🔴",
            "selected": "🟢"
        }
        status_emoji = status_emojis.get(effective_status, "⚪")
        
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{company} - {title}")
                st.caption(f"Applied: {date_applied} | Job Id: {job_id}")
                st.code(doc.get("file_name", "N/A"), language="text")
            with col2:
                st.write(f"**Status:** {status_emoji} {effective_status.upper()}")
            cold_status = "Sent" if doc.get("sent_cold_email", False) else "Not Sent"
            linkedin_status = "Sent" if doc.get("sent_linkedin_message", False) else "Not Sent"
            st.caption(f"Cold Email: {cold_status} | LinkedIn: {linkedin_status}")
            
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                options = ["not applied", "applied", "interview", "rejected", "selected"]
                new_status = st.selectbox(
                    "Update Status", 
                    options=options, 
                    index=options.index(effective_status) if effective_status in options else 0, 
                    key=f"status_{doc['_id']}"
                )
                if new_status != effective_status:
                    update_application_status(doc["_id"], new_status)
                    st.success("Updated status!")
                    st.rerun()
            with col_b:
                current_fav = doc.get("favorite", False)
                new_fav = st.checkbox("Favorite", value=current_fav, key=f"fav_{doc['_id']}")
                if new_fav != current_fav:
                    update_application_toggle(doc["_id"], "favorite", new_fav)
                    st.success("Favorite updated!")
                    st.rerun()
            with col_c:
                current_cold = doc.get("sent_cold_email", False)
                new_cold = st.checkbox("Sent Cold Email", value=current_cold, key=f"cold_{doc['_id']}")
                if new_cold != current_cold:
                    update_application_toggle(doc["_id"], "sent_cold_email", new_cold)
                    st.success("Cold Email status updated!")
                    st.rerun()
            with col_d:
                current_linked = doc.get("sent_linkedin_message", False)
                new_linked = st.checkbox("Sent LinkedIn Message", value=current_linked, key=f"linked_{doc['_id']}")
                if new_linked != current_linked:
                    update_application_toggle(doc["_id"], "sent_linkedin_message", new_linked)
                    st.success("LinkedIn Message status updated!")
                    st.rerun()
            
            col_resume, col_delete = st.columns(2)
            with col_resume:
                if st.button("Show Resume Data", key=f"gen_{doc['_id']}"):
                    st.markdown("### Resume Points")
                    render_resume(doc.get("resume_content"))
            with col_delete:
                if st.button("Delete", key=f"delete_{doc['_id']}"):
                    delete_application(doc["_id"])
                    st.success("Application deleted!")
                    st.rerun()
            
            if st.button("Generate LinkedIn Message", key=f"linkedin_{doc['_id']}"):
                st.write("LinkedIn message generated!")
                message = generate_linkedin_message(company, title, job_id)
                st.code(message, language="text")
            
            with st.expander("Job Description"):
                st.write(doc.get('job_description', 'No description available.'))
            if i < len(filtered_apps) - 1:
                st.divider()
    
if __name__ == "__main__":
    main()
