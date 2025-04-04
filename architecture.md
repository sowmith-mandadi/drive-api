# Conference CMS Architecture Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph Frontend[Angular Frontend]
        UI[User Interface]
        Services[Angular Services]
    end

    subgraph Backend[Flask Backend]
        API[API Layer]
        Services[Business Services]
        Repos[Data Repositories]
    end

    subgraph Cloud[Google Cloud Platform]
        VertexAI[Vertex AI]
        Firestore[Firestore DB]
        GCS[Cloud Storage]
        VectorSearch[Vector Search]
        Drive[Google Drive]
    end

    UI --> Services
    Services --> API
    API --> Services
    Services --> Repos
    Repos --> Firestore
    Repos --> GCS
    Services --> VertexAI
    Services --> VectorSearch
    Services --> Drive
```

## 2. Component Architecture

```mermaid
graph LR
    subgraph Frontend[Frontend Components]
        Search[Search Component]
        Content[Content Detail]
        Upload[Upload Component]
        Header[Header/Footer]
    end

    subgraph Backend[Backend Services]
        ContentService[Content Service]
        RAGService[RAG Service]
        AIService[AI Service]
        DriveService[Drive Service]
    end

    subgraph Data[Data Layer]
        Firestore[Firestore]
        Storage[Cloud Storage]
        VectorDB[Vector DB]
    end

    Search --> ContentService
    Content --> ContentService
    Upload --> ContentService
    ContentService --> Firestore
    ContentService --> Storage
    RAGService --> AIService
    RAGService --> VectorDB
    DriveService --> Drive
```

## 3. Data Flow for RAG Features

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant VectorDB
    participant VertexAI

    User->>Frontend: Ask Question
    Frontend->>Backend: POST /rag/ask
    Backend->>VectorDB: Search Similar Content
    VectorDB-->>Backend: Return Relevant Chunks
    Backend->>VertexAI: Generate Answer
    VertexAI-->>Backend: Return Answer
    Backend-->>Frontend: Return Response
    Frontend-->>User: Display Answer
```

## 4. Content Processing Pipeline

```mermaid
graph TD
    A[Upload Content] --> B[Document Processing]
    B --> C[Text Extraction]
    C --> D[Generate Embeddings]
    D --> E[Store in Vector DB]
    C --> F[Store in Firestore]
    A --> G[Store Files in GCS]
    
    subgraph Processing[Processing Steps]
        B
        C
        D
    end
    
    subgraph Storage[Storage Layer]
        E
        F
        G
    end
```

## 5. Security Architecture

```mermaid
graph TB
    subgraph Client[Client Layer]
        Browser[Web Browser]
        OAuth[OAuth Flow]
    end

    subgraph Security[Security Layer]
        HTTPS[HTTPS]
        Auth[Authentication]
        Authz[Authorization]
    end

    subgraph API[API Layer]
        RateLimit[Rate Limiting]
        Validation[Input Validation]
    end

    Browser --> HTTPS
    HTTPS --> Auth
    Auth --> OAuth
    Auth --> Authz
    Authz --> RateLimit
    RateLimit --> Validation
```

## 6. Development vs Production Environment

```mermaid
graph LR
    subgraph Dev[Development]
        LocalAPI[Local API Server]
        MockData[Mock Data]
        DevTools[Dev Tools]
    end

    subgraph Prod[Production]
        Gunicorn[Gunicorn Server]
        CloudDB[Cloud Database]
        CloudStorage[Cloud Storage]
    end

    Dev --> LocalAPI
    LocalAPI --> MockData
    Dev --> DevTools
    
    Prod --> Gunicorn
    Gunicorn --> CloudDB
    Gunicorn --> CloudStorage
``` 