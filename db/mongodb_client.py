import pymongo
import streamlit as st
import logging

def get_mongo_client():
    """
    Returns a pymongo.MongoClient instance using the connection string from st.secrets.
    """
    logging.info("Attempting to create MongoDB client.")
    client = pymongo.MongoClient(st.secrets["MONGODB_URI"])
    logging.info("MongoDB client created successfully.")
    return client
