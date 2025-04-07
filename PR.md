# Fix API Structure and Add Convenience Scripts

## Changes

- Added `run_api.py` script in the root directory to make it easy to run the FastAPI backend
- Added `setup_fastapi.sh` script to help set up the Python environment for FastAPI
- Updated README.md with instructions on how to run the FastAPI backend

## Why This Change

Previously, users were trying to run the API scripts directly from the root directory, which didn't work:

```
python api_server.py
python api_minimal.py
python3 api_minimal.py
```

These commands were failing with "No such file or directory" errors because the API scripts are located in the `backend/fast_backend` directory.

The new `run_api.py` script enables users to run the API scripts from the root directory without having to navigate to the backend directory. It automatically adds the necessary paths to the Python path and launches the API server.

## How to Test

1. Set up the FastAPI environment:
   ```
   ./setup_fastapi.sh
   ```

2. Run the minimal API:
   ```
   python run_api.py
   ```

3. Or run the full server API:
   ```
   python run_api.py --type server
   ```

4. Visit http://localhost:8000 and http://localhost:8000/docs to verify the API is running 