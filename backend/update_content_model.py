#!/usr/bin/env python
"""
Script to update existing Firestore documents with new content model fields.
This script adds 'latest' and 'recommended' fields to existing documents.
"""
import os
import sys
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
    
    # Get collection name from environment variable or use default
    collection_name = os.environ.get('FIRESTORE_COLLECTION_CONTENT', 'content')
    print(f"Using collection: {collection_name}")
    
    # Get all documents from the collection
    docs = list(db.collection(collection_name).stream())
    print(f"Found {len(docs)} documents in collection '{collection_name}'")
    
    # Count how many documents need updating
    updated_count = 0
    already_updated_count = 0
    
    # Process each document
    print("\nUpdating documents:")
    for doc in docs:
        doc_id = doc.id
        data = doc.to_dict()
        updates_needed = False
        
        # Check if document needs 'latest' field
        if "latest" not in data:
            data["latest"] = False
            updates_needed = True
            print(f"  - Adding 'latest' field to document '{doc_id}'")
        
        # Check if document needs 'recommended' field
        if "recommended" not in data:
            data["recommended"] = False
            updates_needed = True
            print(f"  - Adding 'recommended' field to document '{doc_id}'")
        
        # Update the document if needed
        if updates_needed:
            data["updated_at"] = datetime.datetime.now().isoformat()
            db.collection(collection_name).document(doc_id).set(data)
            updated_count += 1
            print(f"  - Updated document '{doc_id}'")
        else:
            already_updated_count += 1
    
    # Print summary
    print("\nUpdate completed:")
    print(f"  - Total documents: {len(docs)}")
    print(f"  - Documents updated: {updated_count}")
    print(f"  - Documents already up-to-date: {already_updated_count}")
    
    # Create a sample document with the new fields
    if input("\nWould you like to create a sample document with the new fields? (y/n): ").lower() == 'y':
        test_id = f"sample-{uuid.uuid4()}"
        test_data = {
            "title": "Sample Updated Document",
            "description": "Created to demonstrate new content model",
            "content_type": "sample",
            "latest": True,
            "recommended": True,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        db.collection(collection_name).document(test_id).set(test_data)
        print(f"Successfully created sample document with ID: {test_id}")
    
    print("\nOperation completed successfully")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 