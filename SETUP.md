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
   - Vertex AI API (if using RAG features)

### 3. Create Service Account Credentials

1. In the Google Cloud Console, go to "APIs & Services" > "Credentials".
2. Click "Create Credentials" and select "Service Account".
3. Enter a name for the service account (e.g., "conference-cms-service").
4. Grant the service account the following roles:
   - Storage Admin
   - Firestore Admin
   - Vertex AI User (if using RAG features)
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
   cd conference-cms
   ```

2. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use env\Scripts\activate
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
   FLASK_SECRET_KEY=your_random_secret_key
   GCS_BUCKET_NAME=your-conference-content-bucket
   VERTEX_AI_LOCATION=us-central1
   VERTEX_AI_PROJECT_ID=your-project-id
   VECTOR_INDEX_ENDPOINT=your-vector-index-endpoint
   VECTOR_INDEX_ID=your-vector-index-id
   ```

6. Start the backend server:
   ```bash
   python run.py
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
   npm start
   ```

5. Access the application at http://localhost:4200 (or another port if 4200 is occupied)

## Vector Search Setup (Optional)

If you want to use the similarity search features with Google's Vector Search:

1. Create a Vector Search Index:
   ```bash
   gcloud ai vector-indexes create \
     --display-name=conference-content-index \
     --location=us-central1 \
     --dimensions=768 \
     --embedding-model=textembedding-gecko
   ```

2. Create a Vector Search Index Endpoint:
   ```bash
   gcloud ai vector-index-endpoints create \
     --display-name=conference-content-endpoint \
     --location=us-central1
   ```

3. Deploy the index to the endpoint:
   ```bash
   gcloud ai vector-index-endpoints deploy-index \
     --index-endpoint=your-endpoint-id \
     --index=your-index-id \
     --deployed-index-id=deployed-index \
     --location=us-central1
   ```

4. Add the endpoint and index IDs to your `.env` file

## Development Mode

The application is designed to work even without a connection to Google Cloud:

- If Firestore is unavailable, an in-memory store will be used with mock data
- If Cloud Storage is unavailable, mock file URLs will be generated
- If Vertex AI is unavailable, simulated AI responses will be provided

This allows for development and testing without requiring a full cloud configuration.

## Troubleshooting

- **CORS Issues**: The backend is configured to allow requests from various origins. If you encounter CORS issues, check the CORS configuration in `app/__init__.py`.
- **Storage Issues**: Verify that your service account has the proper permissions for Google Cloud Storage and that your bucket name is correctly set in the `.env` file.
- **No `.env` File**: If you don't have a `.env` file, the application will use default values for development mode. Create one based on the `.env.example` file for production use. 