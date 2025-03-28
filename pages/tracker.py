
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

# -- Caching the DB call to speed up repeated runs
@st.cache_data
def fetch_all_applications():
    return get_all_applications()

def clear_application_cache():
    """Helper to clear the cached list of applications after an update."""
    st.cache_data.clear()

# Helper function to parse date applied
def get_date(app):
    date_str = app.get("date_applied", "")
    try:
        # If date is empty or starts with '0000', treat it as invalid
        if not date_str or date_str.startswith("0000"):
            raise ValueError("Invalid date with year=0 or empty string")

        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

        # If the parsed date is before 1970, forcibly set it to 1970-01-01
        if dt.year < 1970:
            dt = datetime(1970, 1, 1)

        return dt

    except Exception:
        # Fallback if parsing or any other error occurs
        return datetime(1970, 1, 1)

def sort_date_newest_key(app):
    dt = get_date(app)  # guaranteed safe for .timestamp()
    return (-dt.timestamp(), app.get("company_name", "").lower(), app.get("title", "").lower())

def sort_date_oldest_key(app):
    dt = get_date(app)  # guaranteed safe
    return (dt.timestamp(), app.get("company_name", "").lower(), app.get("title", "").lower())


def main():
    st.title("Job Application Tracker 📋")

    # Retrieve all applications from cache
    applications = fetch_all_applications()
    if not applications:
        st.info("No applications found. Add job applications to track them.")
        logging.info("No applications found.")
        return

    # -- Build metrics (applied, not applied, interview, etc.)
    metrics = {"applied": 0, "not applied": 0, "interview": 0, "rejected": 0, "selected": 0}
    for app in applications:
        primary = app.get("primary_status", app.get("status", "not applied"))
        secondary = app.get("secondary_status", "")
        if primary == "applied":
            metrics["applied"] += 1
        else:
            metrics["not applied"] += 1
        if secondary in metrics:
            metrics[secondary] += 1

    cold_email_not_sent = sum(1 for app in applications if not app.get("sent_cold_email", False))
    linkedin_not_sent = sum(1 for app in applications if not app.get("sent_linkedin_message", False))

    # -- Metrics Display
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

    # -- SIDEBAR FILTERS
    with st.sidebar:
        st.header("Filters")

        # Wrap in a single form so we only rerun after pressing "Apply Filters"
        with st.form("filter_form"):
            status_options = ["not applied", "applied", "interview", "rejected", "selected"]
            status_filter = st.multiselect(
                "Status",
                options=status_options,
                default=st.session_state.get("status_filter", [])
            )
            companies = sorted(list(set(app.get("company_name", "") for app in applications)))
            company_filter = st.multiselect(
                "Company",
                options=companies,
                default=st.session_state.get("company_filter", [])
            )
            search_query = st.text_input(
                "Search (Role or Company)",
                value=st.session_state.get("search_query", "")
            )
            favorite_filter = st.checkbox(
                "Favorites Only",
                value=st.session_state.get("favorite_filter", False)
            )
            cold_email_not_sent_filter = st.checkbox(
                "Jobs with NO Cold Email Sent",
                value=st.session_state.get("cold_email_not_sent_filter", False)
            )
            linkedin_not_sent_filter = st.checkbox(
                "Jobs with NO LinkedIn Message Sent",
                value=st.session_state.get("linkedin_not_sent_filter", False)
            )
            missing_both_filter = st.checkbox(
                "Jobs missing BOTH Cold Email & LinkedIn",
                value=st.session_state.get("missing_both_filter", False)
            )

            # Example additional filter (date range). Expand as needed:
            # date_start = st.date_input("Earliest applied date")
            # date_end = st.date_input("Latest applied date")

            sort_options = ["Date (newest first)", "Date (oldest first)", "Company", "Status"]
            sort_by = st.selectbox(
                "Sort by",
                options=sort_options,
                index=sort_options.index(st.session_state.get("sort_by", "Date (newest first)"))
            )

            submitted = st.form_submit_button("Apply Filters")
            if submitted:
                st.session_state.status_filter = status_filter
                st.session_state.company_filter = company_filter
                st.session_state.search_query = search_query
                st.session_state.favorite_filter = favorite_filter
                st.session_state.cold_email_not_sent_filter = cold_email_not_sent_filter
                st.session_state.linkedin_not_sent_filter = linkedin_not_sent_filter
                st.session_state.missing_both_filter = missing_both_filter
                st.session_state.sort_by = sort_by

                # Reset pagination to page 0 whenever filters change
                st.session_state.current_page = 0

                st.rerun()

    # -- APPLY FILTERS
    filtered_apps = applications.copy()
    # Load filters from session_state
    status_filter = st.session_state.get("status_filter", [])
    company_filter = st.session_state.get("company_filter", [])
    search_query = st.session_state.get("search_query", "").lower()
    favorite_filter = st.session_state.get("favorite_filter", False)
    cold_email_not_sent_filter = st.session_state.get("cold_email_not_sent_filter", False)
    linkedin_not_sent_filter = st.session_state.get("linkedin_not_sent_filter", False)
    missing_both_filter = st.session_state.get("missing_both_filter", False)
    sort_by = st.session_state.get("sort_by", "Date (newest first)")

    if status_filter:
        filtered_apps = [
            app for app in filtered_apps
            if (app.get("primary_status", "not applied") in status_filter
               or app.get("secondary_status", "") in status_filter)
        ]
    if company_filter:
        filtered_apps = [app for app in filtered_apps if app.get("company_name", "") in company_filter]
    if search_query:
        filtered_apps = [
            app for app in filtered_apps
            if search_query in app.get("company_name", "").lower()
               or search_query in app.get("title", "").lower()
        ]
    if favorite_filter:
        filtered_apps = [app for app in filtered_apps if app.get("favorite", False)]
    if cold_email_not_sent_filter:
        filtered_apps = [app for app in filtered_apps if not app.get("sent_cold_email", False)]
    if linkedin_not_sent_filter:
        filtered_apps = [app for app in filtered_apps if not app.get("sent_linkedin_message", False)]
    if missing_both_filter:
        filtered_apps = [
            app for app in filtered_apps
            if not app.get("sent_cold_email", False) and not app.get("sent_linkedin_message", False)
        ]

    # Example: you could also filter by a date range if you tracked date range in session:
    # if date_start and date_end:
    #     filtered_apps = [
    #         app for app in filtered_apps
    #         if date_start <= get_date(app).date() <= date_end
    #     ]

    # -- APPLY SORTING
    if sort_by == "Date (newest first)":
        filtered_apps.sort(key=sort_date_newest_key)
    elif sort_by == "Date (oldest first)":
        filtered_apps.sort(key=sort_date_oldest_key)
    elif sort_by == "Company":
        filtered_apps.sort(key=lambda app: (app.get("company_name", "").lower(), get_date(app)))
    elif sort_by == "Status":
        filtered_apps.sort(key=lambda app: app.get("primary_status", "not applied"))

    # -- PAGINATION (LOCAL)
    PAGE_SIZE = 10
    if "current_page" not in st.session_state:
        st.session_state.current_page = 0

    total_apps = len(filtered_apps)
    start_index = st.session_state.current_page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    paged_apps = filtered_apps[start_index:end_index]

    st.write(f"**Displaying {len(paged_apps)} of {total_apps} filtered applications.**")

    # -- DISPLAY APPLICATIONS
    status_emojis = {
        "not applied": "🟠",
        "applied": "🟢",
        "interview": "🔵",
        "rejected": "🔴",
        "selected": "🟢"
    }

    for doc in paged_apps:
        company = doc.get('company_name', '')
        title = doc.get('title', '')
        job_id = doc.get('job_id', 'N/A')
        date_applied = doc.get('date_applied', 'N/A')
        primary_status = doc.get("primary_status", doc.get("status", "not applied"))
        secondary_status = doc.get("secondary_status", "")
        effective_status = secondary_status if secondary_status else primary_status
        emoji = status_emojis.get(effective_status, "⚪")

        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{company} - {title}")
                st.caption(f"Applied: {date_applied} | Job Id: {job_id}")
                st.code(doc.get("file_name", ""), language="text")
            with col2:
                st.write(f"**Status:** {emoji} {effective_status.upper()}")

            # Wrap toggles + status update in a single form to reduce reload
            with st.form(f"update_form_{doc['_id']}"):
                # Select new status
                options = ["not applied", "applied", "interview", "rejected", "selected"]
                current_effective_index = options.index(effective_status) if effective_status in options else 0
                new_status = st.selectbox("Update Status", options, index=current_effective_index)

                # Checkboxes for favorite, cold email, linkedin message
                current_fav = doc.get("favorite", False)
                new_fav = st.checkbox("Favorite", value=current_fav)

                current_cold = doc.get("sent_cold_email", False)
                new_cold = st.checkbox("Sent Cold Email", value=current_cold)

                current_linked = doc.get("sent_linkedin_message", False)
                new_linked = st.checkbox("Sent LinkedIn Message", value=current_linked)

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    # Only update if changed
                    if new_status != effective_status:
                        update_application_status(doc["_id"], new_status)
                    if new_fav != current_fav:
                        update_application_toggle(doc["_id"], "favorite", new_fav)
                    if new_cold != current_cold:
                        update_application_toggle(doc["_id"], "sent_cold_email", new_cold)
                    if new_linked != current_linked:
                        update_application_toggle(doc["_id"], "sent_linkedin_message", new_linked)

                    clear_application_cache()
                    st.success("Changes saved!")
                    st.rerun()

            # Action buttons outside the form
            colA, colB, colC = st.columns(3)
            with colA:
                if st.button("Show Resume Data", key=f"resume_{doc['_id']}"):
                    st.markdown("### Resume Points")
                    render_resume(doc.get("resume_content", {}))

            with colB:
                if st.button("Delete Application", key=f"delete_{doc['_id']}"):
                    delete_application(doc["_id"])
                    clear_application_cache()
                    st.success("Application deleted!")
                    st.rerun()

            with colC:
                if st.button("Generate LinkedIn Message", key=f"linkedin_{doc['_id']}"):
                    message = generate_linkedin_message(company, title, job_id)
                    st.write("**LinkedIn message:**")
                    st.code(message, language="text")

            st.divider()

    # PAGINATION BUTTONS
    pagination_col1, pagination_col2 = st.columns([1, 1])
    with pagination_col1:
        if st.session_state.current_page > 0:
            if st.button("Previous Page"):
                st.session_state.current_page -= 1
                st.rerun()

    with pagination_col2:
        if end_index < total_apps:
            if st.button("Next Page"):
                st.session_state.current_page += 1
                st.rerun()

if __name__ == "__main__":
    main()
