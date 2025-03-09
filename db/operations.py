from db.mongodb_client import get_mongo_client
import streamlit as st
from datetime import datetime
import logging

def get_applications_collection():
    logging.info("Fetching applications collection.")
    client = get_mongo_client()
    db = client[st.secrets["DATABASE_NAME"]]
    collection = db[st.secrets["COLLECTION_NAME"]]
    logging.info("Applications collection retrieved.")
    return collection

def insert_application(company, title, job_id, resume_content, job_description, status="not applied", matching_score=None):
    logging.info("Inserting application for company: %s, title: %s", company, title)
    collection = get_applications_collection()
    doc = {
        "company_name": company,
        "title": title,
        "job_id": job_id,
        "resume_content": resume_content,
        "job_description": job_description,
        "status": status,
    }
    if matching_score is not None:
        doc["matching_score"] = matching_score
    if status == "applied":
        doc["date_applied"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = collection.insert_one(doc)
    logging.info("Application inserted with ID: %s", result.inserted_id)
    return result.inserted_id

def update_application_status(doc_id, new_status):
    logging.info("Updating application ID %s to status %s", doc_id, new_status)
    collection = get_applications_collection()
    update_fields = {"status": new_status}
    if new_status == "applied":
        update_fields["date_applied"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    collection.update_one({"_id": doc_id}, {"$set": update_fields})
    logging.info("Application status updated.")

def get_all_applications():
    logging.info("Retrieving all applications.")
    collection = get_applications_collection()
    apps = list(collection.find({}))
    logging.info("Retrieved %d applications.", len(apps))
    return apps

def delete_application(doc_id):
    logging.info("Deleting application with ID: %s", doc_id)
    collection = get_applications_collection()
    collection.delete_one({"_id": doc_id})
    logging.info("Application deleted.")
