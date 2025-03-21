# Conference Content Management and Discovery Platform

A scalable, cloud-native platform for managing, discovering, and analyzing conference content using Google Cloud services. This platform streamlines content uploads, enables AI-powered search and discovery, and provides insights into content usage.

## Features

- **Content Upload and Management**
  - File upload support for conference resources
  - Metadata management including title, track, tags, presenters, etc.
  - Support for drive links and external resources

- **Content Discovery**
  - AI-powered search capabilities (RAG)
  - Filtering by track, tags, and session types
  - Detailed content view with metadata

- **Mock Data Support**
  - Graceful fallback to mock data when cloud services are unavailable
  - Development-friendly error handling

## Architecture

- **Frontend**: Angular with Material Design
- **Backend**: Python Flask
- **Cloud Infrastructure**: Google Cloud Platform (GCP)
- **Database**: Firestore for metadata
- **Storage**: Google Cloud Storage for content files

## Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Google Cloud account with:
  - Firestore
  - Cloud Storage
- Service account credentials

### Backend Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your credentials:
   - Create a Google Cloud project
   - Enable required APIs (Firestore, Cloud Storage)
   - Create a service account and download the key as `credentials.json`
   - Place the credentials file in the project root

5. Create a `.env` file with:
   ```
   GCS_BUCKET_NAME=your-conference-content-bucket
   FLASK_SECRET_KEY=your_random_secret_key
   ```

6. Start the backend:
   ```
   python flask_app.py
   ```
   The server will run on port 3000 by default.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   ng serve
   ```

4. Access the application at http://localhost:4200

## API Endpoints

- **GET /**: Check if the API is running
- **POST /upload**: Upload content with metadata
- **GET /recent-content**: Get recent content with pagination
- **POST /rag/ask**: Ask a question using RAG
- **POST /rag/summarize**: Summarize a document using AI

## Development

The application is designed to work with or without cloud services. When cloud services are unavailable:

- Mock data will be provided instead of actual database records
- File URLs will be simulated
- All endpoints will return valid responses

This allows for development and testing without requiring a full cloud configuration.

## License

MIT 