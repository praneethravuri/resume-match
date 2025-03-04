import pymongo
import streamlit as st

def get_mongo_client():
    """
    Returns a pymongo.MongoClient instance using the connection string from st.secrets.
    """
    return pymongo.MongoClient(st.secrets["MONGODB_URI"])
