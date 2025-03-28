import pymongo
import streamlit as st
from datetime import datetime
import logging
from db.mongodb_client import get_mongo_client

def get_applications_collection():
    logging.info("Fetching applications collection.")
    client = get_mongo_client()
    db = client[st.secrets["DATABASE_NAME"]]
    collection = db[st.secrets["COLLECTION_NAME"]]
    logging.info("Applications collection retrieved.")
    return collection

def insert_application(company, title, job_id, resume_content, job_description, sanitized_filename, status="not applied", matching_score=None):
    logging.info(
        "Inserting application for company: %s, title: %s", company, title)
    collection = get_applications_collection()
    doc = {
        "company_name": company,
        "title": title,
        "job_id": job_id,
        "resume_content": resume_content,
        "job_description": job_description,
        "primary_status": status,
        "secondary_status": "",
        "file_name": sanitized_filename,
        "favorite": False,
        "sent_cold_email": False,
        "sent_linkedin_message": False
    }
    if matching_score is not None:
        doc["matching_score"] = matching_score
    if status == "applied":
        doc["date_applied"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        doc["date_applied"] = ""
    result = collection.insert_one(doc)
    logging.info("Application inserted with ID: %s", result.inserted_id)
    return result.inserted_id

def update_application_status(doc_id, new_status):
    logging.info("Updating application ID %s with new status %s",
                 doc_id, new_status)
    collection = get_applications_collection()
    update_fields = {}
    if new_status == "not applied":
        update_fields["primary_status"] = "not applied"
        update_fields["secondary_status"] = ""
        update_fields["date_applied"] = ""
    elif new_status == "applied":
        update_fields["primary_status"] = "applied"
        update_fields["secondary_status"] = ""
        update_fields["date_applied"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
    elif new_status in ["interview", "rejected", "selected"]:
        update_fields["primary_status"] = "applied"
        update_fields["secondary_status"] = new_status
    else:
        update_fields["status"] = new_status
    collection.update_one({"_id": doc_id}, {"$set": update_fields})
    logging.info("Application status updated with fields: %s", update_fields)

def update_application_toggle(doc_id, field, value):
    logging.info("Updating application %s: setting %s to %s",
                 doc_id, field, value)
    collection = get_applications_collection()
    collection.update_one({"_id": doc_id}, {"$set": {field: value}})
    logging.info("Application toggle updated.")

def get_all_applications():
    logging.info("Retrieving all applications (unpaginated).")
    collection = get_applications_collection()
    apps = list(collection.find({}))
    logging.info("Retrieved %d applications.", len(apps))
    return apps

def delete_application(doc_id):
    logging.info("Deleting application with ID: %s", doc_id)
    collection = get_applications_collection()
    collection.delete_one({"_id": doc_id})
    logging.info("Application deleted.")


# Example: Server-side pagination if needed
def get_applications_paginated(page=0, page_size=10):
    """
    Retrieve a slice of applications from the DB with skip/limit.
    Sort by date_applied descending if it is stored as a datetime or
    a consistent format. Adjust as needed.
    """
    logging.info("Retrieving paginated applications: page=%s, page_size=%s", page, page_size)
    collection = get_applications_collection()

    # If date_applied is stored as string "YYYY-MM-DD HH:MM:SS", you can sort by it as text
    # but it's safer to store date_applied as a proper datetime field for correct sorting.
    # For demonstration, we do .sort("date_applied", -1) on the string field:
    skip_count = page * page_size
    cursor = (collection
              .find({})
              .sort("date_applied", -1)
              .skip(skip_count)
              .limit(page_size)
             )
    apps = list(cursor)
    logging.info("Retrieved %d applications from page %d", len(apps), page)
    return apps