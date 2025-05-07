#!/usr/bin/env python
"""
Test script to check Firestore access and add test data.
"""
import os
import sys
import json
import datetime
import uuid
from google.cloud import firestore

# Print environment info
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
print(f"FIRESTORE_COLLECTION_CONTENT: {os.environ.get('FIRESTORE_COLLECTION_CONTENT', 'content')}")

try:
    # Initialize Firestore
    db = firestore.Client()
    print("Successfully connected to Firestore")
    
    # List collections
    collections = db.collections()
    print("Collections:")
    for collection in collections:
        print(f"- {collection.id}")
        # Count documents
        docs = list(collection.limit(5).stream())
        print(f"  - Documents: {len(docs)}")
        if docs:
            # Print a sample document
            sample = docs[0].to_dict()
            sample_id = docs[0].id
            print(f"  - Sample document ID: {sample_id}")
            print(f"  - Sample fields: {list(sample.keys())[:5]}")
    
    # Create a test document in both 'content' and 'Content' collections
    collections_to_try = ['content', 'Content']
    test_id = f"test-{uuid.uuid4()}"
    test_data = {
        "title": "Test Document",
        "description": "Created for testing Firestore access",
        "content_type": "test",
        "created_at": datetime.datetime.now().isoformat(),
        "updated_at": datetime.datetime.now().isoformat()
    }
    
    print("\nAttempting to create test documents:")
    for collection in collections_to_try:
        try:
            db.collection(collection).document(test_id).set(test_data)
            print(f"Successfully created document in '{collection}' with ID: {test_id}")
        except Exception as e:
            print(f"Error creating document in '{collection}': {str(e)}")
    
    print("\nTest completed successfully")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
