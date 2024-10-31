from fastapi import FastAPI, HTTPException, status
from google.cloud import storage
import os
import snowflake.connector
from snowflake.connector import DictCursor
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import pathlib
import logging
import re

# Initialize logging
logger = logging.getLogger("fastapi")
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure Google Cloud Storage (GCS) Client
try:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")

    resolved_path = pathlib.Path(credentials_path).resolve()
    if not resolved_path.exists():
        raise FileNotFoundError(f"Google Cloud credentials file not found at: {resolved_path}")

    # Initialize Google Cloud Storage client
    storage_client = storage.Client.from_service_account_json(str(resolved_path))
    logger.info("Google Cloud Storage client initialized successfully.")
except Exception as e:
    logger.error("Error initializing Google Cloud Storage client:", e)
    raise HTTPException(status_code=500, detail="Failed to initialize Google Cloud Storage client")

# Snowflake connection utility
def create_connection_to_snowflake():
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database="PUBLICATIONS_DB",
            schema="PUBLICATIONS_SCHEMA"
        )
        logger.info("Snowflake connection established.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to Snowflake: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Snowflake")

# Function to close the Snowflake connection
def close_connection(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    logger.info("Snowflake connection closed.")

# Function to parse the GCS path and generate an authenticated URL
def get_authenticated_url(gcs_path):
    match = re.match(r"gs://([^/]+)/(.+)", gcs_path)
    if match:
        bucket_name = match.group(1)
        blob_name = match.group(2)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        # Generate a signed URL, valid for 1 hour
        return blob.generate_signed_url(version="v4", expiration=3600)
    else:
        raise ValueError("Invalid GCS path format")

# Define the explore_documents function to fetch data from Snowflake and generate signed URLs
def explore_documents():
    conn = create_connection_to_snowflake()
    if conn is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={'status': status.HTTP_503_SERVICE_UNAVAILABLE, 'message': 'Database not found'}
        )

    try:
        cursor = conn.cursor(DictCursor)
        # Fetch all documents without limit
        query = "SELECT title, pdf_link, image_link FROM PUBLICATIONS_DB.PUBLICATIONS_SCHEMA.PUBLICATIONS_DATA"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Format the response data
        documents = []
        for row in rows:
            pdf_link = row["PDF_LINK"]
            image_link = row.get("IMAGE_LINK")

            # Generate authenticated URLs if links are available
            pdf_authenticated_url = get_authenticated_url(pdf_link) if pdf_link else None
            image_authenticated_url = get_authenticated_url(image_link) if image_link else None

            document = {
                "title": row["TITLE"],
                "pdf_gcs_path": pdf_link,
                "pdf_authenticated_url": pdf_authenticated_url
            }
            
            # Include image URL if it exists
            if image_authenticated_url:
                document["image_authenticated_url"] = image_authenticated_url

            documents.append(document)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={'documents': documents, 'count': len(documents)}
        )

    except Exception as e:
        logger.error(f"Error in explore_documents: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': 'Error fetching documents'}
        )

    finally:
        close_connection(conn, cursor)


# Define the FastAPI endpoint to call explore_documents
@app.get("/explore_documents")
async def get_documents():
    return explore_documents()
