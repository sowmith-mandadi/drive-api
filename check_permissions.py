import os
import json
import logging
from google.cloud import storage, firestore
import firebase_admin
from firebase_admin import credentials
from google.oauth2 import service_account

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_credentials_file():
    """Check if the credentials file exists and is valid."""
    logger.info("Checking credentials file...")
    
    creds_file = "credentials.json"
    if not os.path.exists(creds_file):
        logger.error("❌ credentials.json file not found!")
        return False
    
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
        for field in required_fields:
            if field not in creds_data:
                logger.error(f"❌ Missing required field '{field}' in credentials.json")
                return False
        
        logger.info(f"✅ credentials.json file is valid! Project ID: {creds_data['project_id']}")
        logger.info(f"✅ Service account email: {creds_data['client_email']}")
        return True
    except Exception as e:
        logger.error(f"❌ Error checking credentials.json: {e}")
        return False

def check_gcs_permissions():
    """Check if the service account has access to GCS."""
    logger.info("Checking GCS permissions...")
    
    try:
        # Initialize storage client with explicit credentials
        credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', 
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        storage_client = storage.Client(credentials=credentials)
        
        # List buckets
        buckets = list(storage_client.list_buckets())
        logger.info(f"✅ Successfully listed buckets. Found {len(buckets)} buckets.")
        for bucket in buckets:
            logger.info(f"  - {bucket.name}")
        
        # Try to get or create bucket
        bucket_name = os.getenv('GCS_BUCKET_NAME', 'conference-cms-content')
        if storage_client.lookup_bucket(bucket_name):
            logger.info(f"✅ Found bucket: {bucket_name}")
            bucket = storage_client.bucket(bucket_name)
        else:
            logger.info(f"❌ Bucket {bucket_name} not found. Trying to create it...")
            try:
                bucket = storage_client.create_bucket(bucket_name)
                logger.info(f"✅ Created bucket: {bucket_name}")
            except Exception as e:
                logger.error(f"❌ Failed to create bucket: {e}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Error checking GCS permissions: {e}")
        return False

def check_firestore_permissions():
    """Check if the service account has access to Firestore."""
    logger.info("Checking Firestore permissions...")
    
    try:
        # Initialize Firebase with explicit credentials
        if not firebase_admin._apps:
            cred = credentials.Certificate('credentials.json')
            firebase_admin.initialize_app(cred)
        
        # Initialize Firestore with explicit credentials
        credentials_obj = service_account.Credentials.from_service_account_file(
            'credentials.json',
            scopes=["https://www.googleapis.com/auth/cloud-platform", 
                   "https://www.googleapis.com/auth/datastore"]
        )
        db = firestore.Client(credentials=credentials_obj)
        
        # Try to list collections
        collections = list(db.collections())
        logger.info(f"✅ Successfully listed collections. Found {len(collections)} collections.")
        for collection in collections:
            logger.info(f"  - {collection.id}")
        
        # Try to query content collection
        try:
            docs = list(db.collection('content').limit(5).stream())
            logger.info(f"✅ Successfully queried content collection. Found {len(docs)} documents.")
        except Exception as e:
            logger.warning(f"⚠️ Error querying content collection: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error checking Firestore permissions: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting permissions check...")
    
    if check_credentials_file():
        logger.info("Credentials file check passed.")
    else:
        logger.error("Credentials file check failed.")
    
    if check_gcs_permissions():
        logger.info("GCS permissions check passed.")
    else:
        logger.error("GCS permissions check failed.")
    
    if check_firestore_permissions():
        logger.info("Firestore permissions check passed.")
    else:
        logger.error("Firestore permissions check failed.") 