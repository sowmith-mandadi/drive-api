# File Indexing Service Guide

## Overview

This guide explains how to use the indexing service for the file upload API system. The indexing service allows you to:

- Automatically index files as they are uploaded
- Manually index existing content in your Firestore database
- Track the status of indexing tasks

## Architecture

The indexing service consists of several components:

1. **IndexService class** - Core service that generates payloads and sends them to the external indexer API
2. **Standalone scripts**:
   - `generate_index_payload.py` - Generates payloads from Firestore content
   - `index_content.py` - Sends payloads to the indexer API
   - `index_all_content.py` - Master script that combines generation and sending

## Configuration

Set the following environment variables in your App Engine configuration:

```
INDEXER_API_ENDPOINT=https://your-indexer-api.com/index
```

## Automatic Indexing

When files are uploaded through the API, the system will:

1. Upload files to Google Cloud Storage
2. Store metadata in Firestore
3. Automatically trigger the indexing service
4. Group content by session ID
5. Send a payload to the indexer API
6. Track the task ID in Firestore

No additional configuration is needed once the environment variables are set.

## Manual Indexing

### Index All Content

To manually index all content in your Firestore database:

```bash
python index_all_content.py --endpoint https://your-indexer-api.com/index
```

Optional parameters:
- `--credentials` - Path to service account credentials file
- `--output-dir` - Directory to store payload JSON files (default: ./payloads)
- `--collection` - Firestore collection name (default: content)
- `--timeout` - Timeout in seconds between API calls (default: 5)
- `--limit` - Maximum number of documents to process (default: 100)

### Generate Payloads Only

To generate payload files without sending them to the indexer API:

```bash
python generate_index_payload.py --output-dir ./payloads
```

Optional parameters:
- `--credentials` - Path to service account credentials file
- `--collection` - Firestore collection name (default: content)
- `--limit` - Maximum number of documents to process (default: 100)

### Send Existing Payloads

To send existing payload files to the indexer API:

```bash
python index_content.py --input-dir ./payloads --endpoint https://your-indexer-api.com/index
```

Optional parameters:
- `--timeout` - Timeout in seconds between API calls (default: 5)

### Check Task Status

To check the status of submitted indexing tasks:

```bash
python index_content.py --endpoint https://your-indexer-api.com/index --check-only
```

## Payload Format

The indexer expects payloads in the following format:

```json
{
  "session_id": "unique-session-identifier",
  "file_list": [
    {
      "file_id": "file-uuid",
      "filename": "example.pdf",
      "mime_type": "application/pdf",
      "url": "https://storage.googleapis.com/bucket/file.pdf",
      "metadata": {
        "key": "value"
      }
    }
  ]
}
```

## Tracking Task Status

The indexing service tracks task status in:

1. The `task_ids` field in Firestore documents
2. A local file (`indexing_results.json`) for the standalone scripts

Task statuses include:
- `submitted` - Task has been sent to the indexer API
- `completed` - Task has been completed successfully
- `error` - An error occurred while processing the task
- `unknown` - Could not determine the task status

## Deployment Management

### Stopping Deployments

To stop a deployment that's currently in progress:

```bash
gcloud app versions cancel-deployment VERSION_ID
```

To list all ongoing operations:

```bash
gcloud app operations list
```

To cancel a specific operation:

```bash
gcloud app operations cancel OPERATION_ID
```

After stopping a deployment, you can deploy a new version:

```bash
gcloud app deploy
```

### Permissions Management

If encountering 403 errors or insufficient permissions when accessing Firestore or other Google Cloud services from App Engine:

```bash
# Get your current project ID
gcloud config get-value project
```

#### Granting Firestore Access

Grant basic Firestore access to your App Engine service account:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com \
  --role=roles/datastore.user
```

For administrative access to Firestore:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com \
  --role=roles/datastore.owner
```

#### Granting Storage Access

Grant Cloud Storage access for file uploads:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:YOUR_PROJECT_ID@appspot.gserviceaccount.com \
  --role=roles/storage.objectAdmin
```

#### Verifying Permissions

Verify the permissions have been applied correctly:

```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:YOUR_PROJECT_ID@appspot.gserviceaccount.com"
```

### Additional Deployment Commands

View deployed versions:

```bash
gcloud app versions list
```

Set traffic splitting between versions:

```bash
gcloud app services set-traffic default --splits=VERSION1=0.8,VERSION2=0.2
```

Migrate traffic immediately to a new version:

```bash
gcloud app services set-traffic default --splits=VERSION=1.0 --migrate
```

View application logs:

```bash
gcloud app logs tail -s default
```

## Troubleshooting

### Common Issues

1. **API Endpoint Not Configured**
   - Ensure `INDEXER_API_ENDPOINT` is set in your environment

2. **Connection Errors**
   - Check your network connectivity
   - Verify the API endpoint is correct and accessible

3. **Rate Limiting**
   - Increase the timeout between requests using the `--timeout` parameter

4. **Authentication Errors**
   - Check if the API requires authentication and provide the appropriate headers

### Logs

Check the application logs to troubleshoot issues:

```bash
gcloud app logs tail -s default
```

## Development Notes

When modifying the indexing service, consider:

1. The service is designed to group content by session ID
2. A single payload is created per session with all related files
3. Task IDs are tracked to check indexing status later
4. Timeouts between API calls are configurable 