# Conference CMS Architecture Documentation

## 1. System Overview
```
[Frontend Layer]
    - Angular Application
        - User Interface Components
        - Angular Services
        - State Management
        - HTTP Client

[Backend Layer]
    - Flask API Server
        - REST API Endpoints
        - Business Logic Services
        - Data Access Layer
        - Authentication/Authorization

[Cloud Layer]
    - Google Cloud Platform Services
        - Vertex AI (for RAG)
        - Firestore (Database)
        - Cloud Storage (File Storage)
        - Vector Search (Semantic Search)
        - Google Drive API
```

## 2. Component Relationships
```
Frontend Components:
    - Search Component
        → ContentService
    - Content Detail Component
        → ContentService
    - Upload Component
        → ContentService
    - Header/Footer
        → Shared Services

Backend Services:
    - ContentService
        → Firestore
        → Cloud Storage
    - RAGService
        → Vertex AI
        → Vector Search
    - DriveService
        → Google Drive API
```

## 3. Data Flow (RAG Feature)
```
1. User Input
   ↓
2. Frontend Service
   ↓
3. Backend API (/rag/ask)
   ↓
4. Vector Search
   ↓
5. Vertex AI
   ↓
6. Response to User
```

## 4. Content Processing Flow
```
Upload Path:
1. File Upload
   ↓
2. Document Processing
   ↓
3. Text Extraction
   ↓
4. Generate Embeddings
   ↓
5. Store in Vector DB

Storage Path:
1. Original File
   ↓
2. Cloud Storage
   ↓
3. Metadata
   ↓
4. Firestore
```

## 5. Security Layers
```
Client Layer:
    - Web Browser
    - OAuth Flow

Security Layer:
    - HTTPS
    - Authentication
    - Authorization

API Layer:
    - Rate Limiting
    - Input Validation
```

## 6. Environment Setup
```
Development:
    - Local API Server
    - Mock Data
    - Development Tools

Production:
    - Gunicorn Server
    - Cloud Database
    - Cloud Storage
```

## Key Technical Features

### Frontend
- Angular 13+
- Material Design Components
- Responsive Layout
- State Management with Services
- HTTP Interceptors for API Calls

### Backend
- Flask REST API
- Google Cloud Integration
- Document Processing
- RAG Implementation
- Vector Search

### Cloud Services
- Vertex AI for RAG
- Firestore for Data Storage
- Cloud Storage for Files
- Vector Search for Semantic Search
- Google Drive Integration

### Security
- OAuth 2.0 Authentication
- HTTPS Encryption
- Rate Limiting
- Input Validation
- Secure File Handling

### Development
- Local Development Environment
- Mock Data Support
- Testing Infrastructure
- CI/CD Pipeline
- Environment Configuration 