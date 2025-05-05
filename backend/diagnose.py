"""
Diagnostic script for checking App Engine environment.
"""
import json
import logging
import os
import platform
import sys
import traceback
from datetime import datetime

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("diagnostics")


def check_directories():
    """Check if important directories exist and are writable."""
    dirs_to_check = ["/tmp", "/tmp/processing", "/tmp/bucket", "/tmp/uploads", os.getcwd()]

    results = {}
    for dir_path in dirs_to_check:
        try:
            # Get directory information
            exists = os.path.exists(dir_path)

            # Try to create if it doesn't exist
            if not exists:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    exists = os.path.exists(dir_path)
                    logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    logger.error(f"Failed to create directory {dir_path}: {str(e)}")

            # Check permissions
            readable = os.access(dir_path, os.R_OK) if exists else False
            writable = os.access(dir_path, os.W_OK) if exists else False
            executable = os.access(dir_path, os.X_OK) if exists else False

            # Try to write a test file
            write_test = False
            if exists and writable:
                test_file = os.path.join(
                    dir_path, f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
                )
                try:
                    with open(test_file, "w") as f:
                        f.write("test")
                    write_test = True
                    # Clean up
                    os.remove(test_file)
                except Exception as e:
                    logger.error(f"Failed to write test file in {dir_path}: {str(e)}")

            results[dir_path] = {
                "exists": exists,
                "readable": readable,
                "writable": writable,
                "executable": executable,
                "write_test": write_test,
            }
        except Exception as e:
            logger.error(f"Error checking directory {dir_path}: {str(e)}")
            results[dir_path] = {"error": str(e)}

    return results


def check_environment():
    """Check environment variables that are relevant to our application."""
    relevant_prefixes = [
        "GOOGLE_",
        "FIREBASE_",
        "GCP_",
        "CLOUD_",
        "PYTHON",
        "PATH",
        "HOME",
        "USER",
        "TEMP",
        "PORT",
    ]

    env_vars = {}
    for key, value in sorted(os.environ.items()):
        # Include if it starts with any of our prefixes (without showing sensitive values)
        if any(key.startswith(prefix) for prefix in relevant_prefixes):
            if "KEY" in key or "SECRET" in key or "PASSWORD" in key or "CREDENTIAL" in key:
                env_vars[key] = "[REDACTED]"
            else:
                env_vars[key] = value

    return env_vars


def check_firestore_connection():
    """Attempt to connect to Firestore and verify access."""
    try:
        from google.cloud import firestore

        logger.info("Initializing Firestore client")
        db = firestore.Client()

        # Try to list collections
        collections = [c.id for c in db.collections()]
        logger.info(f"Successfully connected to Firestore. Found collections: {collections}")

        return {"status": "success", "collections": collections}
    except Exception as e:
        logger.error(f"Firestore connection failed: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}


def get_system_info():
    """Get basic system information."""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "system": platform.system(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "cwd": os.getcwd(),
        "timestamp": datetime.now().isoformat(),
    }


def run_diagnostics():
    """Run all diagnostic checks and return results."""
    logger.info("Starting diagnostic checks")

    results = {
        "system_info": get_system_info(),
        "directory_checks": check_directories(),
        "environment": check_environment(),
    }

    # Only check Firestore if we're in a GCP environment
    if os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            results["firestore"] = check_firestore_connection()
        except ImportError:
            logger.warning("google-cloud-firestore not installed, skipping Firestore check")
            results["firestore"] = {"status": "skipped", "reason": "library not installed"}
    else:
        logger.info("Not in GCP environment, skipping Firestore check")
        results["firestore"] = {"status": "skipped", "reason": "not in GCP environment"}

    logger.info("Diagnostic checks completed")
    return results


if __name__ == "__main__":
    try:
        results = run_diagnostics()

        # Print results to stdout
        print(json.dumps(results, indent=2))

        # Also save to a file in /tmp
        output_file = f"/tmp/app_diagnostics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Diagnostic results saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error running diagnostics: {str(e)}", exc_info=True)
        print(f"Error running diagnostics: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
