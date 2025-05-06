#!/usr/bin/env python3
"""
Test script to verify that the service account can access Firestore.

Usage:
  python test_firestore.py --service-account-path credentials.json

This script will attempt to connect to Firestore and perform basic operations
to verify that the service account has the proper permissions.
"""

import argparse
import json
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def test_firestore_access():
    """
    Test whether the service account can access Firestore.
    
    Returns:
        True if the test is successful, False otherwise.
    """
    print("=== Testing Service Account Access to Firestore ===\n")
    
    # 1. Check if service account credentials file exists
    service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not service_account_path:
        print("❌ Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
        print("   Set this environment variable to the path of your service account key file.")
        return False
        
    if not os.path.exists(service_account_path):
        print(f"❌ Error: Service account key file not found at '{service_account_path}'")
        print("   Please check that the file exists and the path is correct.")
        return False
        
    print(f"✅ Service account key file found at '{service_account_path}'")
    
    # 2. Check the credentials file
    try:
        with open(service_account_path, 'r') as f:
            creds_data = json.load(f)
            if 'type' not in creds_data or creds_data['type'] != 'service_account':
                print("⚠️ Warning: The credentials file doesn't appear to be a valid service account key.")
                print("   Make sure you're using a JSON key file downloaded from the Google Cloud Console.")
                
            print(f"✅ Service account info:")
            print(f"   Project ID: {creds_data.get('project_id', 'unknown')}")
            print(f"   Client email: {creds_data.get('client_email', 'unknown')}")
            
    except json.JSONDecodeError:
        print("⚠️ Warning: Could not parse the credentials file as JSON.")
        print("   Make sure the file contains valid JSON data.")
        return False
    except Exception as e:
        print(f"⚠️ Warning: Error reading credentials file: {str(e)}")
        return False
    
    # 3. Initialize Firestore client
    try:
        from google.cloud import firestore
        
        print("✅ Successfully imported Firestore client library")
        
        # Create a client
        db = firestore.Client()
        print(f"✅ Successfully created Firestore client")
        
        # Print client details
        print(f"   Project ID: {db.project}")
        
    except Exception as e:
        print(f"❌ Error initializing Firestore client: {str(e)}")
        return False
    
    # 4. Test basic Firestore operations
    try:
        # Try listing collections
        collections = list(db.collections())
        print(f"✅ Successfully listed {len(collections)} collections")
        
        for i, collection in enumerate(collections[:5]):  # Show up to 5 collections
            print(f"   - Collection {i+1}: {collection.id}")
        
        # Try a simple query
        docs = list(db.collection("_verification").limit(1).get())
        print(f"✅ Successfully queried test collection")
        
        # Try a test write
        test_ref = db.collection("_test_verification").document("service-account-test")
        test_ref.set({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "test": "Service account test",
        })
        print(f"✅ Successfully wrote test document")
        
        # Read it back
        test_doc = test_ref.get()
        print(f"✅ Successfully read test document")
        
        # Delete it
        test_ref.delete()
        print(f"✅ Successfully deleted test document")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Firestore operations: {str(e)}")
        print("   This could mean the service account doesn't have proper permissions.")
        print("   Make sure the service account has the Cloud Datastore User or Owner role.")
        return False


def test_firestore_default_credentials():
    """Test Firestore access with application default credentials."""
    print("\n=== Testing Application Default Credentials for Firestore ===\n")
    
    try:
        # Remove specific credential path to test defaults
        original_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if original_creds:
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        
        from google.cloud import firestore
        
        # Create a client with default credentials
        db = firestore.Client()
        print("✅ Successfully created Firestore client with default credentials")
        
        # Print client details
        print(f"   Project ID: {db.project}")
        
        # Restore original credentials
        if original_creds:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = original_creds
            
        return True
    except Exception as e:
        print(f"❌ Error with default credentials: {str(e)}")
        
        # Restore original credentials
        if original_creds:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = original_creds
            
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test service account access to Firestore")
    parser.add_argument(
        "--service-account-path", 
        help="Path to the service account key file"
    )
    parser.add_argument(
        "--test-default",
        action="store_true",
        help="Also test with application default credentials"
    )
    
    args = parser.parse_args()
    
    # Set environment variable if provided
    if args.service_account_path:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = args.service_account_path
        
    # Run the test with service account credentials
    success = test_firestore_access()
    
    # Optionally test with default credentials
    default_success = True
    if args.test_default:
        default_success = test_firestore_default_credentials()
    
    # Exit with appropriate code
    sys.exit(0 if success and default_success else 1) 