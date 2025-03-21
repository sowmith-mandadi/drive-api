# Conference Content Management System Setup Guide

This guide provides detailed instructions for setting up the Conference Content Management System.

## Google Cloud Setup

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown at the top of the page.
3. Click "New Project" and give it a name (e.g., "conference-cms").
4. Click "Create" to create the project.

### 2. Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library".
2. Search for and enable the following APIs:
   - Cloud Firestore API
   - Cloud Storage API

### 3. Create Service Account Credentials

1. In the Google Cloud Console, go to "APIs & Services" > "Credentials".
2. Click "Create Credentials" and select "Service Account".
3. Enter a name for the service account (e.g., "conference-cms-service").
4. Grant the service account the following roles:
   - Storage Admin
   - Firestore Admin
5. Click "Done" to create the service account.
6. Click on the service account in the list, then go to the "Keys" tab.
7. Click "Add Key" > "Create new key", select JSON format, and click "Create".
8. The key file will be downloaded to your computer. Rename it to `credentials.json` and place it in the project root directory.

### 4. Create a Google Cloud Storage Bucket

1. In the Google Cloud Console, go to "Storage" > "Browser".
2. Click "Create Bucket".
3. Enter a globally unique name for your bucket (e.g., "your-conference-content-bucket").
4. Choose a region for your bucket (e.g., "us-central1").
5. Leave other settings as default and click "Create".

## Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd drive-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your configuration values:
   ```
   GCS_BUCKET_NAME=your-conference-content-bucket
   FLASK_SECRET_KEY=your_random_secret_key
   ```

6. Start the backend server:
   ```bash
   python flask_app.py
   ```
   
   The server will run on port 3000 by default.

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Update the API URL in `src/environments/environment.ts`:
   ```typescript
   export const environment = {
     production: false,
     apiUrl: 'http://localhost:3000',
   };
   ```

4. Start the development server:
   ```bash
   ng serve
   ```

5. Access the application at http://localhost:4200

## Development Notes

The application is designed to work even without a connection to Google Cloud:

- If Firestore is unavailable, mock data will be returned
- If Cloud Storage is unavailable, mock file URLs will be generated
- All endpoints will return valid responses regardless of cloud connectivity

This allows for development and testing without requiring a full cloud configuration.

## Troubleshooting

- **CORS Issues**: The backend is configured to allow requests from various origins. If you encounter CORS issues, check the CORS configuration in `flask_app.py`.
- **Storage Issues**: Verify that your service account has the proper permissions for Google Cloud Storage and that your bucket name is correctly set in the `.env` file.
- **No `.env` File**: If you don't have a `.env` file, the application will use default values. Create one based on the `.env.example` file. 