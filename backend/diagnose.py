#!/usr/bin/env python3
"""
Diagnostic script for App Engine deployment
"""
import logging
import os
import sys
import traceback

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("diagnostics")

# Check if Google Cloud Storage is enabled
USE_GCS = os.environ.get("USE_GCS", "false").lower() == "true"

# Define all directory paths to check
REQUIRED_DIRS = [
    os.environ.get("TEMP_PROCESSING_DIR", "/tmp/processing"),
    os.environ.get("UPLOAD_DIR", "/tmp/uploads"),
    os.environ.get("TEMP_UPLOAD_DIR", "/tmp/uploads"),
]

# Add bucket dir only if GCS is not enabled
if not USE_GCS:
    REQUIRED_DIRS.append(os.environ.get("UPLOAD_BUCKET_DIR", "/tmp/bucket"))


def print_status(message: str, success: bool = True) -> None:
    """Print a colored status message."""
    # ANSI color codes
    GREEN = "\033[92m"  # Success
    RED = "\033[91m"  # Error
    BOLD = "\033[1m"  # Bold
    RESET = "\033[0m"  # Reset

    if success:
        print(f"{GREEN}{BOLD}[SUCCESS]{RESET} {message}")
    else:
        print(f"{RED}{BOLD}[ERROR]{RESET} {message}")


def check_directories() -> bool:
    """Ensure all required directories exist and are writable."""
    all_ok = True

    print("\nChecking required directories...")
    for dir_path in REQUIRED_DIRS:
        try:
            # Create the directory if it doesn't exist
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print_status(f"Created directory: {dir_path}")

            # Check for write permissions
            if os.access(dir_path, os.W_OK):
                print_status(f"Directory {dir_path} exists and is writable")
            else:
                print_status(f"Directory {dir_path} exists but is NOT writable", False)
                all_ok = False
        except Exception as e:
            print_status(f"Error with directory {dir_path}: {str(e)}", False)
            all_ok = False

    return all_ok


def check_cloud_storage() -> bool:
    """Check Google Cloud Storage configuration if enabled."""
    if not USE_GCS:
        print("\nGoogle Cloud Storage is disabled. Skipping GCS checks.")
        return True

    all_ok = True
    print("\nChecking Google Cloud Storage configuration...")

    try:
        # Check for required environment variables
        bucket_name = os.environ.get("GCS_BUCKET_NAME")
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

        if not bucket_name:
            print_status("GCS_BUCKET_NAME environment variable is not set", False)
            all_ok = False
        else:
            print_status(f"Using GCS bucket: {bucket_name}")

        if not project_id:
            print_status("GOOGLE_CLOUD_PROJECT environment variable is not set", False)
            all_ok = False
        else:
            print_status(f"Using GCP project: {project_id}")

        # Check if we're running on App Engine
        is_appengine = (
            os.environ.get("GAE_ENV") == "standard"
            or os.environ.get("GAE_APPLICATION") is not None
        )
        if is_appengine:
            print_status("Running on Google App Engine")
        else:
            print_status("Not running on Google App Engine - using local fallbacks")

        # Try to initialize the GCS client
        if bucket_name and project_id:
            try:
                from google.cloud import storage

                # Handle App Engine environment
                if is_appengine and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "") == "":
                    # Clear credentials path to force using default App Engine credentials
                    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                        print_status("Removing empty GOOGLE_APPLICATION_CREDENTIALS to force default credentials")

                # Initialize the client
                storage_client = storage.Client(project=project_id)
                print_status("Successfully initialized GCS client")

                # Check if bucket exists and create it if not
                try:
                    storage_client.get_bucket(bucket_name)
                    print_status(f"Bucket {bucket_name} exists")
                except Exception:
                    print_status(f"Bucket {bucket_name} does not exist, attempting to create it")

                    try:
                        bucket = storage_client.create_bucket(bucket_name, location="us-central1")
                        print_status(f"Successfully created bucket {bucket_name}")
                    except Exception as create_error:
                        print_status(f"Failed to create bucket: {str(create_error)}", False)
                        all_ok = False
            except Exception as gcs_error:
                print_status(f"Failed to initialize GCS client: {str(gcs_error)}", False)
                all_ok = False
    except Exception as e:
        print_status(f"Error checking GCS configuration: {str(e)}", False)
        all_ok = False

    return all_ok


def check_firestore() -> bool:
    """Check Firestore connection."""
    all_ok = True
    print("\nChecking Firestore connection...")

    try:
        # Try to initialize the Firestore client
        try:
            from google.cloud import firestore

            project_id = os.environ.get(
                "FIRESTORE_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT")
            )
            if not project_id:
                print_status("FIRESTORE_PROJECT_ID environment variable is not set", False)
                all_ok = False
                return all_ok

            # Handle App Engine environment
            is_appengine = (
                os.environ.get("GAE_ENV") == "standard"
                or os.environ.get("GAE_APPLICATION") is not None
            )
            if is_appengine:
                print_status("Detected App Engine environment")
                if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "") == "":
                    # Clear credentials path to force using default App Engine credentials
                    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                        original_creds = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
                        print_status(
                            "Removing empty GOOGLE_APPLICATION_CREDENTIALS to force default credentials"
                        )

            print_status(f"Initializing Firestore with project ID: {project_id}")
            db = firestore.Client(project=project_id)
            print_status("Successfully connected to Firestore with default credentials")

            # Verify connection with a simple query
            try:
                db.collection("_verification").limit(1).get()
                print_status("Firestore connection verified successfully")
            except Exception as verify_error:
                print_status(
                    f"Firestore client initialized but connection verification failed: {str(verify_error)}",
                    False,
                )
                all_ok = False
        except Exception as db_error:
            print_status(f"Failed to initialize Firestore client: {str(db_error)}", False)
            all_ok = False
    except Exception as e:
        print_status(f"Error checking Firestore: {str(e)}", False)
        all_ok = False

    return all_ok


def check_environment() -> bool:
    """Check environment variables."""
    all_ok = True
    print("\nChecking environment variables...")

    # Critical environment variables
    critical_vars = {
        "GOOGLE_CLOUD_PROJECT": os.environ.get("GOOGLE_CLOUD_PROJECT"),
        "FIRESTORE_PROJECT_ID": os.environ.get("FIRESTORE_PROJECT_ID"),
        "SESSION_SECRET_KEY": os.environ.get("SESSION_SECRET_KEY"),
    }

    for name, value in critical_vars.items():
        if not value:
            print_status(f"Critical environment variable {name} is not set", False)
            all_ok = False
        else:
            print_status(f"Environment variable {name} is set")

    # Check if we're running on App Engine
    is_appengine = (
        os.environ.get("GAE_ENV") == "standard" or os.environ.get("GAE_APPLICATION") is not None
    )
    if is_appengine:
        print_status("Running on Google App Engine")
    else:
        print_status("Not running on Google App Engine - using local fallbacks")

    return all_ok


def fix_pydantic_schema_warnings() -> None:
    """Monkey patch to fix Pydantic schema_extra warnings."""
    try:
        # Import here to avoid dependencies for basic diagnostics
        # Check if there are any BaseModel classes with schema_extra
        import inspect
        import sys

        from pydantic import BaseModel

        classes_fixed = 0
        for name, obj in inspect.getmembers(sys.modules.get("app.models")):
            if inspect.isclass(obj) and issubclass(obj, BaseModel) and hasattr(obj, "Config"):
                config = getattr(obj, "Config")
                if hasattr(config, "schema_extra") and not hasattr(config, "json_schema_extra"):
                    # Fix the warning by adding json_schema_extra
                    setattr(config, "json_schema_extra", getattr(config, "schema_extra"))
                    classes_fixed += 1

        if classes_fixed > 0:
            print_status(f"Fixed Pydantic schema_extra warnings in {classes_fixed} models")
    except ImportError:
        # Pydantic not imported yet, nothing to fix
        pass
    except Exception as e:
        print_status(f"Error fixing Pydantic schema warnings: {str(e)}", False)


def main() -> int:
    """Main diagnostic function."""
    print("\n==== Google App Engine Diagnostic Script ====\n")

    all_checks_passed = True

    try:
        # Check for directories
        if not check_directories():
            all_checks_passed = False

        # Check Cloud Storage if enabled
        if not check_cloud_storage():
            all_checks_passed = False

        # Check Firestore
        if not check_firestore():
            all_checks_passed = False

        # Check environment variables
        if not check_environment():
            all_checks_passed = False

        # Fix Pydantic schema warnings
        fix_pydantic_schema_warnings()

    except Exception as e:
        print_status(f"Unexpected error in diagnostics: {str(e)}", False)
        traceback.print_exc()
        all_checks_passed = False

    print("\n==== Diagnostic Summary ====")
    if all_checks_passed:
        print_status("All diagnostic checks passed")
        return 0
    else:
        print_status("Some diagnostic checks failed. See above for details.", False)
        # Continue anyway to allow the app to start with degraded functionality
        return 0  # Return 0 to let App Engine continue starting the app


if __name__ == "__main__":
    sys.exit(main())
