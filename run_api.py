#!/usr/bin/env python3
"""
Run API server script - launches the FastAPI server from the root directory.
"""
import os
import sys
import importlib.util
import argparse

def run_api(api_type="minimal"):
    """Run the API server based on specified type."""
    # Determine which API to run
    if api_type == "minimal":
        module_name = "api_minimal"
    elif api_type == "server":
        module_name = "api_server"
    else:
        print(f"Error: Unknown API type: {api_type}")
        print("Valid options are: 'minimal' or 'server'")
        sys.exit(1)
    
    # Set up the path to the module
    api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                           "backend", "fast_backend", f"{module_name}.py")
    
    if not os.path.exists(api_path):
        print(f"Error: Could not find API file at {api_path}")
        sys.exit(1)
    
    # Add the directory to the Python path
    fast_backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                   "backend", "fast_backend")
    sys.path.insert(0, fast_backend_dir)
    
    # Import and run the module
    try:
        import uvicorn
        
        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(module_name, api_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Run the API server
        port = int(os.getenv("PORT", "8000"))
        uvicorn.run(f"{module_name}:app", host="0.0.0.0", port=port, reload=True)
    except ImportError as e:
        print(f"Error: Failed to import required modules: {e}")
        print("Make sure uvicorn is installed by running:")
        print("pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"Error running API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Drive API server")
    parser.add_argument("--type", choices=["minimal", "server"], 
                        default="minimal", 
                        help="API type to run (minimal or server)")
    args = parser.parse_args()
    
    run_api(api_type=args.type) 