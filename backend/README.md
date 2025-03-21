# Conference Content Management API

A Flask-based API for conference content management with RAG capabilities using Google Vertex AI.

## Project Structure

```
drive-api/
├── app/                    # Main application code
│   ├── api/                # API routes and blueprints
│   │   ├── content_routes.py
│   │   ├── health_routes.py
│   │   └── rag_routes.py
│   ├── extractors/         # Document text extractors
│   ├── models/             # Data models
│   ├── repository/         # Data access layer
│   │   ├── firestore_repo.py
│   │   ├── storage_repo.py
│   │   └── vector_repo.py
│   ├── services/           # Business logic layer
│   │   ├── ai_service.py
│   │   ├── content_service.py
│   │   ├── embedding_service.py
│   │   └── rag_service.py
│   └── utils/              # Utility functions
├── config/                 # Configuration
│   ├── environments/       # Environment-specific configurations
│   └── settings.py
├── scripts/                # Utility scripts
│   └── test_api.py
├── tests/                  # Test suite
├── run.py                  # Development entry point
└── wsgi.py                 # Production entry point
```

## Features

- Content upload and management
- RAG (Retrieval-Augmented Generation) for answering questions about content
- Document processing and embedding
- Vector search for finding similar content
- AI-generated summaries and tags

## Requirements

See `requirements.txt` in the root directory for all dependencies.

## Setup

1. Ensure you have Python 3.9+ installed
2. Install dependencies:
   ```
   pip install -r ../requirements.txt
   ```
3. Set up the necessary environment variables (see .env.example in the root directory)
4. Place your Google Cloud `credentials.json` file in the root directory

## Running the API

### Development

Run the API with hot reloading for development:

```bash
cd drive-api
python run.py
```

The API will be available at http://localhost:3000 by default.

### Production

For production deployment, use Gunicorn with the WSGI entry point:

```bash
cd drive-api
gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

## Testing

Run the API test script to validate all endpoints:

```bash
cd drive-api
python scripts/test_api.py
```

## API Documentation

### Health Check

- `GET /health` - Check API health

### Content Endpoints

- `GET /recent-content` - Get recent content with pagination
- `POST /content-by-ids` - Get content items by IDs
- `GET /popular-tags` - Get most popular tags
- `POST /upload` - Upload new content with files

### RAG Endpoints

- `POST /rag/ask` - Ask a question using RAG
- `POST /rag/summarize` - Generate an AI summary for content
- `POST /rag/generate-tags` - Generate AI tags for content
- `POST /rag/similar` - Find similar content items 