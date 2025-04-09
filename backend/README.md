# Conference CMS FastAPI Backend

This is the FastAPI implementation of the Conference Content Management System API. It provides endpoints for managing conference materials with Google Drive integration and RAG capabilities.

## Features

- Google Drive integration for importing files
- Document text extraction with page/slide tracking
- RAG capabilities using Vertex AI
- Vector search for similarity matching
- Content management and tagging
- Google OAuth authentication
- Firestore database integration

## Getting Started

### Prerequisites

- Python 3.9+
- Google Cloud account with Drive API enabled
- Google OAuth credentials
- Docker and Docker Compose (optional, for local development with Firestore emulator)

### Installation

1. Clone the repository
2. Navigate to the FastAPI backend directory:
   ```bash
   cd backend/fastapi_backend
   ```
3. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
4. Update the `.env` file with your credentials and settings

### Configuration

Create a `.env` file with the following settings:

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
FIRESTORE_PROJECT_ID=conference-cms
FIRESTORE_EMULATOR_HOST=localhost:8080

# Session Settings
SESSION_SECRET_KEY=your-secret-key

# RAG Settings
VERTEX_AI_PROJECT=your-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_MODEL_ID=text-bison
```

### Running the API

#### Local Development

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```
3. The API will be available at http://localhost:8000
4. Access the interactive documentation at http://localhost:8000/docs

#### Using Docker Compose (with Firestore Emulator)

```bash
docker-compose up
```

This will start both the FastAPI application and a Firestore emulator for local development.

### Authentication

The API uses Google OAuth for authentication. Follow these steps to authenticate:

1. Visit `/api/auth/login` in your browser
2. You will be redirected to Google's consent screen
3. After authentication, you will be redirected back to the application
4. Check authentication status at `/api/auth/status`

## API Documentation

The API provides the following endpoints:

### Authentication

- `GET /api/auth/login`: Initiate OAuth login flow
- `GET /api/auth/callback`: Handle OAuth callback
- `GET /api/auth/logout`: Log out
- `GET /api/auth/status`: Check authentication status

### Drive Integration

- `GET /api/drive/files`: List files from Google Drive
- `GET /api/drive/files/{file_id}`: Get metadata for a specific Drive file
- `POST /api/drive/import`: Import files from Google Drive

### Content Management

- `GET /api/content/`: List all content with pagination
- `GET /api/content/{content_id}`: Get content by ID
- `POST /api/content/`: Create new content with optional file upload
- `PUT /api/content/{content_id}`: Update existing content
- `DELETE /api/content/{content_id}`: Delete content
- `POST /api/content/search`: Search for content

### RAG Capabilities

- `POST /api/rag/ask`: Ask a question about content
- `POST /api/rag/{content_id}/summarize`: Generate a summary of content
- `POST /api/rag/{content_id}/tags`: Generate tags for content
- `GET /api/rag/{content_id}/similar`: Find similar content

## Developer Tools

The project includes several tools to maintain code quality and provide a better developer experience:

### API Documentation

We use OpenAPI extensions for detailed API documentation. The API documentation is available at:

- `/api/docs` - Custom Swagger UI for exploring the API

### Code Quality Tools

The following tools are configured for code quality:

- **Black**: Code formatter that ensures a consistent code style
- **Flake8**: Linter that checks for style and potential bugs
- **isort**: Sorts and organizes import statements
- **mypy**: Static type checker for Python

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. To set up:

1. Install pre-commit: `pip install pre-commit`
2. Install hooks: `pre-commit install`

The pre-commit configuration will automatically check your code for:
- Formatting issues
- Linting errors
- Type checking issues
- Trailing whitespace and other common issues

### Logging

The application uses structured logging with `structlog` to generate JSON logs that are easily parsable by log analysis tools.

## Development

### Project Structure

```
backend/fastapi_backend/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── content.py      # Content management endpoints
│   │       ├── drive.py        # Drive integration endpoints
│   │       └── rag.py          # RAG endpoints
│   ├── core/
│   │   ├── auth.py             # Authentication utilities
│   │   └── config.py           # Application settings
│   ├── db/
│   │   └── firestore_client.py # Firestore client
│   ├── models/
│   │   └── content.py          # Pydantic models
│   ├── repositories/
│   │   └── content_repository.py # Data access layer
│   ├── services/
│   │   ├── content_service.py  # Content service
│   │   ├── drive_service.py    # Drive integration service
│   │   ├── extraction_service.py # Text extraction service
│   │   └── rag_service.py      # RAG service
│   └── utils/                  # Utility functions
├── tests/                      # Unit and integration tests
├── .env                        # Environment variables
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker configuration
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
└── setup.sh                    # Setup script
```

### Testing

Run tests with pytest:

```bash
pytest
```

## Deployment

### Google Cloud Run

1. Build the Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/conference-cms-api
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy conference-cms-api \
     --image gcr.io/your-project-id/conference-cms-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Environment Variables for Production

Make sure to set these environment variables in your production environment:

- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth callback URL
- `FRONTEND_URL`: URL of your frontend application
- `FIRESTORE_PROJECT_ID`: GCP project ID for Firestore
- `SESSION_SECRET_KEY`: Secret key for session encryption
- `VERTEX_AI_PROJECT`: GCP project ID for Vertex AI
- `VERTEX_AI_LOCATION`: Region for Vertex AI
- `VERTEX_MODEL_ID`: Model ID for RAG

## Contributing

1. Create a feature branch from main
2. Make your changes
3. Write tests for your changes
4. Submit a pull request 