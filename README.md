# Conference Content Management API with Google Drive Integration

This application provides content management for conference materials with advanced Retrieval-Augmented Generation (RAG) capabilities using Google Vertex AI. It consists of a FastAPI backend API and an Angular frontend, with seamless Google Drive integration for importing and managing conference content.

## Features

- Upload and store conference content (presentations, documents, etc.)
- Extract text from uploaded documents (PDF, PowerPoint) with page/slide tracking
- Generate embeddings for content and metadata
- Index content in Vector Search for similarity search
- Provide RAG-powered answers to questions about the content
- Find similar documents based on semantic similarity
- Generate AI summaries and tags for uploaded content
- Import files directly from Google Drive with OAuth authentication
- Advanced search capabilities across all conference materials

## Project Structure

```
/
├── backend/              # FastAPI backend API
│   ├── app/              # Main application
│   │   ├── api/          # API routes and controllers
│   │   ├── core/         # Core configuration and utilities
│   │   ├── db/           # Database clients
│   │   ├── models/       # Data models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic services
│   │   └── utils/        # Utility functions
│   ├── tests/            # Test suite
│   ├── Dockerfile        # Docker configuration
│   ├── docker-compose.yml # Docker Compose configuration
│   ├── main.py           # Application entry point
│   └── requirements.txt  # Python dependencies
├── frontend/             # Angular frontend
│   ├── src/              # Angular source code
│   │   ├── app/          # Application components
│   │   │   ├── components/ # UI components
│   │   │   ├── services/ # Frontend services
│   │   │   └── models/   # Data models
│   │   ├── assets/       # Static assets
│   │   └── environments/ # Environment configurations
│   └── package.json      # NPM dependencies
├── .env                  # Environment variables (not in repo)
├── credentials.json      # GCP credentials (not in repo)
└── setup.sh              # Setup script for the FastAPI backend
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js and npm for frontend
- Google Cloud Platform account with the following services enabled:
  - Vertex AI API
  - Firestore
  - Cloud Storage
  - Vector Search (optional, for enhanced similarity search)
  - Google Drive API (for Google Drive integration)

### Backend Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd conference-cms
   ```

2. Run the setup script to create a virtual environment and install dependencies:
   ```
   chmod +x setup.sh
   ./setup.sh
   ```

3. Create a `credentials.json` file with your GCP service account key

4. Create a `.env` file in the backend directory with the following variables:
   ```
   # API Settings
   PORT=8000

   # Google API Settings
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback

   # Frontend URL
   FRONTEND_URL=http://localhost:4200

   # Firestore Settings
   FIRESTORE_PROJECT_ID=your-project-id
   FIRESTORE_EMULATOR_HOST=localhost:8080  # For local development

   # Session Settings
   SESSION_SECRET_KEY=your-secret-key

   # RAG Settings
   VERTEX_AI_PROJECT=your-project-id
   VERTEX_AI_LOCATION=us-central1
   VERTEX_RAG_MODEL=gemini-1.5-pro
   TEXT_EMBEDDING_MODEL=textembedding-gecko@latest

   # Vector Search Settings
   VECTOR_INDEX_ENDPOINT=your-vector-index-endpoint-id
   VECTOR_INDEX_ID=your-vector-index-id
   ```

### Frontend Installation

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

### Google Drive Integration Setup

To enable Google Drive integration:

1. Create a Google Cloud project and enable the Google Drive API
2. Create OAuth 2.0 credentials in the Google Cloud Console
3. Add the required scopes for Google Drive access:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.metadata.readonly`
4. Configure your OAuth consent screen with appropriate information
5. Add your authentication credentials to the `.env` file

### Vector Search Setup (Optional)

For enhanced similarity search capabilities, set up a Vector Search Index in Google Cloud:

1. Create a Vector Search Index:
   ```
   gcloud ai vector-indexes create \
     --display-name=conference-content-index \
     --location=us-central1 \
     --dimensions=768 \
     --embedding-model=textembedding-gecko
   ```

2. Create a Vector Search Index Endpoint:
   ```
   gcloud ai vector-index-endpoints create \
     --display-name=conference-content-endpoint \
     --location=us-central1
   ```

3. Deploy the index to the endpoint:
   ```
   gcloud ai vector-index-endpoints deploy-index \
     --index-endpoint=your-endpoint-id \
     --index=your-index-id \
     --deployed-index-id=deployed-index \
     --location=us-central1
   ```

4. Add the endpoint and index IDs to your `.env` file

## Running the Application

### Starting the Backend API

Navigate to the backend directory and start the FastAPI server:

```
cd backend
python main.py
```

The backend will run on http://localhost:8000

API documentation is available at http://localhost:8000/docs

### Using Docker Compose (with Firestore Emulator)

For local development with a Firestore emulator:

```
cd backend
docker-compose up
```

This will start both the FastAPI application and a Firestore emulator.

### Starting the Frontend

Navigate to the frontend directory and run:

```
npm start
```

The frontend will run on http://localhost:4200 (or another port if 4200 is occupied)

## API Endpoints

### Authentication

- `GET /api/auth/login`: Initiate OAuth login flow
- `GET /api/auth/callback`: Handle OAuth callback
- `GET /api/auth/logout`: Log out
- `GET /api/auth/status`: Check authentication status

### Content Management

- `GET /api/content/`: List all content with pagination
- `GET /api/content/{content_id}`: Get content by ID
- `POST /api/content/`: Create new content with optional file upload
- `PUT /api/content/{content_id}`: Update existing content
- `DELETE /api/content/{content_id}`: Delete content
- `POST /api/content/search`: Search for content
- `GET /api/content/recent`: Get recent content with pagination
- `GET /api/content/popular-tags`: Get most popular tags
- `POST /api/content/by-ids`: Get multiple content items by their IDs

### Drive Integration

- `GET /api/drive/files`: List files from Google Drive
- `GET /api/drive/files/{file_id}`: Get metadata for a specific Drive file
- `POST /api/drive/import`: Import files from Google Drive
- `GET /api/drive/folders`: List folders from Google Drive

### RAG Capabilities

- `POST /api/rag/ask`: Ask a question about content
- `POST /api/rag/{content_id}/summarize`: Generate a summary of content
- `POST /api/rag/{content_id}/tags`: Generate tags for content
- `GET /api/rag/{content_id}/similar`: Find similar content

### System Health

- `GET /api/health`: Basic health check
- `GET /api/health/info`: Detailed system information

## Document Processing

The API automatically processes the following document types:

- PDF files: Text is extracted with page number tracking
- PowerPoint files: Text is extracted with slide number tracking

This enables precise search results that reference the specific page or slide where information is found.

## Development Mode

The application can run in development mode without a complete GCP setup. In this mode:
- In-memory storage is used instead of Firestore and Cloud Storage
- Mock responses are provided for AI-related features
- All functionality can be tested without cloud dependencies

## Deployment

### Google Cloud Run

1. Build the Docker image:
   ```
   cd backend
   gcloud builds submit --tag gcr.io/your-project-id/conference-cms-api
   ```

2. Deploy to Cloud Run:
   ```
   gcloud run deploy conference-cms-api \
     --image gcr.io/your-project-id/conference-cms-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## License

[Your License]

## Security Considerations

The application implements the following security measures:
- OAuth 2.0 for secure Google Drive integration
- Secure storage of sensitive credentials
- HTTPS for all API communication
- Input validation for all endpoints
- Rate limiting for API requests 