# Vector Processing Backend

This document describes how to set up and configure the vector processing backend that integrates with the main Conference CMS API.

## Overview

The vector processing backend is a separate service that:

1. Listens for file processing tasks via Cloud Tasks
2. Retrieves files from Google Cloud Storage
3. Processes files using Vertex AI
4. Stores vector embeddings in a vector database

## Prerequisites

- Google Cloud Platform account
- Project with the following APIs enabled:
  - Cloud Storage
  - Cloud Tasks
  - Vertex AI
  - Firestore
  - App Engine or Cloud Run (for hosting)

## Setup Instructions

### 1. Create Google Cloud Resources

#### Create Cloud Storage Bucket

```bash
gcloud storage buckets create gs://YOUR_PROJECT_ID-uploads
```

#### Create Cloud Tasks Queue

```bash
gcloud tasks queues create vector-processing \
  --location=us-central1
```

### 2. Configure IAM Permissions

Ensure the service accounts for both backends have appropriate permissions:

- Main Backend Service Account:
  - Storage Object Creator (`roles/storage.objectCreator`)
  - Cloud Tasks Enqueuer (`roles/cloudtasks.enqueuer`)

- Vector Processing Backend Service Account:
  - Storage Object Viewer (`roles/storage.objectViewer`)
  - Vertex AI User (`roles/aiplatform.user`)
  - Cloud Tasks Admin (`roles/cloudtasks.admin`)

### 3. Deploy Vector Processing Backend

1. Create a new App Engine service or Cloud Run service
2. Deploy with the following environment variables:

```yaml
env_variables:
  GCS_BUCKET_NAME: "YOUR_PROJECT_ID-uploads"
  VECTOR_DB_ENDPOINT: "YOUR_VECTOR_DB_ENDPOINT"
  VERTEX_AI_LOCATION: "us-central1"
  VERTEX_AI_PROJECT: "YOUR_PROJECT_ID"
  TEXT_EMBEDDING_MODEL: "textembedding-gecko@latest"
  FIRESTORE_PROJECT_ID: "YOUR_PROJECT_ID"
```

## API Endpoint

The vector processing backend should expose the following endpoint:

### POST /api/process

Processes a file for vector embedding.

**Request Body:**

```json
{
  "content_id": "string",
  "gcs_path": "string",
  "file_url": "string",
  "file_name": "string",
  "content_type": "string"
}
```

**Response:**

```json
{
  "status": "success|error",
  "message": "string",
  "content_id": "string"
}
```

## Integration Flow

1. Main backend uploads file to GCS
2. Main backend creates a Cloud Task with file metadata
3. Vector processor backend receives the task
4. Vector processor retrieves file from GCS
5. Vector processor extracts text using Vertex AI
6. Vector processor generates embeddings
7. Vector processor stores embeddings in vector database
8. Vector processor updates content status in Firestore

## Monitoring and Debugging

- Monitor Cloud Tasks queue in GCP Console
- Check logs for both backends in Cloud Logging
- Monitor Vertex AI usage and quotas

## Development Setup

To develop and test locally, set up a local environment with the necessary emulators:

1. Install Google Cloud SDK
2. Run Cloud Tasks emulator for local development
3. Run Firestore emulator for local development
4. Use environment variables to point to local emulators
