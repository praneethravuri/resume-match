from db.mongodb_client import get_mongo_client
import streamlit as st
from datetime import datetime

def get_applications_collection():
    client = get_mongo_client()
    db = client[st.secrets["DATABASE_NAME"]]
    collection = db[st.secrets["COLLECTION_NAME"]]
    return collection

def insert_application(company, title, job_id, resume_content, job_description, status="not applied", matching_score=None):
    """
    Inserts a new application record into the MongoDB collection.
    If status is 'applied', adds the current date as 'date_applied'.
    """
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
        doc["date_applied"] = datetime.now().strftime("%Y-%m-%d")
    result = collection.insert_one(doc)
    return result.inserted_id

def update_application_status(doc_id, new_status):
    """
    Updates the application status for the document with the given _id.
    If new_status is 'applied', adds the current date as 'date_applied'.
    """
    collection = get_applications_collection()
    update_fields = {"status": new_status}
    if new_status == "applied":
        update_fields["date_applied"] = datetime.now().strftime("%Y-%m-%d")
    collection.update_one({"_id": doc_id}, {"$set": update_fields})

def get_all_applications():
    """
    Retrieves all application documents from the collection.
    """
    collection = get_applications_collection()
    return list(collection.find({}))

def delete_application(doc_id):
    """
    Deletes the application document with the given _id.
    """
    collection = get_applications_collection()
    collection.delete_one({"_id": doc_id})
