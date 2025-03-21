# Cursor Rules for Drive API Project

## Project Overview
This application provides content management for conference materials with advanced Retrieval-Augmented Generation (RAG) capabilities using Google Vertex AI. It consists of a Flask backend API and an Angular frontend.

## Architecture

### Backend (Flask)
- Located in `/backend` directory
- RESTful API written in Python with Flask
- Uses Google Vertex AI for text embedding and RAG features
- Core functionality:
  - Document upload and storage in Google Cloud Storage
  - Text extraction from documents (PDF, PowerPoint)
  - Vector embeddings generation
  - Similarity search via Vector Search
  - RAG-powered Q&A

### Frontend (Angular)
- Located in `/frontend` directory
- Single page application using Angular
- Communicates with backend via REST API
- Features:
  - Document upload interface
  - Content browsing and search
  - RAG-powered Q&A interface

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type annotations
- Structure:
  - `/app`: Main application code
  - `/app/core`: Core functionality and services
  - `/app/utils`: Utility functions
  - `/app/blueprints`: API routes organized by feature
  - `/tests`: Test files (pytest)

### TypeScript/Angular (Frontend)
- Follow Angular style guide
- Use strict typing
- Structure:
  - `/src/app/components`: UI components
  - `/src/app/services`: Data services
  - `/src/app/models`: Data models/interfaces

## API Structure

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

## Development Guidelines

### Environment Setup
- Use virtual environment for Python development
- Required environment variables are documented in `.env.example`
- Run `cloud_shell_setup.sh` for setting up Google Cloud Shell

### Testing
- Write tests for all new functionality
- Backend: Use pytest
- Frontend: Use Angular testing tools (Jasmine/Karma)
- Run tests before committing: `python run_all_tests.py`

### Git Workflow
- Main branch: `master`
- Create feature branches for new development
- Submit PRs for code review
- CI/CD pipeline runs tests on PR submission

### Security Guidelines
- Never commit credentials (they should be in .env, not in the repo)
- Use environment variables for all secrets
- Validate all user inputs
- Follow OWASP security guidelines

## Dependencies and Integration

### Google Cloud Services
- Vertex AI: For embeddings and RAG
- Cloud Storage: For storing documents
- Vector Search: For similarity search

### Development Dependencies
- Backend: See `backend/requirements.txt`
- Frontend: See `frontend/package.json`

## When Generating Code with Cursor

- Follow existing patterns in the codebase
- Maintain separation of concerns
- Add appropriate error handling
- Include tests for new functionality
- Update documentation when adding features 