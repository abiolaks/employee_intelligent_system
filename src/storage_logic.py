import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient
import io

# Load environment variables silently
load_dotenv(verbose=False)


def get_azure_credentials():
    """Retrieve credentials from environment with validation"""
    conn_str = os.getenv("AZURE_CONNECTION_STRING")
    container = os.getenv("AZURE_CONTAINER_NAME")

    if not all([conn_str, container]):
        st.error("Azure configuration incomplete - check .env file")
        st.stop()
    return conn_str, container


def load_azure_data(blob_name):
    """Secure backend-only Azure access"""
    conn_str, container = get_azure_credentials()

    try:
        blob_service = BlobServiceClient.from_connection_string(conn_str)
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        return blob_client.download_blob().readall()
    except Exception as e:
        st.error(f"Secure Azure access failed: {str(e)}")
        st.stop()


def load_data():
    """User-facing data loader"""
    source = st.radio("Data Source", ["Local Upload", "Azure Storage"])

    if source == "Local Upload":
        uploaded = st.file_uploader("Choose CSV", type="csv")
        return pd.read_csv(uploaded) if uploaded else None

    # Azure flow - only asks for blob name
    default_blob = os.getenv("DEFAULT_BLOB_NAME", "")
    blob_name = default_blob

    if st.button("Load Securely"):
        if not blob_name:
            st.warning("Please specify a filename")
            return None

        with st.spinner("Accessing secure storage..."):
            data = load_azure_data(blob_name)
            st.success("Data loaded securely!")
            return pd.read_csv(io.BytesIO(data))

    return None
