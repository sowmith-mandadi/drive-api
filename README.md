# Conference Content Management API with RAG

This application provides content management for conference materials with advanced Retrieval-Augmented Generation (RAG) capabilities using Google Vertex AI. It consists of a Flask backend API and an Angular frontend.

## Features

- Upload and store conference content (presentations, documents, etc.)
- Extract text from uploaded documents (PDF, PowerPoint) with page/slide tracking
- Generate embeddings for content and metadata
- Index content in Vector Search for similarity search
- Provide RAG-powered answers to questions about the content
- Find similar documents based on semantic similarity
- Generate AI summaries and tags for uploaded content

## Project Structure

```
/
├── backend/              # Flask backend API
│   ├── app/              # Main application
│   │   ├── api/          # API routes and controllers
│   │   ├── extractors/   # Document extraction modules (PDF, PPTX)
│   │   ├── models/       # Data models
│   │   ├── repository/   # Data access layer
│   │   └── services/     # Business logic services
│   ├── config/           # Configuration files
│   ├── scripts/          # Utility scripts
│   └── tests/            # Test suite
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
├── run.py                # Application entry point
├── wsgi.py               # WSGI entry point for production
└── requirements.txt      # Python dependencies
```

## Setup

### Prerequisites

- Python 3.8+
- Node.js and npm for frontend
- Google Cloud Platform account with the following services enabled:
  - Vertex AI API
  - Firestore
  - Cloud Storage
  - Vector Search (optional, for enhanced similarity search)

### Backend Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd conference-cms
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `credentials.json` file with your GCP service account key

4. Create a `.env` file with the following variables:
   ```
   GCP_PROJECT_ID=your-project-id
   GCP_LOCATION=us-central1
   GCS_BUCKET_NAME=your-bucket-name
   VERTEX_RAG_MODEL=gemini-1.5-pro
   VECTOR_INDEX_ENDPOINT=your-vector-index-endpoint-id  # Optional
   VECTOR_INDEX_ID=your-vector-index-id  # Optional
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

Start the API server:

```
python run.py
```

The backend will run on http://localhost:3000

For production deployment, use Gunicorn:

```
gunicorn -w 4 -b 0.0.0.0:3000 wsgi:app
```

### Starting the Frontend

Navigate to the frontend directory and run:

```
npm start
```

The frontend will run on http://localhost:4200 (or another port if 4200 is occupied)

## API Endpoints

### Content Management

- `POST /upload`: Upload conference content with metadata
- `POST /content-by-ids`: Get multiple content items by their IDs
- `GET /popular-tags`: Get most popular tags
- `GET /recent-content`: Get recent content with pagination

### RAG Features

- `POST /rag/ask`: Ask a question using RAG
- `POST /rag/summarize`: Summarize a document using Vertex AI
- `POST /rag/generate-tags`: Generate tags for a document using Vertex AI
- `POST /rag/similar`: Find similar documents based on a query or content ID

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

## License

[Your License] 